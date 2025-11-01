# WSGI entry point for PythonAnywhere
import sys
import os

# Add the project directory to the path
path = os.path.dirname(os.path.abspath(__file__))
if path not in sys.path:
    sys.path.insert(0, path)

# Import the Flask app
from app import app, socketio

# For PythonAnywhere, we need to expose the app
application = app

# Note: WebSocket support may be limited on PythonAnywhere free tier
# SocketIO polling fallback should work automatically

