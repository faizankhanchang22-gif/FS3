# HOMELANDER BOT - SYSTEM ARCHITECTURE

## 🎯 System Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                     HOMELANDER BOT SYSTEM v2.0                      │
└─────────────────────────────────────────────────────────────────────┘

                          External: Telegram User
                                    │
                                    │ /start, /login, /verify...
                                    ▼
         ┌──────────────────────────────────────────────────┐
         │         homelander_bot.py (Main)                 │
         │              (450+ lines)                        │
         ├──────────────────────────────────────────────────┤
         │                                                  │
         │  ┌──────────────────────────────────────────┐   │
         │  │  Configuration Layer                     │   │
         │  ├──────────────────────────────────────────┤   │
         │  │  • BOT_TOKEN (from .env)                 │   │
         │  │  • WEBAPP_URL (from .env)                │   │
         │  │  • OWNER_ID                              │   │
         │  │  • THEME (HOMELANDER branding)           │   │
         │  └──────────────────────────────────────────┘   │
         │                                                  │
         │  ┌──────────────────────────────────────────┐   │
         │  │  Authentication Layer (NEW)              │   │
         │  ├──────────────────────────────────────────┤   │
         │  │  • OTPManager class                      │   │
         │  │  •  ├─ generate_otp()                    │   │
         │  │  •  ├─ create_otp()                      │   │
         │  │  •  ├─ validate_otp()                    │   │
         │  │  •  ├─ mark_verified()                   │   │
         │  │  •  └─ is_verified()                     │   │
         │  │  • @require_verification decorator       │   │
         │  │  • OTP_STORE (in-memory)                 │   │
         │  └──────────────────────────────────────────┘   │
         │                                                  │
         │  ┌──────────────────────────────────────────┐   │
         │  │  Command Handlers                        │   │
         │  ├──────────────────────────────────────────┤   │
         │  │  Public (No Verification):               │   │
         │  │  • /start      → Register user           │   │
         │  │  • /help       → Show commands           │   │
         │  │  • /stats      → Show statistics         │   │
         │  │  • /login ◄─── NEW! Generate OTP         │   │
         │  │  • /verify ◄── NEW! Validate OTP         │   │
         │  │                                          │   │
         │  │  Protected (Requires Verification):      │   │
         │  │  • /profile ◄─ NEW! @require_verif      │   │
         │  │  • /redeem ◄── NEW! @require_verif      │   │
         │  └──────────────────────────────────────────┘   │
         │                                                  │
         │  ┌──────────────────────────────────────────┐   │
         │  │  Data Management Layer                   │   │
         │  ├──────────────────────────────────────────┤   │
         │  │  • DataManager class                     │   │
         │  │  •  ├─ load_json()                       │   │
         │  │  •  ├─ save_json()                       │   │
         │  │  •  ├─ get_user()                        │   │
         │  │  •  └─ save_user()                       │   │
         │  └──────────────────────────────────────────┘   │
         │                                                  │
         └──────────────────────────────────────────────────┘
                             │
             ┌───────────────┼───────────────┐
             │               │               │
             ▼               ▼               ▼
        (Files)         (Memory)          (Telegram)
             │               │               │
    ┌────────┴────────┐  │  │         (API Calls)
    │                 │  │  │
    ▼                 ▼  ▼  ▼
┌──────────┐  ┌──────────────────────┐  Telegram
│ users.   │  │   OTP_STORE (RAM)    │  ← /start, /help, /stats
│ json     │  │                      │  → Responses
├──────────┤  │  {user_id: {         │
│{user_id} │  │    otp,              │
│ token    │  │    uid,              │
│ premium  │  │    expires_at,       │
│ toji     │  │    attempts_left     │
│ checks   │  │  }}                  │
└──────────┘  └──────────────────────┘

┌──────────────┐  ┌────────────────────────────┐
│redeems.json  │  │verified_users.json (NEW)   │
├──────────────┤  ├────────────────────────────┤
│{code} {      │  │{user_id: {                 │
│ used,        │  │  uid,                      │
│ used_by,     │  │  verified_at               │
│ used_at      │  │}}                          │
└──────────────┘  └────────────────────────────┘

┌──────────────┐
│.env          │
├──────────────┤
│BOT_TOKEN     │ ◄─── Secure (Never in code)
│WEBAPP_URL    │
│BACKEND_URL   │
└──────────────┘
```

---

## 🔄 Data Flow Diagrams

### 1. User Registration Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    REGISTRATION FLOW                             │
└─────────────────────────────────────────────────────────────────┘

    User sends /start
           │
           ▼
    ┌──────────────┐
    │ start()      │
    └──────────────┘
           │
     Checks: Is user existing?
           │
    ┌──────┴──────┐
    │             │
   YES            NO
    │             │
    │      ┌──────────────────┐
    │      │ Generate token   │
    │      └──────────────────┘
    │             │
    │      ┌──────────────────┐
    │      │ Create new_user  │
    │      └──────────────────┘
    │             │
    │      ┌──────────────────────┐
    │      │ Save to users.json   │
    │      └──────────────────────┘
    │             │
    └──────┬──────┘
           │
           ▼
    ┌──────────────────────────────┐
    │ Send: "Registration Complete"│
    │ - Next: /login <uid>         │
    │ - Token shown                │
    └──────────────────────────────┘
           │
           ▼
       User sees button:
    "🌐 Open Web App"
```

### 2. Verification Flow (NEW)

```
┌────────────────────────────────────────────────────────────────────┐
│                  OTP + UID VERIFICATION FLOW                        │
└────────────────────────────────────────────────────────────────────┘

    User sends: /login 12345
           │
           ▼
    ┌──────────────────────────────┐
    │ OTPManager.create_otp()      │
    │  user_id=123456789           │
    │  uid="12345"                 │
    └──────────────────────────────┘
           │
    ┌──────┴──────────────────────┐
    │                              │
    ▼                              ▼
Generate 6-digit        Store in OTP_STORE
OTP: "654321"          {
                         123456789: {
                           otp: "654321",
                           uid: "12345",
                           expires_at: now+120s,
                           attempts_left: 3
                         }
                       }
           │
           ▼
    Send to User:
    "🔐 Your OTP: 654321"
    "Valid: 120 seconds"
    "Attempts: 3"
           │
           ▼
    User sends: /verify 654321
           │
           ▼
    ┌──────────────────────────────┐
    │ OTPManager.validate_otp()    │
    └──────────────────────────────┘
           │
    ┌──────┼──────┐
    │      │      │
    ▼      ▼      ▼
  VALID  EXPIRED INVALID
    │      │      │
    │      │      └─→ Decrement attempts
    │      │           │
    │      │           ├─→ 2 left: "Retry"
    │      │           ├─→ 1 left: "Last try"
    │      │           └─→ 0 left: "Blocked"
    │      │
    │      └─→ Delete OTP from store
    │           "OTP expired"
    │
    └─→ SUCCESS!
        │
        ▼
    ┌──────────────────────────────┐
    │ OTPManager.mark_verified()   │
    │                              │
    │ Save to verified_users.json: │
    │ {                            │
    │   "123456789": {             │
    │     "uid": "12345",          │
    │     "verified_at": now       │
    │   }                          │
    │ }                            │
    └──────────────────────────────┘
        │
        ▼
    Send: "✅ ACCESS GRANTED"
    User is now verified!
        │
        ▼
    /profile, /redeem now WORK ✅
```

### 3. Protected Command Flow

```
┌────────────────────────────────────────────────────────────────┐
│            PROTECTED COMMAND EXECUTION FLOW                     │
└────────────────────────────────────────────────────────────────┘

    User sends: /profile
           │
           ▼
    ┌──────────────────────────────┐
    │ @require_verification        │ ◄─── NEW DECORATOR
    │   decorator wrapper          │
    └──────────────────────────────┘
           │
           ▼
    Check: Is user verified?
           │
        ┌──┴──┐
        │     │
       YES    NO
        │     │
        │     └─→ Send error:
        │         "🔐 UNAUTHORIZED"
        │         "Use /login first"
        │         │
        │         └─→ Return (exit)
        │
        ▼
    Verified user allowed
        │
        ▼
    Execute: profile(update, context)
        │
        ▼
    ┌──────────────────────────────┐
    │ Load verified_users.json     │
    │ Get user's UID               │
    │ Show profile with UID        │
    └──────────────────────────────┘
        │
        ▼
    Send: Profile info
    - Username
    - UID ◄─── FROM VERIFIED USERS!
    - Premium status
    - Stats
```

---

## 📊 State Transitions

```
                          ┌──────────────┐
                          │  NEW USER    │
                          └──────┬───────┘
                                 │ /start
                                 ▼
                    ┌────────────────────────┐
                    │    REGISTERED USER     │ ✓ In users.json
                    │    NOT VERIFIED        │ ✓ Token generated
                    └────────────┬───────────┘
                                 │ /login <uid>
                                 ▼
                    ┌────────────────────────┐
                    │   AWAITING OTP INPUT   │ ✓ OTP sent
                    │   OTP IN MEMORY        │ ✓ 120s timer
                    │   3 ATTEMPTS LEFT      │ ✓ Stored in OTP_STORE
                    └────────────┬───────────┘
                                 │
                    ┌────────────┴────────────┐
                    │                         │
         /verify <OTP>           /verify <WRONG>
                    │                         │
                   YES                       ✗ Attempts--
                    │                         │
                    ▼                         ▼
        ┌────────────────────┐    ┌─────────────────────┐
        │ VERIFIED USER      │    │ RETRY (Attempts: 2) │
        │ ✓ In verified_     │    │ (Back to awaiting)  │
        │   users.json       │    └─────────────────────┘
        │ ✓ UID stored       │               │
        │ ✓ verified_at: now │               │ /verify <WRONG> again
        └────────┬───────────┘               │
                 │                           ▼
                 │                ┌─────────────────────┐
                 │                │ RETRY (Attempts: 1) │
                 │                └─────────────────────┘
                 │                           │
                 │                /verify <WRONG> again 3rd time
                 │                           │
                 ▼                           ▼
        ┌───────────────────┐    ┌───────────────────────┐
        │ CAN USE PROTECTED │    │ BLOCKED               │
        │ COMMANDS:         │    │ Must /login again     │
        │ ✓ /profile        │    │ Delete OTP_STORE[uid] │
        │ ✓ /redeem         │    └───────────────────────┘
        │ ✓ /help           │               │
        │ ✓ /stats          │               │ /login <uid> again
        └───────────────────┘               │
                                             ▼
                                    (Back to AWAITING OTP)
```

---

## 🔐 Security Architecture

```
┌─────────────────────────────────────────────────────────────┐
│              SECURITY LAYERS (NEW)                          │
└─────────────────────────────────────────────────────────────┘

Layer 1: Token Security
┌─────────────────────────────────────────────────────────────┐
│ BEFORE: BOT_TOKEN = "8543...0"  (in code) ❌ EXPOSED        │
│ AFTER:  BOT_TOKEN = os.getenv("BOT_TOKEN")  ✅ SAFE         │
│                                                              │
│ Protection: Token only in .env (git-ignored)                │
└─────────────────────────────────────────────────────────────┘

Layer 2: User Verification
┌─────────────────────────────────────────────────────────────┐
│ BEFORE: /profile = anyone  ❌ NO PROTECTION                 │
│ AFTER:  /profile = verified only  ✅ PROTECTED              │
│                                                              │
│ @require_verification                                       │
│  └─ OTPManager.is_verified(user_id)                         │
│      └─ Check verified_users.json                           │
│          └─ Allow if verified ✓                             │
│          └─ Deny if not ✗                                   │
└─────────────────────────────────────────────────────────────┘

Layer 3: OTP Generation & Storage
┌─────────────────────────────────────────────────────────────┐
│ • Random 6-digit OTP                                        │
│ • Stored in-memory ONLY (ephemeral)                         │
│ • Never persisted to disk                                   │
│ • Auto-deletes after:                                       │
│   ├─ Successful verification                                │
│   ├─ 120 second expiry                                      │
│   └─ User cancels (implicit)                                │
└─────────────────────────────────────────────────────────────┘

Layer 4: Brute-Force Protection
┌─────────────────────────────────────────────────────────────┐
│ Try wrong OTP:                                              │
│ ├─ Try #1 (wrong) → "Attempts: 2 left" ⚠️                  │
│ ├─ Try #2 (wrong) → "Attempts: 1 left" 🚨                  │
│ └─ Try #3 (wrong) → "BLOCKED. /login again" 🔒              │
│                                                              │
│ Blocks attacker after 3 attempts                            │
└─────────────────────────────────────────────────────────────┘

Layer 5: Time Limits
┌─────────────────────────────────────────────────────────────┐
│ OTP valid: 120 seconds only                                 │
│ If expired → "OTP expired. /login again"                    │
│                                                              │
│ Prevents:                                                   │
│ ├─ Long-term OTP reuse                                      │
│ ├─ Offline OTP cracking                                     │
│ └─ Slow brute-force attacks                                 │
└─────────────────────────────────────────────────────────────┘

Layer 6: Persistent Verification
┌─────────────────────────────────────────────────────────────┐
│ verified_users.json:                                        │
│ {                                                           │
│   "user_id": {                                              │
│     "uid": "user_provided_uid",                             │
│     "verified_at": "ISO timestamp"                          │
│   }                                                         │
│ }                                                           │
│                                                              │
│ • Survives bot restarts ✓                                   │
│ • Read-only from commands                                   │
│ • Only written by OTPManager                                │
└─────────────────────────────────────────────────────────────┘

Layer 7: Silent Error Handling
┌─────────────────────────────────────────────────────────────┐
│ BEFORE: print(f"Error {context.error}")  ❌ LEAKS SECRETS   │
│ AFTER:  pass  (silent)  ✅ NO INFO LEAKAGE                 │
│                                                              │
│ Error messages:                                             │
│ ✓ Shown to user only                                        │
│ ✓ Generic (no system details)                               │
│ ✓ No credentials/tokens logged                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 📁 File Dependencies

```
Configuration Files:
  ├─ .env                    ◄─ MUST CREATE
  ├─ .env.example            ◄─ TEMPLATE PROVIDED
  └─ .gitignore              ◄─ ADD: .env

Data Files:
  ├─ users.json              ◄─ CREATE ON /start
  ├─ verified_users.json     ◄─ CREATE ON /verify (NEW!)
  ├─ redeems.json            ◄─ EXISTING
  └─ proxies.json            ◄─ EXISTING

Code Files:
  ├─ homelander_bot.py       ◄─ NEW (run this)
  ├─ toji_bot.py             ◄─ OLD (can delete)
  └─ requirements.txt        ◄─ EXISTING (has all deps)

Documentation:
  ├─ HOMELANDER_UPGRADE.md   ◄─ Full Architecture
  ├─ MIGRATION.md            ◄─ Setup Guide
  ├─ EXACT_CHANGES.md        ◄─ Code Diffs
  ├─ QUICK_REF.md            ◄─ Dev Reference
  ├─ DEPLOYMENT.md           ◄─ Deployment
  └─ SUMMARY.md              ◄─ Executive Summary

Class Hierarchies:
  Application
    ├─ CommandHandler(login)
    ├─ CommandHandler(verify)
    ├─ CommandHandler(profile)    ◄─ Protected
    ├─ CommandHandler(redeem)     ◄─ Protected
    ├─ CallbackQueryHandler
    └─ MessageHandler

Utility Classes:
  ├─ OTPManager (NEW!)
  │   ├─ generate_otp()
  │   ├─ create_otp()
  │   ├─ validate_otp()
  │   ├─ mark_verified()
  │   └─ is_verified()
  │
  └─ DataManager
      ├─ load_json()
      ├─ save_json()
      ├─ get_user()
      └─ save_user()
```

---

## 🎯 Integration Points

```
External Systems:

1. Telegram API
   ├─ /start         → user registration
   ├─ /login <uid>   → OTP generation
   ├─ /verify <otp>  → verification
   └─ /profile       → protected access

2. Web App (unchanged)
   └─ WebAppInfo(url=WEBAPP_URL)
      ├─ Open Web App button
      └─ Users can use checkers after verified

3. Backend API (unchanged)
   └─ BACKEND_URL for advanced features

4. File System
   ├─ .env               ◄─ Read (config)
   ├─ users.json        ◄─ Read/Write (user data)
   ├─ verified_users.json◄─ Read/Write (verification)
   └─ redeems.json      ◄─ Read/Write (codes)

5. Memory (RAM)
   └─ OTP_STORE         ◄─ Volatile (expires automatically)
```

---

## 🚀 Process Flow (Summary)

```
START BOT
   │
   ▼
Load .env (BOT_TOKEN)
   │
   ▼
Initialize OTPManager
   │
   ▼
Load DataManager
   │
   ▼
Setup Command Handlers:
  ├─ /start (public)
  ├─ /login (public) ◄─ NEW
  ├─ /verify (public) ◄─ NEW
  ├─ /profile (@require_verification) ◄─ NEW
  ├─ /redeem (@require_verification) ◄─ NEW
  ├─ /help (public)
  ├─ /stats (public)
  └─ Callbacks & Messages
   │
   ▼
Running (await commands)
   │
  User sends command
   │
   ├─ /start → register user
   ├─ /login → generate OTP
   ├─ /verify → validate & mark verified
   ├─ /profile → check verification, show profile
   └─ ...
   │
   ▼
Store data (JSON files)
   │
   ▼
Send response to user
```

---

**Architecture Version:** 2.0  
**Status:** Production Ready ✅  
**Last Updated:** 2026-05-02
