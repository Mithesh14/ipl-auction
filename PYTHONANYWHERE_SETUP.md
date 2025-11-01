# 🔧 PythonAnywhere Setup - Next Steps

You're seeing "Hello from Flask!" which means PythonAnywhere is working, but you need to configure it for the IPL Auction app.

---

## ✅ Current Status
- ✅ PythonAnywhere account: Working
- ✅ Flask deployment: Working  
- ⚠️ Need to: Configure for IPL Auction app

---

## 📋 Setup Steps

### Step 1: Update WSGI File

In your PythonAnywhere dashboard, edit `/var/www/mithesh_pythonanywhere_com_wsgi.py`:

**Replace the entire file with:**

```python
# WSGI entry point for PythonAnywhere
import sys
import os

# Add the project directory to the path
project_home = '/home/mithesh/ipl-auction'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Change to project directory
os.chdir(project_home)

# Import the Flask app
from wsgi import application

# Note: WebSocket support may be limited on PythonAnywhere free tier
# SocketIO polling fallback should work automatically
```

**OR** if PythonAnywhere auto-generated file uses different format:

```python
import sys
import os

project_home = '/home/mithesh/ipl-auction'
if project_home not in sys.path:
    sys.path = [project_home] + sys.path

os.chdir(project_home)

from wsgi import app as application  # noqa
```

---

### Step 2: Verify Files Are Cloned

1. Go to **Files** tab in PythonAnywhere
2. Navigate to `/home/mithesh/ipl-auction`
3. Verify these files exist:
   - ✅ `app.py`
   - ✅ `wsgi.py`
   - ✅ `requirements.txt`
   - ✅ `AUCTION.xlsx`
   - ✅ `templates/` folder
   - ✅ `static/` folder

**If files are missing**, clone the repo:

```bash
cd ~
git clone https://github.com/Mithesh14/ipl-auction.git
cd ipl-auction
```

---

### Step 3: Install Dependencies

Open **Bash** console and run:

```bash
cd ~/ipl-auction
pip3.10 install --user -r requirements.txt
```

This installs all required packages (Flask, SocketIO, pandas, etc.)

---

### Step 4: Initialize Database

In **Bash** console:

```bash
cd ~/ipl-auction
python3.10 populate_users.py
```

This creates the database and adds all 9 users.

---

### Step 5: Configure Static Files

1. Go to **Web** tab
2. Scroll to **Static files** section
3. Add static file mapping:
   - **URL:** `/static/`
   - **Directory:** `/home/mithesh/ipl-auction/static/`
4. Click **Add**

---

### Step 6: Initialize App Data

The app needs to load player data on first run. In **Bash** console:

```bash
cd ~/ipl-auction
python3.10 -c "from app import init_db, load_raw_data; init_db(); load_raw_data(); print('✅ Data loaded!')"
```

---

### Step 7: Reload Web App

1. Go to **Web** tab
2. Click green **Reload** button
3. Wait 10-20 seconds
4. Visit: `https://mithesh.pythonanywhere.com`

---

## 🎯 Expected Result

After setup, visiting `https://mithesh.pythonanywhere.com` should show:
- ✅ Login page (not "Hello from Flask!")
- ✅ You can log in with credentials
- ✅ Auction interface appears after login

---

## 🐛 Troubleshooting

### Still seeing "Hello from Flask!"?

**Problem:** WSGI file pointing to wrong project
**Solution:** Update WSGI file path to `/home/mithesh/ipl-auction/wsgi.py`

### "ModuleNotFoundError: No module named 'flask'"

**Problem:** Dependencies not installed
**Solution:** Run `pip3.10 install --user -r requirements.txt`

### "No such file or directory: 'AUCTION.xlsx'"

**Problem:** Excel file not in project directory
**Solution:** Upload `AUCTION.xlsx` to `/home/mithesh/ipl-auction/`

### Database errors

**Problem:** Database not initialized
**Solution:** Run `python3.10 populate_users.py`

### Static files not loading (CSS/JS broken)

**Problem:** Static files not configured
**Solution:** Add static file mapping in Web tab:
- URL: `/static/`
- Directory: `/home/mithesh/ipl-auction/static/`

---

## 📝 Quick Checklist

- [ ] WSGI file updated to point to `/home/mithesh/ipl-auction/wsgi.py`
- [ ] Files cloned from GitHub to `/home/mithesh/ipl-auction/`
- [ ] Dependencies installed (`pip3.10 install --user -r requirements.txt`)
- [ ] Database initialized (`python3.10 populate_users.py`)
- [ ] Static files configured in Web tab
- [ ] App data loaded (player data)
- [ ] Web app reloaded
- [ ] Test at `https://mithesh.pythonanywhere.com`

---

## ✅ Success!

Once configured, your IPL Auction app will be live at:
**https://mithesh.pythonanywhere.com**

Login credentials:
- Username: `mithesh` (admin)
- Password: `mithesh`
- (Same for other users: susan/susan, etc.)

