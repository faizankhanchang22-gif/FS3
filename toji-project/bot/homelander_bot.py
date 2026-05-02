#!/usr/bin/env python3
"""
HOMELANDER Telegram Bot - The Boys Themed (Secured with OTP/UID)
Upgraded with secure token management and verification system
"""

import asyncio
import json
import secrets
import hashlib
import uuid
import os
from datetime import datetime, timedelta
from typing import Dict, Optional
import sys
import io

# Fix Windows console encoding
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, filters, MessageHandler
from telegram.constants import ParseMode

# ============== SECURE CONFIGURATION ==============

# Load token from environment variable (REQUIRED)
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Validate token is configured
if not BOT_TOKEN:
    print("\n" + "="*60)
    print("❌ BOT TOKEN NOT CONFIGURED")
    print("="*60)
    print("\nPlease set the BOT_TOKEN environment variable:")
    print("  1. Create .env file in project root")
    print("  2. Add: BOT_TOKEN=your_telegram_bot_token")
    print("  3. Run bot again")
    print("\nSee .env.example for template")
    print("="*60 + "\n")
    sys.exit(1)

# Validate token format (should be: number:string)
if not (":" in BOT_TOKEN and len(BOT_TOKEN) > 20):
    print("\n❌ INVALID BOT TOKEN FORMAT")
    print("Token should be: numeric_id:alphanumeric_string\n")
    sys.exit(1)

OWNER_ID = 8606381959
WEBAPP_URL = os.getenv("WEBAPP_URL", "http://localhost:5173")
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

# Theme
THEME = {
    "name": "HOMELANDER",
    "emoji": "🔥",
    "tagline": "⚡ POWER ABOVE ALL ⚡",
    "color": "#DC143C",
    "tagline_error": "❌ UNAUTHORIZED — YOU ARE NOT READY",
    "tagline_success": "✅ ACCESS GRANTED — HOMELANDER APPROVES"
}

# Data files
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.dirname(SCRIPT_DIR)
USERS_FILE = os.path.join(DATA_DIR, "users.json")
REDEEMS_FILE = os.path.join(DATA_DIR, "redeems.json")
VERIFIED_USERS_FILE = os.path.join(DATA_DIR, "verified_users.json")

# In-memory OTP storage
OTP_STORE: Dict[int, Dict] = {}

# ============== OTP & VERIFICATION SYSTEM ==============

class OTPManager:
    """Manages OTP generation, validation, and expiry"""
    
    @staticmethod
    def generate_otp() -> str:
        """Generate 6-digit OTP"""
        return ''.join([str(secrets.randbelow(10)) for _ in range(6)])
    
    @staticmethod
    def create_otp(user_id: int, uid: str) -> str:
        """Create OTP for user with UID"""
        otp = OTPManager.generate_otp()
        expires_at = datetime.utcnow() + timedelta(seconds=120)
        
        OTP_STORE[user_id] = {
            "otp": otp,
            "uid": uid,
            "expires_at": expires_at.isoformat(),
            "attempts_left": 3,
            "created_at": datetime.utcnow().isoformat()
        }
        
        return otp
    
    @staticmethod
    def validate_otp(user_id: int, otp: str) -> tuple[bool, str]:
        """Validate OTP for user"""
        if user_id not in OTP_STORE:
            return False, "⚠️ No OTP found. Use /login first."
        
        otp_data = OTP_STORE[user_id]
        
        # Check expiry
        expires_at = datetime.fromisoformat(otp_data["expires_at"])
        if datetime.utcnow() > expires_at:
            del OTP_STORE[user_id]
            return False, "⏱️ OTP expired (2 minutes). Request a new one with /login"
        
        # Check attempts
        if otp_data["attempts_left"] <= 0:
            del OTP_STORE[user_id]
            return False, "🚫 Too many failed attempts. Use /login again."
        
        # Validate OTP
        if otp_data["otp"] == otp:
            uid = otp_data["uid"]
            del OTP_STORE[user_id]
            return True, uid
        else:
            otp_data["attempts_left"] -= 1
            return False, f"❌ Invalid OTP. {otp_data['attempts_left']} attempts left."
    
    @staticmethod
    def mark_verified(user_id: int, uid: str) -> None:
        """Mark user as verified"""
        verified = DataManager.load_json(VERIFIED_USERS_FILE)
        verified[str(user_id)] = {
            "uid": uid,
            "verified_at": datetime.utcnow().isoformat()
        }
        DataManager.save_json(VERIFIED_USERS_FILE, verified)
    
    @staticmethod
    def is_verified(user_id: int) -> bool:
        """Check if user is verified"""
        verified = DataManager.load_json(VERIFIED_USERS_FILE)
        return str(user_id) in verified


def require_verification(func):
    """Decorator to require verification for premium commands"""
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        
        if not OTPManager.is_verified(user_id):
            await update.message.reply_text(
                f"🔐 {THEME['tagline_error']}\n\n"
                f"Use /login <UID> to verify first.",
                parse_mode=ParseMode.HTML
            )
            return
        
        return await func(update, context)
    
    return wrapper


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
    def get_all_users() -> Dict:
        return DataManager.load_json(USERS_FILE)


# ============== COMMAND HANDLERS ==============

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Start command - Register user"""
    user = update.effective_user
    
    existing = DataManager.get_user(user.id)
    is_verified = OTPManager.is_verified(user.id)
    
    if existing:
        token = existing.get("token")
        status = "✅ VERIFIED" if is_verified else "🔐 PENDING VERIFICATION"
        message = f"""
{THEME['emoji']} <b>Welcome back, {user.first_name}!</b> {THEME['emoji']}

{THEME['tagline']}

You're already registered. Use the button below to access <b>HOMELANDER</b>.

<b>Verification:</b> {status}
<b>Status:</b> {"✅ PREMIUM" if existing.get("premium") else "❌ FREE"}
"""
    else:
        # Create new user
        token = f"{user.id}_{hashlib.sha256(str(uuid.uuid4()).encode()).hexdigest()[:16]}"
        
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

Next, verify your identity using /login <your_uid>

<b>Commands:</b>
/login - Start verification
/profile - View your profile
/help - Show help
"""
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🌐 Web App", web_app=WebAppInfo(url=WEBAPP_URL))],
        [InlineKeyboardButton("📋 Pricing", callback_data="pricing")],
    ])
    
    await update.message.reply_text(message, parse_mode=ParseMode.HTML, reply_markup=keyboard)


async def login(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Login command - Generate OTP"""
    user_id = update.effective_user.id
    
    if len(context.args) < 1:
        await update.message.reply_text(
            f"🔐 <b>Login Command</b>\n\n"
            f"Usage: /login <UID>\n\n"
            f"Example: /login 12345\n\n"
            f"Send your UID to generate an OTP.",
            parse_mode=ParseMode.HTML
        )
        return
    
    uid = context.args[0]
    
    # Generate OTP
    otp = OTPManager.create_otp(user_id, uid)
    
    message = f"""
🔐 <b>VERIFICATION CODE GENERATED</b> 🔐

{THEME['tagline']}

<b>Your OTP:</b>
<code>{otp}</code>

<b>Valid for:</b> 2 minutes (120 seconds)
<b>Attempts:</b> 3

<b>Next Step:</b>
Use: /verify {otp}
"""
    
    await update.message.reply_text(message, parse_mode=ParseMode.HTML)


async def verify(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Verify command - Validate OTP"""
    user_id = update.effective_user.id
    
    if len(context.args) < 1:
        await update.message.reply_text(
            f"Usage: /verify <OTP>\n\nExample: /verify 123456",
            parse_mode=ParseMode.HTML
        )
        return
    
    otp = context.args[0]
    is_valid, result = OTPManager.validate_otp(user_id, otp)
    
    if is_valid:
        uid = result
        OTPManager.mark_verified(user_id, uid)
        
        message = f"""
{THEME['emoji']} <b>{THEME['tagline_success']}</b> {THEME['emoji']}

<b>✅ Verification Successful!</b>

Your identity has been verified. You now have full access to HOMELANDER.

<b>UID:</b> <code>{uid}</code>
<b>Verified At:</b> {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}

<b>Next Steps:</b>
1. /profile - View your profile
2. /redeem - Redeem premium codes
3. Use the Web App for advanced features
"""
    else:
        message = f"""
{THEME['emoji']} <b>{THEME['tagline_error']}</b> {THEME['emoji']}

{result}
"""
    
    await update.message.reply_text(message, parse_mode=ParseMode.HTML)


@require_verification
async def profile(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show user profile (requires verification)"""
    user_id = update.effective_user.id
    user = DataManager.get_user(user_id)
    
    if not user:
        await update.message.reply_text("❌ Not registered. Use /start")
        return
    
    verified_users = DataManager.load_json(VERIFIED_USERS_FILE)
    verified_info = verified_users.get(str(user_id), {})
    
    premium_text = f"✅ Until {user.get('premium_expires_at', 'N/A')}" if user.get('premium') else "❌ Redeem a code"
    
    profile_msg = f"""
{THEME['emoji']} <b>YOUR PROFILE</b> {THEME['emoji']}

<b>Username:</b> @{user.get('username')}
<b>User ID:</b> <code>{user.get('user_id')}</code>
<b>UID:</b> <code>{verified_info.get('uid', 'N/A')}</code>

<b>Premium Status:</b> {premium_text}
<b>Total Checks:</b> {user.get('total_checks', 0)}
<b>Total Hits:</b> {user.get('total_hits', 0)}

<b>Verified:</b> ✅ Yes
<b>Registered:</b> {user.get('registered_at')}
"""
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔑 Redeem Code", callback_data="redeem")],
        [InlineKeyboardButton("🌐 Web App", web_app=WebAppInfo(url=WEBAPP_URL))],
    ])
    
    await update.message.reply_text(profile_msg, parse_mode=ParseMode.HTML, reply_markup=keyboard)


@require_verification
async def redeem(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Redeem code command (requires verification)"""
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔑 Enter Code", callback_data="redeem_enter")],
        [InlineKeyboardButton("🌐 Purchase", url="https://t.me/homelander")],
    ])
    
    msg = f"""
{THEME['emoji']} <b>REDEEM CODE</b> {THEME['emoji']}

{THEME['tagline']}

Enter your premium code to activate <b>HOMELANDER PREMIUM</b>.

<b>$5 / Week</b>
✅ All Checkers Unlimited
✅ Hit Notifications
✅ Premium Support
"""
    await update.message.reply_text(msg, parse_mode=ParseMode.HTML, reply_markup=keyboard)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Help command"""
    help_text = f"""
{THEME['emoji']} <b>HOMELANDER COMMANDS</b> {THEME['emoji']}

{THEME['tagline']}

<b>Authentication:</b>
/login - Start verification with UID
/verify - Verify OTP code

<b>Core Commands:</b>
/start - Register & get started
/profile - View your profile (requires verification)
/redeem - Redeem a premium code (requires verification)
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
    
    await update.message.reply_text(help_text, parse_mode=ParseMode.HTML, reply_markup=keyboard)


async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show bot statistics"""
    all_users = DataManager.get_all_users()
    verified_users = DataManager.load_json(VERIFIED_USERS_FILE)
    
    premium_count = sum(1 for u in all_users.values() if u.get("premium"))
    total_checks = sum(u.get("total_checks", 0) for u in all_users.values())
    total_hits = sum(u.get("total_hits", 0) for u in all_users.values())
    
    stats_msg = f"""
{THEME['emoji']} <b>HOMELANDER STATISTICS</b> {THEME['emoji']}

<b>Total Users:</b> {len(all_users)}
<b>Verified Users:</b> {len(verified_users)}
<b>Premium Users:</b> {premium_count}
<b>Total Checks:</b> {total_checks}
<b>Total Hits:</b> {total_hits}

{THEME['tagline']}
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

{THEME['tagline']}

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

{THEME['tagline_success']}

<b>✅ Success!</b>

Your HOMELANDER PREMIUM is now active!

<b>Expires:</b> {expires_at.strftime('%Y-%m-%d %H:%M:%S')}

<b>Code Used:</b> <code>{code}</code>

<b>Next Steps:</b>
1. /profile - View your details
2. 🌐 Open Web App
3. Start checking cards
"""
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🌐 Web App", web_app=WebAppInfo(url=WEBAPP_URL))],
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
    """Handle errors silently"""
    pass  # No logging of secrets


# ============== MAIN ==============

def main() -> None:
    """Start the bot"""
    print(f"\n🔥 HOMELANDER SYSTEM INITIALIZING 🔥\n")
    print(f"⚡ POWER ABOVE ALL ⚡\n")
    
    # Verify token loaded
    if not BOT_TOKEN:
        print("❌ ERROR: BOT_TOKEN not set!")
        sys.exit(1)
    
    # Create application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("login", login))
    application.add_handler(CommandHandler("verify", verify))
    application.add_handler(CommandHandler("profile", profile))
    application.add_handler(CommandHandler("redeem", redeem))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("stats", stats))
    
    # Callback handlers
    application.add_handler(CallbackQueryHandler(button_callback))
    
    # Message handler for redeem codes
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Error handler
    application.add_error_handler(error_handler)
    
    # Run bot
    print("✅ Bot started successfully!")
    application.run_polling()


if __name__ == "__main__":
    main()
