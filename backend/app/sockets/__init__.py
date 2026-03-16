def register_handlers(socketio):
    from app.sockets.lobby import register_lobby_handlers
    from app.sockets.game import register_game_handlers
    register_lobby_handlers(socketio)
    register_game_handlers(socketio)
