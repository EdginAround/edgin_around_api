import marshmallow
from marshmallow import fields as mf

from typing import Optional

from . import defs, geometry


class Actor:
    id: defs.ActorId
    position: Optional[geometry.Point]
    entity_name: str

    class Schema(marshmallow.Schema):
        id = mf.Integer()
        position = mf.Nested(geometry.Point.Schema)
        entity_name = mf.String()

        @marshmallow.post_load
        def make(self, data, **kwargs):
            return Actor(**data)

    def __init__(
        self,
        id: defs.ActorId,
        entity_name: str,
        position: Optional[geometry.Point] = None,
    ) -> None:
        self.id = id
        self.position = position
        self.entity_name = entity_name

    def get_id(self) -> defs.ActorId:
        return self.id

    def is_visible(self) -> bool:
        return self.position is not None
