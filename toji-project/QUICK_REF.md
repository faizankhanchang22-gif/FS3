# HOMELANDER BOT - DEVELOPER QUICK REFERENCE

## 🚀 Start Bot
```bash
cd /workspaces/FS3/toji-project
python homelander_bot.py
```

## 🔑 Environment Setup
```bash
# Copy template
cp .env.example .env

# Edit with your token
nano .env
# Or use VS Code:
code .env
```

**Content:**
```
BOT_TOKEN=8543073349:AAE4g6AcLSgBTEz5b3sXaBJlDIhZnQopVE0
WEBAPP_URL=http://localhost:5173
BACKEND_URL=http://localhost:8000
```

## 📋 Command Reference

### Public Commands (No Verification)
```bash
/start              Register
/login <uid>        Generate OTP (e.g., /login 12345)
/verify <otp>       Verify OTP (e.g., /verify 654321)
/help               Show commands
/stats              Statistics
```

### Protected Commands (Verification Required)
```bash
/profile            View profile ⭐
/redeem             Redeem code ⭐
```

## 🔐 Verification Flow

```
1. User → /start (registers)
2. User → /login 12345 (gets OTP)
3. Bot → "Your OTP: 654321" (valid 120s)
4. User → /verify 654321 (verifies)
5. Bot → "✅ ACCESS GRANTED"
6. User → /profile (works!)
```

## 📁 Key Files

| File | Purpose | Auto-Created |
|------|---------|---|
| `homelander_bot.py` | Main bot code | No |
| `.env` | Configuration | No (from template) |
| `users.json` | User data | Yes (on /start) |
| `verified_users.json` | Verified users | Yes (on /verify) |
| `redeems.json` | Redeem codes | Existing |

## 🐛 Debug OTP
```python
# In Python shell to test OTP:
from bot.homelander_bot import OTPManager

# Create OTP
otp = OTPManager.create_otp(user_id=123456789, uid="test_uid")
print(f"OTP: {otp}")

# Validate OTP
is_valid, msg = OTPManager.validate_otp(user_id=123456789, otp=otp)
print(f"Valid: {is_valid}, Message: {msg}")
```

## ⚠️ Common Issues

| Issue | Solution |
|-------|----------|
| Bot won't start | Check BOT_TOKEN in .env |
| "No OTP found" | User must /login first |
| "OTP expired" | 2 minute limit, send /login again |
| "Too many attempts" | 3 tries per OTP, user blocked |
| Verification not persistent | Check verified_users.json exists |

## 📊 File Sizes
```
homelander_bot.py      ~15 KB
users.json            ~Variable (10 KB+)
verified_users.json   ~1-2 KB per verified user
redeems.json          ~Variable
```

## 🔍 Monitoring

### Check Verified Users
```bash
cat verified_users.json | jq .
```

### Check User Data
```bash
cat users.json | jq '."123456789"'
```

### Check OTP Activity (in-memory only)
```python
# Start bot, then in another terminal:
python -c "from bot.homelander_bot import OTP_STORE; print(OTP_STORE)"
```

## 🧪 Test Sequence
```bash
# Terminal 1: Start bot
python homelander_bot.py

# Terminal 2 (Telegram or test script):
/start
/login 12345
# Bot responds with OTP, e.g., 654321
/verify 654321
# Should see: "✅ ACCESS GRANTED"

# Try protected command
/profile
# Should work now!

# Try again without verification (new user):
# /profile should fail until verified
```

## 🚀 Production Checklist
- [ ] .env file created
- [ ] BOT_TOKEN is correct
- [ ] .env added to .gitignore
- [ ] homelander_bot.py is executable
- [ ] python-telegram-bot installed
- [ ] Test /login → /verify flow works
- [ ] Test /profile access control works
- [ ] Verified users persist after restart
- [ ] No .env in git repo
- [ ] Old toji_bot.py archived/deleted

## 📞 Support
- Check HOMELANDER_UPGRADE.md for full docs
- Check MIGRATION.md for detailed guide
- Check EXACT_CHANGES.md for file diffs

## 🎯 Next Steps
1. Create .env from template
2. Add BOT_TOKEN
3. Run `python homelander_bot.py`
4. Test in Telegram: /start → /login → /verify → /profile
5. Deploy to production

**Version:** 2.0 (Secure OTP)  
**Status:** ✅ Ready  
**Last Updated:** 2026-05-02
