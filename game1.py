from events import Event, MoveEvent, UseItemEvent, InspectEvent, ThinkEvent, HelpEvent

def _get_location_by_id(place_id: str, map: Map) -> tuple[bool, tuple[Place | None, Room | None, Area | None, Map | None]]:
    """Search for a place by its ID in the map and return it along with its room, area, and the map."""
    for area in map.area_list:
        for room in area.room_list:
            if room.id == place_id:
                return True, (room, room, area, map)
            for place in room.place_list:
                if place.id == place_id:
                    return True, (place, room, area, map)
    return False, (None, None, None, None)

class Game:
    pass

class GameObject:
    """Base interactive entity with `targeted_function`."""

    def __init__(self, name: str, description: str, id: str):
        """Initialize with `name`, `description`, and `id`."""
        self.name = name
        self.description = description
        self.id = id
        self.isknown = False

    def as_saveable_object(self):
        """Return a dictionary representation of the object for saving."""
        return {
            'name': self.name,
            'description': self.description,
            'id': self.id
        }
    
    def load_from_json_object(self, json_object:dict):
        """Load object properties from a JSON object."""
        self.name = json_object['name']
        self.description = json_object['description']
        self.id = json_object['id']

class Player(GameObject):
    """Player character, inherits from `GameObject`."""

    def __init__(self, name: str, description: str, id: str, items: list[Item], current_room: Room):
        """Initialize with `name`, `description`, and `id`."""
        super().__init__(name, description, id)
        self.items = items if items is not None else []
        self.current_room = current_room
    
    def as_saveable_object(self):
        base_dict = super().as_saveable_object()
        base_dict.update({
            'items': [item.as_saveable_object() for item in self.items],
            'current_room': self.current_room.id if self.current_room else None
        })
        return base_dict
    
    def load_from_json_object(self, json_object: dict):
        super().load_from_json_object(json_object)
        self.items = [Item(**item_data) for item_data in json_object.get('items', [])]
        self.current_room = Room(**json_object['current_room']) if json_object.get('current_room') else None

class NPC(GameObject):
    """Non-player character, inherits from `GameObject`."""

    def __init__(self, name: str, description: str, id: str):
        """Initialize with `name`, `description`, and `id`."""
        super().__init__(name, description, id)
    
    def as_saveable_object(self):
        return super().as_saveable_object()
    
    def load_from_json_object(self, json_object: dict):
        super().load_from_json_object(json_object)

class Item(GameObject):
    """Item that can be interacted with, inherits from `GameObject`."""

    def __init__(self, name: str, description: str, id: str, used_msg: str, amount: int = 1, use_times:int = 1):
        """Initialize with `name`, `description`, and `id`."""
        super().__init__(name, description, id)
        self.used_msg = used_msg if used_msg else f"Usaste {name}."
        self.amount = amount
        self.use_times = use_times
    
    def as_saveable_object(self):
        base_dict = super().as_saveable_object()
        base_dict.update({
            'used_msg': self.used_msg,
            'amount': self.amount,
            'use_times': self.use_times
        })
        return base_dict

    def load_from_json_object(self, json_object: dict):
        super().load_from_json_object(json_object)
        self.used_msg = json_object['used_msg']
        self.amount = json_object['amount']
        self.use_times = json_object['use_times']

class Place(GameObject):
    """Location in the game world, inherits from `GameObject`."""

    def __init__(self, name: str, description: str, id: str, item_list: list[Item], npc_list: list[NPC]):
        """Initialize with `name`, `description`, and `id`."""
        super().__init__(name, description, id)
        self.item_list = item_list if item_list is not None else []
        self.npc_list = npc_list if npc_list is not None else []
    
    def as_saveable_object(self):
        base_dict = super().as_saveable_object()
        base_dict.update({
            'item_list': [item.as_saveable_object() for item in self.item_list],
            'npc_list': [npc.as_saveable_object() for npc in self.npc_list]
        })
        return base_dict
    
    def load_from_json_object(self, json_object: dict):
        super().load_from_json_object(json_object)
        self.item_list = [Item(**item_data) for item_data in json_object.get('item_list', [])]
        self.npc_list = [NPC(**npc_data) for npc_data in json_object.get('npc_list', [])]

class Room(Place):
    """Room in the game world, inherits from `Place`."""

    def __init__(self, name: str, description: str, id: str, place_list: list[Place], item_list: list[Item], npc_list: list[NPC]):
        """Initialize with `name`, `description`, and `id`."""
        super().__init__(name, description, id, item_list, npc_list)
        self.place_list = place_list if place_list is not None else []
    
    def as_saveable_object(self):
        base_dict = super().as_saveable_object()
        base_dict.update({
            'place_list': [place.as_saveable_object() for place in self.place_list]
        })
        return base_dict
    
    def load_from_json_object(self, json_object: dict):
        super().load_from_json_object(json_object)
        self.place_list = [Place(**place_data) for place_data in json_object.get('place_list', [])]

class Area(GameObject):
    """Area in the game world, inherits from `GameObject`."""

    def __init__(self, name: str, description: str, id: str, room_list: list[Room], conections: dict[Room,list[Room]]):
        """Initialize with `name`, `description`, and `id`."""
        super().__init__(name, description, id)
        self.room_list = room_list if room_list  else []
        self.conections = conections if conections  else {}
    
    def as_saveable_object(self):
        base_dict = super().as_saveable_object()
        base_dict.update({
            'room_list': [room.as_saveable_object() for room in self.room_list],
            'conections': {room.id: [connected_room.id for connected_room in connections] 
                          for room, connections in self.conections.items()}
        })
        return base_dict
    
    def load_from_json_object(self, json_object: dict, room_dict: dict | None = None):
        super().load_from_json_object(json_object)
        self.room_list = [Room(**room_data) for room_data in json_object.get('room_list', [])]
        
        # Rebuild room_dict for connection mapping
        if room_dict is None:
            room_dict = {room.id: room for room in self.room_list}
        
        # Reconstruct connections using room IDs
        conections_data = json_object.get('conections', {})
        self.conections = {room_dict[room_id]: [room_dict[conn_id] for conn_id in conn_ids]
                          for room_id, conn_ids in conections_data.items() if room_id in room_dict}

class Map(GameObject):
    """Map of the game world, inherits from `GameObject`."""

    def __init__(self, name: str, description: str, id: str, area_list: list[Area], connections: dict[Area,list[Area]]):
        """Initialize with `name`, `description`, and `id`."""
        super().__init__(name, description, id)
        self.area_list = area_list if area_list else []
        self.connections = connections if connections else {}
    
    def as_saveable_object(self):
        base_dict = super().as_saveable_object()
        base_dict.update({
            'area_list': [area.as_saveable_object() for area in self.area_list],
            'connections': {area.id: [connected_area.id for connected_area in connections]
                           for area, connections in self.connections.items()}
        })
        return base_dict
    
    def load_from_json_object(self, json_object: dict, area_dict: dict | None = None):
        super().load_from_json_object(json_object)
        self.area_list = [Area(**area_data) for area_data in json_object.get('area_list', [])]
        
        # Rebuild area_dict for connection mapping
        if area_dict is None:
            area_dict = {area.id: area for area in self.area_list}
        
        # Reconstruct connections using area IDs
        connections_data = json_object.get('connections', {})
        self.connections = {area_dict[area_id]: [area_dict[conn_id] for conn_id in conn_ids]
                           for area_id, conn_ids in connections_data.items() if area_id in area_dict}