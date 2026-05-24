from flask import Flask
from config import Config
from extensions import login_manager
from models import User
from db import close_db, init_db

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize Flask extensions
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.get(int(user_id))

    # Register blueprints
    from routes.main import main_bp
    from routes.auth import auth_bp
    from routes.analytics import analytics_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(analytics_bp)

    # Register teardown function to close database connections
    app.teardown_appcontext(close_db)

    # Create database tables
    with app.app_context():
        init_db()

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)
