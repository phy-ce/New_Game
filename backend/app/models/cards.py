import random
import uuid
from app.services.effects import gain_gold, gain_energy, draw, do_damage, summon, damage_target, gain_block, gain_strength, champion_place, twist_blade, gain_passive, heal_owner

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
    "Block": {
        "name": "Block",
        "cost": 2,
        "energy_cost": 1,
        "type": "action",
        "effect": "Gain 3 Block",
        "image": "block.png",
        "effects": [gain_block(3)],
    },
    "Strike": {
        "name": "Strike",
        "cost": 1,
        "energy_cost": 1,
        "type": "action",
        "effect": "Deal 4 damage to target",
        "image": "strike.png",
        "needs_target": True,
        "effects": [damage_target(4)],
    },
    "Blabber": {
        "name": "Blabber",
        "cost": 3,
        "energy_cost": 0,
        "type": "action",
        "effect": "Deal 1 damage to target, +1 Card",
        "image": "strike.png",
        "needs_target": True,
        "effects": [damage_target(1), draw(1)],
    },
    "Work": {
        "name": "Work",
        "cost": 4,
        "energy_cost": 1,
        "type": "action",
        "effect": "+1 Card, +2 Gold",
        "image": "village.png",
        "effects": [draw(1), gain_gold(2)],
    },
    "Study": {
        "name": "Study",
        "cost": 5,
        "energy_cost": 1,
        "type": "action",
        "effect": "+3 Cards",
        "image": "smithy.png",
        "effects": [draw(3)],
    },
    "Twist Blade": {
        "name": "Twist Blade",
        "cost": 2,
        "energy_cost": 1,
        "type": "action",
        "effect": "Deal 3 damage. If opponent was damaged this turn, deal 10 instead.",
        "image": "strike.png",
        "effects": [twist_blade()],
    },
    "Fortify": {
        "name": "Fortify",
        "cost": 5,
        "energy_cost": 1,
        "type": "action",
        "effect": "+8 Block, +2 Cards",
        "image": "block.png",
        "effects": [gain_block(8), draw(2)],
    },
    "Recharge": {
        "name": "Recharge",
        "cost": 4,
        "energy_cost": 0,
        "type": "action",
        "effect": "+1 Card, +1 Energy",
        "image": "village.png",
        "effects": [draw(1), gain_energy(1)],
    },
    "Farm": {
        "name": "Farm",
        "cost": 3,
        "energy_cost": 2,
        "type": "action",
        "champion": True,
        "effect": "Champion 0/4. Each turn: +1 HP, +1 Gold.",
        "image": "village.png",
        "effects": [champion_place(hp=4, attack=0, effect=[heal_owner(1), gain_gold(1)])],
    },
    "Sleep": {
        "name": "Sleep",
        "cost": 3,
        "energy_cost": 1,
        "type": "action",
        "effect": "Next turn: +2 Energy.",
        "image": "village.png",
        "effects": [gain_passive("rest", 1)],
    },
    "Watchtower": {
        "name": "Watchtower",
        "cost": 5,
        "energy_cost": 2,
        "type": "action",
        "champion": True,
        "effect": "Champion 2/15.",
        "image": "village.png",
        "effects": [champion_place(hp=15, attack=2)],
    },
    "Wall": {
        "name": "Wall",
        "cost": 4,
        "energy_cost": 1,
        "type": "action",
        "champion": True,
        "effect": "Champion 0/8. Absorbs all damage dealt to you.",
        "image": "block.png",
        "effects": [champion_place(hp=8, attack=0, absorbs_damage=True)],
    },
    "Ritual": {
        "name": "Ritual",
        "cost": 7,
        "energy_cost": 3,
        "type": "action",
        "exhaust": True,
        "effect": "Gain Ritual passive: +1 Strength each turn. Exhaust.",
        "image": "village.png",
        "effects": [gain_passive("ritual", 1)],
    },
    "Train": {
        "name": "Train",
        "cost": 5,
        "energy_cost": 0,
        "type": "action",
        "effect": "+1 Strength",
        "image": "village.png",
        "effects": [gain_strength(1)],
    },
    "Doublestrike": {
        "name": "Doublestrike",
        "cost": 5,
        "energy_cost": 1,
        "type": "action",
        "effect": "Deal 4 damage twice to one target",
        "image": "strike.png",
        "needs_target": True,
        "effects": [damage_target(4), damage_target(4)],
    },
    "Bat": {
        "name": "Bat",
        "cost": 4,
        "energy_cost": 2,
        "type": "action",
        "effect": "Summon 2 Bats (2/3)",
        "image": "bat.png",
        "effects": [summon("Bat"), summon("Bat")],
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
    "Summon": 10,
    "Strike": 10,
    "Block": 10,
    "Recharge": 10,
    "Fortify": 10,
    "Twist Blade": 10,
    "Blabber": 10,
    "Work": 10,
    "Study": 10,
    "Bat": 10,
    "Doublestrike": 10,
    "Train": 10,
    "Ritual": 10,
    "Sleep": 10,
    "Watchtower": 10,
    "Wall": 10,
    "Farm": 10,
}


_CLIENT_FIELDS = {"name", "cost", "energy_cost", "type", "effect", "image", "needs_target", "exhaust"}


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
    for _ in range(6):
        deck.append(create_card("Copper"))
    for name in ["Strike", "Strike", "Block", "Block"]:
        deck.append(create_card(name))
    random.shuffle(deck)
    return deck


def create_market():
    """Create a market with 12 randomly selected cards from the full card pool."""
    selected = random.sample(list(CARD_TEMPLATES.keys()), 12)
    return {name: {"count": MARKET_SUPPLY.get(name, 10)} for name in selected}
