from fastapi import FastAPI
from app.routes import weather_routes, forecast_routes

app = FastAPI(title="SkyCast Core")

app.include_router(weather_routes.router)
app.include_router(forecast_routes.router)

@app.get("/")
def root():
    return {"message": "Welcome to SkyCast Core - Real-Time Weather API"}
