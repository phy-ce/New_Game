import uuid
from app.services.effects import gain_gold

UNIT_TEMPLATES = {
    "Bat": {
        "name": "Bat",
        "hp": 3,
        "attack": 3,
        "description": "A swift bat.",
        "image": "bat.png",
    },
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
    template = UNIT_TEMPLATES[unit_type]
    return {
        "id": str(uuid.uuid4())[:8],
        "name": unit_type,
        "current_hp": template["hp"],
        "attack": template.get("attack", 0),
        "owner": owner_index,
    }
