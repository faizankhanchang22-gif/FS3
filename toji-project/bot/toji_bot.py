#!/usr/bin/env python3
"""
HOMELANDER Telegram Bot - The Boys Themed
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

BOT_TOKEN = "8543073349:AAE4g6AcLSgBTEz5b3sXaBJlDIhZnQopVE0"
OWNER_ID = 8606381959
WEBAPP_URL = "http://localhost:5173"  # Or your actual URL
BACKEND_URL = "http://localhost:8000"

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
REDEEMS_FILE = os.path.join(DATA_DIR, "redeems.json")

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
    
    if existing:
        token = existing.get("token")
        message = f"""
{THEME['emoji']} <b>Welcome back, {user.first_name}!</b> {THEME['emoji']}

You're already registered. Use the button below to access <b>HOMELANDER</b>.

<b>Your Token:</b> <code>{token}</code>

<b>Status:</b> {"✅ PREMIUM" if existing.get("premium") else "❌ FREE (Redeem a code)"}
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

Your token has been generated. Use the button below to access the <b>Web Platform</b> or redeem a code to activate premium.

<b>Token:</b> <code>{token}</code>

<b>Commands:</b>
/redeem - Redeem a premium code
/profile - View your profile
/help - Show help
"""
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🌐 Open Web App", web_app=WebAppInfo(url=WEBAPP_URL))],
        [InlineKeyboardButton("📋 Pricing", callback_data="pricing")],
    ])
    
    await update.message.reply_text(message, parse_mode=ParseMode.HTML, reply_markup=keyboard)

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
    print(f"\n🔴 Starting HOMELANDER Telegram Bot... 🔴\n")
    print(f"Owner: {OWNER_ID}")
    print(f"Token: {BOT_TOKEN[:20]}...")
    print(f"Webapp: {WEBAPP_URL}\n")
    
    # Create application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Command handlers
    application.add_handler(CommandHandler("start", start))
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
    application.run_polling()

if __name__ == "__main__":
    main()
