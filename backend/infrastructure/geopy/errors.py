from dataclasses import dataclass

from geopy.exc import GeocoderTimedOut


@dataclass(eq=False)
class AddressIsNotExists(Exception):
    address: str
    city: str

    @property
    def message(self):
        return f"{self.address} is not exists in the city {self.city}"


@dataclass(eq=False)
class GeolocatorBadGateway(Exception):
    @property
    def message(self):
        return "Service is not work"
