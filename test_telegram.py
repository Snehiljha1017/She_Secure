#!/usr/bin/env python3
"""
Quick Telegram Bot Test Script
Tests if the Telegram bot can send messages
"""

import json
import os
from urllib import request as urlrequest, error as urlerror

# Load bot token
config_path = "instance/telegram_bot.json"
if os.path.exists(config_path):
    with open(config_path, 'r') as f:
        config = json.load(f)
        bot_token = config.get("TELEGRAM_BOT_TOKEN", "")
else:
    print("❌ Config file not found!")
    exit(1)

if not bot_token:
    print("❌ Bot token not set!")
    exit(1)

print(f"✅ Bot token loaded: {bot_token[:20]}...")

# Function to send message
def send_telegram_message(chat_id, message):
    """Send a message via Telegram"""
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    
    payload = {
        "chat_id": str(chat_id),
        "text": message
    }
    
    try:
        req = urlrequest.Request(
            url,
            data=json.dumps(payload).encode('utf-8'),
            method='POST',
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"\n📤 Sending to chat_id: {chat_id}")
        print(f"📝 Message: {message[:50]}...")
        
        with urlrequest.urlopen(req, timeout=10) as response:
            result = json.loads(response.read().decode('utf-8'))
            
            if result.get('ok'):
                print(f"✅ SUCCESS! Message ID: {result.get('result', {}).get('message_id')}")
                return True
            else:
                error_msg = result.get('description', 'Unknown error')
                print(f"❌ FAILED: {error_msg}")
                return False
                
    except urlerror.HTTPError as e:
        error = e.read().decode('utf-8', errors='replace')
        print(f"❌ HTTP Error: {error}")
        return False
    except urlerror.URLError as e:
        print(f"❌ Connection Error: {str(e)}")
        return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

# Test messages
print("\n" + "="*60)
print("🧪 TELEGRAM BOT TEST")
print("="*60)

# Get test chat ID from user
chat_id = input("\n📱 Enter your Telegram Chat ID to test sending: ").strip()

if not chat_id:
    print("❌ No chat ID provided!")
    exit(1)

# Send test message
test_message = """✅ Test message from SheSecure!

If you see this, the Telegram bot is working correctly and messages can be sent.

🚨 This means your emergency alerts will be delivered!"""

print("\n" + "="*60)
success = send_telegram_message(chat_id, test_message)
print("="*60)

if success:
    print("\n✅ TELEGRAM IS WORKING!")
    print("🎉 Your emergency alerts will be delivered successfully!")
else:
    print("\n❌ TELEGRAM TEST FAILED!")
    print("💡 Check that:")
    print("   1. Chat ID is correct")
    print("   2. You opened the Telegram bot and tapped /start")
    print("   3. Bot token is correct in instance/telegram_bot.json")
    print("   4. Your internet connection is working")
