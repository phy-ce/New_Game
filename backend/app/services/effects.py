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
    """Apply damage to a player, consuming block first."""
    if player.get("block", 0) > 0:
        absorbed = min(player["block"], amount)
        player["block"] -= absorbed
        amount -= absorbed
    if amount > 0:
        player["hp"] -= amount


def do_damage(amount):
    def effect(game, pi):
        _apply_damage(game["players"][1 - pi], amount)

    return effect


def gain_block(amount):
    def effect(game, pi):
        game["players"][pi]["block"] += amount

    return effect



def damage_target(amount):
    def effect(game, pi):
        target = game.get("_play_target")
        opp = game["players"][1 - pi]
        if not target or target == "opponent":
            _apply_damage(opp, amount)
        else:
            for unit in list(opp["field"]):
                if unit["id"] == target:
                    unit["current_hp"] -= amount
                    if unit["current_hp"] <= 0:
                        opp["field"].remove(unit)
                        game["log"].append(f"{unit['name']} is destroyed!")
                    break
    return effect


def summon(unit_type):
    def effect(game, pi):
        from app.models.units import create_unit
        game["players"][pi]["field"].append(create_unit(unit_type, pi))

    return effect
