from fastapi import FastAPI

app = FastAPI(title="Smart Travel Planner API")

@app.get("/health")
def health_check():
    return {"status": "ok"}