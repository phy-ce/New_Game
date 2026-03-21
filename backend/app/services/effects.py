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


def do_damage(amount):
    def effect(game, pi):
        game["players"][1 - pi]["hp"] -= amount

    return effect


def gain_buys(amount):
    def effect(game, pi):
        game["turn_state"]["buys"] += amount

    return effect


def summon(unit_type):
    def effect(game, pi):
        from app.models.units import create_unit
        game["players"][pi]["field"].append(create_unit(unit_type, pi))

    return effect
