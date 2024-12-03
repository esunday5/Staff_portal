from sqlalchemy import create_engine

# Replace with your database URL
DATABASE_URL = "mysql+pymysql://Super_Admin:Emmanate1$$@localhost/ekondo_db"

try:
    engine = create_engine(DATABASE_URL)
    connection = engine.connect()
    print("Connection successful")
except Exception as e:
    print(f"Error: {e}")
