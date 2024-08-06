from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from geopy.geocoders import Nominatim
from _mock_data_.user_addr import customer_addr, driver_poss

router = APIRouter()
geolocator = Nominatim(user_agent="hordiienkoq")
customer_location = geolocator.geocode(customer_addr)
driver_location = geolocator.geocode(driver_poss)

@router.get("/geocode")
async def geocode():
    print(customer_location)
    if customer_location and driver_location:
        return JSONResponse(
            content = {
                "customer": {
                    "latitude": customer_location.latitude, 
                    "longitude": customer_location.longitude
                },
                "driver": {
                    "latitude": driver_location.latitude, 
                    "longitude": driver_location.longitude
                }
                }
            )
    else:
        return JSONResponse(content={"error": "Address not found"}, status_code=404)