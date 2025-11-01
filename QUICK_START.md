# ⚡ Quick Start - Global Access in 2 Minutes

## For Users in Different Locations (US, India, etc.)

### 🎯 Fastest Method: ngrok

**1. Install ngrok** (one-time setup)
```bash
brew install ngrok/ngrok/ngrok
# Or download from: https://ngrok.com/download
```

**2. Start your server**
```bash
source venv/bin/activate
python app.py
```

**3. In a NEW terminal, start ngrok**
```bash
ngrok http 8080
```

**4. Share the URL**
ngrok will show something like:
```
Forwarding: https://abc123-def456.ngrok-free.app
```

**Share this URL with everyone!** ✅

---

## Alternative: Use the Helper Script

```bash
chmod +x start_ngrok.sh
./start_ngrok.sh
```

This starts both the server and ngrok automatically.

---

## 🔑 Login Credentials

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

---

## 📝 Notes

- **Admin:** Only `mithesh` can start auction pools
- **ngrok URL:** Changes each time you restart (free version)
- **For permanent URL:** See `DEPLOYMENT_GUIDE.md` for Railway/Render options

---

**Need help?** Check `DEPLOYMENT_GUIDE.md` for more options!

