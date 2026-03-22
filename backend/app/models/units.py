import uuid
from app.services.effects import gain_gold

UNIT_TEMPLATES = {
    "Goblin": {
        "name": "Goblin",
        "hp": 3,
        "attack": 0,
        "description": "Gains 1 gold for owner at end of turn.",
        "image": "goblin.png",
        "effect": gain_gold(1),
    },
}

_CLIENT_FIELDS = {"name", "hp", "attack", "description", "image"}


def get_client_templates():
    return {
        name: {k: v for k, v in template.items() if k in _CLIENT_FIELDS}
        for name, template in UNIT_TEMPLATES.items()
    }


def create_unit(unit_type, owner_index):
    return {
        "id": str(uuid.uuid4())[:8],
        "name": unit_type,
        "current_hp": UNIT_TEMPLATES[unit_type]["hp"],
        "owner": owner_index,
    }
