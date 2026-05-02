#!/usr/bin/env python3
"""
Homelander Telegram Bot - Premium Checker Platform
Bot owner: 8606381959
"""

import asyncio
import json
import secrets
import time
import base64
from datetime import datetime, timedelta
from typing import Dict, Optional
import sys
import io

# Fix Windows console encoding issues
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from telegram.constants import ParseMode

# JWT-like token functions
def create_session_token(user_id: int, username: str) -> str:
    """Create a JWT-like session token that frontend can validate"""
    expires_at = datetime.now() + timedelta(seconds=SESSION_DURATION)
    
    # Create payload
    payload = {
        "user_id": user_id,
        "username": username,
        "created_at": datetime.now().isoformat(),
        "expires_at": expires_at.isoformat(),
        "active": True
    }
    
    # Encode as base64 (simple JWT-like format)
    header = base64.urlsafe_b64encode(json.dumps({"typ": "JWT", "alg": "none"}).encode()).decode().rstrip('=')
    payload_b64 = base64.urlsafe_b64encode(json.dumps(payload).encode()).decode().rstrip('=')
    signature = base64.urlsafe_b64encode(secrets.token_bytes(32)).decode().rstrip('=')
    
    return f"{header}.{payload_b64}.{signature}"

# Bot Configuration
BOT_TOKEN = "8627502122:AAGUonCxXmMuep2J7GHDUAOxO-RCazNpMi8"
OWNER_ID = 8606381959
WEBAPP_URL = "http://localhost:5173"  # Local development URL
SESSION_DURATION = 30 * 60  # Legacy duration; session flow is disabled

# Data Storage - Use absolute path to shared directory
import os
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.dirname(SCRIPT_DIR)  # Parent directory (toji-project)
USERS_FILE = os.path.join(DATA_DIR, "users.json")
SESSIONS_FILE = os.path.join(DATA_DIR, "sessions.json")
REDEEM_CODES_FILE = os.path.join(DATA_DIR, "redeem_codes.json")
VERIFIED_USERS_FILE = os.path.join(DATA_DIR, "verified_users.json")

# Path logs disabled to prevent encoding errors on Windows
# print(f"Data directory: {DATA_DIR}")
# print(f"Users file: {USERS_FILE}")
# print(f"Sessions file: {SESSIONS_FILE}")


class DataManager:
    """Manage user data and sessions"""
    
    @staticmethod
    def load_users() -> Dict:
        try:
            with open(USERS_FILE, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
    
    @staticmethod
    def save_users(users: Dict):
        with open(USERS_FILE, 'w') as f:
            json.dump(users, f, indent=2)
    
    @staticmethod
    def load_sessions() -> Dict:
        try:
            with open(SESSIONS_FILE, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
    
    @staticmethod
    def save_sessions(sessions: Dict):
        with open(SESSIONS_FILE, 'w') as f:
            json.dump(sessions, f, indent=2)
    
    @staticmethod
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
    user = update.effective_user
    users = DataManager.load_users()
    
    # Check if user is registered
    if str(user.id) not in users:
        # Show registration message
        welcome_text = f"""
🌟 <b>Welcome to Homelander Checker Platform!</b> 🌟

👤 <b>User:</b> {user.first_name}
🆔 <b>ID:</b> <code>{user.id}</code>

⚠️ <b>You are not registered yet!</b>

Register now to use the Homelander web and Telegram checker.

📌 <b>Features:</b>
• Single plan: $5/week
• CC & account checkers
• SK key validation
• PayPal, Stripe, Shopify tools
• Telegram channel alerts

<i>🔒 Premium • ⚡ Fast • 🎯 The Boys style</i>
"""
        keyboard = [[InlineKeyboardButton("📝 REGISTER NOW", callback_data="register")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.effective_message.reply_text(
            welcome_text,
            parse_mode=ParseMode.HTML,
            reply_markup=reply_markup
        )
    else:
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
        
        await update.effective_message.reply_text(
            welcome_back,
            parse_mode=ParseMode.HTML,
            reply_markup=reply_markup
        )


async def register_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle registration"""
    query = update.callback_query
    await query.answer()
    
    user = update.effective_user
    users = DataManager.load_users()
    
    # Register user
    users[str(user.id)] = {
        "user_id": user.id,
        "username": user.username or "N/A",
        "first_name": user.first_name or "N/A",
        "last_name": user.last_name or "N/A",
        "registered_at": datetime.now().isoformat(),
        "total_checks": 0,
        "total_hits": 0,
        "premium": False
    }
    DataManager.save_users(users)
    
    success_text = f"""
✅ <b>Registration Successful!</b> ✅

🎊 <b>Welcome to Homelander, {user.first_name}!</b>

Your account has been created with:
🆔 <b>User ID:</b> <code>{user.id}</code>
👤 <b>Username:</b> @{user.username or 'N/A'}

🚀 <b>Next Step:</b> Open the Homelander WebApp or redeem a code.

💰 <b>Single Plan:</b> $5 / week
"""
    keyboard = [
        [InlineKeyboardButton("🌐 OPEN WEB APP", callback_data="create_session")],
        [InlineKeyboardButton("🧾 REDEEM CODE", callback_data="redeem_help")],
        [InlineKeyboardButton("🔙 Back to Start", callback_data="start_again")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        success_text,
        parse_mode=ParseMode.HTML,
        reply_markup=reply_markup
    )


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

👤 <b>User:</b> {user_data.get('first_name', 'N/A')}
🆔 <b>ID:</b> <code>{user_data.get('user_id', 'N/A')}</code>
📅 <b>Registered:</b> {user_data.get('registered_at', 'N/A')[:10]}

📈 <b>Activity:</b>
• Total Checks: {user_data.get('total_checks', 0)}
• Total Hits: {user_data.get('total_hits', 0)}
• Success Rate: {((user_data.get('total_hits', 0) / max(user_data.get('total_checks', 1), 1)) * 100):.1f}%

💎 <b>Premium:</b> {'✅ Yes' if user_data.get('premium') else '❌ No'}

<i>Keep checking to increase your stats!</i>
"""
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


async def start_again_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Return to start menu"""
    query = update.callback_query
    await query.answer()
    
    # Trigger start command
    await start_command(update, context)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""
    help_text = f"""
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
    
    if str(user.id) not in users:
        await update.message.reply_text(
            "⚠️ Please register first! Use /start",
            parse_mode=ParseMode.HTML
        )
        return
    
    user_data = users[str(user.id)]
    
    stats_text = f"""
📊 <b>Your Statistics</b> 📊

👤 User: {user_data.get('first_name', 'N/A')}
📅 Registered: {user_data.get('registered_at', 'N/A')[:10]}

📈 Checks: {user_data.get('total_checks', 0)}
🎯 Hits: {user_data.get('total_hits', 0)}
💎 Premium: {'Yes' if user_data.get('premium') else 'No'}
"""
    await update.message.reply_text(stats_text, parse_mode=ParseMode.HTML)


def main():
    """Start the bot"""
    print("Starting Homelander Telegram Bot...")
    print(f"Bot Token: {BOT_TOKEN[:20]}...")
    
    # Create application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
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
    
    print("Bot started successfully!")
    print("Waiting for users...")
    
    # Run the bot
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
