from __future__ import annotations

import random

from typing import TYPE_CHECKING, Callable

from pyStory.crash import error_proceding

#Fixes circular imports
if TYPE_CHECKING:
    from pyStory.elements import Game

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
    def has_events(cls) -> bool:
        """Check if there are any events currently in the sequence.
        
        Returns:
            bool: True if there are events in the sequence, False otherwise.
        """
        return len(cls.events) > 0

    @classmethod
    def get_oldest_event(cls) -> Event|None:
        """Get the oldest event in the sequence without removing it.
        
        Returns:
            Event|None: The oldest event if the sequence is not empty, None otherwise.
        """
        if cls.events:
            return cls.events[0]
        else:
            return None

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

class HasMovedEvent(Event):
    """Event triggered after the player has successfully moved to a new location.
    
    This event is created after a movement action has been completed, allowing the game
    to react to the player's arrival at a new location. It differs from MoveEvent, which
    represents the intent to move before the action is executed.
    
    Attributes:
        target_place_name (str): The name of the location the player has moved to.
    """
    def __init__(self, target_place_name:str):
        """Initialize a has moved event.
        
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
    def __init__(self, id: str, trigger_events: tuple[Event,...], required_flags: set[str], effect: Callable[[Game], None], solve_normally: bool = False):
        """Initialize a story situation.
        
        Args:
            id (str): Unique identifier for the situation.
            trigger_events (tuple[Event]): The events that can trigger this situation.
            required_flags (set[str]): Flags that must be present for the situation to trigger.
            effect (Callable): Function taking a Game parameter to execute.
            solve_normally (bool): Whether to also solve the event normally. Defaults to False.
        """
        self.id = id
        self.trigger_events = trigger_events
        self.required_flags = required_flags
        self.effect = effect
        self.solve_normally = solve_normally

    def is_trigger(self, event: Event) -> bool:
        """Check if the given event matches any of the trigger events.
        
        Args:
            event (Event): The event to check.
            
        Returns:
            bool: True if the event matches any of the trigger events.
        """
        return any(Event.match(trigger_event, event) for trigger_event in self.trigger_events)

    def execute_effect(self, game: Game):
        """Execute the effect of the story situation.
        
        Args:
            game (Game): The game instance.
        """
        self.effect(game)

def find_story(game: Game, event:Event, story_situations: list[StorySituation]) -> tuple[StorySituation|None, bool]:
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
        if situation.is_trigger(event) and not (situation.id in game.triggered_events): 
            if situation.required_flags.issubset(set(game.triggered_events)):
                return situation, True
            else:
                return situation, False
    return None, True

def solve_story(game:Game, situation:StorySituation, event:Event):
    """Execute the effect of a triggered story situation and update game state.
    
    This function handles the execution of a story situation's effect, marks the
    situation as triggered, and optionally applies standard event solving.
    
    Args:
        game (Game): The game instance.
        situation (StorySituation): The story situation to execute.
    """
    #Check if an event triggers any story situation and execute its effect if it does
    situation.execute_effect(game)
    game.trigger_situation(situation.id)
    if situation.solve_normally:
        solve_standard_event(game, event)

def solve_standard_event(game: Game, event: Event) -> tuple[bool, str]:
    """Process and solve a standard game event.
    
    Handles the game logic for standard events (move, take item, inspect, think, help).
    Returns information about whether the screen needs refreshing and a message for the player.
    
    Args:
        game (Game): The game instance.
        event (Event): The event to process.
        
    Returns:
        tuple[bool, str]: (screen_refresh_needed, message_to_player)
    """
    if isinstance(event, MoveEvent):
        target_place_name = event.target_place_name
        room = game.player.current_room
        place = game.player.current_place
        area = game.player.current_area
        if game.player.in_place(target_place_name) or game.player.in_room(target_place_name):
            return False, "Ya estas aquí."
        
        if room.has_place(target_place_name):
            new_place = room.get_place(target_place_name)
            if new_place is None:
                error_proceding(game, game.player, event)
            game.player.current_place = new_place
            new_place.gets_discovered()
            EventSeq.add_event(HasMovedEvent(target_place_name))
            return False, f"Te moviste hacia {target_place_name}."
        
        if area.has_room_from_name(target_place_name):
            target_room = area.get_room_by_name(target_place_name)
            if target_room is None:
                error_proceding(game, game.player, event)
            if area.is_connected(target_room, room):
                game.player.current_room = target_room
                game.player.current_place = target_room
                target_room.gets_discovered()
                EventSeq.add_event(HasMovedEvent(target_place_name))
                return True, f"Te moviste hacia {target_place_name}."
            elif target_room.isknown:
                return False, f"No creo que pueda ir hacia {target_place_name} desde aquí."
            else:
                return False, f"No conozco ningún lugar llamado {target_place_name}."
        else:
            return False, f"No creo que haya eso por aquí."
    
    elif isinstance(event, TakeItemEvent):
        item_name = event.item_name
        place = game.player.current_place
        if place.has_item_by_name(item_name):
            item = place.get_item_by_name(item_name)
            if item is None:
                error_proceding(game, game.player, event)
            if item.takeable:
                game.player.items.append(item)
                place.item_list.remove(item)
                return False, f"Has tomado {item_name}."
            else:
                return False, f"No creo que me sirva tomar {item_name}."
        else:
            return False, f"No creo que haya un objeto llamado {item_name} justo aquí."
    
    elif isinstance(event, InspectEvent):
        target_object_name = event.target_object_name
        place = game.player.current_place
        room = game.player.current_room
        area = game.player.current_area

        #Check if the object is in the current place
        if place.has_item_by_name(target_object_name):
            item = place.get_item_by_name(target_object_name)
            if item is None:
                error_proceding(game, game.player, event)
            return False, item.description
        
        #Check if the object is the current place
        if place.name.lower() == target_object_name.lower():
            return False, place.description
        
        #Check if the object is the current room
        if room.name.lower() == target_object_name.lower():
            return False, room.description
        
        #Si nos estamos examinando
        if game.player.name.lower() == target_object_name.lower():
            return False, game.player.description
        
        if any(item_name.lower() == target_object_name.lower() for item_name in game.player.get_item_names()):
            item = game.player.get_item_by_name(target_object_name)
            if item is None:
                error_proceding(game, game.player, event)
            return False, item.description
        
        return False, f"No hay nada llamado {target_object_name} justo aquí."
    
    elif isinstance(event, ThinkEvent):
        if random.random() < CLUE_CHANCE:
            return False, game.throw_clue()
        else:
            return False, random.choice(game.player.thoughts)
    else:
        error_proceding(game, game.player, event)
        return True, "Ocurrió un error al procesar tu acción, se generó un archivo, mándamelo pls klsajfñls"

def process_input(response:str)->bool:
    """Parse player input and create corresponding game events.
    
    Processes player text input by parsing commands and creating appropriate event
    objects. Supports commands: MOVERSE A, TOMAR, USAR _ EN _, EXAMINAR, AYUDA, PENSAR.
    
    Args:
        response (str): Raw text input from the player.
        
    Returns:
        bool: True if input was valid and an event was created, False otherwise.
    """
    response_stripped = response.strip()
    response_lower = response_stripped.lower()
    
    if response_lower.startswith("moverse a "):
        target_place_name = response_lower[len("moverse a "):].strip()
        EventSeq.add_event(MoveEvent(target_place_name))
        return True
    elif response_lower.startswith("tomar "):
        item_name = response_lower[len("tomar "):].strip()
        EventSeq.add_event(TakeItemEvent(item_name))
        return True
    elif response_lower.startswith("usar "):
        use_payload = response_lower[len("usar "):].strip()
        separator = " en "
        if separator not in use_payload:
            return False

        separator_index = use_payload.find(separator)
        item_name = use_payload[:separator_index].strip()
        target_object_name = use_payload[separator_index + len(separator):].strip()
        if not item_name or not target_object_name:
            return False

        EventSeq.add_event(UseItemEvent(item_name, target_object_name))
        return True

    elif response_lower.startswith("examinar "):
        target_object_name = response_lower[len("examinar "):].strip()
        EventSeq.add_event(InspectEvent(target_object_name))
        return True
    elif response_lower == "ayuda":
        EventSeq.add_event(HelpEvent())
        return True
    elif response_lower == "pensar":
        EventSeq.add_event(ThinkEvent())
        return True
    elif response_lower == "salir":
        EventSeq.add_event(ExitEvent())
        return True
    else:
        return False