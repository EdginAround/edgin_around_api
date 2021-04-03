import unittest

import marshmallow

from typing import Any, Dict

from edgin_around_api import actions

class SerdeTest(unittest.TestCase):
    """Provides common functionality to all serialisation-deserialisation tests."""

    def assert_serde(
            self,
            dictionary: Dict[str, Any],
            schema: marshmallow.Schema,
            typ: type,
        ) -> None:
        """
        Checks if the given dictionary when deserialized with the given schema has the passed type
        and when serialised again is equal to the original dictionary.
        """

        object = schema.load(dictionary)
        self.assertEqual(type(object), typ)
        parsed = schema.dump(object)
        if hasattr(object, 'to_string'):
            self.assertFalse('\n' in object.to_string())
        self.assertDictEqual(dictionary, parsed)


