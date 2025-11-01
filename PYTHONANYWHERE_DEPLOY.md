# 🚀 Deploy to PythonAnywhere

PythonAnywhere is perfect for Flask apps! Here's how to deploy your IPL Auction app.

---

## ✅ Prerequisites

- ✅ GitHub repository: `https://github.com/Mithesh14/ipl-auction`
- ✅ PythonAnywhere account (free tier available)
- ✅ All files are committed and pushed to GitHub

---

## 📋 Step-by-Step Deployment

### Step 1: Sign Up for PythonAnywhere

1. Go to: **https://www.pythonanywhere.com/**
2. Click **"Beginner: Sign up for free account"**
3. Create account with email/password
4. Verify email if required

---

### Step 2: Clone Your GitHub Repository

1. In PythonAnywhere, go to **"Files"** tab
2. Open **"Bash"** console
3. Run:

```bash
cd ~
git clone https://github.com/Mithesh14/ipl-auction.git
cd ipl-auction
```

**Note:** If repository is private, you'll need to:
- Use SSH key, or
- Use Personal Access Token in URL: `https://YOUR_TOKEN@github.com/Mithesh14/ipl-auction.git`

---

### Step 3: Install Dependencies

In the Bash console:

```bash
cd ~/ipl-auction
pip3.10 install --user -r requirements.txt
```

**Note:** PythonAnywhere uses Python 3.10 by default. Adjust if needed.

---

### Step 4: Set Up Database

The database will be auto-created on first run. But let's initialize it:

```bash
cd ~/ipl-auction
python3.10 populate_users.py
```

This creates the database and adds all users.

---

### Step 5: Configure WSGI File

1. Go to **"Web"** tab in PythonAnywhere dashboard
2. Click **"Add a new web app"**
3. Select **"Flask"**
4. Choose **Python 3.10**
5. For **"Path to your WSGI file"**, enter:
   ```
   /home/YOUR_USERNAME/ipl-auction/wsgi.py
   ```
   (Replace `YOUR_USERNAME` with your PythonAnywhere username)

---

### Step 6: Configure Static Files

In the **"Web"** tab, scroll to **"Static files"** section:

1. **URL:** `/static/`
   **Directory:** `/home/YOUR_USERNAME/ipl-auction/static/`

2. Click **"Add"**

---

### Step 7: Set Environment Variables (if needed)

In the **"Web"** tab, find **"Code"** section:

- **Source code:** `/home/YOUR_USERNAME/ipl-auction`
- **Working directory:** `/home/YOUR_USERNAME/ipl-auction`

In **"WSGI configuration file"**, you can add environment variables if needed:

```python
import os
os.environ['SECRET_KEY'] = 'your-secret-key-here'
```

---

### Step 8: Reload Web App

1. Go to **"Web"** tab
2. Click **"Reload"** button (green button)
3. Your app will be live at: `https://YOUR_USERNAME.pythonanywhere.com`

---

## 🔧 Important Notes

### WebSocket Support

- **Free tier:** WebSocket support may be limited
- **Solution:** Flask-SocketIO automatically falls back to polling
- Your app will work, but real-time updates may use HTTP polling instead of WebSocket

### Database Location

- Database file: `~/ipl-auction/auction.db`
- This persists across app reloads
- **Backup regularly!**

### File Paths

- Make sure all paths in `app.py` use relative paths
- Excel file: Should be uploaded to `~/ipl-auction/AUCTION.xlsx`
- Database: Auto-creates at `~/ipl-auction/auction.db`

### Logs

- **Error logs:** Check "Web" tab → "Error log"
- **Server log:** Check "Web" tab → "Server log"

---

## 🎯 Quick Checklist

- [ ] Clone repository from GitHub
- [ ] Install dependencies (`pip3.10 install --user -r requirements.txt`)
- [ ] Run `populate_users.py` to initialize database
- [ ] Create Flask web app in PythonAnywhere dashboard
- [ ] Set WSGI file path to `wsgi.py`
- [ ] Configure static files directory
- [ ] Upload `AUCTION.xlsx` to `~/ipl-auction/` (if needed)
- [ ] Reload web app
- [ ] Test at `https://YOUR_USERNAME.pythonanywhere.com`

---

## 🐛 Troubleshooting

### Error: "No module named 'flask'"
**Solution:** Run `pip3.10 install --user -r requirements.txt`

### Error: "Database locked"
**Solution:** Make sure only one instance is accessing the database. Check for multiple web apps pointing to same database.

### WebSocket not working
**Solution:** This is normal on free tier. Flask-SocketIO will use polling fallback automatically.

### 404 Not Found
**Solution:** 
- Check WSGI file path is correct
- Verify source code directory is correct
- Check error logs in "Web" tab

### Static files not loading
**Solution:** 
- Verify static files mapping in "Web" tab
- Check path: `/home/YOUR_USERNAME/ipl-auction/static/`

---

## 🔄 Updating Your App

When you push updates to GitHub:

```bash
cd ~/ipl-auction
git pull origin main
```

Then **Reload** your web app in PythonAnywhere dashboard.

---

## 📞 Support

- PythonAnywhere help: https://help.pythonanywhere.com/
- Your app URL: `https://YOUR_USERNAME.pythonanywhere.com`

---

## ✅ Your Repository is Ready!

All required files are already in your GitHub repo:
- ✅ `wsgi.py` (WSGI entry point)
- ✅ `requirements.txt` (dependencies)
- ✅ `app.py` (Flask application)
- ✅ `populate_users.py` (database setup)
- ✅ Static files and templates

Just follow the steps above!

