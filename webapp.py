from webapp import app
from waitress import serve

if __name__ == '__main__':
    # Start the Flask app with waitress
    serve(app, host="0.0.0.0", port=5000)