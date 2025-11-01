from flask import Flask, render_template, jsonify, request, session, redirect, url_for, flash
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import pandas as pd
import random
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
import re
import time
from urllib.parse import quote
import sqlite3
from datetime import datetime
import json
import os
import socket

def get_local_ip():
    """Get local IP address for network access"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "localhost"

app = Flask(__name__, static_folder='static', template_folder='templates')
app.config['SECRET_KEY'] = 'ipl-auction-secret-key-change-in-production'
app.config['DATABASE'] = 'auction.db'
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Initialize extensions
socketio = SocketIO(app, cors_allowed_origins="*")
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Auction state (shared across all users)
auction_state = {
    'status': 'waiting',  # waiting, active, paused, completed
    'current_player': None,
    'current_player_index': 0,
    'current_category': None,
    'current_set': None,
    'active_pool': None,  # Track which pool is active (format: "category_set")
    'bids': {},  # {player_name: [{'user_id': X, 'amount': Y, 'timestamp': Z}]}
    'sold_players': {},  # {player_name: {'user_id': X, 'amount': Y, 'team_name': Z}}
    'start_time': None,
    'room_id': 'main_auction_room'
}

# Initialize database
def init_db():
    """Initialize database with tables"""
    conn = sqlite3.connect(app.config['DATABASE'])
    c = conn.cursor()
    
    # Users table
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        team_name TEXT,
        purse REAL DEFAULT 100.0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # Teams table (playing 11)
    c.execute('''CREATE TABLE IF NOT EXISTS teams (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        player_name TEXT NOT NULL,
        player_category TEXT,
        purchase_price REAL,
        position INTEGER,
        is_captain INTEGER DEFAULT 0,
        FOREIGN KEY (user_id) REFERENCES users (id),
        UNIQUE(user_id, player_name)
    )''')
    
    # Bids table
    c.execute('''CREATE TABLE IF NOT EXISTS bids (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        player_name TEXT NOT NULL,
        amount REAL NOT NULL,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        is_winning INTEGER DEFAULT 0,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )''')
    
    # Auction log
    c.execute('''CREATE TABLE IF NOT EXISTS auction_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        player_name TEXT NOT NULL,
        category TEXT,
        base_price REAL,
        sold_to_user_id INTEGER,
        final_price REAL,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (sold_to_user_id) REFERENCES users (id)
    )''')
    
    conn.commit()
    conn.close()

# User model for Flask-Login
class User(UserMixin):
    def __init__(self, id, username, email, team_name, purse):
        self.id = id
        self.username = username
        self.email = email
        self.team_name = team_name
        self.purse = purse

@login_manager.user_loader
def load_user(user_id):
    conn = sqlite3.connect(app.config['DATABASE'])
    c = conn.cursor()
    c.execute('SELECT id, username, email, team_name, purse FROM users WHERE id = ?', (user_id,))
    user_data = c.fetchone()
    conn.close()
    if user_data:
        return User(user_data[0], user_data[1], user_data[2], user_data[3], user_data[4])
    return None

# Configuration
EXCEL_FILE = 'AUCTION.xlsx'  # Make sure this matches your Excel file name
SHEET_NAME = 0
COLUMNS = [
    'Indian Bat', 'Foreign Bat', 'Indian AR', 'Foreign AR',
    'Indian Pace', 'Foreign Pace', 'Indian spin', 'Foreign spin', 'Wicketkeepers'
]

# Foreign player categories
FOREIGN_CATEGORIES = ['Foreign Bat', 'Foreign AR', 'Foreign Pace', 'Foreign spin']

def is_foreign_player(category):
    """Check if player category is foreign"""
    return category in FOREIGN_CATEGORIES

# Admin username
ADMIN_USERNAME = 'mithesh'

# Global variable to store raw player data (unshuffled)
raw_player_data = None
# Store shuffled splits per category to ensure no duplicates between sets
category_shuffled_splits = {}
# Cache for internet-fetched player data
player_info_cache = {}

def load_raw_data():
    """Load Excel file and store raw player data"""
    global raw_player_data
    
    if raw_player_data is not None:
        return raw_player_data
    
    df = pd.read_excel(EXCEL_FILE, sheet_name=SHEET_NAME)
    data = {}
    
    for col in COLUMNS:
        if col not in df.columns:
            continue
        
        players = df[col].dropna().astype(str).tolist()
        players = [p.strip() for p in players if p.strip() and p.strip().lower() != 'nan']
        
        data[col] = {
            'players': players,
            'total': len(players)
        }
    
    raw_player_data = data
    return data

def get_shuffled_set(category, set_num):
    """Get a shuffled set for a category, ensuring no duplicates between sets"""
    if raw_player_data is None:
        load_raw_data()
    
    if category not in raw_player_data:
        return []
    
    # If this category hasn't been shuffled yet, shuffle once and store both sets
    if category not in category_shuffled_splits:
        players = raw_player_data[category]['players'].copy()
        random.shuffle(players)  # Shuffle once per category
        
        n = len(players)
        mid = (n + 1) // 2
        
        # Store both sets so they remain consistent
        category_shuffled_splits[category] = {
            'set1': players[:mid],
            'set2': players[mid:]
        }
    
    # Return the appropriate set (already shuffled and split)
    return category_shuffled_splits[category][f'set{set_num}']

# Removed unused load_and_prepare_data() function

@app.route('/')
def index():
    """Home page - redirects based on auth status"""
    mode = request.args.get('mode', 'login')
    if current_user.is_authenticated:
        return render_template('auction.html')
    return render_template('auth.html', mode=mode)

@app.route('/auction')
@login_required
def auction_page():
    """Auction page route"""
    is_admin = current_user.username.lower() == ADMIN_USERNAME.lower()
    return render_template('auction.html', is_admin=is_admin)

@app.route('/login', methods=['POST'])
def login():
    """User login API"""
    data = request.get_json()
    username = data.get('username', '').strip()
    password = data.get('password', '')
    
    conn = sqlite3.connect(app.config['DATABASE'])
    c = conn.cursor()
    c.execute('SELECT id, username, email, team_name, purse, password_hash FROM users WHERE username = ?', (username,))
    user_data = c.fetchone()
    conn.close()
    
    if user_data and check_password_hash(user_data[5], password):
        user = User(user_data[0], user_data[1], user_data[2], user_data[3], user_data[4])
        login_user(user, remember=True)
        return jsonify({'success': True, 'user': {
            'id': user.id, 'username': user.username, 'team_name': user.team_name, 'purse': user.purse
        }})
    return jsonify({'success': False, 'message': 'Invalid credentials'}), 401

# Signup removed - users are pre-registered by admin

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return jsonify({'success': True})

@app.route('/api/user-info')
def user_info():
    """Get current user info"""
    if not current_user.is_authenticated:
        return jsonify({'error': 'Not authenticated'}), 401
    return jsonify({
        'id': current_user.id,
        'username': current_user.username,
        'team_name': current_user.team_name,
        'purse': current_user.purse
    })

@app.after_request
def after_request(response):
    """Add headers to prevent 403 errors"""
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

@app.route('/api/init', methods=['POST'])
def init_auction():
    """Initialize auction - resets shuffle state and returns categories"""
    try:
        global category_shuffled_splits
        # Reset shuffled splits for a fresh auction
        category_shuffled_splits = {}
        
        raw_data = load_raw_data()
        
        # Return category info without pre-shuffled data
        categories_info = {}
        for col in COLUMNS:
            if col in raw_data:
                total = raw_data[col]['total']
                mid = (total + 1) // 2
                categories_info[col] = {
                    'set1_count': mid,
                    'set2_count': total - mid,
                    'total': total
                }
        
        return jsonify({
            'success': True,
            'categories': COLUMNS,
            'category_info': categories_info
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/get-category-set/<category>/<set_num>')
def get_category_set(category, set_num):
    """Get a freshly shuffled set for a category"""
    try:
        set_num = int(set_num)
        if set_num not in [1, 2]:
            return jsonify({'success': False, 'error': 'Set number must be 1 or 2'}), 400
        
        players = get_shuffled_set(category, set_num)
        
        # Add base price information for each player
        players_with_prices = []
        for player in players:
            players_with_prices.append({
                'name': player,
                'base_price': get_player_base_price(player),
                'is_critical': is_critical_player(player)
            })
        
        return jsonify({
            'success': True,
            'category': category,
            'set': set_num,
            'players': players_with_prices,
            'count': len(players_with_prices)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Critical players list (will have base price of 3 cr, others get 1 cr)
CRITICAL_PLAYERS = {
    'virat kohli', 'rohit sharma', 'shubman gill', 'suryakumar yadav',
    'ruturaj gaikwad', 'yashasvi jaiswal', 'shreyas iyer', 'hardik pandya',
    'ravindra jadeja', 'jasprit bumrah', 'mohammed shami', 'mohammed siraj',
    'yuzvendra chahal', 'kuldeep yadav', 'ravichandran ashwin',
    'ms dhoni', 'rishabh pant', 'kl rahul', 'david warner', 'quinton de kock',
    'andre russell', 'glenn maxwell', 'ben stokes', 'mitchell starc',
    'pat cummins', 'trent boult', 'rashid khan', 'sunil narine',
    'jos buttler', 'heinrich klaasen', 'dinesh karthik', 'sanju samson'
}

def is_critical_player(player_name):
    """Check if a player is a critical player"""
    return player_name.lower().strip() in CRITICAL_PLAYERS

def get_player_base_price(player_name):
    """Get base price for a player (3 cr for critical, 1 cr for others)"""
    return 3 if is_critical_player(player_name) else 1

# Player details database with stats and images
PLAYER_DETAILS = {
    'shubman gill': {
        'category': 'Indian Bat',
        'matches': 91,
        'runs': 2790,
        'strike_rate': 134.07,
        'fifties': 19,
        'hundreds': 3,
        'average': 37.7,
        'image_url': 'https://www.iplt20.com/assets/images/headshots/webp/3761.webp',
        'description': 'An elegant right-handed opening batsman, known for his classical style and ability to score big runs. A key player for Gujarat Titans.'
    },
    'virat kohli': {
        'category': 'Indian Bat',
        'matches': 237,
        'runs': 7263,
        'strike_rate': 130.02,
        'fifties': 50,
        'hundreds': 7,
        'average': 37.2,
        'image_url': 'https://www.iplt20.com/assets/images/headshots/webp/164.webp',
        'description': 'One of the greatest batsmen of all time, known for his aggressive yet consistent batting. Former captain of RCB.'
    },
    'rohit sharma': {
        'category': 'Indian Bat',
        'matches': 243,
        'runs': 6211,
        'strike_rate': 130.49,
        'fifties': 42,
        'hundreds': 1,
        'average': 30.3,
        'image_url': 'https://www.iplt20.com/assets/images/headshots/webp/107.webp',
        'description': 'A prolific opener and captain, known for his effortless hitting and ability to score big hundreds. Led Mumbai Indians to multiple titles.'
    },
    'suryakumar yadav': {
        'category': 'Indian Bat',
        'matches': 139,
        'runs': 3241,
        'strike_rate': 143.32,
        'fifties': 21,
        'hundreds': 1,
        'average': 29.0,
        'image_url': 'https://www.iplt20.com/assets/images/headshots/webp/1069.webp',
        'description': 'Known for his 360-degree batting and innovative shots. A dynamic middle-order batsman for Mumbai Indians.'
    },
    'ruturaj gaikwad': {
        'category': 'Indian Bat',
        'matches': 52,
        'runs': 1797,
        'strike_rate': 135.52,
        'fifties': 14,
        'hundreds': 1,
        'average': 39.1,
        'image_url': 'https://www.iplt20.com/assets/images/headshots/webp/2877.webp',
        'description': 'A stylish opener known for his elegant stroke play and consistency. Plays for Chennai Super Kings.'
    },
    'yashasvi jaiswal': {
        'category': 'Indian Bat',
        'matches': 37,
        'runs': 1176,
        'strike_rate': 148.48,
        'fifties': 9,
        'hundreds': 1,
        'average': 33.6,
        'image_url': 'https://www.iplt20.com/assets/images/headshots/webp/3982.webp',
        'description': 'A young explosive opener with incredible talent. Known for his aggressive batting style.'
    },
    'hardik pandya': {
        'category': 'Indian AR',
        'matches': 123,
        'runs': 2309,
        'wickets': 53,
        'strike_rate': 138.67,
        'economy': 9.08,
        'image_url': 'https://www.iplt20.com/assets/images/headshots/webp/2740.webp',
        'description': 'A dynamic all-rounder, known for his powerful hitting and crucial wickets. Captained Gujarat Titans.'
    },
    'ravindra jadeja': {
        'category': 'Indian AR',
        'matches': 226,
        'runs': 2692,
        'wickets': 152,
        'strike_rate': 127.61,
        'economy': 7.56,
        'image_url': 'https://www.iplt20.com/assets/images/headshots/webp/234.webp',
        'description': 'A world-class all-rounder known for his left-arm spin, explosive batting, and exceptional fielding.'
    },
    'jasprit bumrah': {
        'category': 'Indian Pace',
        'matches': 120,
        'wickets': 145,
        'economy': 7.39,
        'best_bowling': '5/10',
        'average': 22.6,
        'image_url': 'https://www.iplt20.com/assets/images/headshots/webp/2769.webp',
        'description': 'One of the best fast bowlers in the world, known for his yorkers, bouncers, and exceptional death bowling.'
    },
    'mohammed shami': {
        'category': 'Indian Pace',
        'matches': 110,
        'wickets': 127,
        'economy': 8.51,
        'best_bowling': '4/11',
        'average': 25.8,
        'image_url': 'https://www.iplt20.com/assets/images/headshots/webp/2699.webp',
        'description': 'A skilled fast bowler known for his ability to swing the ball and pick up wickets in the powerplay.'
    },
    'mohammed siraj': {
        'category': 'Indian Pace',
        'matches': 79,
        'wickets': 78,
        'economy': 8.68,
        'best_bowling': '4/21',
        'average': 27.8,
        'image_url': 'https://www.iplt20.com/assets/images/headshots/webp/3840.webp',
        'description': 'A fiery fast bowler known for his pace, swing, and ability to pick up wickets in the powerplay. A key bowler for RCB.'
    },
    'yuzvendra chahal': {
        'category': 'Indian spin',
        'matches': 145,
        'wickets': 187,
        'economy': 7.68,
        'best_bowling': '5/40',
        'average': 22.3,
        'image_url': 'https://www.iplt20.com/assets/images/headshots/webp/2375.webp',
        'description': 'India\'s leading leg-spinner, known for his googlies and ability to pick up wickets in the middle overs.'
    },
    'kuldeep yadav': {
        'category': 'Indian spin',
        'matches': 77,
        'wickets': 81,
        'economy': 8.25,
        'best_bowling': '4/14',
        'average': 27.3,
        'image_url': 'https://www.iplt20.com/assets/images/headshots/webp/2668.webp',
        'description': 'A talented left-arm wrist spinner known for his variations and ability to trouble batsmen.'
    },
    'ravichandran ashwin': {
        'category': 'Indian spin',
        'matches': 197,
        'wickets': 171,
        'economy': 7.01,
        'best_bowling': '4/34',
        'average': 28.7,
        'image_url': 'https://www.iplt20.com/assets/images/headshots/webp/8.webp',
        'description': 'A wily off-spinner with a wide array of variations, known for his tactical acumen and ability to pick up crucial wickets.'
    },
    'ms dhoni': {
        'category': 'Wicketkeepers',
        'matches': 250,
        'runs': 5082,
        'strike_rate': 135.92,
        'fifties': 24,
        'hundreds': 0,
        'catches': 142,
        'stumpings': 42,
        'image_url': 'https://www.iplt20.com/assets/images/headshots/webp/59.webp',
        'description': 'The legendary captain and wicketkeeper, known for his cool leadership and finishing abilities. Led CSK to multiple titles.'
    },
    'rishabh pant': {
        'category': 'Wicketkeepers',
        'matches': 98,
        'runs': 2838,
        'strike_rate': 147.97,
        'fifties': 15,
        'hundreds': 1,
        'image_url': 'https://www.iplt20.com/assets/images/headshots/webp/3160.webp',
        'description': 'An explosive wicketkeeper-batsman known for his fearless batting and ability to change the game.'
    },
    'kl rahul': {
        'category': 'Wicketkeepers',
        'matches': 118,
        'runs': 4163,
        'strike_rate': 134.42,
        'fifties': 32,
        'hundreds': 4,
        'average': 46.2,
        'image_url': 'https://www.iplt20.com/assets/images/headshots/webp/2923.webp',
        'description': 'A classy opening batsman and wicketkeeper, known for his consistency and ability to anchor innings.'
    },
    'david warner': {
        'category': 'Foreign Bat',
        'matches': 176,
        'runs': 6397,
        'strike_rate': 139.92,
        'fifties': 60,
        'hundreds': 4,
        'average': 41.5,
        'image_url': 'https://www.iplt20.com/assets/images/headshots/webp/170.webp',
        'description': 'An explosive Australian opener, known for his aggressive batting and leadership. Former captain of Sunrisers Hyderabad.'
    },
    'quinton de kock': {
        'category': 'Foreign Bat',
        'matches': 96,
        'runs': 2907,
        'strike_rate': 134.65,
        'fifties': 21,
        'hundreds': 2,
        'image_url': 'https://www.iplt20.com/assets/images/headshots/webp/149.webp',
        'description': 'A destructive wicketkeeper-batsman from South Africa, known for his explosive starts at the top of the order.'
    },
    'travis head': {
        'category': 'Foreign Bat',
        'matches': 12,
        'runs': 553,
        'strike_rate': 166.41,
        'fifties': 4,
        'hundreds': 1,
        'average': 46.1,
        'image_url': 'https://www.iplt20.com/assets/images/headshots/webp/1281.webp',
        'description': 'An aggressive Australian opener known for his explosive batting and ability to score quickly.'
    },
    'andre russell': {
        'category': 'Foreign AR',
        'matches': 112,
        'runs': 2262,
        'wickets': 96,
        'strike_rate': 174.00,
        'economy': 9.04,
        'image_url': 'https://www.iplt20.com/assets/images/headshots/webp/153.webp',
        'description': 'A powerful all-rounder from West Indies, known for his explosive batting and effective fast bowling.'
    },
    'glenn maxwell': {
        'category': 'Foreign AR',
        'matches': 124,
        'runs': 2719,
        'wickets': 33,
        'strike_rate': 157.62,
        'economy': 8.15,
        'image_url': 'https://www.iplt20.com/assets/images/headshots/webp/134.webp',
        'description': 'The "Big Show" - an explosive all-rounder known for his incredible hitting and useful off-spin bowling.'
    },
    'ben stokes': {
        'category': 'Foreign AR',
        'matches': 43,
        'runs': 935,
        'wickets': 28,
        'strike_rate': 134.50,
        'economy': 8.55,
        'image_url': 'https://www.iplt20.com/assets/images/headshots/webp/1154.webp',
        'description': 'A world-class all-rounder from England, known for his match-winning performances with both bat and ball.'
    },
    'mitchell starc': {
        'category': 'Foreign Pace',
        'matches': 110,
        'wickets': 156,
        'economy': 7.89,
        'best_bowling': '5/14',
        'average': 21.9,
        'image_url': 'https://www.iplt20.com/assets/images/headshots/webp/118.webp',
        'description': 'One of the world\'s premier fast bowlers, known for his pace, swing, and devastating yorkers.'
    },
    'pat cummins': {
        'category': 'Foreign Pace',
        'matches': 51,
        'wickets': 60,
        'economy': 8.55,
        'best_bowling': '4/29',
        'average': 25.6,
        'image_url': 'https://www.iplt20.com/assets/images/headshots/webp/125.webp',
        'description': 'Australia\'s Test and ODI captain, a world-class fast bowler known for his accuracy and ability to reverse swing.'
    },
    'rashid khan': {
        'category': 'Foreign spin',
        'matches': 109,
        'wickets': 139,
        'economy': 6.67,
        'best_bowling': '4/24',
        'average': 20.8,
        'image_url': 'https://www.iplt20.com/assets/images/headshots/webp/157.webp',
        'description': 'One of the best leg-spinners in T20 cricket, known for his googlies and exceptional economy rate.'
    },
    'sunil narine': {
        'category': 'Foreign spin',
        'matches': 163,
        'wickets': 163,
        'economy': 6.73,
        'best_bowling': '5/19',
        'average': 25.8,
        'image_url': 'https://www.iplt20.com/assets/images/headshots/webp/146.webp',
        'description': 'A mystery spinner and explosive batsman, known for his unreadable variations and power hitting.'
    },
    'jos buttler': {
        'category': 'Wicketkeepers',
        'matches': 96,
        'runs': 3223,
        'strike_rate': 147.61,
        'fifties': 19,
        'hundreds': 5,
        'average': 39.3,
        'image_url': 'https://www.iplt20.com/assets/images/headshots/webp/161.webp',
        'description': 'An explosive English wicketkeeper-batsman, known for his aggressive stroke play and ability to score quickly.'
    },
    'heinrich klaasen': {
        'category': 'Wicketkeepers',
        'matches': 41,
        'runs': 1387,
        'strike_rate': 177.22,
        'fifties': 8,
        'hundreds': 1,
        'average': 36.5,
        'image_url': 'https://www.iplt20.com/assets/images/headshots/webp/1245.webp',
        'description': 'A destructive South African wicketkeeper-batsman, known for his power hitting and ability to clear boundaries.'
    },
    'dinesh karthik': {
        'category': 'Wicketkeepers',
        'matches': 242,
        'runs': 4516,
        'strike_rate': 135.28,
        'fifties': 20,
        'hundreds': 0,
        'image_url': 'https://www.iplt20.com/assets/images/headshots/webp/102.webp',
        'description': 'An experienced wicketkeeper-batsman, known for his finishing abilities and calm presence under pressure.'
    },
    'sanju samson': {
        'category': 'Wicketkeepers',
        'matches': 152,
        'runs': 3888,
        'strike_rate': 136.30,
        'fifties': 22,
        'hundreds': 3,
        'average': 29.4,
        'image_url': 'https://www.iplt20.com/assets/images/headshots/webp/258.webp',
        'description': 'An elegant right-handed wicketkeeper-batsman, known for his aggressive stroke play and leadership for Rajasthan Royals.'
    },
    'trent boult': {
        'category': 'Foreign Pace',
        'matches': 95,
        'wickets': 117,
        'economy': 8.32,
        'best_bowling': '4/18',
        'average': 27.4,
        'image_url': 'https://www.iplt20.com/assets/images/headshots/webp/151.webp',
        'description': 'A world-class left-arm fast bowler from New Zealand, known for his swing and ability to take early wickets.'
    },
    'kagiso rabada': {
        'category': 'Foreign Pace',
        'matches': 69,
        'wickets': 106,
        'economy': 8.34,
        'best_bowling': '4/21',
        'average': 23.5,
        'image_url': 'https://www.iplt20.com/assets/images/headshots/webp/138.webp',
        'description': 'A fiery South African fast bowler known for his pace, accuracy, and ability to bowl deadly yorkers.'
    },
    'jofra archer': {
        'category': 'Foreign Pace',
        'matches': 35,
        'wickets': 46,
        'economy': 7.69,
        'best_bowling': '3/15',
        'average': 21.3,
        'image_url': 'https://www.iplt20.com/assets/images/headshots/webp/3850.webp',
        'description': 'An express fast bowler from England, known for his raw pace and ability to bowl consistently at 150+ km/h.'
    }
}

def fetch_player_info_from_internet(player_name):
    """Fetch player information from internet sources"""
    player_lower = player_name.lower().strip()
    
    # Check cache first
    if player_lower in player_info_cache:
        return player_info_cache[player_lower]
    
    info = {
        'source': 'internet',
        'fetched_at': time.time()
    }
    
    try:
        # Try Wikipedia first for general information
        wiki_url = f"https://en.wikipedia.org/wiki/{quote(player_name.replace(' ', '_'))}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        wiki_response = requests.get(wiki_url, headers=headers, timeout=5)
        
        if wiki_response.status_code == 200:
            soup = BeautifulSoup(wiki_response.content, 'html.parser')
            
            # Extract description from Wikipedia
            paragraphs = soup.find_all('p')
            description = None
            for p in paragraphs[:3]:  # Check first 3 paragraphs
                text = p.get_text().strip()
                if len(text) > 100 and player_name.split()[0].lower() in text.lower():
                    description = text[:500]  # Limit to 500 characters
                    break
            
            if description:
                info['description'] = description + "... (Source: Wikipedia)"
            
            # Try to find infobox with basic stats
            infobox = soup.find('table', class_='infobox')
            if infobox:
                # Extract birth date, nationality, etc.
                rows = infobox.find_all('tr')
                for row in rows:
                    th = row.find('th')
                    td = row.find('td')
                    if th and td:
                        key = th.get_text().strip().lower()
                        value = td.get_text().strip()
                        
                        if 'born' in key or 'date of birth' in key:
                            info['birth_info'] = value
                        if 'nationality' in key or 'country' in key:
                            info['nationality'] = value
                        if 'nickname' in key:
                            info['nickname'] = value
            
            # Try to find image
            img = soup.find('img', class_=lambda x: x and 'thumb' in x.lower())
            if img and img.get('src'):
                img_url = img['src']
                if img_url.startswith('//'):
                    img_url = 'https:' + img_url
                elif img_url.startswith('/'):
                    img_url = 'https://en.wikipedia.org' + img_url
                info['wikipedia_image'] = img_url
        
        # Try ESPN Cricinfo for cricket-specific stats
        try:
            cricinfo_search_url = f"https://www.espncricinfo.com/search?q={quote(player_name)}"
            cricinfo_response = requests.get(cricinfo_search_url, headers=headers, timeout=5)
            
            if cricinfo_response.status_code == 200:
                cricinfo_soup = BeautifulSoup(cricinfo_response.content, 'html.parser')
                # Look for player profile link
                profile_link = cricinfo_soup.find('a', href=lambda x: x and '/players/' in x)
                if profile_link:
                    info['cricinfo_url'] = 'https://www.espncricinfo.com' + profile_link['href']
                    info['description'] = info.get('description', '') + f' View detailed stats on ESPN Cricinfo.'
        except:
            pass
        
        # Cache the result
        player_info_cache[player_lower] = info
        
    except requests.exceptions.Timeout:
        info['error'] = 'Request timeout - internet connection may be slow'
        print(f"Timeout fetching info for {player_name}")
        player_info_cache[player_lower] = info
    except requests.exceptions.ConnectionError:
        info['error'] = 'Connection error - check internet connection'
        print(f"Connection error fetching info for {player_name}")
        player_info_cache[player_lower] = info
    except Exception as e:
        print(f"Error fetching info for {player_name}: {str(e)}")
        info['error'] = str(e)
        player_info_cache[player_lower] = info
    
    return info

@app.route('/api/player-info/<player_name>')
def get_player_info(player_name):
    """Get detailed information about a player including stats and image"""
    player_lower = player_name.lower().strip()
    
    # Try to find player in database first
    player_info = PLAYER_DETAILS.get(player_lower)
    
    if player_info:
        # Player found with detailed stats, enhance with internet data
        try:
            internet_info = fetch_player_info_from_internet(player_name)
            
            # Merge internet data if available
            if 'description' in internet_info and not player_info.get('description'):
                player_info['description'] = internet_info.get('description')
            if 'wikipedia_image' in internet_info and not player_info.get('image_url'):
                player_info['image_url'] = internet_info.get('wikipedia_image')
            if 'birth_info' in internet_info:
                player_info['birth_info'] = internet_info.get('birth_info')
            if 'nationality' in internet_info:
                player_info['nationality'] = internet_info.get('nationality')
            
            player_info['source'] = 'database_enhanced'
            if 'cricinfo_url' in internet_info:
                player_info['external_links'] = {'cricinfo': internet_info['cricinfo_url']}
        except:
            pass
        
        return jsonify({
            'success': True,
            'name': player_name,
            'info': player_info
        })
    else:
        # Player not in database, try to fetch from internet
        category = get_player_category(player_name)
        
        try:
            internet_info = fetch_player_info_from_internet(player_name)
            
            # Combine with basic info
            combined_info = {
                'category': category,
                'source': 'internet',
                **internet_info
            }
            
            if 'description' not in combined_info:
                combined_info['description'] = f'{player_name} is a professional cricket player. Statistics and detailed information may be available from cricket databases.'
            
            return jsonify({
                'success': True,
                'name': player_name,
                'info': combined_info
            })
        except Exception as e:
            # Fallback to basic info if internet fetch fails
            return jsonify({
                'success': True,
                'name': player_name,
                'info': {
                    'category': category,
                    'source': 'basic',
                    'description': f'{player_name} is part of the IPL auction pool. Detailed statistics coming soon!',
                    'image_url': None
                }
            })

def get_player_category(player_name):
    """Determine which category a player belongs to"""
    raw_data = load_raw_data()
    
    for category, info in raw_data.items():
        if player_name in info['players']:
            return category
    return 'Unknown'

# WebSocket events for real-time bidding
@socketio.on('connect')
def handle_connect(auth):
    """User connects to auction room"""
    # Note: Socket.IO doesn't directly use Flask-Login sessions
    # In production, you'd want to verify the session here
    # For now, we'll trust authenticated users
    join_room(auction_state['room_id'])
    # Send current auction state
    emit('auction_state', auction_state)

@socketio.on('disconnect')
def handle_disconnect():
    """User disconnects"""
    if current_user.is_authenticated:
        leave_room(auction_state['room_id'])
        emit('user_disconnected', {'username': current_user.username}, room=auction_state['room_id'])

@socketio.on('place_bid')
def handle_bid(data):
    """Handle player bid"""
    player_name = data.get('player_name')
    amount = float(data.get('amount', 0))
    
    if not player_name or amount <= 0:
        emit('bid_error', {'message': 'Invalid bid'})
        return
    
    # Get user info from session
    user_id = getattr(current_user, 'id', None) if current_user.is_authenticated else None
    if not user_id:
        emit('bid_error', {'message': 'Please log in to place bids'})
        return
    
    # Check if user has enough purse
    conn = sqlite3.connect(app.config['DATABASE'])
    c = conn.cursor()
    c.execute('SELECT purse FROM users WHERE id = ?', (user_id,))
    user_purse = c.fetchone()[0]
    
    # Calculate total spent
    c.execute('SELECT COALESCE(SUM(final_price), 0) FROM auction_log WHERE sold_to_user_id = ?', (user_id,))
    total_spent = c.fetchone()[0] or 0
    
    available_purse = user_purse - total_spent
    
    if amount > available_purse:
        conn.close()
        emit('bid_error', {'message': f'Insufficient funds! Available: {available_purse:.2f} Cr'})
        return
    
    # Check if bid is higher than current highest
    current_bids = auction_state['bids'].get(player_name, [])
    highest_bid = max([b['amount'] for b in current_bids], default=0)
    
    if amount <= highest_bid:
        conn.close()
        emit('bid_error', {'message': f'Bid must be higher than {highest_bid} Cr'})
        return
    
    # Get user info from session/request (simplified - in production use proper auth)
    user_id = getattr(current_user, 'id', None) if current_user.is_authenticated else None
    if not user_id:
        emit('bid_error', {'message': 'Please log in to place bids'})
        return
    
    # Record bid
    bid_entry = {
        'user_id': user_id,
        'username': current_user.username,
        'team_name': current_user.team_name,
        'amount': amount,
        'timestamp': datetime.now().isoformat()
    }
    
    if player_name not in auction_state['bids']:
        auction_state['bids'][player_name] = []
    auction_state['bids'][player_name].append(bid_entry)
    
    # Save to database
    c.execute('INSERT INTO bids (user_id, player_name, amount) VALUES (?, ?, ?)',
             (user_id, player_name, amount))
    conn.commit()
    conn.close()
    
    # Broadcast bid to all users
    emit('new_bid', {
        'player_name': player_name,
        'bid': bid_entry,
        'highest_bid': amount
    }, room=auction_state['room_id'], include_self=True)

@socketio.on('sell_player')
def handle_sell(data):
    """Sell player to highest bidder (admin/auctioneer function)"""
    # Check if user is admin
    user_id = getattr(current_user, 'id', None) if current_user.is_authenticated else None
    if not user_id:
        emit('sell_error', {'message': 'Please log in'})
        return
    
    # Verify admin status
    conn = sqlite3.connect(app.config['DATABASE'])
    c = conn.cursor()
    c.execute('SELECT username FROM users WHERE id = ?', (user_id,))
    user_data = c.fetchone()
    conn.close()
    
    if not user_data or user_data[0].lower() != ADMIN_USERNAME.lower():
        emit('sell_error', {'message': 'Only admin can sell players'})
        return
    
    player_name = data.get('player_name')
    if not player_name or player_name not in auction_state['bids']:
        emit('sell_error', {'message': 'No bids for this player'})
        return
    
    bids = auction_state['bids'][player_name]
    if not bids:
        emit('sell_error', {'message': 'No bids found'})
        return
    
    # Find highest bidder
    highest_bid = max(bids, key=lambda x: x['amount'])
    winner_id = highest_bid['user_id']
    final_price = highest_bid['amount']
    
    # Update database
    conn = sqlite3.connect(app.config['DATABASE'])
    c = conn.cursor()
    
    # Get player info
    base_price = get_player_base_price(player_name)
    category = get_player_category(player_name)
    
    # Get current purse before deduction
    c.execute('SELECT username, team_name, purse FROM users WHERE id = ?', (winner_id,))
    winner_info = c.fetchone()
    
    # Deduct from winner's purse
    c.execute('UPDATE users SET purse = purse - ? WHERE id = ?', (final_price, winner_id))
    
    # Log sale
    c.execute('''INSERT INTO auction_log (player_name, category, base_price, sold_to_user_id, final_price)
                 VALUES (?, ?, ?, ?, ?)''', (player_name, category, base_price, winner_id, final_price))
    
    # Add to winner's team
    c.execute('''INSERT OR REPLACE INTO teams (user_id, player_name, player_category, purchase_price)
                 VALUES (?, ?, ?, ?)''', (winner_id, player_name, category, final_price))
    
    # Mark winning bid
    c.execute('UPDATE bids SET is_winning = 1 WHERE user_id = ? AND player_name = ? AND amount = ?',
             (winner_id, player_name, final_price))
    
    # Calculate remaining purse
    remaining_purse = winner_info[2] - final_price
    
    conn.commit()
    conn.close()
    
    # Update auction state
    auction_state['sold_players'][player_name] = {
        'user_id': winner_id,
        'team_name': winner_info[1],
        'amount': final_price
    }
    
    # Clear bids for this player
    if player_name in auction_state['bids']:
        del auction_state['bids'][player_name]
    
    # Broadcast sale
    socketio.emit('player_sold', {
        'player_name': player_name,
        'buyer': winner_info[0],
        'team_name': winner_info[1],
        'price': final_price,
        'remaining_purse': remaining_purse
    }, room=auction_state['room_id'])

@socketio.on('start_auction')
def handle_start_auction(data):
    """Start/pause/resume auction"""
    action = data.get('action', 'start')
    
    # Prevent starting new pool if one is already active
    if action == 'start' and auction_state['status'] == 'active' and auction_state['active_pool']:
        socketio.emit('auction_error', {
            'message': f'Pool "{auction_state["current_category"]} - Set {auction_state["current_set"]}" is already in progress. Please complete or pause it first.'
        }, room=auction_state['room_id'])
        return
    
    auction_state['status'] = 'active' if action == 'start' else action
    
    if action == 'start' and data.get('category') and data.get('set'):
        category = data['category']
        set_num = int(data['set'])
        players = get_shuffled_set(category, set_num)
        
        players_with_prices = []
        for player in players:
            players_with_prices.append({
                'name': player,
                'base_price': get_player_base_price(player),
                'is_critical': is_critical_player(player)
            })
        
        auction_state['current_category'] = category
        auction_state['current_set'] = set_num
        auction_state['active_pool'] = f"{category}_{set_num}"
        auction_state['current_player_index'] = 0
        auction_state['current_player'] = players_with_prices[0] if players_with_prices else None
        auction_state['start_time'] = datetime.now().isoformat()
        
        # Broadcast pool start announcement
        socketio.emit('pool_started', {
            'category': category,
            'set': set_num,
            'message': f'Auction started: {category} - Set {set_num}'
        }, room=auction_state['room_id'])
    
    socketio.emit('auction_state', auction_state, room=auction_state['room_id'])

@socketio.on('next_player')
def handle_next_player():
    """Move to next player"""
    if auction_state['status'] != 'active':
        return
    
    category = auction_state['current_category']
    set_num = auction_state['current_set']
    if not category or not set_num:
        return
    
    players = get_shuffled_set(category, set_num)
    players_with_prices = []
    for player in players:
        players_with_prices.append({
            'name': player,
            'base_price': get_player_base_price(player),
            'is_critical': is_critical_player(player)
        })
    
    next_index = auction_state['current_player_index'] + 1
    if next_index < len(players_with_prices):
        auction_state['current_player_index'] = next_index
        auction_state['current_player'] = players_with_prices[next_index]
        auction_state['bids'][players_with_prices[next_index]['name']] = []
        socketio.emit('auction_state', auction_state, room=auction_state['room_id'])

# API routes for team management
@app.route('/api/my-team')
@login_required
def my_team():
    """Get user's purchased players"""
    conn = sqlite3.connect(app.config['DATABASE'])
    c = conn.cursor()
    c.execute('''SELECT t.player_name, t.player_category, t.purchase_price, t.position, 
                 al.final_price, t.is_captain FROM teams t
                 LEFT JOIN auction_log al ON t.player_name = al.player_name AND t.user_id = al.sold_to_user_id
                 WHERE t.user_id = ? ORDER BY t.position''', (current_user.id,))
    players = []
    for row in c.fetchall():
        category = row[1] or 'Unknown'
        players.append({
            'name': row[0],
            'category': category,
            'price': row[4] or row[2],
            'position': row[3],
            'is_foreign': is_foreign_player(category),
            'is_captain': bool(row[5]) if row[5] is not None else (row[3] == 1)  # Default position 1 as captain
        })
    
    # Get current purse
    c.execute('SELECT purse FROM users WHERE id = ?', (current_user.id,))
    purse = c.fetchone()[0]
    c.execute('SELECT COALESCE(SUM(final_price), 0) FROM auction_log WHERE sold_to_user_id = ?', (current_user.id,))
    spent = c.fetchone()[0] or 0
    
    conn.close()
    return jsonify({
        'players': players,
        'purse_remaining': purse - spent,
        'total_spent': spent
    })

@app.route('/api/update-playing-11', methods=['POST'])
@login_required
def update_playing_11():
    """Update playing 11 positions"""
    data = request.get_json()
    players_order = data.get('players', [])  # List of {name, position}
    captain_name = data.get('captain')  # Optional captain name
    
    conn = sqlite3.connect(app.config['DATABASE'])
    c = conn.cursor()
    
    # Clear existing positions and captain flags
    c.execute('UPDATE teams SET position = NULL, is_captain = 0 WHERE user_id = ?', (current_user.id,))
    
    # Update positions
    for item in players_order:
        player_name = item.get('name')
        position = item.get('position')
        if player_name and position is not None:
            is_captain = 1 if (captain_name == player_name or position == 1) else 0
            c.execute('UPDATE teams SET position = ?, is_captain = ? WHERE user_id = ? AND player_name = ?',
                     (position, is_captain, current_user.id, player_name))
    
    conn.commit()
    conn.close()
    return jsonify({'success': True})

if __name__ == '__main__':
    # Initialize database
    init_db()
    
    # Load player data
    try:
        load_raw_data()
        print("Auction data loaded successfully!")
        print(f"Categories: {COLUMNS}")
        print(f"Total categories: {len(COLUMNS)}")
        print("\n" + "="*60)
        print("🏏 IPL MULTIPLAYER AUCTION SYSTEM")
        print("="*60)
        print(f"\n✅ Server starting on:")
        print(f"   Local:    http://localhost:8080")
        print(f"   Network:  http://{get_local_ip()}:8080")
        print(f"\n📡 For same WiFi network:")
        print(f"   http://{get_local_ip()}:8080")
        print(f"\n🌐 For global access:")
        print(f"   Deploy to Render.com or Railway.app via GitHub")
        print(f"   See DEPLOY.md for instructions")
        print("="*60 + "\n")
        PORT = 8080
        # Allow PORT from environment for cloud hosting
        import os
        PORT = int(os.environ.get('PORT', PORT))
        socketio.run(app, debug=True, host='0.0.0.0', port=PORT, allow_unsafe_werkzeug=True)
    except Exception as e:
        print(f"Error starting server: {e}")
        import traceback
        traceback.print_exc()

