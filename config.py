import os
import logging
from flask_sqlalchemy import SQLAlchemy

class Config:
    # Application settings
    SECRET_KEY = os.environ.get('SECRET_KEY', 'eKM_5eCur3t-K3y#2024!')  # Default secret key
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 
                                         'mysql+pymysql://Super_Admin:Emmanate1$$@localhost/ekondo_db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    CORS_HEADERS = 'Content-Type'
    UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')  # Store receipts here

    # Logging configuration
    LOGGING_LEVEL = os.environ.get('LOGGING_LEVEL', 'INFO').upper()
    LOGGING_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    LOGGING_LOCATION = os.environ.get('LOGGING_LOCATION', 'app.log')

    # Database settings
    DB_POOL_SIZE = 10  # Number of connections to keep open
    DB_POOL_TIMEOUT = 30  # Timeout in seconds to wait for a connection to become available

    # Feature flags
    ENABLE_NEW_FEATURE = os.environ.get('ENABLE_NEW_FEATURE', 'False').lower() == 'true'

    # Rate limiting
    RATELIMIT_DEFAULT = "200 per day; 50 per hour"  # Adjust based on application needs

    @staticmethod
    def init_app(app):
        pass

# Configure logging
logging.basicConfig(
    level=Config.LOGGING_LEVEL,
    format=Config.LOGGING_FORMAT,
    handlers=[logging.FileHandler(Config.LOGGING_LOCATION), logging.StreamHandler()]
)
