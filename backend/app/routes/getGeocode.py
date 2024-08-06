from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse, HTMLResponse

from geopy.geocoders import Nominatim

router = APIRouter()

@router.post("/geocode")
async def geocode(request: Request):
    body = await request.json()
    address = body.get('address')
    geolocator = Nominatim(user_agent="hordiienkoq")
    location = geolocator.geocode(address)
    if location:
        return JSONResponse(content={"latitude": location.latitude, "longitude": location.longitude})
    else:
        return JSONResponse(content={"error": "Address not found"}, status_code=404)