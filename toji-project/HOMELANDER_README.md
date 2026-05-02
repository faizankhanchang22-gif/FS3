# 🔴 HOMELANDER - The Boys Themed Bot 🔴

**The absolute power checker platform**

---

## Features

🔴 **Token-Based Authentication** (No more sessions!)
🔴 **Redeem Code System** for premium access  
🔴 **Telegram Bot Integration** with The Boys theme
🔴 **Web Dashboard** (React + Tailwind)
🔴 **Real-Time Hit Notifications** to Telegram
🔴 **$5/Week Premium Plan** (Single tier)
🔴 **CC Checkers** - PayPal, Stripe Auth, Shopify, and more
🔴 **Leaderboard & Stats**
🔴 **Admin Panel** for code generation

---

## Quick Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Initialize Redeem Codes

```bash
python3 generate_redeems.py 50
```

This will create 50 redeem codes for premium access.

### 3. Start Backend

```bash
cd backend
python3 main.py
```

Backend runs on `http://localhost:8000`

### 4. Start Telegram Bot

```bash
cd bot
python3 toji_bot.py
```

### 5. Start Web Dashboard

```bash
cd ../app
npm run dev
```

Web app runs on `http://localhost:5173`

---

## Configuration

### Bot Token
- Current: `8543073349:AAE4g6AcLSgBTEz5b3sXaBJlDIhZnQopVE0`
- Change in: `backend/main.py` and `bot/toji_bot.py`

### Owner ID
- Current: `8606381959`
- Change in: `backend/main.py` and `bot/toji_bot.py`

### Telegram Group (Hits Channel)
- Current: `-1003700444046`
- Change in: `backend/main.py`

### Web URL
- Development: `http://localhost:5173`
- Production: Update in `bot/toji_bot.py` (WEBAPP_URL)

---

## API Endpoints

### Authentication

**Register User:**
```
POST /api/auth/register
{
  "user_id": 123456789,
  "username": "homelander_fan",
  "first_name": "John"
}
Response: { "token": "123456789_abc123...", "success": true }
```

**Redeem Code:**
```
POST /api/auth/redeem?token=TOKEN
{
  "code": "HOMELANDER-XXXX"
}
```

### Checkers

**PayPal Charge ($0.1):**
```
POST /api/checker/paypal-charge?token=TOKEN
{
  "cards": ["5555555555554444|12|25|123"],
  "use_proxy": false
}
```

**Stripe Auth:**
```
POST /api/checker/stripe-auth?token=TOKEN
{
  "cards": ["5555555555554444|12|25|123"],
  "use_proxy": false
}
```

### User Data

**Get Profile:**
```
GET /api/user/profile?token=TOKEN
```

**Get Leaderboard:**
```
GET /api/leaderboard
```

---

## Telegram Bot Commands

- `/start` - Register and get started
- `/profile` - View your profile and stats
- `/redeem` - Redeem a premium code
- `/stats` - View global statistics
- `/help` - Show all commands

---

## Hit Notifications

When a card hits or charge goes through:

**Private Message (User):**
```
🔴 YON HIT A LICK! 🔴

Check Type: PayPal Charge ($0.1)
Card: ****4444
Result: ✅ HIT - CHARGED
Amount Charged: $0.10
```

**Group Channel (Owner/Admins):**
```
🔴 HOMELANDER HIT! 🔴

User: @username (ID: 123456789)
Type: PayPal Charge ($0.1)
Card: ****4444
Status: ✅ HIT - CHARGED
Amount: $0.10

Extra Data: {...}
Timestamp: 2024-05-02 14:30:45 UTC
```

---

## Authentication Flow (No Sessions!)

1. **User registers** → Telegram sends `/start` → Bot generates token
2. **Token format:** `{user_id}_{random_hash}`
3. **Each request** includes `?token=TOKEN` query parameter
4. **Backend validates** token against users.json
5. **Premium check** → If expired, returns 403 Forbidden
6. **No token expiration** → Premium subscription expires instead

**Benefits:**
✅ Simpler than sessions
✅ Stateless API
✅ Easier error handling
✅ No session cleanup needed

---

## Redeem Code System

### For Admin

Generate 50 codes:
```bash
python3 generate_redeems.py 50
```

This creates codes like: `HOMELANDER-ABC123D456`

Code structure (redeems.json):
```json
{
  "HOMELANDER-ABC123": {
    "code": "HOMELANDER-ABC123",
    "plan": "HOMELANDER PREMIUM",
    "created_at": "2024-05-02T...",
    "used": false,
    "used_by": null,
    "used_at": null
  }
}
```

### For Users

1. Get code from admin
2. Use `/redeem` command in Telegram
3. Send code → Premium activated for 7 days
4. Each code can only be used once

---

## Pricing

- **Plan:** HOMELANDER PREMIUM
- **Price:** $5.00 / Week
- **Duration:** 7 Days
- **Auto-Renew:** No (Redeem code only)
- **Features:**
  - All CC Checkers Unlimited
  - Stripe/PayPal/Shopify Auth
  - Unlimited Cards Per Check
  - Premium Proxy Support
  - Real-Time Hit Notifications
  - Priority Support

---

## Data Files

```
toji-project/
├── users.json         # All user data + tokens
├── redeems.json       # Redeem codes inventory
├── proxies.json       # Proxy list
└── hits.json          # Hit logs (optional)
```

---

## Admin Panel

Generate stats:
```
GET /api/admin/stats?admin_token=ADMIN_TOKEN
```

Admin token format: `admin_{sha256_hash(OWNER_ID)[:16]}`

---

## Troubleshooting

### Bot not sending hits
- Check `GROUP_CHAT_ID` in `backend/main.py`
- Verify bot is admin in the group
- Check Telegram API token

### Invalid token errors
- Ensure token format: `{user_id}_{hash}`
- Check user exists in users.json
- Verify token match

### Premium expired
- User needs to redeem new code
- API returns 403 Forbidden
- User should use `/redeem` in Telegram

---

## The Boys Theme Connection

🔴 **HOMELANDER** = Red-themed super-powered bot
🔴 **Supe Strength** = Unlimited checker power
🔴 **Absolute Control** = Full platform dominance
🔴 **The Collective** = The community behind it

**Tagline:** *"The absolute power" - All checking tools in one deadly platform*

---

**Made by: The Collective**
**Status:** ❤️ SOARING HIGH 🔴
