from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
from routes.getGeocode import router as geocode
from fastapi.staticfiles import StaticFiles

app = FastAPI()

templates = Jinja2Templates(directory=str(Path(__file__).parent))

app.include_router(geocode)

app.mount("/", StaticFiles(directory="../../frontend/dist", html=True), name="static")

