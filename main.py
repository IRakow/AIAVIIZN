"""
Main entry point for Google App Engine
"""
from app import app

# This allows Google App Engine to find and run the Flask app
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=False)