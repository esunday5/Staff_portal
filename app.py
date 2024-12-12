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
from flask_dotenv import DotEnv
from flasgger import Swagger
from dotenv import load_dotenv
from config import Config  # Import Config class from config.py
from extensions import db, migrate, csrf  # Import db, migrate, csrf from extensions.py
from routes import main_blueprint as main_bp, auth_blueprint as auth_bp
from datetime import datetime
import redis  # Import redis for rate limiting storage
from waitress import serve  # Import waitress for production-ready server


app = Flask(__name__)


# Initialize logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Redis client configuration
redis_client = redis.StrictRedis.from_url("redis://localhost:6379/0", decode_responses=True)

# Flask-Limiter with Redis storage
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="redis://localhost:6379/0"
)

def create_app():
    """Application Factory Pattern for creating the Flask application."""
    app = Flask(__name__) 
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://Super_Admin:Emmanate1$$@localhost/ekondo_db' 

    # Initialize extensions with the app
    db.init_app(app) 
    migrate.init_app(app, db) 

    # Load configuration from Config class
    app.config.from_object('config.Config')

    # Load environment variables from .env
    DotEnv(app)
    load_dotenv()

    # Enable CORS
    CORS(app)

    # Add security headers with Talisman
    Talisman(app)

    # Initialize Swagger for API documentation
    Swagger(app)

    # Initialize Limiter with Redis storage
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

    @app.route('/')
    def hello_world():
        return 'Hello, World!'

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

# Load environment variables
load_dotenv()

if __name__ == "__main__":
    app = create_app()

    # SSL Configuration for HTTPS
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(
        certfile='C:/Users/IT/PycharmProjects/ekondo_expense_mgt/ssl/cert.pem',
        keyfile='C:/Users/IT/PycharmProjects/ekondo_expense_mgt/ssl/key.pem'
    )

    # Run the app with HTTPS
    app.run(host='0.0.0.0', port=5000, ssl_context=context)