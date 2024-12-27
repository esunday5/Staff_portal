import os
import msgspec
import logging
from flask import Flask, jsonify
from flask_login import LoginManager
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_talisman import Talisman
from flasgger import Swagger
from flask_swagger_ui import get_swaggerui_blueprint
from flask_migrate import Migrate
from flask_mail import Mail, Message 
from dotenv import load_dotenv
from extensions import db, migrate, csrf
from routes import main_blueprint, auth_blueprint
from redis import Redis
from limits.storage import RedisStorage
from extensions import init_session
from flask_seasurf import SeaSurf
import redis
from waitress import serve
from models import (
    User, Branch, Department, Role, Expense, CashAdvance, OpexCapexRetirement,
    PettyCashAdvance, PettyCashRetirement, StationaryRequest, Notification,
    DocumentUploads, Transaction, RequestHistory, NotificationSettings,
    FileMetadata, ExpenseApprovalWorkflow, AuditLog
)

# Initialize logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Load environment variables
load_dotenv()

# Redis connection initialization (no forced SSL replacement)
def create_redis_client(url, decode_responses=True):
    """
    Redis connection setup without SSL enforcement.
    """
    return Redis.from_url(url, decode_responses=decode_responses)

# Load Redis URL from environment variable
redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")  # Default to local Redis if not set

try:
    redis_client = create_redis_client(redis_url)
    redis_client.ping()
    logging.info("Redis connection successful.")
except Exception as e:
    logging.error(f"Redis connection failed: {e}")
    redis_client = None

# Ensure directories exist
def ensure_directory_exists(directory):
    if not os.path.exists(directory):
        try:
            os.makedirs(directory)
            logging.info(f"Directory '{directory}' created successfully.")
        except Exception as e:
            logging.error(f"Failed to create directory '{directory}': {e}")

# Rate limiter setup
limiter = Limiter(key_func=get_remote_address, storage_uri=redis_url)

def create_app():
    app = Flask(__name__)

    csrf = SeaSurf(app)

# App configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
    'DATABASE_URL',
    'postgresql+pg8000://ekondo_db_928i_user:mZYdsPY2wTfgkaNbOnUgoWTPI72kdc5k@dpg-ctjc7ed2ng1s73bidflg-a.oregon-postgres.render.com/ekondo_db_928i'
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'eKM_5eCur3t-K3y#2024!')


    # Ensure directories exist
    ensure_directory_exists("uploads/receipts")
    ensure_directory_exists("uploads/docs")

    # Initialize extensions
    db.init_app(app)
    init_session(app)
    migrate.init_app(app, db)
    csrf.init_app(app)
    CORS(app, resources={r"/*": {"origins": "*"}})
    limiter.init_app(app)

    # Initialize LoginManager
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login_user_api'  # Login view for unauthorized access

    # Define user_loader
    @login_manager.user_loader
    def load_user(user_id):
        """Load user by user_id."""
        return User.query.get(int(user_id))
    
         # User loader for Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))


    # Register blueprints
    app.register_blueprint(main_blueprint, url_prefix='/main')
    app.register_blueprint(auth_blueprint, url_prefix='/api/auth')

    # Swagger setup
    SWAGGER_URL = '/swagger'
    API_URL = '/static/swagger.json'
    swaggerui_blueprint = get_swaggerui_blueprint(
        SWAGGER_URL, API_URL, config={'app_name': "Ekondo EMS API"}
    )
    app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

    # Error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return jsonify({"error": "Resource not found"}), 404

    @app.errorhandler(500)
    def internal_error(error):
        logging.error(f"Internal server error: {error}")
        db.session.rollback()
        return jsonify({"error": "Internal server error"}), 500

    # Healthcheck Endpoint
    @app.route('/healthcheck')
    def healthcheck():
        """
        Healthcheck endpoint to test Redis and Database connectivity.
        """
        try:
            # Test database connection
            db.session.execute('SELECT 1')
            # Test Redis connection
            redis_client.ping()
            return {"status": "healthy"}, 200
        except Exception as e:
            return {"error": str(e)}, 500

    # Home route
    @app.route('/')
    def home():
        return jsonify({"message": "Welcome to the Ekondo Expense Management System!"})

    return app

# Expose the app globally for Gunicorn
app = create_app()

if __name__ == "__main__":
    app = create_app()
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=False)

