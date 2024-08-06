from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from geopy.geocoders import Nominatim
from pathlib import Path
app = FastAPI()

templates = Jinja2Templates(directory=str(Path(__file__).parent))

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/geocode")
async def geocode(request: Request):
    body = await request.json()
    address = body.get('address')
    geolocator = Nominatim(user_agent="hordiienkoq")
    location = geolocator.geocode(address)
    if location:
        return JSONResponse(content={"latitude": location.latitude, "longitude": location.longitude})
    else:
        return JSONResponse(content={"error": "Address not found"}, status_code=404)
