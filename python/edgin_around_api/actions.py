import abc, json
from dataclasses import dataclass

import marshmallow
from marshmallow import fields as mf
from marshmallow_enum import EnumField
from marshmallow_oneofschema import OneOfSchema

from typing import Iterable, List, Optional, Sequence, cast

from . import actors, defs, geometry, inventory


class Action(abc.ABC):
    class Schema(marshmallow.Schema):
        pass

    def __init__(self) -> None:
        pass

    def to_string(self) -> str:
        return json.dumps(ActionSchema().dump(self))


@dataclass
class ActorCreationAction(Action, defs.Serializable):
    SERIALIZATION_NAME = "actor_creation"

    actors: List[actors.Actor]

    class Schema(marshmallow.Schema):
        actors = mf.List(mf.Nested(actors.Actor.Schema))

        @marshmallow.post_load
        def make(self, data, **kwargs) -> Action:
            return ActorCreationAction(**data)


@dataclass
class ActorDeletionAction(Action, defs.Serializable):
    SERIALIZATION_NAME = "actor_deletion"

    actor_ids: List[defs.ActorId]

    class Schema(marshmallow.Schema):
        actor_ids = mf.List(mf.Integer())

        @marshmallow.post_load
        def make(self, data, **kwargs) -> Action:
            return ActorDeletionAction(**data)


@dataclass
class ConfigurationAction(Action, defs.Serializable):
    SERIALIZATION_NAME = "configuration"

    hero_actor_id: defs.ActorId
    elevation: geometry.Elevation

    class Schema(marshmallow.Schema):
        hero_actor_id = mf.Integer()
        elevation = mf.Nested(geometry.Elevation.Schema)

        @marshmallow.post_load
        def make(self, data, **kwargs) -> Action:
            return ConfigurationAction(**data)


@dataclass
class CraftBeginAction(Action, defs.Serializable):
    SERIALIZATION_NAME = "craft_begin"

    crafter_id: defs.ActorId

    class Schema(marshmallow.Schema):
        crafter_id = mf.Integer()

        @marshmallow.post_load
        def make(self, data, **kwargs) -> Action:
            return CraftBeginAction(**data)


@dataclass
class CraftEndAction(Action, defs.Serializable):
    SERIALIZATION_NAME = "craft_end"

    crafter_id: defs.ActorId

    class Schema(marshmallow.Schema):
        crafter_id = mf.Integer()

        @marshmallow.post_load
        def make(self, data, **kwargs) -> Action:
            return CraftEndAction(**data)


@dataclass
class IdleAction(Action, defs.Serializable):
    SERIALIZATION_NAME = "idle"

    actor_id: defs.ActorId

    class Schema(marshmallow.Schema):
        actor_id = mf.Integer()

        @marshmallow.post_load
        def make(self, data, **kwargs) -> Action:
            return IdleAction(**data)


@dataclass
class DamageAction(Action, defs.Serializable):
    SERIALIZATION_NAME = "damage"

    dealer_id: defs.ActorId
    receiver_id: defs.ActorId
    variant: defs.DamageVariant
    hand: defs.Hand

    class Schema(marshmallow.Schema):
        dealer_id = mf.Integer()
        receiver_id = mf.Integer()
        variant = EnumField(defs.DamageVariant)
        hand = EnumField(defs.Hand)

        @marshmallow.post_load
        def make(self, data, **kwargs) -> Action:
            return DamageAction(**data)


@dataclass
class InventoryUpdateAction(Action, defs.Serializable):
    SERIALIZATION_NAME = "inventory_update"

    owner_id: defs.ActorId
    inventory: inventory.Inventory

    class Schema(marshmallow.Schema):
        owner_id = mf.Integer()
        inventory = mf.Nested(inventory.Inventory.Schema)

        @marshmallow.post_load
        def make(self, data, **kwargs) -> Action:
            return InventoryUpdateAction(**data)


@dataclass
class LocalizationAction(Action, defs.Serializable):
    SERIALIZATION_NAME = "localization"

    actor_id: defs.ActorId
    position: geometry.Point

    class Schema(marshmallow.Schema):
        actor_id = mf.Integer()
        position = mf.Nested(geometry.Point.Schema)

        @marshmallow.post_load
        def make(self, data, **kwargs) -> Action:
            return LocalizationAction(**data)


@dataclass
class MotionAction(Action, defs.Serializable):
    SERIALIZATION_NAME = "motion"

    actor_id: defs.ActorId
    speed: float
    bearing: float
    duration: float

    class Schema(marshmallow.Schema):
        actor_id = mf.Integer()
        speed = mf.Float()
        bearing = mf.Float()
        duration = mf.Float()

        @marshmallow.post_load
        def make(self, data, **kwargs) -> Action:
            return MotionAction(**data)


@dataclass
class PickBeginAction(Action, defs.Serializable):
    SERIALIZATION_NAME = "pick_begin"

    who: defs.ActorId
    what: defs.ActorId

    class Schema(marshmallow.Schema):
        who = mf.Integer()
        what = mf.Integer()

        @marshmallow.post_load
        def make(self, data, **kwargs) -> Action:
            return PickBeginAction(**data)


@dataclass
class PickEndAction(Action, defs.Serializable):
    SERIALIZATION_NAME = "pick_end"

    who: defs.ActorId

    class Schema(marshmallow.Schema):
        who = mf.Integer()

        @marshmallow.post_load
        def make(self, data, **kwargs) -> Action:
            return PickEndAction(**data)


@dataclass
class StatUpdateAction(Action, defs.Serializable):
    SERIALIZATION_NAME = "stat_update"

    actor_id: defs.ActorId
    stats: defs.Stats

    class Schema(marshmallow.Schema):
        actor_id = mf.Integer()
        stats = mf.Nested(defs.Stats.Schema)

        @marshmallow.post_load
        def make(self, data, **kwargs) -> Action:
            return StatUpdateAction(**data)


_ACTIONS = cast(
    Sequence[defs.Serializable],
    (
        ActorCreationAction,
        ActorDeletionAction,
        ConfigurationAction,
        CraftBeginAction,
        CraftEndAction,
        DamageAction,
        IdleAction,
        InventoryUpdateAction,
        LocalizationAction,
        MotionAction,
        PickBeginAction,
        PickEndAction,
        StatUpdateAction,
    ),
)


class ActionSchema(OneOfSchema):
    """A schema for any type of action."""

    type_schemas = {cls.SERIALIZATION_NAME: cls.Schema for cls in _ACTIONS}
    type_names = {cls: cls.SERIALIZATION_NAME for cls in _ACTIONS}

    def get_obj_type(self, obj):
        name = self.type_names.get(type(obj), None)
        if name is not None:
            return name
        else:
            raise Exception("Unknown object type: {}".format(obj.__class__.__name__))


def action_from_json_string(string: str) -> Optional[Action]:
    """
    Converts a JSON string into an action.
    If conversion fails prints the reason and returns `None`.
    """

    try:
        data = json.loads(string)
        res = ActionSchema().load(data)
        return res
    except Exception as e:
        print(f"Action deserialisation failure: {e} - ({string})")
        return None
