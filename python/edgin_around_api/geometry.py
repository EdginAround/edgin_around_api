import abc, enum
from dataclasses import dataclass
from math import asin, atan2, cos, degrees, pi, radians, sin, sqrt

import marshmallow
from marshmallow import fields as mf
from marshmallow_oneofschema import OneOfSchema

from typing import Callable, Iterable, Iterator, List, Optional, Set, Tuple, cast


class Coordinates:
    @staticmethod
    def cartesian_to_spherical(x, y, z):
        r = sqrt(x * x + y * y + z * z)
        theta = atan2(sqrt(x * x + z * z), y) if y != 0.0 else 0.5 * pi
        phi = atan2(x, z) if z != 0.0 else 0.5 * pi
        return r, theta, phi

    @staticmethod
    def cartesian_to_geographical_radians(x, y, z):
        coords = Coordinates.cartesian_to_spherical(x, y, z)
        return Coordinates.spherical_to_geographical_radians(*coords)

    @staticmethod
    def cartesian_to_geographical_degrees(x, y, z):
        coords = Coordinates.cartesian_to_spherical(x, y, z)
        return Coordinates.spherical_to_geographical_degrees(*coords)

    @staticmethod
    def spherical_to_cartesian(r, theta, phi):
        z = r * sin(theta) * cos(phi)
        x = r * sin(theta) * sin(phi)
        y = r * cos(theta)
        return x, y, z

    @staticmethod
    def spherical_to_geographical_radians(r, theta, phi):
        lat = 0.5 * pi - theta
        lon = phi if phi <= pi else phi - 2.0 * pi
        return r, lat, lon

    @staticmethod
    def spherical_to_geographical_degrees(r, theta, phi):
        r, lat, lon = Coordinates.spherical_to_geographical_radians(r, theta, phi)
        return r, degrees(lat), degrees(lon)

    @staticmethod
    def geographical_radians_to_spherical(r, lat, lon):
        theta = 0.5 * pi - lat
        phi = lon if lon >= 0 else lon + 2.0 * pi
        return r, theta, phi

    @staticmethod
    def geographical_degrees_to_spherical(r, lat, lon):
        return Coordinates.geographical_radians_to_spherical(r, radians(lat), radians(lon))


class Coordinate:
    """Position expressed in geographical coordinates with radians."""

    def __init__(self, lat, lon) -> None:
        self.lat = lat
        self.lon = lon

    def bearing_to(self, other: "Coordinate") -> float:
        """Calculates bearing between two coordinates."""

        x = sin(other.lon - self.lon) * cos(other.lat)
        y = cos(self.lat) * sin(other.lat) - sin(self.lat) * cos(other.lat) * cos(
            other.lon - self.lon
        )

        return atan2(x, y)

    def great_circle_distance_to(self, other: "Coordinate", radius: float) -> float:
        sin1 = sin(0.5 * abs(self.lat - other.lat))
        sin2 = sin(0.5 * abs(self.lon - other.lon))
        return 2 * radius * asin(sqrt(sin1 * sin1 + cos(self.lat) * cos(other.lat) * sin2 * sin2))

    def moved_by(self, distance, bearing, radius) -> "Coordinate":
        angular_distance = distance / radius
        cad = cos(angular_distance)
        sad = sin(angular_distance)

        cb = cos(bearing)
        sb = sin(bearing)

        slat1 = sin(self.lat)
        clat1 = cos(self.lat)

        lat2 = asin(slat1 * cad + clat1 * sad * cb)
        slat2 = sin(lat2)
        lon2 = self.lon + atan2(sb * sad * clat1, cad - slat1 * slat2)

        return Coordinate(lat2, lon2)

    def to_point(self) -> "Point":
        r, theta, phi = Coordinates.geographical_radians_to_spherical(1.0, self.lat, self.lon)
        return Point(theta, phi)


class Point:
    """Position expressed in spherical coordinates."""

    class Schema(marshmallow.Schema):
        theta = mf.Float()
        phi = mf.Float()

        @marshmallow.post_load
        def make(self, data, **kwargs):
            return Point(**data)

    def __init__(self, theta: float, phi: float) -> None:
        self.theta = theta
        self.phi = phi

    def bearing_to(self, other: "Point") -> float:
        """Calculates bearing between two points expressed in spherical coordinates."""

        coord1 = self.to_coordinate()
        coord2 = other.to_coordinate()
        return coord1.bearing_to(coord2)

    def great_circle_distance_to(self, other: "Point", radius: float) -> float:
        coord1 = self.to_coordinate()
        coord2 = other.to_coordinate()
        return coord1.great_circle_distance_to(coord2, radius)

    def moved_by(self, distance, bearing, radius) -> "Point":
        return self.to_coordinate().moved_by(distance, bearing, radius).to_point()

    def to_coordinate(self) -> Coordinate:
        r, lat, lon = Coordinates.spherical_to_geographical_radians(1.0, self.theta, self.phi)
        return Coordinate(lat, lon)


class _Terrains(enum.Enum):
    HILLS = "hills"
    RANGES = "ranges"
    CONTINENTS = "continents"


class _TerrainInfo(abc.ABC):
    def evaluate(self, pos: Point, radius: float) -> float:
        pass

    def get_name(self) -> str:
        ...

    def get_origin(self) -> Point:
        ...


@dataclass
class Hills(_TerrainInfo):
    origin: Point

    class Schema(marshmallow.Schema):
        origin = mf.Nested(Point.Schema)

        @marshmallow.post_load
        def make(self, data, **kwargs):
            return Hills(**data)

    def evaluate(self, pos: Point, radius: float) -> float:
        return (
            0.006
            * radius
            * (pos.theta / pi - 1)
            * sin(50 * pos.phi)
            * (pos.theta / pi - 2)
            * sin(50 * pos.theta)
        )

    def get_name(self) -> str:
        return _Terrains.HILLS.value

    def get_origin(self) -> Point:
        return self.origin


@dataclass
class Ranges(_TerrainInfo):
    origin: Point

    class Schema(marshmallow.Schema):
        origin = mf.Nested(Point.Schema)

        @marshmallow.post_load
        def make(self, data, **kwargs):
            return Ranges(**data)

    def evaluate(self, pos: Point, radius: float) -> float:
        return 0.012 * radius * cos(10 * pos.theta + pi) * cos(10 * pos.phi)

    def get_name(self) -> str:
        return _Terrains.RANGES.value

    def get_origin(self) -> Point:
        return self.origin


@dataclass
class Continents(_TerrainInfo):
    origin: Point

    class Schema(marshmallow.Schema):
        origin = mf.Nested(Point.Schema)

        @marshmallow.post_load
        def make(self, data, **kwargs):
            return Continents(**data)

    def evaluate(self, pos: Point, radius: float) -> float:
        return 0.018 * radius * sin(pos.theta) * sin(pos.phi)

    def get_name(self) -> str:
        return _Terrains.CONTINENTS.value

    def get_origin(self) -> Point:
        return self.origin


class _TerrainSchema(OneOfSchema):
    type_schemas = {
        _Terrains.HILLS.value: Hills.Schema,
        _Terrains.RANGES.value: Ranges.Schema,
        _Terrains.CONTINENTS.value: Continents.Schema,
    }

    type_names = {
        Hills: _Terrains.HILLS.value,
        Ranges: _Terrains.RANGES.value,
        Continents: _Terrains.CONTINENTS.value,
    }

    def get_obj_type(self, obj):
        name = self.type_names.get(type(obj), None)
        if name is not None:
            return name
        else:
            raise Exception("Unknown object type: {}".format(obj.__class__.__name__))


class Elevation:
    class Schema(marshmallow.Schema):
        radius = mf.Float()
        terrain = mf.List(mf.Nested(_TerrainSchema))

        @marshmallow.post_load
        def make(self, data, **kwargs):
            schema = _TerrainSchema()
            ef = Elevation(data["radius"])
            ef.terrain = data["terrain"]
            return ef

    def __init__(self, radius: float) -> None:
        self.radius = radius
        self.terrain: List[_TerrainInfo] = list()

    def add(self, terrain: _TerrainInfo) -> None:
        self.terrain.append(terrain)

    def get_radius(self) -> float:
        return self.radius

    def evaluate_without_radius(self, position: Point) -> float:
        return sum(terrain.evaluate(position, self.radius) for terrain in self.terrain)

    def evaluate_with_radius(self, position: Point) -> float:
        return self.radius + self.evaluate_without_radius(position)
