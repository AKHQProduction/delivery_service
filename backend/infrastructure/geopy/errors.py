from dataclasses import dataclass


@dataclass(eq=False)
class AddressIsNotExists(Exception):
    address: str
    city: str

    @property
    def message(self):
        return f"{self.address} is not exists in the city {self.city}"
