from dataclasses import dataclass


@dataclass(eq=False)
class LocationNotFoundError(Exception):
    pass
