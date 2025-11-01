# 🏏 IPL Mega Auction 2025

A real-time multiplayer auction platform for conducting IPL player auctions with live bidding, team management, and playing XI selection.

## ✨ Features

- 🎯 **Real-time Multiplayer Bidding** - Live auction with WebSocket-based real-time updates
- 👥 **User Authentication** - Secure login system with pre-registered users
- 💰 **Purse Management** - Track team budgets (100 Cr per team) with automatic deduction
- 📊 **Team Management** - Build your team and select playing XI with drag-and-drop
- 👑 **Admin Controls** - Admin can start auctions, manage player pools, and finalize sales
- 🌍 **Foreign Player Indicators** - Visual markers for foreign players (✈️) and captain (⭐)
- 📡 **Live Auction Feed** - Professional auction feed showing all bids and transactions
- 📱 **Responsive Design** - Modern, smooth UI optimized for all devices

## 🚀 Quick Start

### Prerequisites

- Python 3.10 or higher
- pip (Python package manager)

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Mithesh14/ipl-auction.git
   cd ipl-auction
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Initialize database:**
   ```bash
   python populate_users.py
   ```

4. **Run the server:**
   ```bash
   python app.py
   ```

5. **Access the application:**
   - Open browser: `http://localhost:8080`
   - Login with credentials (see below)

## 👤 Login Credentials

All users are pre-registered with `username = password`:

| Username | Password | Role |
|----------|----------|------|
| mithesh   | mithesh   | Admin |
| susan     | susan     | User |
| minigv    | minigv    | User |
| suku      | suku      | User |
| hemanth   | hemanth   | User |
| thillu    | thillu    | User |
| ruben     | ruben     | User |
| keerthi   | keerthi   | User |
| aki       | aki       | User |

**Note:** Only `mithesh` has admin privileges (can start auctions and sell players).

## 🎮 How to Use

### For Admin (mithesh):

1. Login with admin credentials
2. Select a player pool category (e.g., "Indian Bat", "Foreign Bat")
3. Click "Start Set 1" or "Start Set 2" to begin auction
4. Players appear one by one for bidding
5. View all bids in real-time
6. Click "Sell to Highest Bidder" to finalize sale
7. Click "Next Player" to continue

### For Other Users:

1. Login with your credentials
2. Wait for admin to start an auction
3. When a player is on the block, enter your bid amount
4. Click "Place Bid" to participate
5. View live feed of all bids
6. Manage your team in "My Team" section
7. Select playing XI with drag-and-drop
8. Mark captain and view foreign players

## 📁 Project Structure

```
ipl-auction/
├── app.py                 # Main Flask application
├── wsgi.py                # WSGI entry point (for PythonAnywhere)
├── populate_users.py      # Database initialization script
├── export_to_excel.py     # Utility to export data to Excel
├── game.py                # Original terminal-based version
├── requirements.txt        # Python dependencies
├── runtime.txt            # Python version for deployment
├── Procfile              # Deployment configuration
├── AUCTION.xlsx          # Player data (Excel file)
├── static/              # Frontend assets
│   ├── auction.css      # Main stylesheet
│   ├── auction.js       # Auction logic
│   └── auth.css         # Login page styles
└── templates/           # HTML templates
    ├── auction.html     # Main auction interface
    └── auth.html        # Login page
```

## 🌐 Deployment

### PythonAnywhere (Recommended for Flask)

1. **Sign up:** https://www.pythonanywhere.com

2. **Clone repository in Bash console:**
   ```bash
   cd ~
   git clone https://github.com/Mithesh14/ipl-auction.git
   cd ipl-auction
   ```

3. **Install dependencies:**
   ```bash
   pip3.10 install --user -r requirements.txt
   ```

4. **Initialize database:**
   ```bash
   python3.10 populate_users.py
   ```

5. **Create Flask web app:**
   - Go to "Web" tab → "Add a new web app"
   - Select Flask → Python 3.10
   - Set WSGI file path: `/home/YOUR_USERNAME/ipl-auction/wsgi.py`

6. **Configure static files:**
   - URL: `/static/`
   - Directory: `/home/YOUR_USERNAME/ipl-auction/static/`

7. **Update main WSGI file** (`/var/www/YOUR_USERNAME_pythonanywhere_com_wsgi.py`):
   ```python
   import sys
   import os
   
   project_home = '/home/YOUR_USERNAME/ipl-auction'
   if project_home not in sys.path:
       sys.path.insert(0, project_home)
   
   os.chdir(project_home)
   from wsgi import app as application
   ```

8. **Reload web app** and access at: `https://YOUR_USERNAME.pythonanywhere.com`

### Other Platforms

- **Railway.app** - Connect GitHub repo, auto-deploys
- **Render.com** - Connect GitHub repo, auto-deploys
- **Heroku** - Use Procfile (already included)

## 🛠️ Tech Stack

- **Backend:**
  - Flask 3.0.0 - Web framework
  - Flask-SocketIO 5.3.5 - Real-time WebSocket communication
  - Flask-Login 0.6.3 - User authentication
  - SQLite - Database

- **Frontend:**
  - HTML5/CSS3 - Modern responsive design
  - JavaScript (ES6+) - Client-side logic
  - Socket.IO Client - Real-time updates

- **Data Processing:**
  - Pandas 2.2.0 - Excel file handling
  - OpenPyXL 3.1.2 - Excel file parsing
  - BeautifulSoup4 4.12.2 - Web scraping for player info

## 📝 Features in Detail

### Auction System
- **Player Categories:** Indian Bat, Foreign Bat, Indian AR, Foreign AR, Indian Pace, Foreign Pace, Indian Spin, Foreign Spin, Wicketkeepers
- **Set-based Organization:** Each category split into Set 1 and Set 2 (no duplicates)
- **Base Pricing:** 1 Cr for regular players, 3 Cr for critical players
- **Real-time Bidding:** All participants see bids instantly
- **Admin Controls:** Only admin can start pools and finalize sales

### Team Management
- **Budget Tracking:** Real-time purse updates after each purchase
- **Playing XI Selection:** Drag-and-drop interface for team selection
- **Player Indicators:**
  - ✈️ Foreign players
  - ⭐ Captain designation
- **Team Roster:** View all purchased players and manage squad

### Live Feed
- Professional auction feed showing:
  - All bids with timestamps
  - Bidder names and amounts
  - Player sales with final prices
  - Leading bid indicators

## 🔧 Configuration

### Admin Settings
- Admin username is set in `app.py`: `ADMIN_USERNAME = 'mithesh'`
- Foreign player categories defined in `FOREIGN_CATEGORIES` list

### Database
- Database file: `auction.db` (auto-created on first run)
- Tables: users, teams, bids, auction_log
- Initialize with: `python populate_users.py`

### Player Data
- Source: `AUCTION.xlsx` Excel file
- Sheet name: "Sheet1"
- Categories in separate columns

## 🐛 Troubleshooting

### Port Already in Use
Change port in `app.py`:
```python
PORT = 8080  # Change to available port
```

### Database Errors
Reinitialize database:
```bash
python populate_users.py
```

### Static Files Not Loading
- Ensure static files are in `/static/` directory
- For PythonAnywhere: Configure static file mapping in Web tab

### WebSocket Issues
- Flask-SocketIO automatically falls back to HTTP polling
- Works on all platforms including PythonAnywhere free tier

## 📄 License

This project is for personal/educational use.

## 👨‍💻 Author

**Mithesh**
- GitHub: [@Mithesh14](https://github.com/Mithesh14)

## 🤝 Contributing

Feel free to fork this project and submit pull requests for improvements!

## ⭐ Show Your Support

If you find this project useful, give it a ⭐ on GitHub!

---

**Built with ❤️ for IPL Auction 2025**
