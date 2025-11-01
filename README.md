# 🏏 IPL Mega Auction 2025 - Multiplayer Auction Platform

A professional real-time multiplayer auction system for IPL player auctions with bidding, team management, and playing 11 selection.

## Features

- ✅ Real-time multiplayer bidding via WebSocket
- ✅ User authentication (pre-registered users)
- ✅ Purse management (100 Cr per team)
- ✅ Playing 11 selection with drag-and-drop
- ✅ Admin controls for auction management
- ✅ Foreign player and captain indicators
- ✅ Live auction feed with professional UI

## Quick Start

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Populate users (if needed):
   ```bash
   python populate_users.py
   ```

3. Run server:
   ```bash
   python app.py
   ```

## Admin Access

- **Admin Username:** mithesh
- Only admin can start auction pools and sell players

## Login Credentials

All users are pre-registered with username = password.

## Deployment

This app is configured for Railway/Render deployment with:
- `Procfile` for web service
- Environment variable PORT support
- Database initialization on startup

## Tech Stack

- Flask (Backend)
- Flask-SocketIO (WebSocket)
- SQLite (Database)
- JavaScript/HTML/CSS (Frontend)
