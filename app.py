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

# Redis client configuration
try:
    redis_client = redis.StrictRedis.from_url(os.environ.get("REDIS_URL", "redis://localhost:6379/0"), decode_responses=True)
    redis_client.ping()
except redis.ConnectionError as e:
    app.logger.error(f"Redis connection failed: {e}")
    redis_client = None

# Flask-Limiter with Redis storage
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri=os.environ.get("REDIS_URL", "redis://localhost:6379/0") if redis_client else None
)

if not redis_client:
    app.logger.warning("Rate limiting is disabled due to Redis connection failure.")
    limiter.enabled = False

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

    # Deployment consideration for Render: SSL configuration handled by Render
    # Therefore, SSL configuration and manual certificate loading is not required for Render
    if os.environ.get("RENDER") != "True":
        cert_path = 'C:/Users/IT/PycharmProjects/ekondo_expense_mgt/ssl/cert.pem'
        key_path = 'C:/Users/IT/PycharmProjects/ekondo_expense_mgt/ssl/key.pem'

        if not os.path.exists(cert_path) or not os.path.exists(key_path):
            app.logger.error("SSL certificate or key file not found. Ensure paths are correct.")
            exit(1)

        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.load_cert_chain(certfile=cert_path, keyfile=key_path)

        # Run the app with Waitress for production
        serve(app, host='localhost', port=5000, url_scheme='https')
    else:
        # For Render deployment, Waitress and SSL are automatically handled by Render.
        # You can remove the SSL section above.
        app.run(host='0.0.0.0', port=5000)
