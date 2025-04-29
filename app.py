import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect

# Configure logging
logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass

# Initialize extensions
db = SQLAlchemy(model_class=Base)
csrf = CSRFProtect()
login_manager = LoginManager()

# Create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "temp_dev_secret")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Configure the database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "postgresql://postgres:123456@localhost:5432/know_your_fan")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16MB max upload size

# Initialize extensions with app
db.init_app(app)
csrf.init_app(app)
login_manager.init_app(app)
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'info'

# Register blueprints
with app.app_context():
    # Import models to create tables
    from models import User, UserProfile, Document, SocialMedia, EsportsProfile
    
    # Import routes from routes directory
    from routes.auth import auth_bp
    from routes.profile import profile_bp
    from routes.social import social_bp
    from routes.dashboard import dashboard_bp
    
    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(social_bp)
    app.register_blueprint(dashboard_bp)
    
    # Register main route
    from routes import main_routes
    
    # Create database tables
    db.create_all()

# Import login manager user loader
@login_manager.user_loader
def load_user(user_id):
    from models import User
    return User.query.get(int(user_id))
