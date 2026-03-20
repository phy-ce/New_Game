import random
from app.models.cards import (
    CARD_TEMPLATES,
    create_starter_deck,
    create_market,
    create_card,
)

HAND_SIZE = 5


def _draw_cards(player, count):
    """Draw cards from deck into hand. Reshuffles discard if deck is empty."""
    for _ in range(count):
        if not player["deck"]:
            if not player["discard"]:
                break  # No cards left anywhere
            player["deck"] = player["discard"]
            player["discard"] = []
            random.shuffle(player["deck"])
        player["hand"].append(player["deck"].pop())


def _reset_turn_state(game):
    """Reset turn state for a new turn."""
    game["turn_state"] = {
        "energy": 3,
        "buys": 1,
        "gold": 0,
        "cards_played": 0,
        "last_played": None,
    }


def start_game(game):
    """Initialize decks, market, draw starting hands, begin turn 1."""
    game["status"] = "playing"
    game["turn"] = 1
    game["current_player"] = 0
    game["market"] = create_market()
    game["pending_choice"] = None
    game["log"] = ["Game started!"]

    for player in game["players"]:
        player["deck"] = create_starter_deck()
        player["hand"] = []
        player["discard"] = []
        _draw_cards(player, HAND_SIZE)

    _reset_turn_state(game)
    game["log"].append(f"{game['players'][0]['name']}'s turn.")


def play_card(game, player_index, card_id):
    """Play a card from hand. Returns (success, error)."""
    if game["pending_choice"] is not None:
        return False, "Must resolve pending choice first"
    if game["current_player"] != player_index:
        return False, "Not your turn"

    player = game["players"][player_index]
    turn = game["turn_state"]

    # Find card in hand
    card = None
    for i, c in enumerate(player["hand"]):
        if c["id"] == card_id:
            card = player["hand"].pop(i)
            break
    if card is None:
        return False, "Card not in hand"

    # Action cards cost an action to play
    if CARD_TEMPLATES[card["name"]]["type"] == "action":
        if turn["actions"] <= 0:
            player["hand"].append(card)  # Put it back
            return False, "No actions remaining"
        turn["actions"] -= 1

    # Apply card effects (placeholder MVP logic)
    _apply_card_effect(game, player_index, card)

    turn["cards_played"] += 1
    turn["last_played"] = card

    # Card goes to discard after being played
    player["discard"].append(card)

    game["log"].append(
        f"{player['name']} plays {card['name']} ({CARD_TEMPLATES[card['name']]['effect']})"
    )
    return True, None


def _apply_card_effect(game, player_index, card):
    """Apply a card's effect. Placeholder MVP implementations."""
    player = game["players"][player_index]
    opponent = game["players"][1 - player_index]
    turn = game["turn_state"]

    name = card["name"]

    if name == "Copper":
        turn["gold"] += 1
    elif name == "Silver":
        turn["gold"] += 2
    elif name == "Gold":
        turn["gold"] += 3
    elif name == "Village":
        _draw_cards(player, 1)
        turn["actions"] += 2
    elif name == "Smithy":
        _draw_cards(player, 3)
    elif name == "Militia":
        turn["gold"] += 2
        opponent["hp"] -= 2
    elif name == "Market":
        _draw_cards(player, 1)
        turn["actions"] += 1
        turn["buys"] += 1
        turn["gold"] += 1
    elif name == "Witch":
        _draw_cards(player, 2)
        opponent["hp"] -= 3


def buy_card(game, player_index, card_name):
    """Buy a card from the market. Returns (success, error)."""
    if game["pending_choice"] is not None:
        return False, "Must resolve pending choice first"
    if game["current_player"] != player_index:
        return False, "Not your turn"

    player = game["players"][player_index]
    turn = game["turn_state"]

    if turn["buys"] <= 0:
        return False, "No buys remaining"
    if card_name not in game["market"]:
        return False, "Card not in market"

    pile = game["market"][card_name]
    if pile["count"] <= 0:
        return False, "Card is sold out"

    cost = pile["template"]["cost"]
    if turn["gold"] < cost:
        return False, f"Not enough gold (need {cost}, have {turn['gold']})"

    # Deduct cost and buy
    turn["gold"] -= cost
    turn["buys"] -= 1
    pile["count"] -= 1

    # Bought card goes to discard
    new_card = create_card(card_name)
    player["discard"].append(new_card)

    game["log"].append(f"{player['name']} buys {card_name} (cost {cost})")
    return True, None


def resolve_choice(game, player_index, choice):
    """Resolve a pending choice. Returns (success, error).
    No cards use this in MVP, but the plumbing is here."""
    if game["pending_choice"] is None:
        return False, "No pending choice"
    if game["current_player"] != player_index:
        return False, "Not your turn"

    pending = game["pending_choice"]
    if choice not in pending["options"]:
        return False, "Invalid choice"

    # TODO: Apply the choice effect based on pending["type"] and pending["source_card"]
    game["log"].append(f"{game['players'][player_index]['name']} chose: {choice}")
    game["pending_choice"] = None
    return True, None


def end_turn(game, player_index):
    """End current player's turn. Discard hand, draw new hand, switch player."""
    if game["pending_choice"] is not None:
        return False, "Must resolve pending choice first"
    if game["current_player"] != player_index:
        return False, "Not your turn"

    player = game["players"][player_index]

    # Discard remaining hand
    player["discard"].extend(player["hand"])
    player["hand"] = []

    # Switch to other player
    game["current_player"] = 1 - player_index
    game["turn"] += 1

    # Reset turn state and draw for next player
    _reset_turn_state(game)
    next_player = game["players"][game["current_player"]]
    _draw_cards(next_player, HAND_SIZE)

    game["log"].append(f"{next_player['name']}'s turn.")
    return True, None


def check_game_over(game):
    """Check if any player's HP is at 0 or below. Returns winner index or None."""
    for i, p in enumerate(game["players"]):
        if p["hp"] <= 0:
            winner = 1 - i
            game["winner"] = winner
            game["status"] = "finished"
            game["log"].append(f"{game['players'][winner]['name']} wins!")
            return winner
    return None
