import random
import uuid
from app.services.effects import gain_gold, gain_energy, draw, do_damage, summon, damage_target, gain_block, gain_strength, champion_place, twist_blade, gain_passive, heal_owner, body_slam

CARD_TEMPLATES = {
    "Strike": {
        "cid": "C00001",
        "name": "Strike",
        "cost": 0,
        "energy_cost": 1,
        "type": "action",
        "effect": "Deal 4 damage",
        "image": "strike.png",
        "needs_target": True,
        "effects": [damage_target(4)],
    },
    "Block": {
        "cid": "C00002",
        "name": "Block",
        "cost": 0,
        "energy_cost": 1,
        "type": "action",
        "effect": "+3 Block",
        "image": "block.png",
        "effects": [gain_block(3)],
    },
    "Copper": {
        "cid": "C00003",
        "name": "Copper",
        "cost": 0,
        "energy_cost": 0,
        "type": "treasure",
        "effect": "+1 Gold",
        "image": "copper.png",
        "effects": [gain_gold(1)],
    },
    "Silver": {
        "cid": "C00004",
        "name": "Silver",
        "cost": 3,
        "energy_cost": 0,
        "type": "treasure",
        "effect": "+2 Gold",
        "image": "silver.png",
        "effects": [gain_gold(2)],
    },
    "Gold": {
        "cid": "C00005",
        "name": "Gold",
        "cost": 6,
        "energy_cost": 0,
        "type": "treasure",
        "effect": "+3 Gold",
        "image": "gold.png",
        "effects": [gain_gold(3)],
    },
    "Twist Blade": {
        "cid": "C00006",
        "name": "Twist Blade",
        "cost": 2,
        "energy_cost": 1,
        "type": "action",
        "effect": "Deal 3 damage. If target's HP was reduced this turn, deal 7 extra damage",
        "image": "strike.png",
        "needs_target": True,
        "effects": [twist_blade()],
    },
    "Heavy Strike": {
        "cid": "C00007",
        "name": "Heavy Strike",
        "cost": 5,
        "energy_cost": 2,
        "type": "action",
        "effect": "Deal 12 damage",
        "image": "strike.png",
        "needs_target": True,
        "effects": [damage_target(12)],
    },
    "Body Slam": {
        "cid": "C00008",
        "name": "Body Slam",
        "cost": 3,
        "energy_cost": 1,
        "type": "action",
        "effect": "Deal damage equal to your current Block",
        "image": "strike.png",
        "needs_target": True,
        "effects": [body_slam()],
    },
    "Study": {
        "cid": "C00009",
        "name": "Study",
        "cost": 5,
        "energy_cost": 1,
        "type": "action",
        "effect": "+3 Cards",
        "image": "smithy.png",
        "effects": [draw(3)],
    },
    "Work": {
        "cid": "C00010",
        "name": "Work",
        "cost": 4,
        "energy_cost": 1,
        "type": "action",
        "effect": "+1 Card, +2 Gold",
        "image": "village.png",
        "effects": [draw(1), gain_gold(2)],
    },
    "Fortify": {
        "cid": "C00011",
        "name": "Fortify",
        "cost": 5,
        "energy_cost": 1,
        "type": "action",
        "effect": "+8 Block, +2 Cards",
        "image": "block.png",
        "effects": [gain_block(8), draw(2)],
    },
    "Recharge": {
        "cid": "C00012",
        "name": "Recharge",
        "cost": 4,
        "energy_cost": 0,
        "type": "action",
        "effect": "+1 Energy, +1 Card",
        "image": "village.png",
        "effects": [draw(1), gain_energy(1)],
    },
    "Sleep": {
        "cid": "C00013",
        "name": "Sleep",
        "cost": 3,
        "energy_cost": 1,
        "type": "action",
        "effect": "Next turn: +2 Energy",
        "image": "village.png",
        "effects": [gain_passive("rest", 1)],
    },
    "Blabber": {
        "cid": "C00014",
        "name": "Blabber",
        "cost": 3,
        "energy_cost": 0,
        "type": "action",
        "effect": "Deal 1 damage, +1 Card",
        "image": "strike.png",
        "needs_target": True,
        "effects": [damage_target(1), draw(1)],
    },
    "Bat": {
        "cid": "C00015",
        "name": "Bat",
        "cost": 4,
        "energy_cost": 2,
        "type": "action",
        "effect": "Summon 2 Bats (2/3)",
        "image": "bat.png",
        "effects": [summon("Bat"), summon("Bat")],
    },
    "Doublestrike": {
        "cid": "C00016",
        "name": "Doublestrike",
        "cost": 5,
        "energy_cost": 1,
        "type": "action",
        "effect": "Deal 2 damage twice",
        "image": "strike.png",
        "needs_target": True,
        "effects": [damage_target(2), damage_target(2)],
    },
    "Train": {
        "cid": "C00017",
        "name": "Train",
        "cost": 5,
        "energy_cost": 0,
        "type": "action",
        "effect": "+1 Strength",
        "image": "village.png",
        "effects": [gain_strength(1)],
    },
    "Ritual": {
        "cid": "C00018",
        "name": "Ritual",
        "cost": 7,
        "energy_cost": 3,
        "type": "action",
        "exhaust": True,
        "effect": "+1 Ritual (Exhaust)",
        "image": "village.png",
        "effects": [gain_passive("ritual", 1)],
    },
    "Wall": {
        "cid": "C00019",
        "name": "Wall",
        "cost": 4,
        "energy_cost": 1,
        "type": "action",
        "champion": True,
        "effect": "Champion 0/8. Absorbs damage dealt to other targets",
        "image": "block.png",
        "effects": [champion_place(hp=8, attack=0, absorbs_damage=True)],
    },
    "Farm": {
        "cid": "C00020",
        "name": "Farm",
        "cost": 3,
        "energy_cost": 2,
        "type": "action",
        "champion": True,
        "effect": "Champion 0/5. Each turn: +1 Gold, +1 HP",
        "image": "village.png",
        "effects": [champion_place(hp=5, attack=0, effect=[heal_owner(1), gain_gold(1)])],
    },
    "Watchtower": {
        "cid": "C00021",
        "name": "Watchtower",
        "cost": 5,
        "energy_cost": 2,
        "type": "action",
        "champion": True,
        "effect": "Champion 0/15. Each turn: deal 2 damage to opponent",
        "image": "village.png",
        "effects": [champion_place(hp=15, attack=2)],
    },
}

# Market supply: starter cards (Strike, Block, Copper) are not in the market
MARKET_SUPPLY = {
    "Silver": 20,
    "Gold": 15,
    "Twist Blade": 10,
    "Heavy Strike": 10,
    "Body Slam": 10,
    "Study": 10,
    "Work": 10,
    "Fortify": 10,
    "Recharge": 10,
    "Sleep": 10,
    "Blabber": 10,
    "Bat": 10,
    "Doublestrike": 10,
    "Train": 10,
    "Ritual": 10,
    "Wall": 10,
    "Farm": 10,
    "Watchtower": 10,
}


_CLIENT_FIELDS = {"name", "cost", "energy_cost", "type", "effect", "image", "needs_target", "exhaust", "cid"}


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
    """Create a starter deck: 6 Coppers + 2 Strikes + 2 Blocks."""
    deck = []
    for _ in range(6):
        deck.append(create_card("Copper"))
    for name in ["Strike", "Strike", "Block", "Block"]:
        deck.append(create_card(name))
    random.shuffle(deck)
    return deck


def create_market():
    """Create a market with 12 randomly selected cards from the full card pool."""
    selected = random.sample(list(MARKET_SUPPLY.keys()), 12)
    return {name: {"count": MARKET_SUPPLY.get(name, 10)} for name in selected}
