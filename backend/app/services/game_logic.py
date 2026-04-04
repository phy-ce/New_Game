import random
from app.models.cards import (
    CARD_TEMPLATES,
    COPPER, GOLD,
    RARE_POOL,
    create_starter_deck,
    create_market,
    create_rare_market,
    create_card,
)
from app.models.units import UNIT_TEMPLATES
from app.models.relics import RELIC_TEMPLATES, create_relic_market, SCHOLARS_TOME, PLAGUE_IDOL, WAR_BANNER, VITALITY_SHARD, ARCANE_CODEX, PHILOSOPHER_STONE
from app.services.effects import _apply_damage, apply_passives
HAND_SIZE = 5


def _draw_cards(player, count):
    for _ in range(count):
        if not player["deck"]:
            if not player["discard"]:
                break
            player["deck"] = player["discard"]
            player["discard"] = []
            random.shuffle(player["deck"])
        player["hand"].append(player["deck"].pop())


def _begin_phase(game, player_index):
    """Start of a player's turn: units attack, reset resources."""
    player = game["players"][player_index]
    opponent = game["players"][1 - player_index]

    for p in game["players"]:
        p["damaged_this_turn"] = False

    for unit in player["field"]:
        if unit.get("is_champion"):
            attack = unit.get("attack", 0)
            unit_effect = unit.get("effect")
        else:
            template = UNIT_TEMPLATES[unit["name"]]
            attack = template["attack"]
            unit_effect = template.get("effect")

        if attack > 0:
            hp_dmg, blocked, abs_name = _apply_damage(opponent, attack)
            log_msg = f"{unit['name']} attacks for {attack}"
            if abs_name:
                log_msg += f" [absorbed by {abs_name}]"
            elif blocked > 0:
                log_msg += f" [{blocked} blocked]"
            game["log"].append(log_msg)
        if unit_effect:
            fns = unit_effect if isinstance(unit_effect, list) else [unit_effect]
            for fn in fns:
                fn(game, player_index)

    player["energy"] = player["max_energy"]
    player["block"] = 0
    game["turn_state"] = {
        "cards_played": 0,
        "played_this_turn": [],
    }

    apply_passives(game, player_index)
    _apply_relic_passives_begin(game, player_index)


def _end_phase(game, player_index):
    """End of a player's turn: discard hand, draw next hand, clear gold."""
    player = game["players"][player_index]

    player["gold"] = 0
    player["discard"].extend(player["hand"])
    player["hand"] = []
    extra = sum(1 for r in player["relics"] if r["rid"] == SCHOLARS_TOME)
    _draw_cards(player, HAND_SIZE + extra * 2)


def start_game(game):
    """Initialize decks, market, draw starting hands, begin turn 1."""
    game["status"] = "playing"
    game["turn"] = 1
    game["current_player"] = 0
    game["market"] = create_market()
    game["market"]["relics"] = create_relic_market()
    game["market"]["rare"] = create_rare_market()
    game["trash"] = []
    game["pending_choice"] = None
    game["log"] = ["Game started!"]

    for i, player in enumerate(game["players"]):
        player["deck"] = create_starter_deck()
        player["hand"] = []
        player["discard"] = []
        player["energy"] = player["max_energy"]
        player["gold"] = 0
        _draw_cards(player, HAND_SIZE)

    _begin_phase(game, 0)
    game["log"].append(f"{game['players'][0]['name']}'s turn.")


def play_card(game, player_index, card_id, target=None):
    """Play a card from hand. Returns (success, error)."""
    if game["pending_choice"] is not None:
        return False, "Must resolve pending choice first"
    if game["current_player"] != player_index:
        return False, "Not your turn"

    player = game["players"][player_index]
    turn = game["turn_state"]

    # Find card in hand
    card = None
    for i, c in enumerate(player["hand"]):
        if c["id"] == card_id:
            card = player["hand"].pop(i)
            break
    if card is None:
        return False, "Card not in hand"

    discount = sum(1 for r in player["relics"] if r["rid"] == ARCANE_CODEX)
    energy_cost = max(0, CARD_TEMPLATES[card["cid"]]["energy_cost"] - discount)
    if player["energy"] < energy_cost:
        player["hand"].append(card)  # Put it back
        return False, "Not enough energy"
    player["energy"] -= energy_cost

    # Apply card effects
    game["_play_target"] = target
    game["_current_card"] = card
    _apply_card_effect(game, player_index, card)
    game.pop("_play_target", None)
    game.pop("_current_card", None)

    turn["cards_played"] += 1
    turn["played_this_turn"].insert(0, card)

    # Champions stay on field; exhausted cards disappear; everything else goes to discard
    template = CARD_TEMPLATES[card["cid"]]
    if not template.get("champion") and not template.get("exhaust"):
        player["discard"].append(card)

    game["log"].append(
        f"{player['name']} plays {card['name']} ({CARD_TEMPLATES[card['cid']]['effect']})"
    )
    return True, None


def _apply_card_effect(game, player_index, card):
    for fn in CARD_TEMPLATES[card["cid"]].get("effects", []):
        fn(game, player_index)


def buy_card(game, player_index, cid):
    """Buy a card from the market. Returns (success, error)."""
    if game["pending_choice"] is not None:
        return False, "Must resolve pending choice first"
    if game["current_player"] != player_index:
        return False, "Not your turn"

    player = game["players"][player_index]
    turn = game["turn_state"]

    if cid not in game["market"]:
        return False, "Card not in market"

    pile = game["market"][cid]
    if pile["count"] <= 0:
        return False, "Card is sold out"

    cost = CARD_TEMPLATES[cid]["cost"]
    if player["gold"] < cost:
        return False, f"Not enough gold (need {cost}, have {player['gold']})"

    player["gold"] -= cost
    pile["count"] -= 1

    new_card = create_card(cid)
    player["discard"].append(new_card)

    card_name = CARD_TEMPLATES[cid]["name"]
    game["log"].append(f"{player['name']} buys {card_name} (cost {cost})")
    return True, None


def buy_rare_card(game, player_index, slot):
    """Buy a rare card by slot index. Refills that slot with a new random rare card."""
    if game["pending_choice"] is not None:
        return False, "Must resolve pending choice first"
    if game["current_player"] != player_index:
        return False, "Not your turn"

    player = game["players"][player_index]
    rare_market = game["market"].get("rare", [])

    if slot < 0 or slot >= len(rare_market):
        return False, "Invalid slot"

    cid = rare_market[slot]["cid"]
    cost = CARD_TEMPLATES[cid]["cost"]
    if player["gold"] < cost:
        return False, f"Not enough gold (need {cost}, have {player['gold']})"

    player["gold"] -= cost
    player["discard"].append(create_card(cid))

    # Refill slot with a new random rare card
    rare_market[slot] = {"cid": random.choice(RARE_POOL)}

    game["log"].append(f"{player['name']} buys {CARD_TEMPLATES[cid]['name']} (rare, cost {cost})")
    return True, None


def buy_relic(game, player_index, rid):
    """Buy a relic from the market. Returns (success, error)."""
    if game["pending_choice"] is not None:
        return False, "Must resolve pending choice first"
    if game["current_player"] != player_index:
        return False, "Not your turn"

    player = game["players"][player_index]
    relics_market = game["market"].get("relics", {})

    if rid not in relics_market:
        return False, "Relic not in market"
    if not relics_market[rid]["available"]:
        return False, "Relic already sold"

    template = RELIC_TEMPLATES[rid]
    cost = template["cost"]
    if player["gold"] < cost:
        return False, f"Not enough gold (need {cost}, have {player['gold']})"

    player["gold"] -= cost
    relics_market[rid]["available"] = False
    player["relics"].append({"rid": rid, "name": template["name"]})

    _apply_relic_immediate(game, player_index, rid)

    game["log"].append(f"{player['name']} acquires {template['name']} (cost {cost})")
    return True, None


def _apply_relic_immediate(game, player_index, rid):
    """Apply immediate one-time relic effects on purchase."""
    player = game["players"][player_index]

    if rid == PHILOSOPHER_STONE:
        # Convert all Copper to Gold in deck, hand, discard
        converted = 0
        for zone in (player["deck"], player["hand"], player["discard"]):
            for card in zone:
                if card["cid"] == COPPER:
                    card["cid"] = GOLD
                    card["name"] = "Gold"
                    converted += 1
        game["log"].append(f"{player['name']}'s Philosopher's Stone converts {converted} Copper into Gold")

    elif rid == WAR_BANNER:
        buffed = 0
        for unit in player["field"]:
            unit["attack"] = unit.get("attack", 0) + 2
            unit["current_hp"] = unit.get("current_hp", 0) + 2
            buffed += 1
        game["log"].append(f"{player['name']}'s War Banner buffs {buffed} unit(s) +2/+2")


def _apply_relic_passives_begin(game, player_index):
    """Apply relic passive effects at the start of a player's turn."""
    player = game["players"][player_index]
    opponent = game["players"][1 - player_index]

    for relic in player["relics"]:
        rid = relic["rid"]

        if rid == PLAGUE_IDOL:
            # Deal 5 to opponent player
            from app.services.effects import _apply_damage
            hp_dmg, blocked, abs_name = _apply_damage(opponent, 5)
            msg = f"{player['name']}'s Plague Idol deals 5 damage to {opponent['name']}"
            if abs_name:
                msg += f" [absorbed by {abs_name}]"
            elif blocked > 0:
                msg += f" [{blocked} blocked]"
            game["log"].append(msg)
            # Deal 5 to each enemy unit
            for unit in list(opponent["field"]):
                unit["current_hp"] -= 5
                if unit["current_hp"] <= 0:
                    opponent["field"].remove(unit)
                    game["log"].append(f"Plague Idol destroys {unit['name']}!")
                    if unit.get("is_champion"):
                        opponent["discard"].append(unit["source_card"])
                else:
                    game["log"].append(f"Plague Idol deals 5 damage to {unit['name']}")

        elif rid == VITALITY_SHARD:
            player["max_hp"] += 10
            game["log"].append(f"{player['name']}'s Vitality Shard: +10 Max HP ({player['max_hp']} total)")


def resolve_choice(game, player_index, choice):
    """Resolve a pending choice. Returns (success, error).
    No cards use this in MVP, but the plumbing is here."""
    if game["pending_choice"] is None:
        return False, "No pending choice"
    if game["current_player"] != player_index:
        return False, "Not your turn"

    pending = game["pending_choice"]
    if choice not in pending["options"]:
        return False, "Invalid choice"

    # TODO: Apply the choice effect based on pending["type"] and pending["source_card"]
    game["log"].append(f"{game['players'][player_index]['name']} chose: {choice}")
    game["pending_choice"] = None
    return True, None


def end_turn(game, player_index):
    """End current player's turn and begin the next player's turn if game isn't over."""
    if game["pending_choice"] is not None:
        return False, "Must resolve pending choice first"
    if game["current_player"] != player_index:
        return False, "Not your turn"

    _end_phase(game, player_index)

    if check_game_over(game):
        return True, None

    game["current_player"] = 1 - player_index
    game["turn"] += 1

    _begin_phase(game, game["current_player"])
    game["log"].append(f"{game['players'][game['current_player']]['name']}'s turn.")
    return True, None


def check_game_over(game):
    """Check if any player's HP is at 0 or below. Returns winner index or None."""
    for i, p in enumerate(game["players"]):
        if p["hp"] <= 0:
            winner = 1 - i
            game["winner"] = winner
            game["status"] = "finished"
            game["log"].append(f"{game['players'][winner]['name']} wins!")
            return winner
    return None
