import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_login import LoginManager
import logging


"""
Use Flask-SQLAlchemy's default declarative base for broad compatibility
with SQLAlchemy 1.4 and 2.x. This avoids requiring DeclarativeBase, which
is only available in SQLAlchemy 2.x.
"""


# Set up logging
logging.basicConfig(level=logging.DEBUG)

# Initialize SQLAlchemy with the default model base
db = SQLAlchemy()

# Create the Flask application
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)  # needed for url_for to generate with https

# Configure the database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///car_rental.db")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize the database with the app
db.init_app(app)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

# Import routes after app is created to avoid circular imports
with app.app_context():
    # Import models for table creation
    from models import User, Car, CarModel, Rental
    
    # Create all tables in the database
    db.create_all()
    
    # Create admin user if it doesn't exist
    from werkzeug.security import generate_password_hash
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin = User(
            username='admin',
            email='admin@carrental.com',
            password_hash=generate_password_hash('admin123'),
            is_admin=True
        )
        db.session.add(admin)
        db.session.commit()
        logging.info("Admin user created")

    # Import and register routes
    import routes