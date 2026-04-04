import random


def gain_gold(amount):
    def effect(game, pi):
        game["players"][pi]["gold"] += amount

    return effect


def gain_energy(amount):
    def effect(game, pi):
        game["players"][pi]["energy"] += amount

    return effect


def draw(amount):
    def effect(game, pi):
        player = game["players"][pi]
        for _ in range(amount):
            if not player["deck"]:
                if not player["discard"]:
                    break
                player["deck"] = player["discard"]
                player["discard"] = []
                random.shuffle(player["deck"])
            player["hand"].append(player["deck"].pop())

    return effect


def _apply_damage(player, amount):
    """Apply damage to a player, consuming block first. Redirects to absorbing champion if present.
    Returns (actual_hp_damage, blocked_amount, absorber_name or None)."""
    absorber_name = None
    for unit in list(player["field"]):
        if unit.get("absorbs_damage"):
            absorber_name = unit["name"]
            overflow = amount - unit["current_hp"]
            unit["current_hp"] -= amount
            if unit["current_hp"] <= 0:
                player["field"].remove(unit)
                if unit.get("is_champion"):
                    player["discard"].append(unit["source_card"])
            if overflow <= 0:
                return 0, 0, absorber_name
            amount = overflow
            break
    blocked = 0
    if player.get("block", 0) > 0:
        blocked = min(player["block"], amount)
        player["block"] -= blocked
        amount -= blocked
    if amount > 0:
        player["hp"] -= amount
        player["damaged_this_turn"] = True
    return amount, blocked, absorber_name


def _damage_log(base, strength, blocked=0, absorber=None):
    total = base + strength
    parts = f"{total} damage"
    if strength > 0:
        parts = f"{total} damage ({base}+{strength})"
    if absorber:
        parts += f" [absorbed by {absorber}]"
    elif blocked > 0:
        parts += f" [{blocked} blocked]"
    return parts


def do_damage(amount):
    def effect(game, pi):
        player = game["players"][pi]
        strength = player.get("strength", 0)
        total = amount + strength
        hp_dmg, blocked, absorber = _apply_damage(game["players"][1 - pi], total)
        game["log"].append(f"{player['name']} deals {_damage_log(amount, strength, blocked, absorber)}")

    return effect


def gain_strength(amount):
    def effect(game, pi):
        game["players"][pi]["strength"] += amount

    return effect


def gain_block(amount):
    def effect(game, pi):
        game["players"][pi]["block"] += amount

    return effect



def _damage_unit(game, player, unit, amount):
    """Apply damage to a unit, handling death and champion discard."""
    unit["current_hp"] -= amount
    if unit["current_hp"] <= 0:
        player["field"].remove(unit)
        game["log"].append(f"{unit['name']} is destroyed!")
        if unit.get("is_champion"):
            player["discard"].append(unit["source_card"])


def damage_target(amount):
    def effect(game, pi):
        target = game.get("_play_target")
        player = game["players"][pi]
        opp = game["players"][1 - pi]
        strength = player.get("strength", 0)
        total = amount + strength
        if not target or target == "opponent":
            hp_dmg, blocked, abs_name = _apply_damage(opp, total)
            game["log"].append(f"{player['name']} deals {_damage_log(amount, strength, blocked, abs_name)}")
        else:
            for unit in list(opp["field"]):
                if unit["id"] == target:
                    wall = next(
                        (u for u in opp["field"] if u.get("absorbs_damage") and u["id"] != unit["id"]),
                        None,
                    )
                    if wall:
                        _damage_unit(game, opp, wall, total)
                        game["log"].append(f"{player['name']} deals {_damage_log(amount, strength)} to {wall['name']}")
                    else:
                        _damage_unit(game, opp, unit, total)
                        game["log"].append(f"{player['name']} deals {_damage_log(amount, strength)} to {unit['name']}")
                    break
    return effect


def body_slam():
    def effect(game, pi):
        player = game["players"][pi]
        target = game.get("_play_target")
        opp = game["players"][1 - pi]
        amount = player.get("block", 0)
        if not target or target == "opponent":
            hp_dmg, blocked, abs_name = _apply_damage(opp, amount)
            log_dmg = f"{amount} damage"
            if abs_name:
                log_dmg += f" [absorbed by {abs_name}]"
            elif blocked > 0:
                log_dmg += f" [{blocked} blocked]"
            game["log"].append(f"{player['name']} deals {log_dmg} (Body Slam)")
        else:
            for unit in list(opp["field"]):
                if unit["id"] == target:
                    wall = next(
                        (u for u in opp["field"] if u.get("absorbs_damage") and u["id"] != unit["id"]),
                        None,
                    )
                    if wall:
                        _damage_unit(game, opp, wall, amount)
                        game["log"].append(f"{player['name']} deals {amount} damage to {wall['name']} (Body Slam)")
                    else:
                        _damage_unit(game, opp, unit, amount)
                        game["log"].append(f"{player['name']} deals {amount} damage to {unit['name']} (Body Slam)")
                    break
    return effect


def twist_blade():
    def effect(game, pi):
        player = game["players"][pi]
        opp = game["players"][1 - pi]
        amount = 10 if opp.get("damaged_this_turn") else 3
        strength = player.get("strength", 0)
        total = amount + strength
        hp_dmg, blocked, abs_name = _apply_damage(opp, total)
        game["log"].append(f"{player['name']}'s Twist Blade deals {_damage_log(amount, strength, blocked, abs_name)}")
    return effect


def champion_place(hp, attack, **flags):
    def effect(game, pi):
        card = game["_current_card"]
        unit = {
            "id": card["id"],
            "name": card["name"],
            "current_hp": hp,
            "attack": attack,
            "owner": pi,
            "is_champion": True,
            "source_card": card,
        }
        unit.update(flags)
        game["players"][pi]["field"].append(unit)
    return effect


def heal_owner(amount):
    def effect(game, pi):
        player = game["players"][pi]
        player["hp"] = min(player["hp"] + amount, player["max_hp"])
        game["log"].append(f"{player['name']} heals {amount} HP")
    return effect


def gain_passive(name, stacks=1):
    def effect(game, pi):
        for passive in game["players"][pi]["passives"]:
            if passive["name"] == name:
                passive["stacks"] += stacks
                return
        game["players"][pi]["passives"].append({"name": name, "stacks": stacks})
    return effect


# --- Passives ---

def _passive_ritual(game, pi, stacks):
    game["players"][pi]["strength"] += stacks
    game["log"].append(f"{game['players'][pi]['name']}'s Ritual triggers: +{stacks} Strength")


def _passive_rest(game, pi, stacks):
    player = game["players"][pi]
    player["energy"] += 2 * stacks
    game["log"].append(f"{player['name']}'s Rest triggers: +{2 * stacks} Energy")
    player["passives"] = [p for p in player["passives"] if p["name"] != "rest"]


_PASSIVE_REGISTRY = {
    "ritual": _passive_ritual,
    "rest": _passive_rest,
}

PASSIVE_INFO = {
    "ritual": {"name": "ritual", "description": "Each turn: +1 Strength per stack."},
    "rest": {"name": "rest", "description": "Next turn: +2 Energy per stack. Consumed after triggering."},
}

def get_passive_info():
    return PASSIVE_INFO


def apply_passives(game, pi):
    for passive in game["players"][pi].get("passives", []):
        handler = _PASSIVE_REGISTRY.get(passive["name"])
        if handler:
            handler(game, pi, passive["stacks"])


def summon(unit_type):
    def effect(game, pi):
        from app.models.units import create_unit
        game["players"][pi]["field"].append(create_unit(unit_type, pi))

    return effect


def damage_all_enemies(amount):
    """Deal damage to the opponent player and each of their units (bypasses absorber per unit)."""
    def effect(game, pi):
        player = game["players"][pi]
        opp = game["players"][1 - pi]
        strength = player.get("strength", 0)
        total = amount + strength
        # Hit opponent player (goes through block/absorber)
        hp_dmg, blocked, abs_name = _apply_damage(opp, total)
        game["log"].append(
            f"{player['name']}'s Thunder Strike deals {_damage_log(amount, strength, blocked, abs_name)} to {opp['name']}"
        )
        # Hit each enemy unit directly
        for unit in list(opp["field"]):
            _damage_unit(game, opp, unit, total)
            if unit in opp["field"]:
                game["log"].append(f"Thunder Strike deals {total} to {unit['name']}")
    return effect



def destroy_target():
    """Destroy target enemy unit outright, or deal 15 damage if targeting the player."""
    def effect(game, pi):
        target = game.get("_play_target")
        player = game["players"][pi]
        opp = game["players"][1 - pi]
        if not target or target == "opponent":
            strength = player.get("strength", 0)
            total = 15 + strength
            hp_dmg, blocked, abs_name = _apply_damage(opp, total)
            game["log"].append(
                f"{player['name']}'s Void Tear deals {_damage_log(15, strength, blocked, abs_name)}"
            )
        else:
            for unit in list(opp["field"]):
                if unit["id"] == target:
                    opp["field"].remove(unit)
                    game["log"].append(f"{player['name']}'s Void Tear destroys {unit['name']}!")
                    if unit.get("is_champion"):
                        opp["discard"].append(unit["source_card"])
                    break
    return effect
