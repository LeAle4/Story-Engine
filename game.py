"""Core entities for a text-adventure engine."""
import random
from typing import Callable
from PyCLI.utils import Callback

def find_object_by_name(name: str, objects: list[GameObject]) -> GameObject | None:
    """Return the first object whose `name` matches or None."""
    for obj in objects:
        if obj.name == name:
            return obj
    return None

def savegame(player: 'Player', game_map: tuple[Area], filename: str) -> None:
    raise NotImplementedError("Savegame functionality is not yet implemented.")

def loadgame(filename: str) -> tuple['Player', tuple[Area]]:
    raise NotImplementedError("Loadgame functionality is not yet implemented.")


class GameObject:
    """Base interactive entity with `targeted_function`."""

    def __init__(self, name: str, description: str, targeted_function: Callable | None = None):
        """Initialize with `name`, `description`, and `targeted_function`."""
        self.name = name
        self.description = description
        if targeted_function is None:
            raise ValueError(f"{self.name} does not have a valid targeted_function. A targeted_function must be provided")
        self.targeted_function = targeted_function

class Item(GameObject):
    """Targetable object that can be taken (`take_callback`)."""

    def __init__(self, name: str, description: str, targeted_function: Callback | None = None, take_callback: Callback | None = None):
        """Initialize with callbacks for targeting and taking."""
        super().__init__(name, description, targeted_function)
        if take_callback is None:
            raise ValueError(f"{self.name} does not have a valid take_callback. A take_callback must be provided")
        self.take_callback = take_callback

class Place(GameObject):
    """Location that can contain `Item` objects."""

    def __init__(self, name: str, description: str, targeted_function: Callback | None = None, items: list = []):
        """Initialize with optional `items` and `targeted_function`."""
        super().__init__(name, description, targeted_function)
        self.items = items

    def add_item(self, item: Item):
        """Add an item to this place."""
        self.items.append(item)

    def remove_item(self, item: Item):
        """Remove an item from this place."""
        self.items.remove(item)

    def get_item(self, item_name: str) -> Item | None:
        """Return item by name or None."""
        return find_object_by_name(item_name, self.items)  # type: ignore

class Room(Place):
    """`Place` with sub-places (e.g., tables, corners)."""

    def __init__(self, name: str, description: str, targeted_function: Callback | None = None, items: list = [], places: list = []):
        """Initialize with optional `items` and `places`."""
        super().__init__(name, description, targeted_function, items)
        self.places = places

    def add_place(self, place: Place):
        """Add a sub-place to this room."""
        self.places.append(place)

    def remove_place(self, place: Place):
        """Remove a sub-place from this room."""
        self.places.remove(place)

class Area:
    """Adjacency map for places."""

    def __init__(self, places: list[Place], adjacency: dict[Place, tuple[Place]]):
        """Initialize with `places` and adjacency mapping."""
        self.places = places
        self.adjacency = adjacency

    def is_adjacent(self, place1: Place, place2: Place) -> bool:
        """Return True if `place2` is adjacent to `place1`."""
        return place2 in self.adjacency.get(place1, ())

class Player(GameObject):
    """Player with inventory, location, and movement."""
    
    def __init__(self, name:str, description:str, current_place:'Place',current_area:'Area',  inventory:list['Item'], clues:dict[str,str], targeted_function: Callback | None = None):
        """Initialize with starting `place`, `area`, and `inventory`."""
        super().__init__(name, description, targeted_function)
        self.current_place = current_place
        self.current_area = current_area
        self.inventory = inventory
        self.clues = clues

    def add_item(self, item:'Item'):
        """Add an item to inventory."""
        self.inventory.append(item)
    
    def remove_item(self, item:'Item'):
        """Remove an item from inventory."""
        self.inventory.remove(item)
    
    def move_to(self, new_place:'Place')->bool:
        """Move to an adjacent place; return True on success."""
        if self.current_area.is_adjacent(self.current_place, new_place):
            self.current_place = new_place
            return True
        return False
    
    def change_area(self, new_area:'Area', new_place:'Place')->None:
        """Switch to a new `Area` and set starting `Place`."""
        self.current_area = new_area
        self.current_place = new_place
    
    def has_item(self, item_name:str)->bool:
        """Return True if an item with `item_name` is in inventory."""
        for item in self.inventory:
            if item.name == item_name:
                return True
        return False
    
    def take_item(self, item_name:str)->bool:
        """Trigger `take_callback` for an item by name if present."""
        for item in self.current_place.items:
            if item.name == item_name:
                item.take_callback()
                return True
        return False
    
    def inspect(self, item_name:str)->'str|None':
        """Return description of an object by name if found."""
        searchable = self.current_place.items + [self.name] + [self.current_place.name]
        if isinstance(self.current_place, Room):
            searchable = searchable + self.current_place.places
        target = find_object_by_name(item_name, searchable) #type: ignore
        if target:
            return target.description
        return None
    
    def use_item(self, item_name:str, target_name:str)->tuple[bool,bool]:
        """Use an inventory item on a target; return (found_item, found_target)."""
        item = find_object_by_name(item_name, self.inventory) #type: ignore
        searchable_targets = self.current_place.items + [self.name] + [self.current_place.name]
        if isinstance(self.current_place, Room):
            searchable_targets = searchable_targets + self.current_place.places
        target = find_object_by_name(target_name, searchable_targets) #type: ignore
        if item and target:
            target.targeted_function(self, item)
        return (True if item else False, True if target else False)

    def think(self, thoughts:tuple[str], chance:float=0.3)->str:
        if random.random() < chance:
            return random.choice(tuple(self.clues.values()))
        return random.choice(thoughts)