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
    """Apply damage to a player, consuming block first. Redirects to absorbing champion if present."""
    for unit in list(player["field"]):
        if unit.get("absorbs_damage"):
            unit["current_hp"] -= amount
            if unit["current_hp"] <= 0:
                player["field"].remove(unit)
                if unit.get("is_champion"):
                    player["discard"].append(unit["source_card"])
            return
    if player.get("block", 0) > 0:
        absorbed = min(player["block"], amount)
        player["block"] -= absorbed
        amount -= absorbed
    if amount > 0:
        player["hp"] -= amount
        player["damaged_this_turn"] = True


def do_damage(amount):
    def effect(game, pi):
        total = amount + game["players"][pi].get("strength", 0)
        _apply_damage(game["players"][1 - pi], total)

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
        opp = game["players"][1 - pi]
        total = amount + game["players"][pi].get("strength", 0)
        if not target or target == "opponent":
            _apply_damage(opp, total)
        else:
            for unit in list(opp["field"]):
                if unit["id"] == target:
                    absorber = next(
                        (u for u in opp["field"] if u.get("absorbs_damage") and u["id"] != unit["id"]),
                        None,
                    )
                    if absorber:
                        _damage_unit(game, opp, absorber, total)
                    else:
                        _damage_unit(game, opp, unit, total)
                    break
    return effect


def twist_blade():
    def effect(game, pi):
        opp = game["players"][1 - pi]
        amount = 10 if opp.get("damaged_this_turn") else 3
        total = amount + game["players"][pi].get("strength", 0)
        _apply_damage(opp, total)
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
