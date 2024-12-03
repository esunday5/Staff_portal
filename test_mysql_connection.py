import mysql.connector

try:
    conn = mysql.connector.connect(
        host='localhost',
        user='Super_Admin',
        password='Emmanate1$$',
        database='ekondo_db'
    )
    print("Connection successful")
except mysql.connector.Error as err:
    print(f"Error: {err}")
