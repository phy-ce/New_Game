import random
import string

# Global in-memory store: { "ABC123": { ...game_state... } }
games = {}


def generate_code():
    """Generate a unique 6-char alphanumeric lobby code."""
    while True:
        code = "".join(random.choices(string.ascii_uppercase + string.digits, k=6))
        if code not in games:
            return code


def create_game(player_name, sid):
    """Create a new game with one player. Returns the lobby code."""
    code = generate_code()
    games[code] = {
        "lobby_code": code,
        "status": "waiting",
        "turn": 0,
        "current_player": 0,
        "winner": None,
        "log": [],
        "market": {},
        "turn_state": {
            "energy": 0,
            "buys": 0,
            "gold": 0,
            "cards_played": 0,
            "last_played": None,
        },
        "pending_choice": None,
        "players": [
            {
                "sid": sid,
                "name": player_name,
                "hp": 30,
                "max_hp": 30,
                "max_energy": 3,
                "hand": [],
                "deck": [],
                "discard": [],
            }
        ],
    }
    return code


def join_game(code, player_name, sid):
    """Add a second player to an existing game. Returns (success, error_message)."""
    if code not in games:
        return False, "Game not found"
    game = games[code]
    if game["status"] != "waiting":
        return False, "Game already started"
    if len(game["players"]) >= 2:
        return False, "Game is full"
    # Prevent duplicate names
    if game["players"][0]["name"] == player_name:
        return False, "Name already taken"
    game["players"].append(
        {
            "sid": sid,
            "name": player_name,
            "hp": 30,
            "max_hp": 30,
            "hand": [],
            "deck": [],
            "discard": [],
        }
    )
    return True, None


def reconnect(code, player_name, new_sid):
    """Update a player's socket ID on reconnect. Returns (player_index, error)."""
    if code not in games:
        return None, "Game not found"
    game = games[code]
    for i, p in enumerate(game["players"]):
        if p["name"] == player_name:
            p["sid"] = new_sid
            return i, None
    return None, "Player not found in this game"


def get_game(code):
    """Get a game by lobby code, or None."""
    return games.get(code)


def find_player_index(game, sid):
    """Find which player index (0 or 1) a socket ID belongs to. Returns None if not found."""
    for i, p in enumerate(game["players"]):
        if p["sid"] == sid:
            return i
    return None
