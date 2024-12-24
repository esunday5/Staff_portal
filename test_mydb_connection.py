import pg8000

try:
    connection = pg8000.connect(
        host='dpg-ctjc7ed2ng1s73bidflg-a.oregon-postgres.render.com',
        user='ekondo_db_928i_user',
        password='mZYdsPY2wTfgkaNbOnUgoWTPI72kdc5k',
        database='ekondo_db_928i'
    )
    print("Connection successful")
    connection.close()
except Exception as e:
    print(f"Error: {e}")
