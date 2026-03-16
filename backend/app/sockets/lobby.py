from flask import request
from flask_socketio import join_room, emit
from app.services import game_manager
from app.services.serializer import serialize_for_player


def register_lobby_handlers(socketio):

    @socketio.on('create_game')
    def handle_create(data):
        player_name = data.get("player_name", "").strip()
        if not player_name:
            emit('error', {"message": "Player name is required"})
            return
        code = game_manager.create_game(player_name, request.sid)
        join_room(code)
        emit('game_created', {"lobby_code": code})

    @socketio.on('join_game')
    def handle_join(data):
        code = data.get("lobby_code", "").strip().upper()
        player_name = data.get("player_name", "").strip()
        if not player_name:
            emit('error', {"message": "Player name is required"})
            return
        if not code:
            emit('error', {"message": "Lobby code is required"})
            return
        success, error = game_manager.join_game(code, player_name, request.sid)
        if not success:
            emit('error', {"message": error})
            return
        join_room(code)
        emit('game_joined', {"lobby_code": code})
        game = game_manager.get_game(code)
        emit('lobby_ready',
             {"players": [p["name"] for p in game["players"]]},
             room=code)

    @socketio.on('reconnect_game')
    def handle_reconnect(data):
        code = data.get("lobby_code", "").strip().upper()
        player_name = data.get("player_name", "").strip()
        if not code or not player_name:
            emit('error', {"message": "Lobby code and player name are required"})
            return
        player_idx, error = game_manager.reconnect(code, player_name, request.sid)
        if error:
            emit('error', {"message": error})
            return
        join_room(code)
        game = game_manager.get_game(code)
        # Only send full game state if the game has started (both players present)
        if game["status"] != "waiting":
            emit('game_state', serialize_for_player(game, player_idx))
        else:
            # Game is still in lobby, just re-send lobby info
            emit('game_joined', {"lobby_code": code})
            if len(game["players"]) == 2:
                emit('lobby_ready',
                     {"players": [p["name"] for p in game["players"]]},
                     room=code)
