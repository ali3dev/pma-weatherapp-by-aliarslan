from fastapi import FastAPI
from app.database import Base, engine

# import models so tables are registered with SQLAlchemy
from app.models import history_model  # noqa: F401
from app.routes import weather_routes, forecast_routes, export_routes, history_routes

# database tables creation
Base.metadata.create_all(bind=engine)

# main app init
app = FastAPI(title="SkyCast CRUD Weather API")

# routes register karna
app.include_router(weather_routes.router)
app.include_router(forecast_routes.router)
app.include_router(export_routes.router)
app.include_router(history_routes.router)

# root endpoint
@app.get("/")
def root():
    return {"message": "Welcome to SkyCast CRUD Weather API"}
