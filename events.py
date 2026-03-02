class Event:
    """Base class for events."""
    pass

class MoveEvent(Event):
    """Event for moving the player."""
    pass

class UseItemEvent(Event):
    """Event for using an item."""
    pass

class InspectEvent(Event):
    """Event for inspecting an object."""
    pass

class ThinkEvent(Event):
    """Event for thinking about something."""
    pass

class HelpEvent(Event):
    """Event for asking for help."""
    pass

class Solver:
    pass
