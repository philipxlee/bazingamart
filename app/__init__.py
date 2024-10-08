from flask import Flask
from flask_login import LoginManager
from .config import Config
from .db import DB
from .index import bp as index_bp
from .users import bp as user_bp
from .carts import bp as carts_bp

login = LoginManager()
login.login_view = 'users.login'


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    app.db = DB(app)
    login.init_app(app)

    app.register_blueprint(index_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(carts_bp)

    return app
