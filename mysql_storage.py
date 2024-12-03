from datetime import datetime
from flask_limiter.util import get_remote_address
from extensions import db

class MySQLStorage:
    def __init__(self, uri=None):
        self.uri = uri

    def init_app(self, app):
        app.config["SQLALCHEMY_DATABASE_URI"] = self.uri
        db.init_app(app)

    def incr(self, key, amount=1, expire=None):
        expire_time = int(datetime.utcnow().timestamp()) + expire
        # Insert or update rate limit in the database
        db.session.execute(
            "INSERT INTO rate_limit (key, value, expiry) VALUES (%s, %s, %s) "
            "ON DUPLICATE KEY UPDATE value = value + %s, expiry = %s",
            (key, amount, expire_time, amount, expire_time)
        )
        db.session.commit()

    def get(self, key):
        # Fetch rate limit data from the database
        result = db.session.execute(
            "SELECT value, expiry FROM rate_limit WHERE key = %s", (key,)
        ).fetchone()
        return result

    def remove(self, key):
        # Remove the rate limit data from the database
        db.session.execute("DELETE FROM rate_limit WHERE key = %s", (key,))
        db.session.commit()
