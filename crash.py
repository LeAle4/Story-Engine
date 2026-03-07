from __future__ import annotations

import json
import time
import traceback
from typing import TYPE_CHECKING, NoReturn

if TYPE_CHECKING:
    from Engine.elements import Game, Player
    from Engine.logic import Event

def error_proceding(game: Game, player: Player, event: Event) -> NoReturn:
    """Handle an error by saving the game and generating a crash report.
    
    This function is called when an unexpected error occurs during game execution.
    It saves the current game state, generates a detailed crash report, and exits.
    
    Args:
        game (Game): The game instance.
        player (Player): The player instance.
        event (Event): The event that caused the error.
        
    Raises:
        SystemExit: Always exits with code 1 after showing error message.
    """
    game.save_game("error_save.json")
    generate_crash_report(game, player, event)
    print("Error Fatal: Algo hice mal en el código, se debe guardó el juego y se generó un reporte de error para que pueda arreglarlo, mándamelo nada más puedas, sorryyy :c.")
    print("El juego se cerrará automáticamente en 10 segundos...")
    time.sleep(10)
    exit(1)

def generate_crash_report(game: Game, player: Player, event: Event) -> str:
    """Generate a comprehensive crash report including all game information at the point of crash.
    
    Creates a detailed report containing player state, event details, triggered events,
    and complete map state. Saves the report to 'crash_report.txt' for debugging.
    
    Args:
        game (Game): The game instance.
        player (Player): The player instance.
        event (Event): The event that triggered the error.
        
    Returns:
        str: JSON-formatted string containing all crash report data.
    """
    # Prefer the active exception traceback; if none exists, include the current call stack.
    exception_traceback = traceback.format_exc()
    if exception_traceback.strip() == "NoneType: None":
        exception_traceback = ""

    stack_trace = "".join(traceback.format_stack())
    report_data = {
        "player_state": {
            "name": player.name,
            "id": player.id,
            "description": player.description,
            "current_room": player.current_room.name,
            "current_room_id": player.current_room.id,
            "current_place": player.current_place.name,
            "current_place_id": player.current_place.id,
            "inventory": [
                {
                    "name": item.name,
                    "id": item.id,
                    "description": item.description,
                    "amount": item.amount,
                    "use_times": item.use_times
                }
                for item in player.items
            ]
        },
        "event_details": {
            "event_type": type(event).__name__,
            "event_params": event.params
        },
        "game_state": {
            "map": game.map.as_saveable_object(),
            "triggered_events": game.triggered_events
        },
        "traceback": {
            "exception_traceback": exception_traceback,
            "stack_trace": stack_trace
        }
    }
    
    with open("game_error_report.txt", "w") as f:
        f.write("=" * 80 + "\n")
        f.write("CRASH REPORT\n")
        f.write("=" * 80 + "\n\n")
        
        f.write("PLAYER STATE:\n")
        f.write("-" * 80 + "\n")
        f.write(f"Player: {player.name} (ID: {player.id})\n")
        f.write(f"Current Room: {player.current_room.name} (ID: {player.current_room.id})\n")
        f.write(f"Current Place: {player.current_place.name} (ID: {player.current_place.id})\n")
        f.write(f"Inventory ({len(player.items)} items):\n")
        for item in player.items:
            f.write(f"  - {item.name} (ID: {item.id}, Amount: {item.amount}, Uses: {item.use_times})\n")
        f.write("\n")
        
        f.write("EVENT DETAILS:\n")
        f.write("-" * 80 + "\n")
        f.write(f"Event Type: {type(event).__name__}\n")
        f.write(f"Event Parameters: {json.dumps(event.params, indent=2, default=str)}\n")
        f.write("\n")

        f.write("TRACEBACK:\n")
        f.write("-" * 80 + "\n")
        if exception_traceback:
            f.write("Exception Traceback:\n")
            f.write(exception_traceback)
            if not exception_traceback.endswith("\n"):
                f.write("\n")
        else:
            f.write("No active exception traceback was available at crash time.\n")
        f.write("\nCurrent Stack Trace:\n")
        f.write(stack_trace)
        if not stack_trace.endswith("\n"):
            f.write("\n")
        f.write("\n")
        
        f.write("TRIGGERED EVENTS:\n")
        f.write("-" * 80 + "\n")
        if game.triggered_events:
            for triggered_event in game.triggered_events:
                f.write(f"  - {triggered_event}\n")
        else:
            f.write("  No triggered events recorded.\n")
        f.write("\n")
        
        f.write("MAP STATE:\n")
        f.write("-" * 80 + "\n")
        f.write(json.dumps(report_data["game_state"]["map"], indent=2, default=str))
        f.write("\n\n")
        
        f.write("FULL REPORT (JSON):\n")
        f.write("-" * 80 + "\n")
        f.write(json.dumps(report_data, indent=2, default=str))
    
    return json.dumps(report_data, indent=2, default=str)
    