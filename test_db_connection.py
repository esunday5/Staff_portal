import os
from sqlalchemy import create_engine

db_url = os.getenv(
    'DATABASE_URL',
    'postgresql+pg8000://ekondo_db_928i_user:mZYdsPY2wTfgkaNbOnUgoWTPI72kdc5k@dpg-ctjc7ed2ng1s73bidflg-a.oregon-postgres.render.com/ekondo_db_928i'
)

try:
    # Create engine with pg8000
    engine = create_engine(db_url)
    with engine.connect() as connection:
        print("Connection successful!")
except Exception as e:
    print(f"Error: {e}")
