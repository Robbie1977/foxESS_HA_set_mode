#!/usr/bin/env python3
"""
FoxESS Work Mode Control Script

See README.md for full documentation, setup instructions, and usage.
"""

import hashlib
import time
import requests
import sys
import json

# Configuration - Replace with your actual values
API_KEY = "your_api_key_here"  # Get from FoxESS personal center -> API Management
INVERTER_SN = "your_inverter_serial_number_here"  # Your inverter's serial number

# API Configuration
DOMAIN = "https://www.foxesscloud.com"
LANG = "en"

def get_signature(path: str, token: str) -> tuple[str, str]:
    """Generate API signature for authentication."""
    timestamp = str(int(time.time() * 1000))
    signature_string = f"{path}\r\n{token}\r\n{timestamp}"
    signature = hashlib.md5(signature_string.encode()).hexdigest()
    return signature, timestamp

def get_headers(path: str) -> dict:
    """Generate request headers with authentication."""
    signature, timestamp = get_signature(path, API_KEY)
    return {
        "Content-Type": "application/json",
        "token": API_KEY,
        "timestamp": timestamp,
        "signature": signature,
        "lang": LANG
    }

def set_work_mode(mode: str) -> dict:
    """Set the working mode of the inverter."""
    path = "/op/v0/device/setting/set"
    url = DOMAIN + path
    payload = {"sn": INVERTER_SN, "key": "WorkMode", "value": mode}
    response = requests.post(url, json=payload, headers=get_headers(path))
    return response.json()

def get_work_mode() -> dict:
    """Get the current working mode of the inverter."""
    path = "/op/v0/device/setting/get"
    url = DOMAIN + path
    payload = {"sn": INVERTER_SN, "key": "WorkMode"}
    response = requests.post(url, json=payload, headers=get_headers(path))
    return response.json()

def main():
    """Main function to handle command line arguments."""
    if len(sys.argv) < 2:
        print("Usage: foxess_control.py <command>")
        print("Commands: get, selfuse, backup, feedin, peakshaving")
        print("\nExample: python3 foxess_control.py get")
        sys.exit(1)

    command = sys.argv[1].lower()

    if command == "get":
        result = get_work_mode()
        print(json.dumps(result, indent=2))
    elif command in ["selfuse", "backup", "feedin", "peakshaving"]:
        mode_map = {
            "selfuse": "SelfUse",
            "backup": "Backup",
            "feedin": "Feedin",
            "peakshaving": "PeakShaving"
        }
        result = set_work_mode(mode_map[command])
        print(json.dumps(result, indent=2))
    else:
        print("Error: Invalid command")
        print("Valid commands: get, selfuse, backup, feedin, peakshaving")
        sys.exit(1)

if __name__ == "__main__":
    main()