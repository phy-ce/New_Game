import os
from flask import Flask, send_from_directory
from flask_socketio import SocketIO

socketio = SocketIO()


def create_app():
    static_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../frontend/dist'))
    app = Flask(__name__, static_folder=static_dir, static_url_path='')
    app.config['SECRET_KEY'] = 'dev-secret-key'

    @app.route('/')
    def index():
        return send_from_directory(app.static_folder, 'index.html')

    # Catch-all: serve index.html for any route not matched by static files.
    # This lets the React SPA handle its own routing.
    @app.errorhandler(404)
    def not_found(e):
        return send_from_directory(app.static_folder, 'index.html')

    socketio.init_app(app, cors_allowed_origins="*")

    from app.sockets import register_handlers
    register_handlers(socketio)

    return app
