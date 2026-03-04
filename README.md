# Engine

A text-adventure game engine for creating interactive fiction and text-based adventure games.

## Features

- **GameObject System**: Base class for all interactive entities
- **Item Management**: Items that can be picked up, used, and interacted with
- **Location System**: Places and Rooms with spatial relationships
- **Area Navigation**: Connect locations with adjacency mapping
- **Player Character**: Full inventory management, movement, and interaction system
- **Event System**: Handle player actions with a flexible event-driven architecture
- **Save/Load**: Built-in game state persistence with JSON serialization
- **Story System**: Trigger custom story situations based on player actions

## Installation

### From source

```bash
# Clone or download the repository
cd Engine
pip install -e .
```

### For development

```bash
pip install -e ".[dev]"
```

## Requirements

- Python >= 3.10

## Quick Start

### Basic Game Setup

```python
from Engine.elements import Game, Map, Area, Room, Place, Item, Player, NPC

# Create items
key = Item(
    name="llave",
    description="Una llave oxidada",
    id="key_001",
    used_msg="Usaste la llave",
    amount=1,
    use_times=1
)

# Create a place within a room
corner = Place(
    name="esquina",
    description="Una esquina oscura de la habitación",
    id="corner_001",
    item_list=[key],
    npc_list=[]
)

# Create a room
bedroom = Room(
    name="dormitorio",
    description="Un dormitorio pequeño y polvoriento",
    id="room_001",
    place_list=[corner],
    item_list=[],
    npc_list=[]
)

# Create an area with room connections
house = Area(
    name="casa",
    description="Una casa abandonada",
    id="area_001",
    room_list=[bedroom],
    conections={bedroom: []}  # Add connected rooms here
)

# Create the game map
game_map = Map(
    name="mundo",
    description="El mundo del juego",
    id="map_001",
    area_list=[house],
    connections={house: []}  # Add connected areas here
)

# Create the player
player = Player(
    name="jugador",
    description="Eres un aventurero",
    id="player_001",
    items=[],
    thoughts=("¿Qué hago aquí?", "Necesito encontrar la salida"),
    current_place=bedroom,
    current_room=bedroom,
    current_area=house
)

# Initialize the game
game = Game(game_map=game_map, player=player, clues=[])
```

### Using the Event System

```python
from Engine.logic import (
    EventSeq, MoveEvent, TakeItemEvent, InspectEvent,
    process_input, solve_standard_event
)

# Process player input
user_input = "TOMAR llave"
if process_input(user_input):
    # Get the generated event
    events = EventSeq.get_events()
    for event in events:
        refresh, message = solve_standard_event(game, player, event)
        print(message)
        EventSeq.resolve_event(event)
else:
    print("Comando no reconocido")
```

### Creating Story Situations

```python
from Engine.logic import StorySituation, InspectEvent

def on_inspect_key(game: Game, player: Player):
    """Custom effect when player inspects the key"""
    print("¡La llave brilla misteriosamente!")
    game.trigger_situation("key_inspected")

# Create a story situation
key_story = StorySituation(
    id="key_inspected",
    trigger_event=InspectEvent("llave"),
    effect=on_inspect_key,
    solve_normally=True  # Also run the standard inspect behavior
)
```

### Save and Load Game

```python
# Save the current game state
game.save_game("savegame.json")

# Load a saved game
game.load_game("savegame.json")
```

## Available Commands

When using the built-in command parser (`process_input`):

- `MOVERSE A <lugar>` - Move to a location
- `TOMAR <objeto>` - Take an item
- `EXAMINAR <objeto>` - Inspect an object
- `PENSAR` - Think (get a clue or random thought)
- `AYUDA` - Show help/tutorial

## Core Classes

- **GameObject**: Base interactive entity with name, description, and ID
- **Item**: Objects that can be picked up and used
- **Place**: Locations that can contain items and NPCs
- **Room**: Places with sub-places (like corners, tables, etc.)
- **Area**: Collections of connected rooms
- **Map**: The complete game world with connected areas
- **Player**: The player character with inventory and location tracking
- **NPC**: Non-player characters
- **Game**: Main game controller with save/load functionality

## Event Classes

- **Event**: Base class for all events
- **MoveEvent**: Player movement
- **TakeItemEvent**: Taking items
- **InspectEvent**: Inspecting objects
- **UseItemEvent**: Using items on targets
- **ThinkEvent**: Player thinking
- **HelpEvent**: Requesting help

## License

MIT License (see LICENSE file)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
