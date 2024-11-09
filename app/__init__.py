from flask import Flask
from flask_login import LoginManager
from .config import Config
from .db import DB

login = LoginManager()
login.login_view = 'users.login'


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    app.db = DB(app)
    login.init_app(app)

    # Imports must happen after app is created to avoid circular imports
    from .index import bp as index_bp
    from .users import bp as user_bp
    from .carts import bp as carts_bp
    from .inventory import bp as inventory_bp
    from .products import bp as products_bp
    from .reviews import bp as reviews_bp
    from .purchases import bp as purchases_bp
    from .orders import bp as orders_bp
    
    app.register_blueprint(products_bp)
    app.register_blueprint(reviews_bp)
    app.register_blueprint(index_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(carts_bp)
    app.register_blueprint(inventory_bp)
    app.register_blueprint(purchases_bp)
    app.register_blueprint(orders_bp)

    return app
