# Engine

A text-adventure game engine for creating interactive fiction and text-based adventure games.

## Features

- **GameObject System**: Base class for all interactive entities
- **Item Management**: Items that can be picked up, used, and interacted with
- **Location System**: Places and Rooms with spatial relationships
- **Area Navigation**: Connect locations with adjacency mapping
- **Player Character**: Full inventory management, movement, and interaction system
- **Flexible Callbacks**: Customizable behavior for actions and interactions

## Installation

### From source

```bash
pip install -e .
```

### For development

```bash
pip install -e ".[dev]"
```

## Quick Start

```python
from engine import Player, Area, Room, Item, Place

# Create game objects and start your adventure
# (Add your example code here)
```

## Classes

- **GameObject**: Base interactive entity with targeted_function
- **Item**: Targetable object that can be taken
- **Place**: Location that can contain items
- **Room**: Place with sub-places (e.g., tables, corners)
- **Area**: Adjacency map for places
- **Player**: Player with inventory, location, and movement

## Requirements

- Python >= 3.10

## License

MIT License (see LICENSE file)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
