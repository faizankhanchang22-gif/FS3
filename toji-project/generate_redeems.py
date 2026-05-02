#!/usr/bin/env python3
"""
HOMELANDER Redeem Code Generator - Admin Tool
"""

import json
import random
import string
import os
from datetime import datetime
from pathlib import Path

DATA_DIR = Path(__file__).parent
REDEEMS_FILE = DATA_DIR / "redeems.json"

def generate_codes(count: int = 10, plan: str = "HOMELANDER PREMIUM"):
    """Generate redeem codes"""
    
    try:
        with open(REDEEMS_FILE, 'r') as f:
            redeems = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        redeems = {}
    
    new_codes = []
    
    for _ in range(count):
        # Generate code: HOMELANDER-XXXXX
        code = f"HOMELANDER-{''.join(random.choices(string.ascii_uppercase + string.digits, k=10))}"
        
        redeems[code] = {
            "code": code,
            "plan": plan,
            "created_at": datetime.utcnow().isoformat(),
            "used": False,
            "used_by": None,
            "used_at": None
        }
        
        new_codes.append(code)
    
    with open(REDEEMS_FILE, 'w') as f:
        json.dump(redeems, f, indent=2)
    
    print(f"✅ Generated {count} redeem codes\n")
    for code in new_codes:
        print(f"  {code}")
    
    print(f"\n✅ Saved to: {REDEEMS_FILE}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        try:
            count = int(sys.argv[1])
        except ValueError:
            count = 10
    else:
        count = 10
    
    # Ensure directory exists
    os.makedirs(DATA_DIR, exist_ok=True)
    
    generate_codes(count)
