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
    from .orders import bp as orders_bp
    import base64

    @app.template_filter('b64encode')
    def b64encode_filter(value):
        """Base64 encode the image data."""
        if value:
            return base64.b64encode(value).decode('utf-8')
        return value
    
    app.register_blueprint(products_bp)
    app.register_blueprint(reviews_bp)
    app.register_blueprint(index_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(carts_bp)
    app.register_blueprint(inventory_bp)
    app.register_blueprint(orders_bp)

    return app
