import random
import uuid
from app.services.effects import gain_gold, gain_energy, draw, do_damage, summon, damage_target, gain_block, gain_strength, champion_place, twist_blade, gain_passive, heal_owner, body_slam, damage_all_enemies, destroy_target

# Card ID constants
STRIKE = "C00001"
BLOCK = "C00002"
COPPER = "C00003"
SILVER = "C00004"
GOLD = "C00005"
TWIST_BLADE = "C00006"
HEAVY_STRIKE = "C00007"
BODY_SLAM = "C00008"
STUDY = "C00009"
WORK = "C00010"
FORTIFY = "C00011"
RECHARGE = "C00012"
SLEEP = "C00013"
BLABBER = "C00014"
BAT = "C00015"
DOUBLESTRIKE = "C00016"
TRAIN = "C00017"
RITUAL = "C00018"
WALL = "C00019"
FARM = "C00020"
WATCHTOWER = "C00021"

# Rare card ID constants
DRAGON_CLAW    = "C00022"
PHOENIX_FEATHER = "C00023"
SHADOW_STEP    = "C00024"
THUNDER_STRIKE = "C00025"
IRON_WILL      = "C00026"
VOID_TEAR      = "C00028"
GLACIAL_SHARD  = "C00029"
SOUL_DRAIN     = "C00030"
ARCANE_SURGE   = "C00031"

CARD_TEMPLATES = {
    "C00001": {
        "name": "Strike",
        "cost": 0,
        "energy_cost": 1,
        "type": "action",
        "rarity": "common",
        "effect": "Deal 4 damage",
        "image": "strike.png",
        "needs_target": True,
        "effects": [damage_target(4)],
    },
    "C00002": {
        "name": "Block",
        "cost": 0,
        "energy_cost": 1,
        "type": "action",
        "rarity": "common",
        "effect": "+3 Block",
        "image": "block.png",
        "effects": [gain_block(3)],
    },
    "C00003": {
        "name": "Copper",
        "cost": 0,
        "energy_cost": 0,
        "type": "treasure",
        "rarity": "common",
        "effect": "+1 Gold",
        "image": "copper.png",
        "effects": [gain_gold(1)],
    },
    "C00004": {
        "name": "Silver",
        "cost": 3,
        "energy_cost": 0,
        "type": "treasure",
        "rarity": "common",
        "effect": "+2 Gold",
        "image": "silver.png",
        "effects": [gain_gold(2)],
    },
    "C00005": {
        "name": "Gold",
        "cost": 6,
        "energy_cost": 0,
        "type": "treasure",
        "rarity": "common",
        "effect": "+3 Gold",
        "image": "gold.png",
        "effects": [gain_gold(3)],
    },
    "C00006": {
        "name": "Twist Blade",
        "cost": 2,
        "energy_cost": 1,
        "type": "action",
        "rarity": "common",
        "effect": "Deal 3 damage. If target's HP was reduced this turn, deal 7 extra damage",
        "image": "strike.png",
        "needs_target": True,
        "effects": [twist_blade()],
    },
    "C00007": {
        "name": "Heavy Strike",
        "cost": 5,
        "energy_cost": 2,
        "type": "action",
        "rarity": "common",
        "effect": "Deal 12 damage",
        "image": "strike.png",
        "needs_target": True,
        "effects": [damage_target(12)],
    },
    "C00008": {
        "name": "Body Slam",
        "cost": 3,
        "energy_cost": 1,
        "type": "action",
        "rarity": "common",
        "effect": "Deal damage equal to your current Block",
        "image": "strike.png",
        "needs_target": True,
        "effects": [body_slam()],
    },
    "C00009": {
        "name": "Study",
        "cost": 5,
        "energy_cost": 1,
        "type": "action",
        "rarity": "common",
        "effect": "+3 Cards",
        "image": "smithy.png",
        "effects": [draw(3)],
    },
    "C00010": {
        "name": "Work",
        "cost": 4,
        "energy_cost": 1,
        "type": "action",
        "rarity": "common",
        "effect": "+1 Card, +2 Gold",
        "image": "village.png",
        "effects": [draw(1), gain_gold(2)],
    },
    "C00011": {
        "name": "Fortify",
        "cost": 5,
        "energy_cost": 1,
        "type": "action",
        "rarity": "common",
        "effect": "+8 Block, +2 Cards",
        "image": "block.png",
        "effects": [gain_block(8), draw(2)],
    },
    "C00012": {
        "name": "Recharge",
        "cost": 4,
        "energy_cost": 0,
        "type": "action",
        "rarity": "common",
        "effect": "+1 Energy, +1 Card",
        "image": "village.png",
        "effects": [draw(1), gain_energy(1)],
    },
    "C00013": {
        "name": "Sleep",
        "cost": 3,
        "energy_cost": 1,
        "type": "action",
        "rarity": "common",
        "effect": "Next turn: +2 Energy",
        "image": "village.png",
        "effects": [gain_passive("rest", 1)],
    },
    "C00014": {
        "name": "Blabber",
        "cost": 3,
        "energy_cost": 0,
        "type": "action",
        "rarity": "common",
        "effect": "Deal 1 damage, +1 Card",
        "image": "strike.png",
        "needs_target": True,
        "effects": [damage_target(1), draw(1)],
    },
    "C00015": {
        "name": "Bat",
        "cost": 4,
        "energy_cost": 2,
        "type": "action",
        "rarity": "common",
        "effect": "Summon 2 Bats (2/3)",
        "image": "bat.png",
        "effects": [summon("Bat"), summon("Bat")],
    },
    "C00016": {
        "name": "Doublestrike",
        "cost": 5,
        "energy_cost": 1,
        "type": "action",
        "rarity": "common",
        "effect": "Deal 2 damage twice",
        "image": "strike.png",
        "needs_target": True,
        "effects": [damage_target(2), damage_target(2)],
    },
    "C00017": {
        "name": "Train",
        "cost": 5,
        "energy_cost": 0,
        "type": "action",
        "rarity": "common",
        "effect": "+1 Strength",
        "image": "village.png",
        "effects": [gain_strength(1)],
    },
    "C00018": {
        "name": "Ritual",
        "cost": 7,
        "energy_cost": 3,
        "type": "action",
        "rarity": "common",
        "exhaust": True,
        "effect": "+1 Ritual (Exhaust)",
        "image": "village.png",
        "effects": [gain_passive("ritual", 1)],
    },
    "C00019": {
        "name": "Wall",
        "cost": 4,
        "energy_cost": 1,
        "type": "action",
        "rarity": "common",
        "champion": True,
        "effect": "Champion 0/8. Absorbs damage dealt to other targets",
        "image": "block.png",
        "effects": [champion_place(hp=8, attack=0, absorbs_damage=True)],
    },
    "C00020": {
        "name": "Farm",
        "cost": 3,
        "energy_cost": 2,
        "type": "action",
        "rarity": "common",
        "champion": True,
        "effect": "Champion 0/5. Each turn: +1 Gold, +1 HP",
        "image": "village.png",
        "effects": [champion_place(hp=5, attack=0, effect=[heal_owner(1), gain_gold(1)])],
    },
    "C00021": {
        "name": "Watchtower",
        "cost": 5,
        "energy_cost": 2,
        "type": "action",
        "rarity": "common",
        "champion": True,
        "effect": "Champion 0/15. Each turn: deal 2 damage to opponent",
        "image": "village.png",
        "effects": [champion_place(hp=15, attack=2)],
    },

    # --- Rare cards ---
    "C00022": {
        "name": "Dragon Claw",
        "cost": 5,
        "energy_cost": 1,
        "type": "action",
        "rarity": "rare",
        "effect": "Deal 8 damage. Gain +2 Strength.",
        "image": "strike.png",
        "needs_target": True,
        "effects": [damage_target(8), gain_strength(2)],
    },
    "C00023": {
        "name": "Phoenix Feather",
        "cost": 6,
        "energy_cost": 0,
        "type": "action",
        "rarity": "rare",
        "effect": "Heal 25 HP.",
        "image": "village.png",
        "effects": [heal_owner(25)],
    },
    "C00024": {
        "name": "Shadow Step",
        "cost": 4,
        "energy_cost": 1,
        "type": "action",
        "rarity": "rare",
        "effect": "+10 Block, draw 3 cards.",
        "image": "block.png",
        "effects": [gain_block(10), draw(3)],
    },
    "C00025": {
        "name": "Thunder Strike",
        "cost": 7,
        "energy_cost": 2,
        "type": "action",
        "rarity": "rare",
        "effect": "Deal 6 damage to the enemy player and each enemy unit.",
        "image": "strike.png",
        "effects": [damage_all_enemies(6)],
    },
    "C00026": {
        "name": "Iron Will",
        "cost": 5,
        "energy_cost": 0,
        "type": "action",
        "rarity": "rare",
        "effect": "+15 Block, +1 Energy.",
        "image": "block.png",
        "effects": [gain_block(15), gain_energy(1)],
    },
    "C00028": {
        "name": "Void Tear",
        "cost": 4,
        "energy_cost": 2,
        "type": "action",
        "rarity": "rare",
        "effect": "Destroy target enemy unit. If targeting the player, deal 15 damage instead.",
        "image": "strike.png",
        "needs_target": True,
        "effects": [destroy_target()],
    },
    "C00029": {
        "name": "Glacial Shard",
        "cost": 7,
        "energy_cost": 1,
        "type": "action",
        "rarity": "rare",
        "effect": "Deal 10 damage. Next turn: +2 Energy.",
        "image": "strike.png",
        "needs_target": True,
        "effects": [damage_target(10), gain_passive("rest", 1)],
    },
    "C00030": {
        "name": "Soul Drain",
        "cost": 5,
        "energy_cost": 2,
        "type": "action",
        "rarity": "rare",
        "effect": "Deal 12 damage. Heal 8 HP.",
        "image": "strike.png",
        "needs_target": True,
        "effects": [damage_target(12), heal_owner(8)],
    },
    "C00031": {
        "name": "Arcane Surge",
        "cost": 6,
        "energy_cost": 0,
        "type": "action",
        "rarity": "rare",
        "effect": "+3 Energy, draw 2 cards.",
        "image": "village.png",
        "effects": [gain_energy(3), draw(2)],
    },
}

# Fixed market: always available
MARKET_FIXED = {
    SILVER: 20,
    GOLD: 15,
}

# General market pool: randomly selected each game
MARKET_POOL = {
    TWIST_BLADE: 10,
    HEAVY_STRIKE: 10,
    BODY_SLAM: 10,
    STUDY: 10,
    WORK: 10,
    FORTIFY: 10,
    RECHARGE: 10,
    SLEEP: 10,
    BLABBER: 10,
    BAT: 10,
    DOUBLESTRIKE: 10,
    TRAIN: 10,
    RITUAL: 10,
    WALL: 10,
    FARM: 10,
    WATCHTOWER: 10,
}


_CLIENT_FIELDS = {"name", "cost", "energy_cost", "type", "rarity", "effect", "image", "needs_target", "exhaust"}


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
        deck.append(create_card(COPPER))
    for cid in [STRIKE, STRIKE, BLOCK, BLOCK]:
        deck.append(create_card(cid))
    random.shuffle(deck)
    return deck


RARE_POOL = [
    DRAGON_CLAW, PHOENIX_FEATHER, SHADOW_STEP, THUNDER_STRIKE, IRON_WILL,
    VOID_TEAR, GLACIAL_SHARD, SOUL_DRAIN, ARCANE_SURGE,
]


def create_market():
    """Create a market with fixed cards (Silver/Gold) + 8 randomly selected common cards."""
    market = {cid: {"count": count} for cid, count in MARKET_FIXED.items()}
    selected = random.sample(list(MARKET_POOL.keys()), 8)
    for cid in selected:
        market[cid] = {"count": MARKET_POOL[cid]}
    return market


def create_rare_market():
    """Create 6 rare card slots, each with a random rare card (with replacement allowed)."""
    return [{"cid": random.choice(RARE_POOL)} for _ in range(6)]
