# 📋 PythonAnywhere Step-by-Step Guide

Detailed instructions for deploying your IPL Auction app on PythonAnywhere.

---

## ✅ Step 1: Update `/home/mithesh/ipl-auction/wsgi.py`

You have two options to get the updated `wsgi.py` file:

### Option A: Pull from GitHub (Recommended)

1. **Go to PythonAnywhere Dashboard**
   - Click on **"Bash"** (top menu)

2. **Navigate to your project directory:**
   ```bash
   cd ~/ipl-auction
   ```

3. **Pull the latest changes:**
   ```bash
   git pull origin main
   ```

4. **Verify the file was updated:**
   ```bash
   cat wsgi.py
   ```
   You should see the updated version with `init_db()` and `load_raw_data()`.

---

### Option B: Copy-Paste Manually

1. **Go to Files tab** in PythonAnywhere
2. **Navigate to:** `/home/mithesh/ipl-auction/wsgi.py`
3. **Click "Edit"** button
4. **Replace the entire file content** with:

```python
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
```

5. **Click "Save"** button (green button at top)

---

## ✅ Step 2: Update Main WSGI File

The main WSGI file that PythonAnywhere uses is located at:
**`/var/www/mithesh_pythonanywhere_com_wsgi.py`**

This file tells PythonAnywhere how to load your Flask app.

### How to Update It:

1. **Go to "Web" tab** in PythonAnywhere dashboard

2. **Click on the WSGI configuration file link:**
   - You'll see: `WSGI configuration file`
   - Click the filename: `mithesh_pythonanywhere_com_wsgi.py`
   - OR manually navigate: `/var/www/mithesh_pythonanywhere_com_wsgi.py`

3. **Replace the entire file content** with:

```python
# +++++++++++ FLASK +++++++++++
# To give your project its own virtualenv:
# /var/www/mithesh_pythonanywhere_com_wsgi.py
import sys

# Add your project directory to the Python path
project_home = '/home/mithesh/ipl-auction'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Change to project directory
import os
os.chdir(project_home)

# Import your Flask app from your wsgi.py file
# This imports the "application" variable from wsgi.py
from wsgi import app as application  # noqa

# If you get an error about module not found, make sure:
# 1. All dependencies are installed: pip3.10 install --user -r requirements.txt
# 2. The project_home path is correct
# 3. wsgi.py exists in /home/mithesh/ipl-auction/
```

**Key Points:**
- `project_home = '/home/mithesh/ipl-auction'` - Points to your project directory
- `from wsgi import app as application` - Imports `app` from your `wsgi.py` file and renames it to `application` (PythonAnywhere requirement)

4. **Click "Save"** button (green button at top)

---

## ✅ Step 3: Verify Setup

### Check Files Exist:

In **Bash console**, verify:

```bash
# Check wsgi.py exists and has correct content
cat ~/ipl-auction/wsgi.py | head -20

# Check main WSGI file
cat /var/www/mithesh_pythonanywhere_com_wsgi.py | head -15

# Check Excel file exists
ls -la ~/ipl-auction/AUCTION.xlsx

# Check static folder exists
ls -la ~/ipl-auction/static/
```

---

## ✅ Step 4: Install Dependencies (If Not Done)

In **Bash console**:

```bash
cd ~/ipl-auction
pip3.10 install --user -r requirements.txt
```

Wait for installation to complete (may take 1-2 minutes).

---

## ✅ Step 5: Initialize Database (If Not Done)

In **Bash console**:

```bash
cd ~/ipl-auction
python3.10 populate_users.py
```

This creates the database and adds all 9 users.

---

## ✅ Step 6: Configure Static Files

1. **Go to "Web" tab**

2. **Scroll down to "Static files" section**

3. **Add static file mapping:**
   - **URL:** `/static/`
   - **Directory:** `/home/mithesh/ipl-auction/static/`
   - Click **"Add"** button

4. **Verify it appears in the list**

---

## ✅ Step 7: Reload Web App

1. **Stay in "Web" tab**

2. **Scroll to top** of the page

3. **Click the green "Reload" button**
   - Button says: `mithesh.pythonanywhere.com`
   - It's a green button

4. **Wait 10-20 seconds** for reload to complete

5. **Look for error messages:**
   - Check "Error log" (scroll down)
   - If you see errors, note them and fix

---

## ✅ Step 8: Test Your App

1. **Open a new browser tab**

2. **Visit:** `https://mithesh.pythonanywhere.com`

3. **Expected Result:**
   - ✅ You should see the **login page** (not "Hello from Flask!")
   - ✅ Page should load with styling (CSS working)
   - ✅ You can enter credentials and login

4. **Test Login:**
   - Username: `mithesh`
   - Password: `mithesh`
   - Click Login
   - Should see the auction interface

---

## 🐛 Troubleshooting

### Error: "No module named 'wsgi'"

**Problem:** Main WSGI file can't find `wsgi.py`

**Solution:**
1. Check `project_home` path is correct: `/home/mithesh/ipl-auction`
2. Verify `wsgi.py` exists: `ls ~/ipl-auction/wsgi.py`
3. Make sure `os.chdir(project_home)` is in the main WSGI file

---

### Error: "No module named 'flask'"

**Problem:** Dependencies not installed

**Solution:**
```bash
cd ~/ipl-auction
pip3.10 install --user -r requirements.txt
```

---

### Error: "No such file: 'AUCTION.xlsx'"

**Problem:** Excel file not in project directory

**Solution:**
1. Upload `AUCTION.xlsx` to `/home/mithesh/ipl-auction/`
2. Or use Files tab → Navigate to directory → Upload file

---

### Still seeing "Hello from Flask!"

**Problem:** WSGI file not pointing to correct project

**Solution:**
1. Check main WSGI file (`/var/www/mithesh_pythonanywhere_com_wsgi.py`)
2. Verify `project_home = '/home/mithesh/ipl-auction'`
3. Verify `from wsgi import app as application`
4. Reload web app

---

### Static files not loading (CSS/JS broken)

**Problem:** Static files not configured

**Solution:**
1. Go to Web tab → Static files
2. Add mapping:
   - URL: `/static/`
   - Directory: `/home/mithesh/ipl-auction/static/`
3. Reload web app

---

### Database errors on login

**Problem:** Database not initialized or users not populated

**Solution:**
```bash
cd ~/ipl-auction
python3.10 populate_users.py
```
Then reload web app.

---

## 📊 File Structure Summary

```
/home/mithesh/ipl-auction/
├── app.py                    # Main Flask application
├── wsgi.py                   # WSGI entry point (imported by main WSGI)
├── requirements.txt          # Python dependencies
├── populate_users.py        # Database setup script
├── AUCTION.xlsx             # Player data
├── static/                   # CSS, JS files
│   ├── auction.css
│   ├── auction.js
│   └── auth.css
└── templates/               # HTML templates
    ├── auction.html
    └── auth.html

/var/www/
└── mithesh_pythonanywhere_com_wsgi.py  # Main WSGI file (points to wsgi.py)
```

---

## ✅ Quick Checklist

- [ ] Updated `/home/mithesh/ipl-auction/wsgi.py` with new version
- [ ] Updated `/var/www/mithesh_pythonanywhere_com_wsgi.py` to import from `wsgi.py`
- [ ] Installed dependencies (`pip3.10 install --user -r requirements.txt`)
- [ ] Initialized database (`python3.10 populate_users.py`)
- [ ] Configured static files in Web tab
- [ ] Reloaded web app
- [ ] Tested at `https://mithesh.pythonanywhere.com`
- [ ] Login works with credentials

---

## 🎯 Summary

**Two WSGI files:**

1. **`/home/mithesh/ipl-auction/wsgi.py`** (Your project's WSGI file)
   - Imports Flask app
   - Initializes database
   - Loads player data
   - Exports `application = app`

2. **`/var/www/mithesh_pythonanywhere_com_wsgi.py`** (PythonAnywhere's main WSGI file)
   - Sets up Python path
   - Imports from your `wsgi.py`
   - Exports `application` for PythonAnywhere server

**The connection:**
```
PythonAnywhere Server
    ↓
/var/www/mithesh_pythonanywhere_com_wsgi.py (main)
    ↓ imports from
/home/mithesh/ipl-auction/wsgi.py (your file)
    ↓ imports from
/home/mithesh/ipl-auction/app.py (Flask app)
```

---

## 🎉 Success!

Once all steps are complete, your app will be live at:
**https://mithesh.pythonanywhere.com**

You can share this URL with anyone in the world!

