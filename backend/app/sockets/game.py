from flask import request
from flask_socketio import emit
from app.services import game_manager
from app.services.game_logic import (
    start_game, play_card, buy_card, buy_rare_card, buy_relic, resolve_choice, end_turn, check_game_over
)
from app.services.serializer import serialize_for_player


def broadcast_state(socketio, game):
    """Send filtered game state to each player individually.
    Also sends a room-level notification as a fallback in case
    a player's SID went stale (e.g. transport upgrade)."""
    code = game["lobby_code"]
    for i, player in enumerate(game["players"]):
        socketio.emit('game_state', serialize_for_player(game, i), to=player["sid"])
    # Fallback: notify the room so any player with a stale SID can re-request state
    socketio.emit('state_updated', {"lobby_code": code}, to=code)


def register_game_handlers(socketio):

    @socketio.on('start_game')
    def handle_start(data):
        code = data.get("lobby_code", "").strip().upper()
        game = game_manager.get_game(code)
        if not game:
            emit('error', {"message": "Game not found"})
            return
        if len(game["players"]) < 2:
            emit('error', {"message": "Need 2 players to start"})
            return
        if game["status"] != "waiting":
            emit('error', {"message": "Game already started"})
            return
        start_game(game)
        broadcast_state(socketio, game)

    @socketio.on('play_card')
    def handle_play(data):
        code = data.get("lobby_code", "").strip().upper()
        card_id = data.get("card_id")
        target = data.get("target")
        game = game_manager.get_game(code)
        if not game:
            emit('error', {"message": "Game not found"})
            return
        player_idx = game_manager.find_player_index(game, request.sid)
        if player_idx is None:
            emit('error', {"message": "Player not found"})
            return
        success, error = play_card(game, player_idx, card_id, target)
        if not success:
            emit('error', {"message": error})
            return
        check_game_over(game)
        broadcast_state(socketio, game)

    @socketio.on('buy_card')
    def handle_buy(data):
        code = data.get("lobby_code", "").strip().upper()
        cid = data.get("cid")
        game = game_manager.get_game(code)
        if not game:
            emit('error', {"message": "Game not found"})
            return
        player_idx = game_manager.find_player_index(game, request.sid)
        if player_idx is None:
            emit('error', {"message": "Player not found"})
            return
        success, error = buy_card(game, player_idx, cid)
        if not success:
            emit('error', {"message": error})
            return
        broadcast_state(socketio, game)

    @socketio.on('buy_rare_card')
    def handle_buy_rare(data):
        code = data.get("lobby_code", "").strip().upper()
        slot = data.get("slot")
        game = game_manager.get_game(code)
        if not game:
            emit('error', {"message": "Game not found"})
            return
        player_idx = game_manager.find_player_index(game, request.sid)
        if player_idx is None:
            emit('error', {"message": "Player not found"})
            return
        success, error = buy_rare_card(game, player_idx, slot)
        if not success:
            emit('error', {"message": error})
            return
        broadcast_state(socketio, game)

    @socketio.on('buy_relic')
    def handle_buy_relic(data):
        code = data.get("lobby_code", "").strip().upper()
        rid = data.get("rid")
        game = game_manager.get_game(code)
        if not game:
            emit('error', {"message": "Game not found"})
            return
        player_idx = game_manager.find_player_index(game, request.sid)
        if player_idx is None:
            emit('error', {"message": "Player not found"})
            return
        success, error = buy_relic(game, player_idx, rid)
        if not success:
            emit('error', {"message": error})
            return
        check_game_over(game)
        broadcast_state(socketio, game)

    @socketio.on('resolve_choice')
    def handle_resolve(data):
        code = data.get("lobby_code", "").strip().upper()
        choice = data.get("choice")
        game = game_manager.get_game(code)
        if not game:
            emit('error', {"message": "Game not found"})
            return
        player_idx = game_manager.find_player_index(game, request.sid)
        if player_idx is None:
            emit('error', {"message": "Player not found"})
            return
        success, error = resolve_choice(game, player_idx, choice)
        if not success:
            emit('error', {"message": error})
            return
        check_game_over(game)
        broadcast_state(socketio, game)

    @socketio.on('end_turn')
    def handle_end_turn(data):
        code = data.get("lobby_code", "").strip().upper()
        game = game_manager.get_game(code)
        if not game:
            emit('error', {"message": "Game not found"})
            return
        player_idx = game_manager.find_player_index(game, request.sid)
        if player_idx is None:
            emit('error', {"message": "Player not found"})
            return
        success, error = end_turn(game, player_idx)
        if not success:
            emit('error', {"message": error})
            return
        broadcast_state(socketio, game)
