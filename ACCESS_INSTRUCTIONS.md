# 🌐 How to Access IPL Auction System - Global Access Guide

## 🚀 Quick Start (2 Minutes) - RECOMMENDED

### Use ngrok for Instant Global Access

**Step 1: Install ngrok**
```bash
# macOS (if you have Homebrew)
brew install ngrok/ngrok/ngrok

# Or download from: https://ngrok.com/download
```

**Step 2: Start Server + ngrok**
```bash
# Option A: Use the automated script
./start_ngrok.sh

# Option B: Manual (two terminals)
# Terminal 1:
source venv/bin/activate
python app.py

# Terminal 2:
ngrok http 8080
```

**Step 3: Share the URL**
ngrok will show you a URL like:
```
Forwarding: https://abc123.ngrok-free.app -> http://localhost:8080
```

**Share this HTTPS URL** with everyone, anywhere in the world!

---

## 🌍 For Users in Different Locations (US, etc.)

Since users are in different locations, you need a **public URL**. Here are the best FREE options:

### Option 1: ngrok ⭐ (Easiest - 2 minutes)
- ✅ Free forever
- ✅ HTTPS included
- ✅ Works globally
- ⚠️ URL changes each restart
- **Setup:** `ngrok http 8080`

### Option 2: Cloudflare Tunnel (Free)
- ✅ Free forever
- ✅ HTTPS included
- **Setup:** `cloudflared tunnel --url http://localhost:8080`

### Option 3: Railway.app (Permanent URL)
- ✅ Free tier
- ✅ Permanent URL
- ✅ Cloud-hosted (your computer can sleep)
- ⚠️ Requires GitHub account

**📄 See `DEPLOYMENT_GUIDE.md` for detailed instructions on all options!**

---

## 📍 For Local Network (Same WiFi Only)

If everyone is on the same WiFi:

### Step 1: Find Your Computer's IP Address

The server will display your IP address when it starts. Look for:
```
Network:  http://XXX.XXX.XXX.XXX:8080
```

### Step 2: Share the URL
Give other users this URL:
```
http://YOUR_IP_ADDRESS:8080
```

For example:
```
http://192.168.1.100:8080
```

### Step 3: Firewall Settings
If others can't connect, you may need to allow port 8080 in firewall:

**macOS:**
1. System Settings → Network → Firewall → Firewall Options
2. Click "+" to add an application
3. Allow Python or add port 8080

## Login Credentials

All users are pre-registered. Use these credentials:

| Username | Password |
|----------|----------|
| mithesh   | mithesh  |
| susan     | susan    |
| minigv    | minigv   |
| suku      | suku     |
| hemanth   | hemanth  |
| thillu    | thillu   |
| ruben     | ruben    |
| keerthi   | keerthi  |
| aki       | aki      |

## Quick Start

1. **Admin (mithesh):** Login and select a player pool to start auction
2. **Other Users:** Login and wait for admin to start auction
3. Once started, all users can bid in real-time
4. Admin can sell players to highest bidder

## Troubleshooting

**Can't connect from other devices?**
- Check firewall settings
- Ensure all devices on same WiFi
- Verify server is running and shows network IP
- Try `http://localhost:8080` on server computer first

**Port already in use?**
- Change port in `app.py` (line with `PORT = 8080`)
- Update URL accordingly

