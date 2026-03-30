import random
import uuid
from app.services.effects import gain_gold, gain_energy, draw, do_damage, summon, damage_target, gain_block, gain_strength, champion_place, twist_blade, gain_passive, heal_owner, body_slam

CARD_TEMPLATES = {
    "C00001": {
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
    "C00002": {
        "cid": "C00002",
        "name": "Block",
        "cost": 0,
        "energy_cost": 1,
        "type": "action",
        "effect": "+3 Block",
        "image": "block.png",
        "effects": [gain_block(3)],
    },
    "C00003": {
        "cid": "C00003",
        "name": "Copper",
        "cost": 0,
        "energy_cost": 0,
        "type": "treasure",
        "effect": "+1 Gold",
        "image": "copper.png",
        "effects": [gain_gold(1)],
    },
    "C00004": {
        "cid": "C00004",
        "name": "Silver",
        "cost": 3,
        "energy_cost": 0,
        "type": "treasure",
        "effect": "+2 Gold",
        "image": "silver.png",
        "effects": [gain_gold(2)],
    },
    "C00005": {
        "cid": "C00005",
        "name": "Gold",
        "cost": 6,
        "energy_cost": 0,
        "type": "treasure",
        "effect": "+3 Gold",
        "image": "gold.png",
        "effects": [gain_gold(3)],
    },
    "C00006": {
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
    "C00007": {
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
    "C00008": {
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
    "C00009": {
        "cid": "C00009",
        "name": "Study",
        "cost": 5,
        "energy_cost": 1,
        "type": "action",
        "effect": "+3 Cards",
        "image": "smithy.png",
        "effects": [draw(3)],
    },
    "C00010": {
        "cid": "C00010",
        "name": "Work",
        "cost": 4,
        "energy_cost": 1,
        "type": "action",
        "effect": "+1 Card, +2 Gold",
        "image": "village.png",
        "effects": [draw(1), gain_gold(2)],
    },
    "C00011": {
        "cid": "C00011",
        "name": "Fortify",
        "cost": 5,
        "energy_cost": 1,
        "type": "action",
        "effect": "+8 Block, +2 Cards",
        "image": "block.png",
        "effects": [gain_block(8), draw(2)],
    },
    "C00012": {
        "cid": "C00012",
        "name": "Recharge",
        "cost": 4,
        "energy_cost": 0,
        "type": "action",
        "effect": "+1 Energy, +1 Card",
        "image": "village.png",
        "effects": [draw(1), gain_energy(1)],
    },
    "C00013": {
        "cid": "C00013",
        "name": "Sleep",
        "cost": 3,
        "energy_cost": 1,
        "type": "action",
        "effect": "Next turn: +2 Energy",
        "image": "village.png",
        "effects": [gain_passive("rest", 1)],
    },
    "C00014": {
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
    "C00015": {
        "cid": "C00015",
        "name": "Bat",
        "cost": 4,
        "energy_cost": 2,
        "type": "action",
        "effect": "Summon 2 Bats (2/3)",
        "image": "bat.png",
        "effects": [summon("Bat"), summon("Bat")],
    },
    "C00016": {
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
    "C00017": {
        "cid": "C00017",
        "name": "Train",
        "cost": 5,
        "energy_cost": 0,
        "type": "action",
        "effect": "+1 Strength",
        "image": "village.png",
        "effects": [gain_strength(1)],
    },
    "C00018": {
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
    "C00019": {
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
    "C00020": {
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
    "C00021": {
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

# Fixed market: always available
MARKET_FIXED = {
    "C00004": 20,   # Silver
    "C00005": 15,   # Gold
}

# General market pool: randomly selected each game
MARKET_POOL = {
    "C00006": 10,   # Twist Blade
    "C00007": 10,   # Heavy Strike
    "C00008": 10,   # Body Slam
    "C00009": 10,   # Study
    "C00010": 10,   # Work
    "C00011": 10,   # Fortify
    "C00012": 10,   # Recharge
    "C00013": 10,   # Sleep
    "C00014": 10,   # Blabber
    "C00015": 10,   # Bat
    "C00016": 10,   # Doublestrike
    "C00017": 10,   # Train
    "C00018": 10,   # Ritual
    "C00019": 10,   # Wall
    "C00020": 10,   # Farm
    "C00021": 10,   # Watchtower
}


_CLIENT_FIELDS = {"name", "cost", "energy_cost", "type", "effect", "image", "needs_target", "exhaust", "cid"}


def get_client_templates():
    """Return card templates with only the fields safe to send to the client."""
    return {
        cid: {k: v for k, v in template.items() if k in _CLIENT_FIELDS}
        for cid, template in CARD_TEMPLATES.items()
    }


def create_card(cid):
    """Create a card instance with cid and name."""
    return {
        "id": str(uuid.uuid4())[:8],
        "cid": cid,
        "name": CARD_TEMPLATES[cid]["name"],
    }


def create_starter_deck():
    """Create a starter deck: 6 Coppers + 2 Strikes + 2 Blocks."""
    deck = []
    for _ in range(6):
        deck.append(create_card("C00003"))  # Copper
    for cid in ["C00001", "C00001", "C00002", "C00002"]:  # Strike x2, Block x2
        deck.append(create_card(cid))
    random.shuffle(deck)
    return deck


def create_market():
    """Create a market with fixed cards (Silver/Gold) + 12 randomly selected cards."""
    market = {cid: {"count": count} for cid, count in MARKET_FIXED.items()}
    selected = random.sample(list(MARKET_POOL.keys()), 12)
    for cid in selected:
        market[cid] = {"count": MARKET_POOL[cid]}
    return market
