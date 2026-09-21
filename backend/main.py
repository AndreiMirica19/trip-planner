import os
import json
from typing import Optional, List
import redis
from fastapi import FastAPI, Depends
from sqlmodel import Field, SQLModel, create_engine, Session, select

app = FastAPI(title="Smart Travel Planner API")

# Environment variables from docker-compose.yml
DATABASE_URL = os.getenv("DATABASE_URL")
REDIS_URL = os.getenv("REDIS_URL")

# Connections
engine = create_engine(DATABASE_URL)
redis_client = redis.Redis.from_url(REDIS_URL, decode_responses=True)


class Trip(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    destination: str
    currency: str = "EUR"


@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)


def get_db():
    with Session(engine) as session:
        yield session


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/trips", response_model=Trip)
def create_trip(trip: Trip, db: Session = Depends(get_db)):
    # 1. Save trip to PostgreSQL
    db.add(trip)
    db.commit()
    db.refresh(trip)

    # 2. Invalidate cache
    redis_client.delete("trips:all")

    # 3. Push a job to the Redis queue for the background worker
    task_payload = json.dumps({
        "trip_id": trip.id,
        "destination": trip.destination,
        "title": trip.title
    })
    redis_client.rpush("trip_tasks", task_payload)

    return trip


@app.get("/trips", response_model=List[Trip])
def get_trips(db: Session = Depends(get_db)):
    # 1. Check Redis Cache
    cached_trips = redis_client.get("trips:all")
    if cached_trips:
        print("--- CACHE HIT: Returning data from Redis ---")
        return json.loads(cached_trips)

    # 2. Cache Miss: Query Postgres
    print("--- CACHE MISS: Querying PostgreSQL ---")
    trips = db.exec(select(Trip)).all()

    # 3. Serialize SQLModel objects to dicts for JSON storage
    trips_data = [trip.model_dump() for trip in trips]

    # 4. Store in Redis with a 5-minute expiration (300 seconds)
    redis_client.set("trips:all", json.dumps(trips_data), ex=300)

    return trips