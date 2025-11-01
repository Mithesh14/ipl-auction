# 🌐 How to Access IPL Auction System

## 🚀 Deployment Options

This application is deployed on a cloud platform for global access.

### For Local Development:

```bash
source venv/bin/activate
python app.py
```

Then access at: `http://localhost:8080`

---

## 📍 For Network Access (Same WiFi)

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

## 🔐 Login Credentials

All users are pre-registered:

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

