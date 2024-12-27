# extensions.py
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_login import LoginManager
from flask_migrate import Migrate 
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flasgger import Swagger
from flask_seasurf import SeaSurf
from flask_session import Session

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()
mail = Mail()
csrf = SeaSurf(app)

def init_app(app):
    db.init_app(app)
    migrate.init_app(app, db)
    limiter.init_app(app)
    mail.init_app(app)

def init_session(app):
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['SESSION_PERMANENT'] = False
    Session(app)

limiter = Limiter(
    key_func=get_remote_address,  # Use IP address for rate-limiting
    default_limits=["2000 per day", "500 per hour"]  # Default rate limits
)
swagger = Swagger()
csrf = CSRFProtect()

# Configure the login manager
login_manager.login_view = "auth.login"  # Redirect unauthenticated users to 'auth.login'
login_manager.login_message = "Please log in to access this page."
login_manager.login_message_category = "info"

# Set up the login manager user loader
@login_manager.user_loader
def load_user(user_id):
    from models import User  # Import the User model here
    try:
        return User.query.get(int(user_id))  # Load user by ID
    except Exception as e:
        db.session.rollback()
        return None
