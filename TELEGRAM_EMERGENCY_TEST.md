# 🚨 TELEGRAM EMERGENCY ALERT - QUICK TEST

## STEP 1: Get Your Own Telegram Chat ID

1. Open Telegram
2. Search for: `@userinfobot`
3. Tap it and send: `/start`
4. Bot will show your Chat ID (e.g., `987654321`)
5. **Copy the number**

---

## STEP 2: Add Yourself As Contact

In SheSecure Dashboard:
1. Scroll to "Trusted Contacts"
2. Fill form:
   ```
   Contact name: Test Me
   Phone: +91XXXXXXXXXX (any number)
   Telegram Chat ID: [your number from step 1]
   ```
3. Click "Add Contact"

---

## STEP 3: Test Emergency Button

1. Click: 🚨 **I'M IN DANGER**
2. Wait 2-3 seconds
3. Check Telegram - you should receive message from your bot!
4. Message should say: "🚨 EMERGENCY: [username] is in danger!"

---

## If Message Not Received:

**Check these in order:**

1. ✓ Is bot token correct in `instance/telegram_bot.json`?
   - Should be: `8706435897:AAEcKbJqg6GFaXG06sE8mlaU80UvNmayK54`

2. ✓ Did you start the bot?
   - Search `@SheSecureBot` (or your bot name)
   - Tap `/start` button

3. ✓ Is chat ID correct?
   - Use @userinfobot to verify your ID
   - No extra spaces

4. ✓ Is Flask running?
   - Terminal should show "Running on http://0.0.0.0:5000"

5. ✓ Check browser console:
   - Open Chrome DevTools: F12
   - Go to "Console" tab
   - Click "I'm in Danger" again
   - Look for any error messages

---

## TELEGRAM BOT API DIRECT TEST

Copy and paste in Python:

```python
import json
from urllib import request as urlrequest

bot_token = "8706435897:AAEcKbJqg6GFaXG06sE8mlaU80UvNmayK54"
chat_id = "YOUR_CHAT_ID_HERE"  # Replace with your ID
message = "Test message from emergency system"

url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
payload = {"chat_id": chat_id, "text": message}

req = urlrequest.Request(
    url,
    data=json.dumps(payload).encode('utf-8'),
    method='POST',
    headers={'Content-Type': 'application/json'}
)

try:
    with urlrequest.urlopen(req) as response:
        result = json.loads(response.read().decode('utf-8'))
        print("✅ SUCCESS!" if result.get('ok') else f"❌ FAIL: {result}")
except Exception as e:
    print(f"❌ ERROR: {e}")
```

---

## What Should Happen:

```
1. You click 🚨 I'M IN DANGER
   ↓
2. Browser sends location + clicks to /api/emergency/danger
   ↓
3. Backend gets all contacts with telegram_chat_id
   ↓
4. For each contact with telegram_chat_id:
   - Calls Telegram API with sendMessage
   - Includes your location
   - Message delivered within 1-2 seconds
   ↓
5. You see in Telegram: Message arrives from bot
```

---

## DEBUGGING CHECKLIST

If still not working, try this:

1. **Get your chat ID:**
   ```
   Go to @userinfobot in Telegram
   Send: /start
   Note the ID shown
   ```

2. **Test admin endpoint:**
   ```
   Open in browser:
   http://localhost:5000/api/test-telegram
   
   Login if prompted
   Look at the output - shows:
   - Is Telegram configured? (true/false)
   - How many contacts total?
   - How many with Telegram IDs?
   - List of all contacts
   ```

3. **Check Flask terminal:**
   ```
   Look for lines like:
   [TELEGRAM DEBUG] Sending to chat_id: 123456
   [TELEGRAM DEBUG] Message: ...
   [TELEGRAM DEBUG] Send result: ...
   
   OR
   
   [TELEGRAM ERROR] Failed for ...
   ```

4. **If still failing:**
   - Check internet connection
   - Verify bot token has no typos
   - Try with different Telegram user
   - Check Telegram app is up to date

---

## QUICK FIX COMMANDS

If you need to reset:

```bash
# Delete database and restart:
del instance\site.db
python app.py

# Test Telegram directly:
python test_telegram.py
```

---

That's it! Follow these steps and Telegram emergency alerts should work.
