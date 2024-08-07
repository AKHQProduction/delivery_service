from fastapi import FastAPI
from routes.getGeocode import router as geocode
from fastapi.staticfiles import StaticFiles

app = FastAPI()

app.include_router(geocode)

app.mount("/", StaticFiles(directory="../frontend/dist", html=True), name="static")
