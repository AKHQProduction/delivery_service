from dataclasses import dataclass


@dataclass(eq=False)
class AddressNotFoundInCityError(Exception):
    address: str
    city: str

    @property
    def message(self):
        return f"{self.address} is not exists in the city {self.city}"


@dataclass(eq=False)
class InvalidAddressInputError(Exception):
    pass


@dataclass(eq=False)
class GeolocatorBadGatewayError(Exception):
    @property
    def message(self):
        return "Service is not work"
