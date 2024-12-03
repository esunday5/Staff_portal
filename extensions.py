# extensions.py
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flasgger import Swagger
from flask_wtf.csrf import CSRFProtect

# Initialize extensions here
db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()
limiter = Limiter(key_func=get_remote_address)
swagger = Swagger()
csrf = CSRFProtect()

# Set up the login manager user loader (you can import your User model here if needed)
@login_manager.user_loader
def load_user(user_id):
    from models import User  # Import your user model here
    return User.query.get(int(user_id))
