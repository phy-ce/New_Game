import random
import uuid
from app.services.effects import gain_gold, gain_energy, draw, do_damage, gain_buys, summon

CARD_TEMPLATES = {
    "Copper": {
        "name": "Copper",
        "cost": 0,
        "energy_cost": 0,
        "type": "treasure",
        "effect": "+1 Gold",
        "image": "copper.png",
        "effects": [gain_gold(1)],
    },
    "Silver": {
        "name": "Silver",
        "cost": 3,
        "energy_cost": 0,
        "type": "treasure",
        "effect": "+2 Gold",
        "image": "silver.png",
        "effects": [gain_gold(2)],
    },
    "Gold": {
        "name": "Gold",
        "cost": 6,
        "energy_cost": 0,
        "type": "treasure",
        "effect": "+3 Gold",
        "image": "gold.png",
        "effects": [gain_gold(3)],
    },
    "Village": {
        "name": "Village",
        "cost": 3,
        "energy_cost": 1,
        "type": "action",
        "effect": "+1 Card, +1 Energy",
        "image": "village.png",
        "effects": [draw(1), gain_energy(1)],
    },
    "Smithy": {
        "name": "Smithy",
        "cost": 4,
        "energy_cost": 1,
        "type": "action",
        "effect": "+3 Cards",
        "image": "smithy.png",
        "effects": [draw(3)],
    },
    "Militia": {
        "name": "Militia",
        "cost": 4,
        "energy_cost": 1,
        "type": "action",
        "effect": "+2 Gold, opponent -2 HP",
        "image": "militia.png",
        "effects": [gain_gold(2), do_damage(2)],
    },
    "Market": {
        "name": "Market",
        "cost": 5,
        "energy_cost": 1,
        "type": "action",
        "effect": "+1 Card, +1 Energy, +1 Buy, +1 Gold",
        "image": "market.png",
        "effects": [draw(1), gain_energy(1), gain_buys(1), gain_gold(1)],
    },
    "Summon": {
        "name": "Summon Minion",
        "cost": 3,
        "energy_cost": 2,
        "type": "action",
        "effect": "summons a minion",
        "image": "witch.png",
        "effects": [summon("Goblin")],
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
    "Summon": 10,
}


_CLIENT_FIELDS = {"name", "cost", "energy_cost", "type", "effect", "image"}


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
        market[name] = {"count": count}
    return market
