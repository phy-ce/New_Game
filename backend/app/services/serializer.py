def serialize_for_player(game, player_index):
    """Return a version of the game state safe to send to player_index.

    - Player sees their own hand, but NOT their deck/discard contents (only counts).
    - Player sees opponent's HP, name, board, hand COUNT, deck COUNT, discard COUNT.
    - Market and turn_state are fully visible to both players.
    - Log is fully visible to both players.
    """
    opponent_index = 1 - player_index
    me = game["players"][player_index]
    opp = game["players"][opponent_index]

    return {
        "lobby_code": game["lobby_code"],
        "status": game["status"],
        "turn": game["turn"],
        "is_my_turn": game["current_player"] == player_index,
        "winner": game.get("winner"),
        "winner_name": game["players"][game["winner"]]["name"] if game.get("winner") is not None else None,
        "log": game["log"][-50:],  # Last 50 log entries

        "market": game["market"],

        "turn_state": game["turn_state"],

        "pending_choice": game["pending_choice"],

        "me": {
            "name": me["name"],
            "hp": me["hp"],
            "max_hp": me["max_hp"],
            "hand": me["hand"],
            "deck_count": len(me["deck"]),
            "discard_count": len(me["discard"]),
        },

        "opponent": {
            "name": opp["name"],
            "hp": opp["hp"],
            "max_hp": opp["max_hp"],
            "hand_count": len(opp["hand"]),
            "deck_count": len(opp["deck"]),
            "discard_count": len(opp["discard"]),
        },
    }
