from webapp import app

if __name__ == '__main__':
    # Start the Flask app in debug mode
    app.run(host="127.0.0.1", port=5000, debug=True)