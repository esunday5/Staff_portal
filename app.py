import os
import logging
import ssl
from flask import Flask, request, jsonify
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_talisman import Talisman
from flask_dotenv import DotEnv
from flasgger import Swagger
from dotenv import load_dotenv
from config import Config  # Import Config class from config.py
from extensions import db, csrf  # Import CSRF extension
from routes import main_blueprint as main_bp, auth_blueprint as auth_bp
from datetime import datetime
import redis  # Import redis for storage
from waitress import serve  # Import waitress

# Initialize logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize extensions
login_manager = LoginManager()
migrate = Migrate()
swagger = Swagger()

# Redis client configuration
redis_client = redis.StrictRedis.from_url("redis://localhost:6379/0", decode_responses=True)

# Initialize Flask-Limiter with Redis storage
limiter = Limiter(
    key_func=get_remote_address, 
    default_limits=["200 per day", "50 per hour"], 
    storage_uri="redis://localhost:6379/0"
)

def create_app():
    app = Flask(__name__)

    # Load configuration from Config class
    app.config.from_object(Config)

    # Load environment variables from .env file
    DotEnv(app)
    load_dotenv()  # Ensure .env file is loaded for environment variables

    # Enable CORS
    CORS(app)

    # Add security headers with Talisman
    Talisman(app)

    # Register Swagger for API documentation
    swagger.init_app(app)

    # Initialize Limiter with Redis storage
    limiter.init_app(app)

    # Initialize extensions with the app
    db.init_app(app)  # Use db from extensions.py
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = 'main.login'  # Adjust this if necessary
    csrf.init_app(app)  # CSRF protection

    # Register blueprints for routes
    app.register_blueprint(main_bp)  # Register the main blueprint
    app.register_blueprint(auth_bp)  # Register the auth blueprint

    # Register error handlers
    register_error_handlers(app)

    # Health check route
    @app.route('/health', methods=['GET'])
    def health_check():
        """Health Check Endpoint"""
        return {"status": "healthy"}, 200

    # API data route for frontend
    @app.route('/api/data', methods=['GET'])
    def get_data():
        """API route to send data to the frontend"""
        return jsonify({"message": "Hello from Flask!"})

    # Example route with rate limiting
    @app.route("/")
    @limiter.limit("5 per minute")  # Example: Rate limit of 5 requests per minute
    def index():
        return "Flask-Limiter is configured with Redis!"

    # Create the database tables if they don't exist
    with app.app_context():
        try:
            # Import models to create tables in the database
            from models import User, Role, Department, Expense, CashAdvance, OpexCapexRetirement, \
                PettyCashAdvance, PettyCashRetirement, StationaryRequest, AuditLog, DocumentUploads, \
                Notification, Transaction, RequestHistory, NotificationSettings, FileMetadata, \
                ExpenseApprovalWorkflow

            # Create all tables
            db.create_all()

        except Exception as e:
            app.logger.error(f"Error creating database tables: {e}")

    return app

def register_error_handlers(app):
    """Register error handlers for 404 and 500 errors"""
    @app.errorhandler(404)
    def page_not_found(e):
        app.logger.warning(f"Page not found: {request.path}")
        return {"error": "Page not found"}, 404

    @app.errorhandler(500)
    def internal_error(e):
        app.logger.error(f"Internal error: {e}")
        return {"error": "Internal server error"}, 500

# Load environment variables from .env file
load_dotenv()

if __name__ == "__main__":
    app = create_app()

    # SSL Configuration
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(certfile='C:/Users/IT/PycharmProjects/ekondo_expense_mgt/ssl/cert.pem',
                            keyfile='C:/Users/IT/PycharmProjects/ekondo_expense_mgt/ssl/key.pem')

    # Use Flask's built-in server for HTTPS
    app.run(host='0.0.0.0', port=5000, ssl_context=context)

