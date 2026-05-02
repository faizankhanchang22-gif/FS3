#!/usr/bin/env python3
"""
HOMELANDER BOT - Security Verification Script
Checks that no tokens are hardcoded and security is properly configured.
"""

import os
import sys
import json
from pathlib import Path

# Colors for output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'
BOLD = '\033[1m'

def check_mark():
    return f"{GREEN}✅{RESET}"

def cross_mark():
    return f"{RED}❌{RESET}"

def warn_mark():
    return f"{YELLOW}⚠️{RESET}"

print(f"\n{BOLD}{BLUE}HOMELANDER BOT - SECURITY VERIFICATION{RESET}\n")
print("="*60)

project_root = Path(__file__).parent
checks_passed = 0
checks_failed = 0

# Check 1: .env file exists
print("\n1. Checking .env file configuration...")
env_file = project_root / ".env"
env_example = project_root / ".env.example"

if env_file.exists():
    print(f"   {check_mark()} .env file found")
    checks_passed += 1
    
    # Check for tokens in .env
    env_content = env_file.read_text()
    if "BOT_TOKEN=" in env_content and "paste_your" not in env_content:
        print(f"   {check_mark()} BOT_TOKEN configured")
        checks_passed += 1
    else:
        print(f"   {cross_mark()} BOT_TOKEN not configured properly")
        print(f"       Edit .env and add: BOT_TOKEN=your_token_here")
        checks_failed += 1
else:
    print(f"   {cross_mark()} .env file NOT found")
    print(f"       Run: cp .env.example .env")
    checks_failed += 1

# Check 2: .env.example exists
print("\n2. Checking .env.example template...")
if env_example.exists():
    print(f"   {check_mark()} .env.example exists")
    example_content = env_example.read_text()
    if "paste_your_bot_token_here" in example_content:
        print(f"   {check_mark()} .env.example contains safe placeholder")
        checks_passed += 2
    else:
        print(f"   {warn_mark()} .env.example might contain real tokens")
        checks_failed += 1
else:
    print(f"   {cross_mark()} .env.example NOT found")
    checks_failed += 1

# Check 3: .gitignore configuration
print("\n3. Checking .gitignore security...")
gitignore = project_root / ".gitignore"
if gitignore.exists():
    print(f"   {check_mark()} .gitignore exists")
    gitignore_content = gitignore.read_text()
    if ".env" in gitignore_content:
        print(f"   {check_mark()} .env is in .gitignore")
        checks_passed += 2
    else:
        print(f"   {cross_mark()} .env NOT in .gitignore")
        print(f"       Add '.env' to .gitignore")
        checks_failed += 1
else:
    print(f"   {cross_mark()} .gitignore NOT found")
    checks_failed += 1

# Check 4: Scan bot files for hardcoded tokens
print("\n4. Scanning bot files for hardcoded tokens...")
bot_files = [
    project_root / "bot" / "homelander_bot.py",
    project_root / "backend" / "main.py"
]

token_signatures = [
    "8543073349:AAE4g6AcLSgBTEz5b3sXaBJlDIhZnQopVE0",  # Old token
    "8627502122:AAHBasPhzRC5NnQX0BB6X83zjgoxSTdWI3I",  # New token
    'BOT_TOKEN = "',  # Hardcoded assignment
]

found_hardcoded = False
for bot_file in bot_files:
    if bot_file.exists():
        content = bot_file.read_text()
        
        # Check for old hardcoded tokens
        for sig in token_signatures[:2]:
            if sig in content:
                print(f"   {cross_mark()} Found possible hardcoded token in {bot_file.name}")
                found_hardcoded = True
                checks_failed += 1
        
        # Check for proper environment loading
        if 'os.getenv("BOT_TOKEN")' in content:
            print(f"   {check_mark()} {bot_file.name} uses os.getenv()")
            checks_passed += 1
        else:
            print(f"   {cross_mark()} {bot_file.name} doesn't use os.getenv()")
            checks_failed += 1

if not found_hardcoded:
    print(f"   {check_mark()} No hardcoded bot tokens found")
    checks_passed += 1

# Check 5: Git check (if repo)
print("\n5. Checking git status...")
git_dir = project_root / ".git"
if git_dir.exists():
    # Check if .env is tracked
    try:
        import subprocess
        result = subprocess.run(
            ["git", "ls-files", ".env"],
            cwd=project_root,
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0 and result.stdout.strip():
            print(f"   {cross_mark()} .env is tracked in git (BAD)")
            print(f"       Run: git rm --cached .env")
            checks_failed += 1
        else:
            print(f"   {check_mark()} .env properly ignored by git")
            checks_passed += 1
    except Exception as e:
        print(f"   {warn_mark()} Could not check git status: {e}")
else:
    print(f"   {warn_mark()} Not a git repository")

# Check 6: Environment variable at runtime
print("\n6. Checking runtime token loading...")
token = os.getenv("BOT_TOKEN")
if token:
    print(f"   {check_mark()} BOT_TOKEN environment variable set")
    if len(token) > 20 and ":" in token:
        print(f"   {check_mark()} Token format looks valid")
        checks_passed += 2
    else:
        print(f"   {cross_mark()} Token format invalid")
        checks_failed += 1
else:
    print(f"   {warn_mark()} BOT_TOKEN not set in environment")
    print(f"       This is OK if .env is not loaded yet")
    print(f"       Run: source .env && python homelander_bot.py")

# Summary
print("\n" + "="*60)
print(f"\n{BOLD}SECURITY VERIFICATION RESULTS{RESET}")
print(f"Checks Passed:  {GREEN}{checks_passed}{RESET}")
print(f"Checks Failed:  {RED}{checks_failed}{RESET}")

if checks_failed == 0:
    print(f"\n{BOLD}{GREEN}✅ ALL SECURITY CHECKS PASSED{RESET}")
    print("\nYour bot is securely configured!")
    sys.exit(0)
else:
    print(f"\n{BOLD}{RED}❌ SECURITY ISSUES DETECTED{RESET}")
    print("\nPlease fix the issues above before deploying.")
    sys.exit(1)
