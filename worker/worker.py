import os
import json
import time
import redis

# Grab the same Redis connection string as FastAPI
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
redis_client = redis.Redis.from_url(REDIS_URL, decode_responses=True)

QUEUE_NAME = "trip_tasks"

def process_trip_itinerary(task_data: dict):
    """Simulates a heavy, long-running task like generating an AI itinerary."""
    trip_id = task_data.get("trip_id")
    destination = task_data.get("destination")
    
    print(f"--> [Worker] Starting background task for Trip #{trip_id} ({destination})...")
    
    # Simulate heavy computation / external API calls
    time.sleep(5) 
    
    print(f"--> [Worker] Successfully generated itinerary for Trip #{trip_id} in {destination}!")

def start_worker():
    print("--> [Worker] Listening for jobs on queue:", QUEUE_NAME)
    
    while True:
        try:
            # blpop (Blocking Left Pop) waits until a message arrives on the queue.
            # Timeout = 0 means wait indefinitely.
            queue_name, message = redis_client.blpop(QUEUE_NAME, timeout=0)
            
            # Parse JSON message payload
            task_data = json.loads(message)
            process_trip_itinerary(task_data)
            
        except Exception as e:
            print(f"--> [Worker] Error processing job: {e}")
            time.sleep(1)

if __name__ == "__main__":
    start_worker()