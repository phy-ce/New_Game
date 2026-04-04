import random

PHILOSOPHER_STONE = "R00001"
SCHOLARS_TOME = "R00002"
PLAGUE_IDOL = "R00003"
WAR_BANNER = "R00004"
VITALITY_SHARD = "R00005"
ARCANE_CODEX = "R00006"

RELIC_TEMPLATES = {
    "R00001": {
        "name": "Philosopher's Stone",
        "cost": 11,
        "description": "Immediately convert all Copper in your deck, hand, and discard into Gold.",
        "effect_type": "immediate",
    },
    "R00002": {
        "name": "Scholar's Tome",
        "cost": 10,
        "description": "Draw 2 extra cards each turn.",
        "effect_type": "passive",
    },
    "R00003": {
        "name": "Plague Idol",
        "cost": 11,
        "description": "Each turn: deal 5 damage to the enemy player and each enemy unit.",
        "effect_type": "passive",
    },
    "R00004": {
        "name": "War Banner",
        "cost": 9,
        "description": "Immediately grant all your units +2 Attack and +2 HP.",
        "effect_type": "immediate",
    },
    "R00005": {
        "name": "Vitality Shard",
        "cost": 10,
        "description": "Each turn: gain 10 Max HP.",
        "effect_type": "passive",
    },
    "R00006": {
        "name": "Arcane Codex",
        "cost": 13,
        "description": "All cards cost 1 less Energy to play (minimum 0).",
        "effect_type": "passive",
    },
}

RELIC_POOL = list(RELIC_TEMPLATES.keys())


def create_relic_market():
    """Pick 3 random relics for this game."""
    selected = random.sample(RELIC_POOL, 3)
    return {rid: {"available": True} for rid in selected}


def get_client_relic_templates():
    return RELIC_TEMPLATES
