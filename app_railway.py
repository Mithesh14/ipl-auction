# Railway/Render deployment version
# This version reads PORT from environment variable for cloud hosting

from app import app, socketio
import os

if __name__ == '__main__':
    # Get port from environment (Railway/Render provides this)
    PORT = int(os.environ.get('PORT', 8080))
    
    # Initialize database
    from app import init_db, load_raw_data
    init_db()
    load_raw_data()
    
    print(f"🚀 Starting on port {PORT}")
    # Use host 0.0.0.0 for cloud deployment
    socketio.run(app, host='0.0.0.0', port=PORT, debug=False, allow_unsafe_werkzeug=True)

