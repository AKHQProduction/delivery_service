from dataclasses import dataclass


@dataclass
class GeoConfig:
    city: str
    user_agent: str
