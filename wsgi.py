# WSGI entry point for PythonAnywhere
import sys
import os

# Add the project directory to the path
path = os.path.dirname(os.path.abspath(__file__))
if path not in sys.path:
    sys.path.insert(0, path)

# Change to project directory (important for file paths)
os.chdir(path)

# Import the Flask app and initialization functions
from app import app, socketio, init_db, load_raw_data

# Initialize database and load player data on first import
# (This happens when PythonAnywhere loads the WSGI file)
try:
    init_db()
    load_raw_data()
except Exception as e:
    # If database already exists or data already loaded, that's fine
    # Only log if it's a real error (not just "already exists")
    if 'already exists' not in str(e).lower() and 'locked' not in str(e).lower():
        import traceback
        print(f"Warning during initialization: {e}")
        traceback.print_exc()

# For PythonAnywhere, we need to expose the app
application = app

# Note: WebSocket support may be limited on PythonAnywhere free tier
# SocketIO polling fallback should work automatically

