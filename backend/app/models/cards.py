import random
import uuid

# Dummy card templates - placeholder data for MVP.
# Each card has a name, cost, and an effect description.
# Real card effects will be implemented later in game_logic.py.
CARD_TEMPLATES = {
    "Copper": {
        "name": "Copper",
        "cost": 0,
        "type": "treasure",
        "effect": "+1 Gold",
        "gold_value": 1,
        "image": "copper.png",
    },
    "Silver": {
        "name": "Silver",
        "cost": 3,
        "type": "treasure",
        "effect": "+2 Gold",
        "gold_value": 2,
        "image": "silver.png",
    },
    "Gold": {
        "name": "Gold",
        "cost": 6,
        "type": "treasure",
        "effect": "+3 Gold",
        "gold_value": 3,
        "image": "gold.png",
    },
    "Village": {
        "name": "Village",
        "cost": 3,
        "type": "action",
        "effect": "+1 Card, +2 Actions",
        "image": "village.png",
    },
    "Smithy": {
        "name": "Smithy",
        "cost": 4,
        "type": "action",
        "effect": "+3 Cards",
        "image": "smithy.png",
    },
    "Militia": {
        "name": "Militia",
        "cost": 4,
        "type": "action",
        "effect": "+2 Gold, opponent -2 HP",
        "image": "militia.png",
    },
    "Market": {
        "name": "Market",
        "cost": 5,
        "type": "action",
        "effect": "+1 Card, +1 Action, +1 Buy, +1 Gold",
        "image": "market.png",
    },
    "Witch": {
        "name": "Witch",
        "cost": 5,
        "type": "action",
        "effect": "+2 Cards, opponent -3 HP",
        "image": "witch.png",
    },
}

# Market supply configuration: how many of each card are available to buy
MARKET_SUPPLY = {
    "Copper": 30,
    "Silver": 20,
    "Gold": 15,
    "Village": 10,
    "Smithy": 10,
    "Militia": 10,
    "Market": 10,
    "Witch": 10,
}


_CLIENT_FIELDS = {"name", "cost", "type", "effect", "image"}


def get_client_templates():
    """Return card templates with only the fields safe to send to the client."""
    return {
        name: {k: v for k, v in template.items() if k in _CLIENT_FIELDS}
        for name, template in CARD_TEMPLATES.items()
    }


def create_card(template_name):
    """Create a card instance (just a reference + unique ID)."""
    return {
        "id": str(uuid.uuid4())[:8],
        "name": template_name,
    }


def create_starter_deck():
    """Create a starter deck: 7 Coppers + 3 random action cards."""
    deck = []
    for _ in range(7):
        deck.append(create_card("Copper"))
    # Add a few action cards so the game is playable from the start
    for name in ["Village", "Smithy", "Militia"]:
        deck.append(create_card(name))
    random.shuffle(deck)
    return deck


def create_market():
    """Create the shared market supply."""
    market = {}
    for name, count in MARKET_SUPPLY.items():
        market[name] = {
            "template": dict(CARD_TEMPLATES[name]),
            "count": count,
        }
    return market
