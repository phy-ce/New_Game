from flask import request
from flask_socketio import emit
from app.services import game_manager
from app.models.cards import CARD_TEMPLATES, create_card
from app.services.effects import _apply_damage
from app.sockets.game import broadcast_state


def register_debug_handlers(socketio):

    @socketio.on('debug_cmd')
    def handle_debug(data):
        code = data.get("lobby_code", "").strip().upper()
        cmd = data.get("cmd")
        game = game_manager.get_game(code)
        if not game:
            emit('error', {"message": "Game not found"})
            return
        player_idx = game_manager.find_player_index(game, request.sid)
        if player_idx is None:
            emit('error', {"message": "Player not found"})
            return
        player = game["players"][player_idx]

        if cmd == "add_card":
            cid = data.get("cid")
            if cid not in CARD_TEMPLATES:
                emit('error', {"message": f"Unknown cid: {cid}"})
                return
            player["hand"].append(create_card(cid))
            game["log"].append(f"[DEBUG] {player['name']} added {CARD_TEMPLATES[cid]['name']} to hand")

        elif cmd == "set_stat":
            stat = data.get("stat")
            value = data.get("value")
            allowed = {"hp", "max_hp", "energy", "max_energy", "gold", "block", "strength"}
            if stat not in allowed:
                emit('error', {"message": f"Unknown stat: {stat}"})
                return
            player[stat] = int(value)
            game["log"].append(f"[DEBUG] {player['name']} set {stat} to {value}")

        elif cmd == "deal_damage":
            amount = data.get("amount", 0)
            opponent = game["players"][1 - player_idx]
            _apply_damage(opponent, int(amount))
            game["log"].append(f"[DEBUG] dealt {amount} damage to {opponent['name']}")

        else:
            emit('error', {"message": f"Unknown debug command: {cmd}"})
            return

        broadcast_state(socketio, game)
