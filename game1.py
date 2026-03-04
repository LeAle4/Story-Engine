from __future__ import annotations

import json
import random

class Game:
    def __init__(self, game_map: Map, player: Player, clues: list[Clue]):
        """Initialize the game with a map and a player."""
        self.map = game_map
        self.player = player
        self.triggered_events = []
        self.clues = clues
    
    def throw_clue(self):
        return random.choice(self.clues).description if self.clues else "Creo que voy muy bien"
    
    def trigger_situation(self, situation_id: str):
        """Mark a story situation as triggered."""
        self.triggered_events.append(situation_id)
        for clue in self.clues:
            if clue.associated_event_id == situation_id:
                self.clues.remove(clue)

    def save_game(self, filename: str):
        """Save the current game state to a file."""
        game_state = {
            'map': self.map.as_saveable_object(),
            'player': self.player.as_saveable_object(),
            'triggered_events': self.triggered_events,
            'clues': [clue.as_saveable_object() for clue in self.clues]
        }
        with open(filename, 'w') as file:
            json.dump(game_state, file, indent=4)
    
    def load_game(self, filename: str):
        """Load a game state from a file."""
        with open(filename, 'r') as file:
            game_state = json.load(file)
        
        self.map = Map.load_from_json_object(game_state['map'])
        self.player = Player.load_from_json_object(game_state['player'], self.map)
        self.triggered_events = game_state.get('triggered_events', [])
        self.clues = [Clue.load_from_json_object(clue_data) for clue_data in game_state.get('clues', [])]

class Clue:
    """Clue that can be discovered in the game."""
    def __init__(self, id: str, description: str, associated_event_id: str):
        """Initialize with `id` and `description`."""
        self.id = id
        self.description = description
        self.associated_event_id = associated_event_id
    
    def as_saveable_object(self) -> dict[str, object]:
        """Return a dictionary representation of the clue for saving."""
        return {
            'id': self.id,
            'description': self.description,
            'associated_event_id': self.associated_event_id
        }
    
    @staticmethod
    def load_from_json_object(json_object: dict):
        """Create and return a clue loaded from a JSON object."""
        return Clue(
            id=json_object['id'],
            description=json_object['description'],
            associated_event_id=json_object['associated_event_id']
        )

class GameObject:
    """Base interactive entity with `targeted_function`."""

    def __init__(self, name: str, description: str, id: str):
        """Initialize with `name`, `description`, and `id`."""
        self.name = name
        self.description = description
        self.id = id
        self.isknown = False

    def as_saveable_object(self) -> dict[str, object]:
        """Return a dictionary representation of the object for saving."""
        return {
            'name': self.name,
            'description': self.description,
            'id': self.id,
            "isknown": self.isknown
        }
    
    @staticmethod
    def load_from_json_object(json_object: dict):
        """Create and return an object loaded from a JSON object."""
        return GameObject(
            name=json_object['name'],
            description=json_object['description'],
            id=json_object['id'],
        )

class Player(GameObject):
    """Player character, inherits from `GameObject`."""

    def __init__(self, name: str, description: str, id: str, items: list[Item], thoughts: tuple[str],current_place: Place, current_room: Room, current_area: Area):
        """Initialize with `name`, `description`, and `id`."""
        super().__init__(name, description, id)
        self.items = items if items is not None else []
        self.thoughts = thoughts
        self.current_place = current_place
        self.current_room = current_room
        self.current_area = current_area
    
    def in_place(self, place_name: str) -> bool:
        return self.current_place.name == place_name

    def as_saveable_object(self) -> dict[str, object]:
        base_dict = super().as_saveable_object()
        base_dict.update({
            'items': [item.as_saveable_object() for item in self.items],
            'thoughts': list(self.thoughts),
            'current_place': self.current_place.id if isinstance(self.current_place, Place) else self.current_place,
            'current_room': self.current_room.id,
            'current_area': self.current_area.id if isinstance(self.current_area, Area) else self.current_area
        })
        return base_dict
    
    @staticmethod
    def load_from_json_object(json_object: dict, game_map: Map):
        items = [Item.load_from_json_object(item_data) for item_data in json_object.get('items', [])]
        thoughts = tuple(json_object.get('thoughts', []))
        
        # Resolve IDs to actual objects using the game map
        current_place_id = json_object['current_place']
        current_room_id = json_object['current_room']
        current_area_id = json_object['current_area']
        
        current_place = game_map.get_from_id(current_place_id)
        current_room = game_map.get_from_id(current_room_id)
        current_area = game_map.get_from_id(current_area_id)
        
        return Player(
            name=json_object['name'],
            description=json_object['description'],
            id=json_object['id'],
            items=items,
            thoughts=thoughts,
            current_place=current_place,
            current_room=current_room,
            current_area=current_area
        )

class NPC(GameObject):
    """Non-player character, inherits from `GameObject`."""

    def __init__(self, name: str, description: str, id: str):
        """Initialize with `name`, `description`, and `id`."""
        super().__init__(name, description, id)
    
    def as_saveable_object(self) -> dict[str, object]:
        return super().as_saveable_object()
    
    @staticmethod
    def load_from_json_object(json_object: dict):
        return NPC(
            name=json_object['name'],
            description=json_object['description'],
            id=json_object['id']
        )

class Item(GameObject):
    """Item that can be interacted with, inherits from `GameObject`."""

    def __init__(self, name: str, description: str, id: str, used_msg: str, amount: int = 1, use_times:int = 1):
        """Initialize with `name`, `description`, and `id`."""
        super().__init__(name, description, id)
        self.used_msg = used_msg if used_msg else f"Usaste {name}."
        self.amount = amount
        self.use_times = use_times
    
    def as_saveable_object(self) -> dict[str, object]:
        base_dict = super().as_saveable_object()
        base_dict.update({
            'used_msg': self.used_msg,
            'amount': self.amount,
            'use_times': self.use_times
        })
        return base_dict

    @staticmethod
    def load_from_json_object(json_object: dict):
        return Item(
            name=json_object['name'],
            description=json_object['description'],
            id=json_object['id'],
            used_msg=json_object['used_msg'],
            amount=json_object['amount'],
            use_times=json_object['use_times']
        )

class Place(GameObject):
    """Location in the game world, inherits from `GameObject`."""

    def __init__(self, name: str, description: str, id: str, item_list: list[Item], npc_list: list[NPC]):
        """Initialize with `name`, `description`, and `id`."""
        super().__init__(name, description, id)
        self.item_list = item_list if item_list is not None else []
        self.npc_list = npc_list if npc_list is not None else []
    
    def gets_discovered(self):
        self.isknown = True
        for item in self.item_list:
            item.isknown = True

    def has_item_by_name(self, item_name: str) -> bool:
        """Check if the place has an item with the given name."""
        return any(item.name == item_name for item in self.item_list)

    def get_item_by_name(self, item_name: str) -> Item | None:
        """Get an item by name from the place."""
        for item in self.item_list:
            if item.name == item_name:
                return item
        return None

    def as_saveable_object(self) -> dict[str, object]:
        base_dict = super().as_saveable_object()
        base_dict.update({
            'item_list': [item.as_saveable_object() for item in self.item_list],
            'npc_list': [npc.as_saveable_object() for npc in self.npc_list]
        })
        return base_dict
    
    @staticmethod
    def load_from_json_object(json_object: dict):
        return Place(
            name=json_object['name'],
            description=json_object['description'],
            id=json_object['id'],
            item_list=[Item.load_from_json_object(item_data) for item_data in json_object.get('item_list', [])],
            npc_list=[NPC.load_from_json_object(npc_data) for npc_data in json_object.get('npc_list', [])]
        )

class Room(Place):
    """Room in the game world, inherits from `Place`."""

    def __init__(self, name: str, description: str, id: str, place_list: list[Place], item_list: list[Item], npc_list: list[NPC]):
        """Initialize with `name`, `description`, and `id`."""
        super().__init__(name, description, id, item_list, npc_list)
        self.place_list = place_list if place_list is not None else []
    
    def has_place(self, place_name: str) -> bool:
        """Check if the room has a place with the given name."""
        return any(place.name == place_name for place in self.place_list)
    
    def get_place(self, place_name: str) -> Place | None:
        """Get a place by name from the room."""
        for place in self.place_list:
            if place.name == place_name:
                return place

    def gets_discovered(self):
        self.isknown = True
        for place in self.place_list:
            place.isknown = True

    def as_saveable_object(self) -> dict[str, object]:
        base_dict = super().as_saveable_object()
        base_dict.update({
            'place_list': [place.as_saveable_object() for place in self.place_list]
        })
        return base_dict
    
    @staticmethod
    def load_from_json_object(json_object: dict):
        return Room(
            name=json_object['name'],
            description=json_object['description'],
            id=json_object['id'],
            place_list=[Place.load_from_json_object(place_data) for place_data in json_object.get('place_list', [])],
            item_list=[Item.load_from_json_object(item_data) for item_data in json_object.get('item_list', [])],
            npc_list=[NPC.load_from_json_object(npc_data) for npc_data in json_object.get('npc_list', [])]
        )

class Area(GameObject):
    """Area in the game world, inherits from `GameObject`."""

    def __init__(self, name: str, description: str, id: str, room_list: list[Room], conections: dict[Room,list[Room]]):
        """Initialize with `name`, `description`, and `id`."""
        super().__init__(name, description, id)
        self.room_list = room_list if room_list  else []
        self.conections = conections if conections  else {}

    def is_connected(self, room1: Room, room2: Room) -> bool:
        """Check if two rooms are connected."""
        return room2 in self.conections.get(room1, [])
    
    def has_room_from_name(self, room_name: str) -> bool:
        """Check if the area has a room with the given name."""
        return any(room.name == room_name for room in self.room_list)

    def get_room_by_name(self, room_name: str) -> Room | None:
        """Get a room by its name."""
        return next((room for room in self.room_list if room.name == room_name), None)

    def as_saveable_object(self) -> dict[str, object]:
        base_dict = super().as_saveable_object()
        base_dict.update({
            'room_list': [room.as_saveable_object() for room in self.room_list],
            'conections': {room.id: [connected_room.id for connected_room in connections] 
                          for room, connections in self.conections.items()}
        })
        return base_dict
    
    @staticmethod
    def load_from_json_object(json_object: dict, room_dict: dict | None = None):
        room_list = [Room.load_from_json_object(room_data) for room_data in json_object.get('room_list', [])]

        if room_dict is None:
            room_dict = {room.id: room for room in room_list}

        conections_data = json_object.get('conections', {})
        conections = {room_dict[room_id]: [room_dict[conn_id] for conn_id in conn_ids]
                      for room_id, conn_ids in conections_data.items() if room_id in room_dict}

        return Area(
            name=json_object['name'],
            description=json_object['description'],
            id=json_object['id'],
            room_list=room_list,
            conections=conections
        )

class Map(GameObject):
    """Map of the game world, inherits from `GameObject`."""

    def __init__(self, name: str, description: str, id: str, area_list: list[Area], connections: dict[Area,list[Area]]):
        """Initialize with `name`, `description`, and `id`."""
        super().__init__(name, description, id)
        self.area_list = area_list if area_list else []
        self.connections = connections if connections else {}
    
    def get_from_id(self, id: str) -> Area | Room | Place | None:
        """Get an area, room, or place by its ID."""
        for area in self.area_list:
            if area.id == id:
                return area
            for room in area.room_list:
                if room.id == id:
                    return room
                for place in room.place_list:
                    if place.id == id:
                        return place
        return None

    def as_saveable_object(self) -> dict[str, object]:
        base_dict = super().as_saveable_object()
        base_dict.update({
            'area_list': [area.as_saveable_object() for area in self.area_list],
            'connections': {area.id: [connected_area.id for connected_area in connections]
                           for area, connections in self.connections.items()}
        })
        return base_dict
    
    @staticmethod
    def load_from_json_object(json_object: dict, area_dict: dict | None = None):
        area_list = [Area.load_from_json_object(area_data) for area_data in json_object.get('area_list', [])]

        if area_dict is None:
            area_dict = {area.id: area for area in area_list}

        connections_data = json_object.get('connections', {})
        connections = {area_dict[area_id]: [area_dict[conn_id] for conn_id in conn_ids]
                       for area_id, conn_ids in connections_data.items() if area_id in area_dict}

        return Map(
            name=json_object['name'],
            description=json_object['description'],
            id=json_object['id'],
            area_list=area_list,
            connections=connections
        )