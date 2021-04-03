import unittest

from math import pi, atan, sqrt, radians

from typing import Any, Dict

from . import common

from edgin_around_api import geometry

class GeometryTest(common.SerdeTest):
    def test_elevation_function_serialization(self) -> None:
        """Checks if the elevation function is serialized and deserialized properly."""

        original: Dict[str, Any] = {
            'radius': 999,
            'terrain': [{
                'type': 'hills',
                'origin': { 'theta': 0.0, 'phi': 0.0 },
            }, {
                'type': 'hills',
                'origin': { 'theta': 1.0, 'phi': 1.0 },
            }, {
                'type': 'ranges',
                'origin': { 'theta': 5.0, 'phi': 2.0 },
            }, {
                'type': 'continents',
                'origin': { 'theta': 8.0, 'phi': 9.0 },
            }]
        }

        self.assert_serde(original, geometry.Elevation.Schema(), geometry.Elevation)

