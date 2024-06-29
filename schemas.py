from dataclasses import dataclass
from pydantic import BaseModel
from enum import Enum


############################
# DTO ######################
@dataclass
class Bus:
    busId: str
    lat: float
    lng: float
    route: str


@dataclass
class WindowBounds:
    south_lat: float
    north_lat: float
    west_lng: float
    east_lng: float

    def is_inside(self, lat, lng) -> bool:
        inside_lat = self.south_lat < lat < self.north_lat
        inside_lng = self.west_lng < lng < self.east_lng
        return inside_lat and inside_lng

    def update(self, south_lat, north_lat, west_lng, east_lng):
        self.south_lat = south_lat
        self.north_lat = north_lat
        self.west_lng = west_lng
        self.east_lng = east_lng


############################
# Validation Schemas #######
class MessageType(str, Enum):
    new_bounds = 'newBounds'
    buses = 'Buses'
    errors = 'Errors'


class CoordinatesSchema(BaseModel):
    south_lat: float
    north_lat: float
    west_lng: float
    east_lng: float


class WindowBoundsSchema(BaseModel):
    msgType: MessageType
    data: CoordinatesSchema


class BusSchema(BaseModel):
    busId: str
    lat: float
    lng: float
    route: str
