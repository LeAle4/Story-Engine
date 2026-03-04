from __future__ import annotations

import random

from typing import TYPE_CHECKING, Callable

from Engine.crash import error_proceding
from Engine.text import TUTORIAL

#Fixes circular imports
if TYPE_CHECKING:
    from game1 import Game, Player, Item

CLUE_CHANCE = 0.3

class Event:
    """Base class for events."""
    def __init__(self, params:dict):
        self.params = params

    @staticmethod
    def match(event1: Event, event2: Event) -> bool:
        """Check if two events match by comparing their parameters and Event type."""
        return event1.params == event2.params and type(event1) == type(event2)

class EventSeq:
    events: list[Event] = []

    @classmethod
    def resolve_event(cls, event:Event):
        """Resolve an event."""
        cls.events.remove(event)
    
    @classmethod
    def add_event(cls, event:Event):
        """Add an event to the sequence."""
        cls.events.append(event)
    
    @classmethod
    def get_events(cls):
        """Get the current events."""
        return cls.events

    @classmethod
    def clear_events(cls):
        """Clear all events."""
        cls.events.clear()

class MoveEvent(Event):
    """Event for moving the player."""
    def __init__(self, target_place_name: str):
        super().__init__({"target_place_name": target_place_name})
        self.target_place_name = target_place_name

class UseItemEvent(Event):
    """Event for using an item."""
    def __init__(self, item_name: str, target_object_name: str):
        super().__init__({"item_name": item_name, "target_object_name": target_object_name})
        self.item_name = item_name
        self.target_object_name = target_object_name

class InspectEvent(Event):
    """Event for inspecting an object."""
    def __init__(self, target_object_name: str):
        super().__init__({"target_object_name": target_object_name})
        self.target_object_name = target_object_name

class TakeItemEvent(Event):
    """Event for taking an item."""
    def __init__(self, item_name: str):
        super().__init__({"item_name": item_name})
        self.item_name = item_name

class ThinkEvent(Event):
    """Event for thinking about something."""
    def __init__(self):
        super().__init__({})

class HelpEvent(Event):
    """Event for asking for help."""
    def __init__(self):
        super().__init__({})

class StorySituation:
    def __init__(self, id: str, trigger_event: Event, effect: Callable[[Game, Player], None], solve_normally: bool = False):
        self.id = id
        self.trigger_event = trigger_event
        self.effect = effect
        self.solve_normally = solve_normally

    def is_trigger(self, event: Event) -> bool:
        """Check if the given event matches the trigger event."""
        return Event.match(self.trigger_event, event)

    def execute_effect(self, game: Game, player: Player):
        """Execute the effect of the story situation."""
        self.effect(game, player)

def is_story(game: Game, event:Event, story_situations: list[StorySituation]) -> bool:
    """Check if an event is a story event by comparing it against the triggers of the story situations."""
    for situation in story_situations:
        if situation.is_trigger(event)and not situation.id in game.triggered_events:
            return True
    return False

def solve_story(game:Game, player:Player, situation:StorySituation):
    """Check the current events against the story situations and execute the effects of any triggered situations."""
    #Check if an event triggers any story situation and execute its effect if it does
    situation.execute_effect(game, player)
    game.trigger_situation(situation.id)
    if situation.solve_normally:
        solve_standard_event(game, player, situation.trigger_event)

def solve_standard_event(game: Game, player: Player, event: Event) -> tuple[bool, str]:
    """Solve a standard event and return a tuple indicating if the screen should be refreshed."""
    if isinstance(event, MoveEvent):
        target_place_name = event.target_place_name
        room = player.current_room
        place = player.current_place
        area = player.current_area
        if player.in_place(target_place_name):
            return False, "Ya estas aquí."
        
        if room.has_place(target_place_name):
            new_place = room.get_place(target_place_name)
            if new_place is None:
                error_proceding(game, player, event)
            player.current_place = new_place
            new_place.gets_discovered()
            return False, f"Te moviste hacia {target_place_name}."
        
        if area.has_room_from_name(target_place_name):
            target_room = area.get_room_by_name(target_place_name)
            if target_room is None:
                error_proceding(game, player, event)
            if area.is_connected(target_room, room):
                player.current_room = target_room
                player.current_place = target_room
                target_room.gets_discovered()
                return True, f"Te moviste hacia {target_place_name}."
            elif target_room.isknown:
                return False, f"No creo que pueda ir hacia {target_place_name} desde aquí."
            else:
                return False, f"No conozco ningún lugar llamado {target_place_name}."
        else:
            return False, f"No creo que haya eso por aquí."
    
    elif isinstance(event, TakeItemEvent):
        item_name = event.item_name
        place = player.current_place
        if place.has_item_by_name(item_name):
            item = place.get_item_by_name(item_name)
            if item is None:
                error_proceding(game, player, event)
            player.items.append(item)
            place.item_list.remove(item)
            return False, f"Has tomado {item_name}."
        else:
            return False, f"No creo que haya un objeto llamado {item_name} justo aquí."
    
    elif isinstance(event, InspectEvent):
        target_object_name = event.target_object_name
        place = player.current_place
        room = player.current_room
        area = player.current_area

        #Check if the object is in the current place
        if place.has_item_by_name(target_object_name):
            item = place.get_item_by_name(target_object_name)
            if item is None:
                error_proceding(game, player, event)
            return False, item.description
        
        #Check if the object is the current place
        if place.name == target_object_name:
            return False, place.description
        
        #Check if the object is the current room
        if room.name == target_object_name:
            return False, room.description
        
        return False, f"No hay nada llamado {target_object_name} justo aquí."

    elif isinstance(event, HelpEvent):
        return True, TUTORIAL
    
    elif isinstance(event, ThinkEvent):
        if random.random() < CLUE_CHANCE:
            return False, random.choice(player.thoughts)
        else:
            return False, game.throw_clue()
    else:
        error_proceding(game, player, event)

def process_input(response:str)->bool:
    """Process the player's input and return the corresponding event."""
    response_stripped = response.strip()
    response_upper = response_stripped.upper()
    
    if response_upper.startswith("MOVERSE A "):
        target_place_name = response_stripped[len("MOVERSE A "):].strip()
        EventSeq.add_event(MoveEvent(target_place_name))
        return True
    elif response_upper.startswith("TOMAR "):
        item_name = response_stripped[len("TOMAR "):].strip()
        EventSeq.add_event(TakeItemEvent(item_name))
        return True
    elif response_upper.startswith("EXAMINAR "):
        target_object_name = response_stripped[len("EXAMINAR "):].strip()
        EventSeq.add_event(InspectEvent(target_object_name))
        return True
    elif response_upper == "AYUDA":
        EventSeq.add_event(HelpEvent())
        return True
    elif response_upper == "PENSAR":
        EventSeq.add_event(ThinkEvent())
        return True
    else:
        return False