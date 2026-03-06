from __future__ import annotations

import json
from pathlib import Path
import random

class Game:
    """Main game controller managing map, player, and game state.
    
    The Game class is the central hub for all game state, including the game map,
    the player character, triggered story events, and available clues.
    
    Attributes:
        map (Map): The game world map containing all areas, rooms, and places.
        player (Player): The player character.
        triggered_events (list): List of IDs of story events that have been triggered.
        clues (list[Clue]): List of available clues to help the player.
    """
    def __init__(self, game_map: Map, player: Player, clues: list[Clue]):
        """Initialize the game with a map and a player.
        
        Args:
            game_map (Map): The game world map.
            player (Player): The player character.
            clues (list[Clue]): List of clues in the game.
        """
        self.map = game_map
        self.player = player
        self.triggered_events = []
        self.clues = clues
    
    def throw_clue(self):
        """Get a random clue from the available clues.
        
        Returns:
            str: The description of a random clue, or a default message if no clues available.
        """
        return random.choice(self.clues).description if self.clues else "Creo que voy muy bien"
    
    def trigger_situation(self, situation_id: str):
        """Mark a story situation as triggered.
        
        Records that a story situation has been triggered and removes its associated clue
        from the available clues.
        
        Args:
            situation_id (str): The ID of the situation being triggered.
        """
        self.triggered_events.append(situation_id)
        for clue in self.clues:
            if clue.associated_event_id == situation_id:
                self.clues.remove(clue)

    def save_game(self, filename: str):
        """Save the current game state to a file.
        
        Serializes all game state (map, player, events, clues) to JSON format.
        
        Args:
            filename (str): The filename to save the game state to.
        """
        game_state = {
            'map': self.map.as_saveable_object(),
            'player': self.player.as_saveable_object(),
            'triggered_events': self.triggered_events,
            'clues': [clue.as_saveable_object() for clue in self.clues]
        }
        with open(filename, 'w') as file:
            json.dump(game_state, file, indent=4)
    
    @staticmethod
    def load_game(filename: str | Path) -> Game:
        """Load a game state from a file.
        
        Deserializes game state from JSON and creates a new Game instance.
        
        Args:
            filename (str): The filename containing the saved game state.
            
        Returns:
            Game: A new Game instance with the loaded state.
        """
        with open(filename, 'r') as file:
            game_state = json.load(file)
        
        game_map = Map.load_from_json_object(game_state['map'])
        player = Player.load_from_json_object(game_state['player'], game_map)
        clues = [Clue.load_from_json_object(clue_data) for clue_data in game_state.get('clues', [])]
        
        game = Game(game_map, player, clues)
        game.triggered_events = game_state.get('triggered_events', [])
        
        return game

class Clue:
    """Clue that can be discovered in the game.
    
    A clue provides hints to help the player progress, and is associated with
    a specific story event.
    
    Attributes:
        id (str): Unique identifier for the clue.
        description (str): The text of the clue to display to the player.
        associated_event_id (str): ID of the story event this clue relates to.
    """
    def __init__(self, id: str, description: str, associated_event_id: str):
        """Initialize with `id` and `description`."""
        self.id = id
        self.description = description
        self.associated_event_id = associated_event_id
    
    def as_saveable_object(self) -> dict[str, object]:
        """Return a dictionary representation of the clue for saving.
        
        Returns:
            dict[str, object]: Dictionary with clue, description, and associated_event_id.
        """
        return {
            'id': self.id,
            'description': self.description,
            'associated_event_id': self.associated_event_id
        }
    
    @staticmethod
    def load_from_json_object(json_object: dict):
        """Create and return a clue loaded from a JSON object.
        
        Args:
            json_object (dict): Dictionary containing clue data from JSON.
            
        Returns:
            Clue: A Clue instance initialized from the JSON data.
        """
        return Clue(
            id=json_object['id'],
            description=json_object['description'],
            associated_event_id=json_object['associated_event_id']
        )

class GameObject:
    """Base interactive entity in the game world.
    
    This is the base class for all game objects including players, NPCs, items,
    places, rooms, areas, and the map itself.
    
    Attributes:
        name (str): The display name of the object.
        description (str): Detailed description of the object.
        id (str): Unique identifier for the object.
        isknown (bool): Whether the player has discovered/seen this object.
    """

    def __init__(self, name: str, description: str, id: str):
        """Initialize with `name`, `description`, and `id`.
        
        Args:
            name (str): The display name of the object.
            description (str): Detailed description of the object.
            id (str): Unique identifier for the object.
        """
        self.name = name
        self.description = description
        self.id = id
        self.isknown = False

    def as_saveable_object(self) -> dict[str, object]:
        """Return a dictionary representation of the object for saving.
        
        Returns:
            dict[str, object]: Dictionary with all object properties for serialization.
        """
        return {
            'name': self.name,
            'description': self.description,
            'id': self.id,
            "isknown": self.isknown
        }
    
    @staticmethod
    def load_from_json_object(json_object: dict):
        """Create and return an object loaded from a JSON object.
        
        Args:
            json_object (dict): Dictionary containing object data from JSON.
            
        Returns:
            GameObject: A GameObject instance initialized from the JSON data.
        """
        return GameObject(
            name=json_object['name'],
            description=json_object['description'],
            id=json_object['id'],
        )

class Player(GameObject):
    """Player character, inherits from `GameObject`.
    
    The Player class represents the protagonist of the game, containing their inventory,
    current location, internal thoughts, and other character details.
    
    Attributes:
        items (list[Item]): Items the player is currently carrying.
        thoughts (tuple[str]): Random thoughts the player can have.
        current_place (Place): The specific place the player is in.
        current_room (Room): The room containing the current place.
        current_area (Area): The area containing the current room.
    """

    def __init__(self, name: str, description: str, id: str, items: list[Item], thoughts: tuple[str,...],current_place: Place, current_room: Room, current_area: Area):
        """Initialize with `name`, `description`, and `id`.
        
        Args:
            name (str): The player's name.
            description (str): Description of the player character.
            id (str): Unique identifier for the player.
            items (list[Item]): Starting items in inventory.
            thoughts (tuple[str]): Available thoughts the player can have.
            current_place (Place): Starting place.
            current_room (Room): Starting room.
            current_area (Area): Starting area.
        """
        super().__init__(name, description, id)
        self.items = items if items is not None else []
        self.thoughts = thoughts
        self.current_place = current_place
        self.current_room = current_room
        self.current_area = current_area
    
    def in_place(self, place_name: str) -> bool:
        """Check if the player is in a specific place.
        
        Args:
            place_name (str): The name of the place to check.
            
        Returns:
            bool: True if the player's current place matches the given name.
        """
        return self.current_place.name.lower() == place_name.lower()

    def as_saveable_object(self) -> dict[str, object]:
        """Return a dictionary representation of the player for saving.
        
        Returns:
            dict[str, object]: Dictionary with all player state for serialization.
        """
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
        """Load a player from a JSON object.
        
        Args:
            json_object (dict): Dictionary containing player data.
            game_map (Map): The game map to resolve location IDs.
            
        Returns:
            Player: A Player instance initialized from the JSON data.
        """
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
    """Non-player character, inherits from `GameObject`.
    
    NPCs are characters in the game world that the player can interact with.
    They are primarily descriptive elements in this version.
    """

    def __init__(self, name: str, description: str, id: str):
        """Initialize with `name`, `description`, and `id`.
        
        Args:
            name (str): The NPC's name.
            description (str): Description of the NPC.
            id (str): Unique identifier for the NPC.
        """
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
    """Item that can be interacted with, inherits from `GameObject`.
    
    Items are objects in the game world that the player can pick up and use.
    They can have usage limits and messages associated with using them.
    
    Attributes:
        used_msg (str): Message displayed when the item is used.
        amount (int): Quantity of the item.
        use_times (int): How many times the item can be used.
    """

    def __init__(self, name: str, description: str, id: str, takeable:bool = False, amount: int = 1, use_times:int = 1):
        """Initialize with `name`, `description`, and `id`.
        
        Args:
            name (str): The item's name.
            description (str): Description of the item.
            id (str): Unique identifier for the item.
            used_msg (str): Message to display when item is used.
            amount (int): Quantity of the item. Defaults to 1.
            use_times (int): Number of times item can be used. Defaults to 1.
        """
        super().__init__(name, description, id)
        self.amount = amount
        self.use_times = use_times
        self.takeable = takeable
    
    def as_saveable_object(self) -> dict[str, object]:
        base_dict = super().as_saveable_object()
        base_dict.update({
            'amount': self.amount,
            'use_times': self.use_times,
            'takeable': self.takeable
        })
        return base_dict

    @staticmethod
    def load_from_json_object(json_object: dict):
        return Item(
            name=json_object['name'],
            description=json_object['description'],
            id=json_object['id'],
            amount=json_object['amount'],
            use_times=json_object['use_times'],
            takeable=json_object['takeable']
        )

class Place(GameObject):
    """Location in the game world, inherits from `GameObject`.
    
    A place is a specific location within a room where the player can interact
    with items and NPCs.
    
    Attributes:
        item_list (list[Item]): Items available in this place.
        npc_list (list[NPC]): NPCs present in this place.
    """

    def __init__(self, name: str, description: str, id: str, item_list: list[Item], npc_list: list[NPC]):
        """Initialize with `name`, `description`, and `id`.
        
        Args:
            name (str): The place's name.
            description (str): Description of the place.
            id (str): Unique identifier for the place.
            item_list (list[Item]): Items in this place.
            npc_list (list[NPC]): NPCs in this place.
        """
        super().__init__(name, description, id)
        self.item_list = item_list if item_list is not None else []
        self.npc_list = npc_list if npc_list is not None else []
    
    def gets_discovered(self):
        """Mark this place as discovered by the player.
        
        Sets the place and all its items as known to the player.
        """
        self.isknown = True
        for item in self.item_list:
            item.isknown = True

    def has_item_by_name(self, item_name: str) -> bool:
        """Check if the place has an item with the given name.
        
        Args:
            item_name (str): The name of the item to check for.
            
        Returns:
            bool: True if an item with that name exists in this place.
        """
        return any(item.name.lower() == item_name.lower() for item in self.item_list)

    def get_item_by_name(self, item_name: str) -> Item | None:
        """Get an item by name from the place.
        
        Args:
            item_name (str): The name of the item to retrieve.
            
        Returns:
            Item | None: The item if found, None otherwise.
        """
        for item in self.item_list:
            if item.name.lower() == item_name.lower():
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
    """Room in the game world, inherits from `Place`.
    
    A room is a larger space that can contain multiple places, items, and NPCs.
    Rooms are connected to other rooms within an area.
    
    Attributes:
        place_list (list[Place]): The specific places within this room.
    """

    def __init__(self, name: str, description: str, id: str, place_list: list[Place], item_list: list[Item], npc_list: list[NPC]):
        """Initialize with `name`, `description`, and `id`.
        
        Args:
            name (str): The room's name.
            description (str): Description of the room.
            id (str): Unique identifier for the room.
            place_list (list[Place]): Places within this room.
            item_list (list[Item]): Items in this room.
            npc_list (list[NPC]): NPCs in this room.
        """
        super().__init__(name, description, id, item_list, npc_list)
        self.place_list = place_list if place_list is not None else []
    
    def has_place(self, place_name: str) -> bool:
        """Check if the room has a place with the given name.
        
        Args:
            place_name (str): The name of the place to check for.
            
        Returns:
            bool: True if a place with that name exists in this room.
        """
        return any(place.name.lower() == place_name.lower() for place in self.place_list)
    
    def get_place(self, place_name: str) -> Place | None:
        """Get a place by name from the room.
        
        Args:
            place_name (str): The name of the place to retrieve.
            
        Returns:
            Place | None: The place if found, None otherwise.
        """
        for place in self.place_list:
            if place.name.lower() == place_name.lower():
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
    """Area in the game world, inherits from `GameObject`.
    
    An area is a large region containing multiple connected rooms. Areas define
    the topology and connectivity of the game world.
    
    Attributes:
        room_list (list[Room]): Rooms contained in this area.
        conections (dict[Room,list[Room]]): Which rooms are connected to each other.
    """

    def __init__(self, name: str, description: str, id: str, room_list: list[Room], conections: dict[Room,list[Room]]):
        """Initialize with `name`, `description`, and `id`.
        
        Args:
            name (str): The area's name.
            description (str): Description of the area.
            id (str): Unique identifier for the area.
            room_list (list[Room]): Rooms in this area.
            conections (dict[Room,list[Room]]): Adjacency information for rooms.
        """
        super().__init__(name, description, id)
        self.room_list = room_list if room_list  else []
        self.conections = conections if conections  else {}

    def is_connected(self, room1: Room, room2: Room) -> bool:
        """Check if two rooms are connected.
        
        Args:
            room1 (Room): The first room.
            room2 (Room): The second room.
            
        Returns:
            bool: True if room2 is adjacent to room1.
        """
        return room2 in self.conections.get(room1, [])
    
    def has_room_from_name(self, room_name: str) -> bool:
        """Check if the area has a room with the given name.
        
        Args:
            room_name (str): The name of the room to check for.
            
        Returns:
            bool: True if a room with that name exists in this area.
        """
        return any(room.name.lower() == room_name.lower() for room in self.room_list)

    def get_room_by_name(self, room_name: str) -> Room | None:
        """Get a room by its name.
        
        Args:
            room_name (str): The name of the room to retrieve.
            
        Returns:
            Room | None: The room if found, None otherwise.
        """
        return next((room for room in self.room_list if room.name.lower() == room_name.lower()), None)

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
    """Map of the game world, inherits from `GameObject`.
    
    The map is the top-level container for all game areas and defines the
    overall structure and connectivity of the game world.
    
    Attributes:
        area_list (list[Area]): All areas in the game world.
        connections (dict[Area,list[Area]]): Which areas are connected to each other.
    """

    def __init__(self, name: str, description: str, id: str, area_list: list[Area], connections: dict[Area,list[Area]]):
        """Initialize with `name`, `description`, and `id`.
        
        Args:
            name (str): The map's name.
            description (str): Description of the map.
            id (str): Unique identifier for the map.
            area_list (list[Area]): All areas in the game world.
            connections (dict[Area,list[Area]]): Adjacency information for areas.
        """
        super().__init__(name, description, id)
        self.area_list = area_list if area_list else []
        self.connections = connections if connections else {}
    
    def get_from_id(self, id: str) -> Area | Room | Place | None:
        """Get an area, room, or place by its ID.
        
        Searches the entire map hierarchy to find an object with the given ID.
        
        Args:
            id (str): The unique identifier to search for.
            
        Returns:
            Area | Room | Place | None: The found object, or None if not found.
        """
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