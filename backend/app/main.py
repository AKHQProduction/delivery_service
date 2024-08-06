from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
from routes.getGeocode import router as geocode

app = FastAPI()

templates = Jinja2Templates(directory=str(Path(__file__).parent))

app.include_router(geocode)

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

