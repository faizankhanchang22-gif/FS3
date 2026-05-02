#!/usr/bin/env python3
"""
<<<<<<< HEAD
Homelander Telegram Bot - Premium Checker Platform
Bot owner: 8606381959
=======
HOMELANDER Telegram Bot - The Boys Themed
>>>>>>> 4e2cf51 (homelander otp security update)
"""

import asyncio
import json
import secrets
import hashlib
import uuid
from datetime import datetime, timedelta
from typing import Dict, Optional
import sys
import io

# Fix Windows console encoding
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo, BotCommand
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, filters, MessageHandler, CallbackContext
from telegram.constants import ParseMode, ChatAction

# ============== CONFIGURATION ==============

<<<<<<< HEAD
# Bot Configuration
BOT_TOKEN = "8627502122:AAGUonCxXmMuep2J7GHDUAOxO-RCazNpMi8"
OWNER_ID = 8606381959
WEBAPP_URL = "http://localhost:5173"  # Local development URL
SESSION_DURATION = 30 * 60  # Legacy duration; session flow is disabled
=======
BOT_TOKEN = "8543073349:AAE4g6AcLSgBTEz5b3sXaBJlDIhZnQopVE0"
OWNER_ID = 8606381959
WEBAPP_URL = "http://localhost:5173"  # Or your actual URL
BACKEND_URL = "http://localhost:8000"
>>>>>>> 4e2cf51 (homelander otp security update)

# Theme
THEME = {
    "name": "HOMELANDER",
    "emoji": "🔴",
    "tagline": "The absolute power",
    "color": "#DC143C"
}

# Data files
import os
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.dirname(SCRIPT_DIR)
USERS_FILE = os.path.join(DATA_DIR, "users.json")
<<<<<<< HEAD
SESSIONS_FILE = os.path.join(DATA_DIR, "sessions.json")
REDEEM_CODES_FILE = os.path.join(DATA_DIR, "redeem_codes.json")
VERIFIED_USERS_FILE = os.path.join(DATA_DIR, "verified_users.json")

# Path logs disabled to prevent encoding errors on Windows
# print(f"Data directory: {DATA_DIR}")
# print(f"Users file: {USERS_FILE}")
# print(f"Sessions file: {SESSIONS_FILE}")
=======
REDEEMS_FILE = os.path.join(DATA_DIR, "redeems.json")
>>>>>>> 4e2cf51 (homelander otp security update)

# ============== DATA MANAGER ==============

class DataManager:
    @staticmethod
    def load_json(filepath: str) -> Dict:
        try:
            with open(filepath, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
    
    @staticmethod
    def save_json(filepath: str, data: Dict):
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
    
    @staticmethod
    def get_user(user_id: int) -> Optional[Dict]:
        users = DataManager.load_json(USERS_FILE)
        return users.get(str(user_id))
    
    @staticmethod
    def save_user(user_id: int, user_data: Dict):
        users = DataManager.load_json(USERS_FILE)
        users[str(user_id)] = user_data
        DataManager.save_json(USERS_FILE, users)
    
    @staticmethod
<<<<<<< HEAD
    def load_redeem_codes() -> Dict:
        try:
            with open(REDEEM_CODES_FILE, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
    
    @staticmethod
    def save_redeem_codes(codes: Dict):
        with open(REDEEM_CODES_FILE, 'w') as f:
            json.dump(codes, f, indent=2)

    @staticmethod
    def load_verified_users() -> Dict:
        try:
            with open(VERIFIED_USERS_FILE, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    @staticmethod
    def save_verified_users(verified_users: Dict):
        with open(VERIFIED_USERS_FILE, 'w') as f:
            json.dump(verified_users, f, indent=2)

    @staticmethod
    def is_user_verified(user_id: int) -> bool:
        verified = DataManager.load_verified_users()
        return bool(verified.get(str(user_id), False))

    @staticmethod
    def mark_user_verified(user_id: int):
        verified = DataManager.load_verified_users()
        verified[str(user_id)] = True
        DataManager.save_verified_users(verified)

    @staticmethod
    def generate_session_token(user_id: int = 0, username: str = "") -> str:
        """Generate a session token - now uses JWT-like format"""
        return create_session_token(user_id, username)
    
    @staticmethod
    def is_session_valid(session_token: str) -> bool:
        sessions = DataManager.load_sessions()
        if session_token not in sessions:
            return False
        session = sessions[session_token]
        expiry = datetime.fromisoformat(session['expires_at'])
        return datetime.now() < expiry
=======
    def get_all_users() -> Dict:
        return DataManager.load_json(USERS_FILE)
>>>>>>> 4e2cf51 (homelander otp security update)

# ============== COMMAND HANDLERS ==============

<<<<<<< HEAD
# OTP and verification persistence
class OTPManager:
    """Manage per-user OTP generation, expiry, and attempt limits."""
    OTPS: Dict[int, Dict] = {}
    MAX_ATTEMPTS = 3
    EXPIRY_SECONDS = 120

    @classmethod
    def generate_otp(cls, user_id: int, uid: str) -> str:
        otp = f"{secrets.randbelow(1000000):06d}"
        expires_at = datetime.now() + timedelta(seconds=cls.EXPIRY_SECONDS)
        cls.OTPS[user_id] = {
            "otp": otp,
            "expires_at": expires_at,
            "attempts": 0,
            "uid": uid
        }
        return otp

    @classmethod
    def get_entry(cls, user_id: int) -> Optional[Dict]:
        entry = cls.OTPS.get(user_id)
        if not entry:
            return None
        if datetime.now() > entry["expires_at"]:
            cls.delete_otp(user_id)
            return None
        return entry

    @classmethod
    def verify_otp(cls, user_id: int, otp: str) -> bool:
        entry = cls.get_entry(user_id)
        if not entry:
            return False

        if entry["otp"] != otp:
            entry["attempts"] += 1
            if entry["attempts"] >= cls.MAX_ATTEMPTS:
                cls.delete_otp(user_id)
            else:
                cls.OTPS[user_id] = entry
            return False

        cls.delete_otp(user_id)
        return True

    @classmethod
    def delete_otp(cls, user_id: int):
        cls.OTPS.pop(user_id, None)


# Initialize data files
for file, default_value in [
    (USERS_FILE, {}),
    (SESSIONS_FILE, {}),
    (REDEEM_CODES_FILE, {
        "HOMELANDER-TRIAL": {
            "status": "available",
            "value": 5,
            "used_by": None,
            "used_at": None
        }
    }),
    (VERIFIED_USERS_FILE, {})
]:
    try:
        with open(file, 'r') as f:
            pass
    except FileNotFoundError:
        with open(file, 'w') as f:
            json.dump(default_value, f, indent=2)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
=======
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Start command - Register user"""
>>>>>>> 4e2cf51 (homelander otp security update)
    user = update.effective_user
    
<<<<<<< HEAD
    # Check if user is registered
    if str(user.id) not in users:
        # Show registration message
        welcome_text = f"""
🌟 <b>Welcome to Homelander Checker Platform!</b> 🌟
=======
    existing = DataManager.get_user(user.id)
    
    if existing:
        token = existing.get("token")
        message = f"""
{THEME['emoji']} <b>Welcome back, {user.first_name}!</b> {THEME['emoji']}
>>>>>>> 4e2cf51 (homelander otp security update)

You're already registered. Use the button below to access <b>HOMELANDER</b>.

<b>Your Token:</b> <code>{token}</code>

<<<<<<< HEAD
Register now to use the Homelander web and Telegram checker.

📌 <b>Features:</b>
• Single plan: $5/week
• CC & account checkers
• SK key validation
• PayPal, Stripe, Shopify tools
• Telegram channel alerts

<i>🔒 Premium • ⚡ Fast • 🎯 The Boys style</i>
=======
<b>Status:</b> {"✅ PREMIUM" if existing.get("premium") else "❌ FREE (Redeem a code)"}
>>>>>>> 4e2cf51 (homelander otp security update)
"""
    else:
<<<<<<< HEAD
        # User is registered, show web and redeem options
        user_data = users[str(user.id)]
        welcome_back = f"""
🎉 <b>Welcome back to Homelander, {user.first_name}!</b> 🎉

✅ <b>You are registered!</b>
📅 <b>Registered:</b> {user_data.get('registered_at', 'N/A')}

Single plan: <b>$5 / week</b>
Use the web app or redeem a code below.
"""
        keyboard = [
            [InlineKeyboardButton("🌐 OPEN WEB APP", callback_data="create_session")],
            [InlineKeyboardButton("🧾 REDEEM CODE", callback_data="redeem_help")],
            [InlineKeyboardButton("📊 MY STATS", callback_data="my_stats")],
            [InlineKeyboardButton("💬 SUPPORT", url="https://t.me/homelanderhits")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
=======
        # Create new user
        token = f"{user.id}_{hashlib.sha256(str(uuid.uuid4()).encode()).hexdigest()[:16]}"
>>>>>>> 4e2cf51 (homelander otp security update)
        
        new_user = {
            "user_id": user.id,
            "username": user.username or "NoUsername",
            "first_name": user.first_name or "User",
            "last_name": user.last_name or "",
            "token": token,
            "registered_at": datetime.utcnow().isoformat(),
            "premium": False,
            "premium_expires_at": None,
            "total_checks": 0,
            "total_hits": 0,
            "redeemed_codes": []
        }
        
        DataManager.save_user(user.id, new_user)
        
        message = f"""
{THEME['emoji']} <b>WELCOME TO HOMELANDER</b> {THEME['emoji']}

{THEME['tagline']}

<b>Registration Complete!</b>

<<<<<<< HEAD
🎊 <b>Welcome to Homelander, {user.first_name}!</b>
=======
Your token has been generated. Use the button below to access the <b>Web Platform</b> or redeem a code to activate premium.
>>>>>>> 4e2cf51 (homelander otp security update)

<b>Token:</b> <code>{token}</code>

<<<<<<< HEAD
🚀 <b>Next Step:</b> Open the Homelander WebApp or redeem a code.

💰 <b>Single Plan:</b> $5 / week
"""
    keyboard = [
        [InlineKeyboardButton("🌐 OPEN WEB APP", callback_data="create_session")],
        [InlineKeyboardButton("🧾 REDEEM CODE", callback_data="redeem_help")],
        [InlineKeyboardButton("🔙 Back to Start", callback_data="start_again")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
=======
<b>Commands:</b>
/redeem - Redeem a premium code
/profile - View your profile
/help - Show help
"""
>>>>>>> 4e2cf51 (homelander otp security update)
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🌐 Open Web App", web_app=WebAppInfo(url=WEBAPP_URL))],
        [InlineKeyboardButton("📋 Pricing", callback_data="pricing")],
    ])
    
    await update.message.reply_text(message, parse_mode=ParseMode.HTML, reply_markup=keyboard)

<<<<<<< HEAD

async def create_session_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle opening the web app"""
    query = update.callback_query
    await query.answer()
    
    user = update.effective_user
    users = DataManager.load_users()
    
    if str(user.id) not in users:
        await query.edit_message_text(
            "⚠️ Please register first! Use /start",
            parse_mode=ParseMode.HTML
        )
        return

    webapp_url = WEBAPP_URL
    
    session_text = f"""
🌐 <b>Homelander WebApp is ready!</b> 🌐

Visit the link below to open the checker dashboard.

📱 <b>WebApp URL:</b>
<code>{webapp_url}</code>

💰 <b>Single Plan:</b> $5 / week

🧾 To redeem a code, send /redeem CODE
"""
    keyboard = [
        [InlineKeyboardButton("🌐 OPEN WEB APP", url=webapp_url)],
        [InlineKeyboardButton("🧾 REDEEM CODE", callback_data="redeem_help")],
        [InlineKeyboardButton("📊 MY STATS", callback_data="my_stats")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        session_text,
        parse_mode=ParseMode.HTML,
        reply_markup=reply_markup
    )


async def redeem_help_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "To redeem a Homelander access code, use /redeem CODE. Example: /redeem HOMELANDER-TRIAL",
        parse_mode=ParseMode.HTML
    )


async def my_stats_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show user stats"""
    query = update.callback_query
    await query.answer()
    
    user = update.effective_user
    if not DataManager.is_user_verified(user.id):
        await query.edit_message_text(
            "⚠️ Please verify using /login",
            parse_mode=ParseMode.HTML
        )
        return

    users = DataManager.load_users()
    
    if str(user.id) not in users:
        await query.edit_message_text(
            "⚠️ Please register first! Use /start",
            parse_mode=ParseMode.HTML
        )
        return
    
    user_data = users[str(user.id)]
    
    stats_text = f"""
📊 <b>Your Homelander Statistics</b> 📊
=======
async def profile(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show user profile"""
    user_id = update.effective_user.id
    user = DataManager.get_user(user_id)
    
    if not user:
        await update.message.reply_text(f"{THEME['emoji']} Use /start to register first!")
        return
    
    premium_text = f"✅ Until {user.get('premium_expires_at', 'N/A')}" if user.get('premium') else "❌ Redeem a code"
    
    profile_msg = f"""
{THEME['emoji']} <b>YOUR PROFILE</b> {THEME['emoji']}

<b>Username:</b> @{user.get('username')}
<b>User ID:</b> <code>{user.get('user_id')}</code>

<b>Premium Status:</b> {premium_text}
<b>Total Checks:</b> {user.get('total_checks', 0)}
<b>Total Hits:</b> {user.get('total_hits', 0)}

<b>Token:</b> <code>{user.get('token')}</code>

<b>Registered:</b> {user.get('registered_at')}
"""
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔑 Redeem Code", callback_data="redeem")],
        [InlineKeyboardButton("🌐 Web App", web_app=WebAppInfo(url=WEBAPP_URL))],
    ])
    
    await update.message.reply_text(profile_msg, parse_mode=ParseMode.HTML, reply_markup=keyboard)

async def redeem(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Redeem code command"""
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔑 Enter Code", callback_data="redeem_enter")],
        [InlineKeyboardButton("🌐 Purchase", url="https://t.me/homelander")],
    ])
    
    msg = f"""
{THEME['emoji']} <b>REDEEM CODE</b> {THEME['emoji']}
>>>>>>> 4e2cf51 (homelander otp security update)

Enter your premium code to activate <b>HOMELANDER PREMIUM</b>.

<b>$5 / Week</b>
✅ All Checkers Unlimited
✅ Hit Notifications
✅ Premium Support
"""
<<<<<<< HEAD
    keyboard = [
        [InlineKeyboardButton("🌐 OPEN WEB APP", callback_data="create_session")],
        [InlineKeyboardButton("🔙 Back", callback_data="start_again")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        stats_text,
        parse_mode=ParseMode.HTML,
        reply_markup=reply_markup
    )
=======
    await update.message.reply_text(msg, parse_mode=ParseMode.HTML, reply_markup=keyboard)
>>>>>>> 4e2cf51 (homelander otp security update)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Help command"""
    help_text = f"""
<<<<<<< HEAD
📖 <b>Homelander Bot Commands</b> 📖

/start - Start the bot / View main menu
/help - Show this help message
/login UID - Request a verification code
/verify OTP - Verify your login code
/redeem CODE - Redeem your access code
/status - Show your plan status
/stats - View your statistics

🔹 <b>How to use:</b>
1. Send /start to register
2. Use /login <UID> to receive a secure OTP
3. Verify with /verify <OTP>
4. Open the Homelander WebApp
5. Start checking
6. Get hit alerts in @homelanderhits

🔹 <b>Single Plan:</b> $5 / week

🔹 <b>Need Help?</b>
Contact: @homelanderhits
"""
    await update.message.reply_text(help_text, parse_mode=ParseMode.HTML)


async def login_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start OTP login with /login <UID>"""
    user = update.effective_user
    args = context.args

    if not args:
        await update.message.reply_text(
            "Usage: /login <UID>\nExample: /login HOMELANDER123",
            parse_mode=ParseMode.HTML
        )
        return

    uid = args[0].strip()
    if not uid:
        await update.message.reply_text(
            "Please provide a valid UID.",
            parse_mode=ParseMode.HTML
        )
        return

    otp_code = OTPManager.generate_otp(user.id, uid)
    await update.message.reply_text(
        f"🔐 Your Homelander verification code is: <code>{otp_code}</code>\n\nThis code expires in 2 minutes. Use /verify <OTP> to complete verification.",
        parse_mode=ParseMode.HTML
    )


async def verify_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Verify the OTP with /verify <OTP>"""
    user = update.effective_user
    args = context.args

    if not args:
        await update.message.reply_text(
            "Usage: /verify <OTP>",
            parse_mode=ParseMode.HTML
        )
        return

    otp = args[0].strip()
    if not otp:
        await update.message.reply_text(
            "Please provide the OTP you received.",
            parse_mode=ParseMode.HTML
        )
        return

    entry = OTPManager.get_entry(user.id)
    if not entry:
        await update.message.reply_text(
            "❌ Invalid OTP.",
            parse_mode=ParseMode.HTML
        )
        return

    if OTPManager.verify_otp(user.id, otp):
        DataManager.mark_user_verified(user.id)
        await update.message.reply_text(
            "✅ Verified successfully",
            parse_mode=ParseMode.HTML
        )
    else:
        attempts_left = OTPManager.MAX_ATTEMPTS - (entry.get("attempts", 0) if entry else 0)
        if attempts_left <= 0:
            await update.message.reply_text(
                "❌ Invalid OTP. Maximum attempts reached. Request a new code with /login <UID>",
                parse_mode=ParseMode.HTML
            )
        else:
            await update.message.reply_text(
                "❌ Invalid OTP",
                parse_mode=ParseMode.HTML
            )


async def redeem_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Redeem a Homelander code"""
    user = update.effective_user
    if not DataManager.is_user_verified(user.id):
        await update.message.reply_text(
            "⚠️ Please verify using /login",
            parse_mode=ParseMode.HTML
        )
        return
    user = update.effective_user
    users = DataManager.load_users()

    if str(user.id) not in users:
        await update.message.reply_text(
            "⚠️ You are not registered yet. Send /start to register.",
            parse_mode=ParseMode.HTML
        )
        return

    args = context.args
    if not args:
        await update.message.reply_text(
            "Please send a code with /redeem CODE",
            parse_mode=ParseMode.HTML
        )
        return

    code = args[0].strip().upper()
    redeem_codes = DataManager.load_redeem_codes()
    entry = redeem_codes.get(code)

    if not entry or entry.get("status") != "available":
        await update.message.reply_text(
            "❌ Invalid or already used code.",
            parse_mode=ParseMode.HTML
        )
        return

    entry["status"] = "used"
    entry["used_by"] = str(user.id)
    entry["used_at"] = datetime.now().isoformat()
    redeem_codes[code] = entry
    DataManager.save_redeem_codes(redeem_codes)

    user_data = users[str(user.id)]
    user_data["premium"] = True
    user_data["premium_expires_at"] = (datetime.now() + timedelta(days=7)).isoformat()
    users[str(user.id)] = user_data
    DataManager.save_users(users)

    await update.message.reply_text(
        f"✅ Code redeemed successfully! Homelander premium is active for 7 days.\nCode: {code}",
        parse_mode=ParseMode.HTML
    )


async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Check plan status"""
    user = update.effective_user
    if not DataManager.is_user_verified(user.id):
        await update.message.reply_text(
            "⚠️ Please verify using /login",
            parse_mode=ParseMode.HTML
        )
        return

    users = DataManager.load_users()
    
    if str(user.id) not in users:
        await update.message.reply_text(
            "⚠️ You are not registered yet. Send /start to register.",
            parse_mode=ParseMode.HTML
        )
        return

    user_data = users[str(user.id)]
    expires_at = user_data.get("premium_expires_at")
    premium_active = user_data.get("premium", False)

    status_text = f"""
📌 <b>Homelander Plan Status</b> 📌

👤 <b>User:</b> {user.first_name}
🆔 <b>ID:</b> <code>{user.id}</code>

💰 <b>Plan:</b> $5 / week
• <b>Premium Active:</b> {'✅ Yes' if premium_active else '❌ No'}
"""
    if expires_at:
        status_text += f"\n• <b>Expires:</b> {expires_at}"

    status_text += f"\n\n🌐 Open the Homelander WebApp: <code>{WEBAPP_URL}</code>"

    await update.message.reply_text(status_text, parse_mode=ParseMode.HTML)


async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show stats command"""
    user = update.effective_user
    if not DataManager.is_user_verified(user.id):
        await update.message.reply_text(
            "⚠️ Please verify using /login",
            parse_mode=ParseMode.HTML
        )
        return

    users = DataManager.load_users()
=======
{THEME['emoji']} <b>HOMELANDER COMMANDS</b> {THEME['emoji']}

/start - Register & get started
/profile - View your profile
/redeem - Redeem a premium code
/stats - View statistics
/help - Show this message

<b>Web App Features:</b>
✅ CC Checkers
✅ PayPal/Stripe Auth
✅ Shopify Checkers
✅ Hit Dashboard
✅ Leaderboard

<b>Support:</b>
@homelander_support
"""
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🌐 Web App", web_app=WebAppInfo(url=WEBAPP_URL))],
        [InlineKeyboardButton("📞 Support", url="https://t.me/homelander_support")],
    ])
>>>>>>> 4e2cf51 (homelander otp security update)
    
    await update.message.reply_text(help_text, parse_mode=ParseMode.HTML, reply_markup=keyboard)

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show bot statistics"""
    all_users = DataManager.get_all_users()
    
    premium_count = sum(1 for u in all_users.values() if u.get("premium"))
    total_checks = sum(u.get("total_checks", 0) for u in all_users.values())
    total_hits = sum(u.get("total_hits", 0) for u in all_users.values())
    
    stats_msg = f"""
{THEME['emoji']} <b>HOMELANDER STATISTICS</b> {THEME['emoji']}

<b>Total Users:</b> {len(all_users)}
<b>Premium Users:</b> {premium_count}
<b>Total Checks:</b> {total_checks}
<b>Total Hits:</b> {total_hits}

<b>Powered By:</b> The Collective
"""
    await update.message.reply_text(stats_msg, parse_mode=ParseMode.HTML)

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle button clicks"""
    query = update.callback_query
    await query.answer()
    
    if query.data == "pricing":
        pricing_msg = f"""
{THEME['emoji']} <b>HOMELANDER PREMIUM</b> {THEME['emoji']}

<b>Price:</b> $5 / Week
<b>Duration:</b> 7 Days
<b>Auto-Renews:</b> Yes

<b>Features Included:</b>
✅ All CC Checkers Unlimited
✅ Stripe/PayPal/Shopify Auth
✅ Unlimited Cards Per Check
✅ Premium Proxy Support
✅ Real-Time Hit Notifications
✅ Priority Support

<b>How to Get:</b>
1. Contact support for redeem code
2. Use /redeem command
3. Activate instant

<b>Payment Methods:</b>
💳 Credit/Debit Card
💰 Cryptocurrency
🏦 Wire Transfer
"""
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔑 Redeem Code", callback_data="redeem_enter")],
            [InlineKeyboardButton("📞 Contact Sales", url="https://t.me/homelander_sales")],
        ])
        await query.edit_message_text(pricing_msg, parse_mode=ParseMode.HTML, reply_markup=keyboard)
    
    elif query.data == "redeem":
        redeem_msg = f"""
{THEME['emoji']} <b>REDEEM YOUR CODE</b> {THEME['emoji']}

Send your code here (without spaces):
"""
        await query.edit_message_text(redeem_msg, parse_mode=ParseMode.HTML)
        context.user_data["awaiting_code"] = True
    
    elif query.data == "redeem_enter":
        await query.edit_message_text(
            f"{THEME['emoji']} <b>Enter your redeem code:</b>\n\nSend it as a message below.",
            parse_mode=ParseMode.HTML
        )
        context.user_data["awaiting_code"] = True

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle text messages"""
    
    if context.user_data.get("awaiting_code"):
        code = update.message.text.strip().upper()
        user_id = update.effective_user.id
        user = DataManager.get_user(user_id)
        
        if not user:
            await update.message.reply_text("❌ Not registered. Use /start")
            return
        
        redeems = DataManager.load_json(REDEEMS_FILE)
        
        if code not in redeems:
            await update.message.reply_text(f"❌ Invalid code: <code>{code}</code>", parse_mode=ParseMode.HTML)
            return
        
        code_data = redeems.get(code, {})
        
        if code_data.get("used"):
            await update.message.reply_text("❌ Code already used!")
            return
        
        if code in user.get("redeemed_codes", []):
            await update.message.reply_text("❌ You already redeemed this code!")
            return
        
        # Apply premium
        expires_at = datetime.utcnow() + timedelta(days=7)
        user["premium"] = True
        user["premium_expires_at"] = expires_at.strftime("%Y-%m-%d %H:%M:%S")
        user["redeemed_codes"].append(code)
        
        code_data["used"] = True
        code_data["used_by"] = user_id
        code_data["used_at"] = datetime.utcnow().isoformat()
        
        DataManager.save_user(user_id, user)
        redeems[code] = code_data
        DataManager.save_json(REDEEMS_FILE, redeems)
        
        context.user_data["awaiting_code"] = False
        
        success_msg = f"""
{THEME['emoji']} <b>PREMIUM ACTIVATED!</b> {THEME['emoji']}

<b>✅ Success!</b>

Your HOMELANDER PREMIUM is now active!

<b>Expires:</b> {expires_at.strftime('%Y-%m-%d %H:%M:%S')}

<b>Next Steps:</b>
1. Open the Web App
2. Start checking cards
3. Receive hit notifications

<b>Code Used:</b> <code>{code}</code>
"""
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🌐 Open Web App", web_app=WebAppInfo(url=WEBAPP_URL))],
            [InlineKeyboardButton("📋 Profile", callback_data="profile")],
        ])
        
        await update.message.reply_text(success_msg, parse_mode=ParseMode.HTML, reply_markup=keyboard)
    else:
        await update.message.reply_text(
            f"{THEME['emoji']} Use /help for available commands",
            parse_mode=ParseMode.HTML
        )

# ============== ERROR HANDLER ==============

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle errors"""
    print(f"Update {update} caused error {context.error}")

# ============== MAIN ==============

def main() -> None:
    """Start the bot"""
<<<<<<< HEAD
    print("Starting Homelander Telegram Bot...")
    print(f"Bot Token: {BOT_TOKEN[:20]}...")
=======
    print(f"\n🔴 Starting HOMELANDER Telegram Bot... 🔴\n")
    print(f"Owner: {OWNER_ID}")
    print(f"Token: {BOT_TOKEN[:20]}...")
    print(f"Webapp: {WEBAPP_URL}\n")
>>>>>>> 4e2cf51 (homelander otp security update)
    
    # Create application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("profile", profile))
    application.add_handler(CommandHandler("redeem", redeem))
    application.add_handler(CommandHandler("help", help_command))
<<<<<<< HEAD
    application.add_handler(CommandHandler("login", login_command))
    application.add_handler(CommandHandler("verify", verify_command))
    application.add_handler(CommandHandler("redeem", redeem_command))
    application.add_handler(CommandHandler("status", status_command))
    application.add_handler(CommandHandler("stats", stats_command))
    
    # Callback handlers
    application.add_handler(CallbackQueryHandler(register_callback, pattern="^register$"))
    application.add_handler(CallbackQueryHandler(create_session_callback, pattern="^create_session$"))
    application.add_handler(CallbackQueryHandler(redeem_help_callback, pattern="^redeem_help$"))
    application.add_handler(CallbackQueryHandler(my_stats_callback, pattern="^my_stats$"))
    application.add_handler(CallbackQueryHandler(start_again_callback, pattern="^start_again$"))
=======
    application.add_handler(CommandHandler("stats", stats))
    
    # Callback handlers
    application.add_handler(CallbackQueryHandler(button_callback))
>>>>>>> 4e2cf51 (homelander otp security update)
    
    # Message handler for redeem codes
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Error handler
    application.add_error_handler(error_handler)
    
    # Run bot
    application.run_polling()

if __name__ == "__main__":
    main()
