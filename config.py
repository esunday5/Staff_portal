import os
import logging
from flask_sqlalchemy import SQLAlchemy

class Config:
    """Base configuration class for the application."""

    # Application settings
    SECRET_KEY = os.environ.get('SECRET_KEY', 'eKM_5eCur3t-K3y#2024!')
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        'mysql+pymysql://Super_Admin:Emmanate1$$@localhost/ekondo_db'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    CSRF_ENABLED = True
    CORS_HEADERS = 'Content-Type'
    UPLOAD_FOLDER = os.path.abspath(os.path.join(os.getcwd(), 'uploads'))

    # Logging configuration
    LOGGING_LEVEL = os.environ.get('LOGGING_LEVEL', 'INFO').split('#')[0].strip().upper()
    LOGGING_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    LOGGING_LOCATION = os.environ.get('LOGGING_LOCATION', 'app.log')

    # Database settings
    try:
        DB_POOL_SIZE = int(os.environ.get('DB_POOL_SIZE', '200').split('#')[0].strip())
    except ValueError:
        DB_POOL_SIZE = 200
        logging.warning("Invalid DB_POOL_SIZE value. Defaulting to 200.")

    try:
        DB_POOL_TIMEOUT = int(os.environ.get('DB_POOL_TIMEOUT', '120').split('#')[0].strip())
    except ValueError:
        DB_POOL_TIMEOUT = 120
        logging.warning("Invalid DB_POOL_TIMEOUT value. Defaulting to 120.")

    ENABLE_NEW_FEATURE = os.environ.get('ENABLE_NEW_FEATURE', 'False').lower() == 'true'
    RATELIMIT_DEFAULT = os.environ.get('RATELIMIT_DEFAULT', "2000 per day; 500 per hour")

    @staticmethod
    def init_app(app):
        os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
        app.logger.info("Upload folder initialized at: %s", Config.UPLOAD_FOLDER)


# Configure logging globally
logging.basicConfig(
    level=Config.LOGGING_LEVEL,
    format=Config.LOGGING_FORMAT,
    handlers=[
        logging.FileHandler(Config.LOGGING_LOCATION),
        logging.StreamHandler()
    ]
)


