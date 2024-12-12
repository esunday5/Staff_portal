from app import create_app

# Run the Flask application with SSL enabled
if __name__ == '__main__':
    app = create_app()
    app.run(host="0.0.0.0", port=5000, ssl_context=('path/to/cert.pem', 'path/to/key.pem'))
