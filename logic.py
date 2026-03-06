from __future__ import annotations

import random

from typing import TYPE_CHECKING, Callable

from pyStory.crash import error_proceding
from pyStory.text import TUTORIAL

#Fixes circular imports
if TYPE_CHECKING:
    from pyStory.elements import Game, Player

CLUE_CHANCE = 0.3

class Event:
    """Base class for all game events.
    
    An event represents an action taken by the player or the system that can be processed
    and handled by the game logic.
    
    Attributes:
        params (dict): A dictionary containing event-specific parameters.
    """
    def __init__(self, params:dict):
        """Initialize an event with parameters.
        
        Args:
            params (dict): Dictionary containing event-specific parameters.
        """
        self.params = params

    @staticmethod
    def match(event1: Event, event2: Event) -> bool:
        """Check if two events match by comparing their parameters and Event type.
        
        Two events are considered a match if they are of the same type and have identical parameters.
        
        Args:
            event1 (Event): First event to compare.
            event2 (Event): Second event to compare.
            
        Returns:
            bool: True if events match, False otherwise.
        """
        return event1.params == event2.params and type(event1) == type(event2)

class EventSeq:
    """Manages a sequence of events to be processed.
    
    This class maintains a queue of events that have been triggered and need to be
    processed by the game. It provides methods to add, retrieve, and remove events
    from the sequence.
    
    Attributes:
        events (list[Event]): Class-level list of events in the sequence.
    """
    events: list[Event] = []

    @classmethod
    def resolve_event(cls, event:Event):
        """Remove an event from the sequence after it has been processed.
        
        Args:
            event (Event): The event to remove from the sequence.
        """
        cls.events.remove(event)
    
    @classmethod
    def add_event(cls, event:Event):
        """Add a new event to the sequence.
        
        Args:
            event (Event): The event to add to the sequence.
        """
        cls.events.append(event)
    
    @classmethod
    def get_events(cls):
        """Retrieve the current list of events.
        
        Returns:
            list[Event]: The list of all events in the sequence.
        """
        return cls.events

    @classmethod
    def clear_events(cls):
        """Clear all events from the sequence.
        
        This removes all events and resets the sequence.
        """
        cls.events.clear()

class MoveEvent(Event):
    """Event triggered when the player wants to move to a different location.
    
    This event is created when the player issues a movement command and contains
    the name of the destination.
    
    Attributes:
        target_place_name (str): The name of the location to move to.
    """
    def __init__(self, target_place_name: str):
        """Initialize a move event.
        
        Args:
            target_place_name (str): The name of the destination location.
        """
        super().__init__({"target_place_name": target_place_name})
        self.target_place_name = target_place_name

class UseItemEvent(Event):
    """Event triggered when the player wants to use an item on a target.
    
    This event is created when the player issues a use command, specifying which
    item to use and what object to use it on.
    
    Attributes:
        item_name (str): The name of the item in the player's inventory.
        target_object_name (str): The name of the object to use the item on.
    """
    def __init__(self, item_name: str, target_object_name: str):
        """Initialize a use item event.
        
        Args:
            item_name (str): The name of the item to use.
            target_object_name (str): The name of the target object.
        """
        super().__init__({"item_name": item_name, "target_object_name": target_object_name})
        self.item_name = item_name
        self.target_object_name = target_object_name

class InspectEvent(Event):
    """Event triggered when the player wants to examine an object or location.
    
    This event allows the player to view detailed descriptions of objects, items,
    rooms, and places.
    
    Attributes:
        target_object_name (str): The name of the object to inspect.
    """
    def __init__(self, target_object_name: str):
        """Initialize an inspect event.
        
        Args:
            target_object_name (str): The name of the object to inspect.
        """
        super().__init__({"target_object_name": target_object_name})
        self.target_object_name = target_object_name

class TakeItemEvent(Event):
    """Event triggered when the player picks up an item.
    
    This event is created when the player issues a take/pick up command for an item
    in their current location.
    
    Attributes:
        item_name (str): The name of the item to take.
    """
    def __init__(self, item_name: str):
        """Initialize a take item event.
        
        Args:
            item_name (str): The name of the item to pick up.
        """
        super().__init__({"item_name": item_name})
        self.item_name = item_name

class ThinkEvent(Event):
    """Event triggered when the player thinks/reflects.
    
    This event gives the player a clue or thought, either from their internal
    thoughts or from game clues.
    """
    def __init__(self):
        """Initialize a think event."""
        super().__init__({})

class HelpEvent(Event):
    """Event triggered when the player asks for help.
    
    This event displays the game tutorial and help information.
    """
    def __init__(self):
        """Initialize a help event."""
        super().__init__({})

class ExitEvent(Event):
    """Event triggered when the player wants to exit the game.
    
    This event is created when the player issues an exit/quit command.
    """
    def __init__(self):
        """Initialize an exit event."""
        super().__init__({})

class StorySituation:
    """Represents a story event with a trigger condition and an effect.
    
    Story situations are used to implement narrative branching and special events
    in the game. When the trigger event occurs, the associated effect is executed.
    
    Attributes:
        id (str): Unique identifier for this story situation.
        trigger_event (Event): The event that must occur to trigger this situation.
        effect (Callable): Function to execute when the trigger occurs.
        solve_normally (bool): Whether to also apply standard event solving after the effect.
    """
    def __init__(self, id: str, trigger_event: Event, effect: Callable[[Game, Player], None], solve_normally: bool = False):
        """Initialize a story situation.
        
        Args:
            id (str): Unique identifier for the situation.
            trigger_event (Event): The event that triggers this situation.
            effect (Callable): Function taking (Game, Player) parameters to execute.
            solve_normally (bool): Whether to also solve the event normally. Defaults to False.
        """
        self.id = id
        self.trigger_event = trigger_event
        self.effect = effect
        self.solve_normally = solve_normally

    def is_trigger(self, event: Event) -> bool:
        """Check if the given event matches the trigger event.
        
        Args:
            event (Event): The event to check.
            
        Returns:
            bool: True if the event matches the trigger event.
        """
        return Event.match(self.trigger_event, event)

    def execute_effect(self, game: Game, player: Player):
        """Execute the effect of the story situation.
        
        Args:
            game (Game): The game instance.
            player (Player): The player instance.
        """
        self.effect(game, player)

def is_story(game: Game, event:Event, story_situations: list[StorySituation]) -> bool:
    """Check if an event is a story event by comparing it against the triggers of the story situations.
    
    Determines whether the given event matches any untriggered story situation trigger.
    
    Args:
        game (Game): The game instance.
        event (Event): The event to check.
        story_situations (list[StorySituation]): List of all possible story situations.
        
    Returns:
        bool: True if the event matches an untriggered story situation, False otherwise.
    """
    for situation in story_situations:
        if situation.is_trigger(event)and not situation.id in game.triggered_events:
            return True
    return False

def solve_story(game:Game, player:Player, situation:StorySituation):
    """Execute the effect of a triggered story situation and update game state.
    
    This function handles the execution of a story situation's effect, marks the
    situation as triggered, and optionally applies standard event solving.
    
    Args:
        game (Game): The game instance.
        player (Player): The player instance.
        situation (StorySituation): The story situation to execute.
    """
    #Check if an event triggers any story situation and execute its effect if it does
    situation.execute_effect(game, player)
    game.trigger_situation(situation.id)
    if situation.solve_normally:
        solve_standard_event(game, player, situation.trigger_event)

def solve_standard_event(game: Game, player: Player, event: Event) -> tuple[bool, str]:
    """Process and solve a standard game event.
    
    Handles the game logic for standard events (move, take item, inspect, think, help).
    Returns information about whether the screen needs refreshing and a message for the player.
    
    Args:
        game (Game): The game instance.
        player (Player): The player instance.
        event (Event): The event to process.
        
    Returns:
        tuple[bool, str]: (screen_refresh_needed, message_to_player)
    """
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
            if item.takeable:
                player.items.append(item)
                place.item_list.remove(item)
                return False, f"Has tomado {item_name}."
            else:
                return False, f"No creo que pueda tomar {item_name}."
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
        
        if player.name == target_object_name:
            return False, player.description
        
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
        return True, "Ocurrió un error al procesar tu acción, se generó un archivo, mándamelo pls klsajfñls"

def process_input(response:str)->bool:
    """Parse player input and create corresponding game events.
    
    Processes player text input by parsing commands and creating appropriate event
    objects. Supports commands: MOVERSE A, TOMAR, EXAMINAR, AYUDA, PENSAR.
    
    Args:
        response (str): Raw text input from the player.
        
    Returns:
        bool: True if input was valid and an event was created, False otherwise.
    """
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
    elif response_upper == "SALIR":
        EventSeq.add_event(ExitEvent())
        return True
    else:
        return False