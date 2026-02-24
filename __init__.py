"""A text-adventure game engine for creating interactive fiction."""

from .game import (
    GameObject,
    Item,
    Place,
    Room,
    Area,
    Player,
    find_object_by_name,
    savegame,
    loadgame,
)

__version__ = "0.1.0"
__all__ = [
    "GameObject",
    "Item",
    "Place",
    "Room",
    "Area",
    "Player",
    "find_object_by_name",
    "savegame",
    "loadgame",
]
