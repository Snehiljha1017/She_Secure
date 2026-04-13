# 📱 Telegram Setup Guide - Step by Step

## What You Need:
- Telegram app (on phone or PC)
- Your Telegram bot token (already configured ✓)
- Trusted contacts with Telegram

---

## STEP 1️⃣: Find Your Bot in Telegram

1. **Open Telegram** (mobile or desktop)
2. **Search for your bot** - Type: `@SheSecureWomenSafetyBot` (or whatever your bot name is)
   - Or search for the bot name you created with BotFather
3. **Tap on the bot** to open it

**Screenshot Example:**
```
Search box → Type bot name → Select bot from search results
```

---

## STEP 2️⃣: Start the Bot (IMPORTANT!)

**This is the critical step everyone misses!**

1. **Open the bot chat**
2. **Tap the `/start` button** (it should appear automatically)
3. **Wait** for the bot to respond
4. **Your chat ID will be stored** by the bot

**What the bot sees:**
```
User: /start
Bot: "Chat started! Your ID: 123456789"
```

**Example:**
```
You open: @YourBotName
You see: [START] button
You tap it → Bot receives your chat ID
```

---

## STEP 3️⃣: Test the Bot

Before adding to contacts, test if it's working:

1. **Send a message** to the bot (any message, like "Hi")
2. **The bot should respond** (indicating connection is working)
3. **Go back to SheSecure dashboard**

---

## STEP 4️⃣: Get Your Telegram Chat ID

### Method A: From Bot (Automatic)

1. Go to SheSecure dashboard
2. Scroll to **"Trusted contacts"** section
3. Click **"Find Telegram Contacts"** button
4. **Your bot will fetch all chat IDs** of people who tapped `/start`
5. Your ID will appear in the list

### Method B: Manual (If Method A doesn't work)

If the automatic discovery doesn't work:

1. **Open your bot chat** in Telegram
2. Go to bot profile → "About" or info section
3. Look for your numeric chat ID (or use a bot like `@userinfobot`)
4. **Copy the number** (example: `987654321`)

---

## STEP 5️⃣: Add Contact to SheSecure

Once you have the Telegram Chat ID:

1. **Go to SheSecure Dashboard**
2. **Scroll to "Trusted Contacts" section**
3. **Fill in the form:**
   ```
   Contact name: Mom
   Phone number: +91XXXXXXXXXX
   Telegram Chat ID: 987654321  ← Paste here!
   ```
4. **Tap "Add Trusted Contact"**
5. ✅ **Done!** Contact is now saved with Telegram ID

---

## STEP 6️⃣: Use "Find Telegram Contacts" Feature

### How it works:

1. **Tell your trusted contacts** to open your bot and tap `/start`
2. **Wait** for them to tap `/start`
3. **Go back to SheSecure Dashboard**
4. **Click "Find Telegram Contacts"** button
5. **All contacts who tapped `/start` will appear in the list**
6. **Click on a contact → it auto-populates the Telegram Chat ID**

### The Flow:

```
Contact opens bot → Taps /start
        ↓
Their chat ID stored in bot updates
        ↓
You click "Find Telegram Contacts"
        ↓
SheSecure queries bot for all chat IDs
        ↓
Lists all contacts who started the bot
        ↓
You select them → Adds to your trusted contacts
```

---

## Example Scenario:

### Your Mom Setup:

1. **You**: "Mom, can you open Telegram and find my bot?"
2. **Mom**: Searches `@SheSecureBot` and taps it
3. **Mom**: Sees the chat and taps `/start` button
4. ✅ **Mom's chat ID is now stored**

5. **You**: Go to SheSecure dashboard
6. **You**: Click "Find Telegram Contacts"
7. **You**: See: "Mom (Chat ID: 123456789)"
8. **You**: Click on it
9. ⚡ **Telegram Chat ID auto-filled in the form**
10. **You**: Click "Save"

---

## Troubleshooting

### ❌ "No Telegram chats found yet"

**Problem:** No one has tapped `/start` on your bot yet

**Solution:**
1. Make sure your trusted contacts **actually tapped `/start`** (not just opened the chat)
2. Wait a few seconds after they tap `/start`
3. Refresh the page: `F5` or `Ctrl+Shift+R`
4. Click "Find Telegram Contacts" again

### ❌ Can't Find the Bot

**Problem:** Can't search for bot in Telegram

**Solution:**
1. Make sure you're using the **correct bot name**
2. Bot name should start with `@` or end with `_bot`
3. Check that bot was created with BotFather
4. Try searching by bot ID number instead

### ❌ Bot Not Responding

**Problem:** Bot opens but doesn't respond to `/start`

**Solution:**
1. **Check bot token** is correct (configured in `app.py`)
2. **Check Flask server is running**:
   - Go to `http://localhost:5000` in browser
   - Should see SheSecure landing page
3. **Restart Flask**:
   - Kill terminal running Flask
   - Run: `python app.py` again
4. **Wait 30 seconds** for bot to initialize

### ❌ Chat ID Not Auto-Filling

**Problem:** Found contacts but Chat ID not showing

**Solution:**
1. **Manually enter it:**
   - Contact name: "Mom"
   - Phone: "+91XXXXXXXXXX"
   - Telegram Chat ID: `123456789` (the number)
2. **Click Add Trusted Contact**

---

## Quick Reference Checklist

- [ ] Bot created with BotFather
- [ ] Bot token configured in SheSecure
- [ ] Flask server running (`python app.py`)
- [ ] Trusted contact opened Telegram bot
- [ ] Trusted contact **tapped `/start`** button
- [ ] Waited 5 seconds
- [ ] Clicked "Find Telegram Contacts"
- [ ] Contact appears in list
- [ ] Chat ID copied and saved
- [ ] Contact added to dashboard

---

## Advanced: Verify Everything Works

### Test sending a message:

1. **Add a contact with Telegram ID**
2. **Go to Dashboard**
3. **Click "Send Emergency Message"**
4. **Type message**: "Test message"
5. **Select contact**
6. **Send**
7. ✅ **Message appears in contact's Telegram within seconds**

---

## Still Having Issues?

**Try this debug path:**

1. **Open bot chat** in Telegram
2. **Send**: `/start`
3. **Bot should respond** with chat ID
4. **Note the number** shown
5. **Enter that number manually** in SheSecure
6. **Test send message** to verify connection

---

## Getting Help

If bot still not responding:

1. **Check bot token** once more - copy from:
   ```
   c:\Users\snehi\OneDrive\Documents\Playground\she-secure\instance\telegram_bot.json
   ```

2. **Verify bot is active** with BotFather - go search for `@BotFather`

3. **Restart Flask completely**:
   - Close terminal (Ctrl+C)
   - Run: `python app.py`
   - Wait for "Running on http://0.0.0.0:5000"

---

## Summary

✅ **The process in 3 steps:**

1. **Contact taps `/start`** on your Telegram bot
2. **Their chat ID is stored** in the bot's update history
3. **You click "Find Telegram Contacts"** to retrieve all chat IDs
4. **Select contact → auto-populate ID → save**
5. **Now can send emergency alerts via Telegram!**

That's it! 🎉
