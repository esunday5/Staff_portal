import os
import logging
import ssl
from flask import Flask, request, jsonify
from flask_login import LoginManager
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_talisman import Talisman
from flasgger import Swagger
from dotenv import load_dotenv
from config import Config
from extensions import db, migrate, csrf
from routes import main_blueprint as main_bp, auth_blueprint as auth_bp
from datetime import datetime
import redis
from waitress import serve
from markupsafe import Markup  # Fix for Flask Markup issue
from sqlalchemy.sql import text  # Import text for SQLAlchemy

# Initialize logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize app
app = Flask(__name__)

# Load environment variables
load_dotenv()

# Redis URL from environment
redis_url = os.getenv("REDIS_URL")

# Redis client configuration
if redis_url:
    try:
        redis_client = redis.StrictRedis.from_url(redis_url, decode_responses=True)
        redis_client.ping()  # Test Redis connection
    except redis.ConnectionError as e:
        app.logger.error(f"Redis connection failed: {e}")
        redis_client = None
else:
    redis_client = None

# Flask-Limiter with Redis storage if available
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

# Use Redis for rate limiting in production, fallback to in-memory if Redis isn't available
if redis_client:
    limiter.init_app(app, storage=redis_client)
else:
    limiter.init_app(app)  # Fallback to in-memory rate limiting

def create_app():
    """Application Factory Pattern for creating the Flask application."""
    app = Flask(__name__)

    # Load configuration from Config class
    app.config.from_object(Config)

    # Initialize extensions with the app
    db.init_app(app)
    migrate.init_app(app, db)

    # Enable CORS
    CORS(app)

    # Add security headers with Talisman
    Talisman(app)

    # Initialize Swagger for API documentation
    Swagger(app)

    # Initialize Limiter
    limiter.init_app(app)

    # Set up Flask-Login
    login_manager = LoginManager(app)
    login_manager.login_view = 'main.login'

    # Register blueprints for routes
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)

    # Register error handlers
    register_error_handlers(app)

    # Root route (home page)
    @app.route('/')
    def home():
        """Home Route."""
        return jsonify({"message": "Welcome to the Ekondo Expense Management System!"})

    # Health check route
    @app.route('/health', methods=['GET'])
    def health_check():
        """Health Check Endpoint."""
        return {"status": "healthy"}, 200

    # Example API route
    @app.route('/api/data', methods=['GET'])
    def get_data():
        """Example API route to send data to the frontend."""
        return jsonify({"message": "Hello from Flask!"})

    # Sample route to demonstrate rate limiting
    @app.route("/some-endpoint")
    @limiter.limit("5 per minute")  # Rate limit: 5 requests per minute
    def some_endpoint():
        return "This is a rate-limited endpoint."

    # Create the database tables if they don't exist
    with app.app_context():
        try:
            from models import (
                User, Role, Department, Expense, CashAdvance, OpexCapexRetirement,
                PettyCashAdvance, PettyCashRetirement, StationaryRequest, AuditLog,
                DocumentUploads, Notification, Transaction, RequestHistory,
                NotificationSettings, FileMetadata, ExpenseApprovalWorkflow
            )
            db.create_all()
            db.session.execute(text('SELECT 1'))  # Test database connection
            app.logger.info("Database connection successful and tables created.")
        except Exception as e:
            app.logger.error(f"Error creating database tables: {e}")

    return app

def register_error_handlers(app):
    """Register error handlers for common HTTP errors."""
    @app.errorhandler(404)
    def page_not_found(e):
        app.logger.warning(f"Page not found: {request.path}")
        return {"error": "Page not found"}, 404

    @app.errorhandler(500)
    def internal_error(e):
        app.logger.error(f"Internal error: {e}")
        return {"error": "Internal server error"}, 500

    @app.errorhandler(Exception)
    def handle_exception(e):
        app.logger.error(f"Unexpected error: {e}")
        return {"error": "Something went wrong. Please try again later."}, 500

if __name__ == "__main__":
    app = create_app()

    if os.getenv('FLASK_ENV') == 'development':  # Only use SSL locally in development
        app.run(host='0.0.0.0', port=5000)  # No SSL in development
    else:
        # For production use, handle SSL separately (e.g., via a reverse proxy like Nginx)
        cert_path = r'C:\path\to\cert.pem'
        key_path = r'C:\path\to\key.pem'

        if not os.path.exists(cert_path) or not os.path.exists(key_path):
            app.logger.error("SSL certificate or key file not found. Ensure paths are correct.")
            exit(1)

        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.load_cert_chain(certfile=cert_path, keyfile=key_path)
        app.run(ssl_context=context, host='0.0.0.0', port=5000)
