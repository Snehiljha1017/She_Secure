# ⚡ QUICK START - Telegram Setup (3 Steps)

## 🎯 The Goal
Get your trusted contacts' Telegram IDs so SheSecure can send them emergency alerts

---

## STEP 1: Tell Contact to Open Bot

**Give your trusted contact these instructions:**

```
1. Open Telegram on your phone
2. Search for: YOUR_BOT_NAME (example: @SheSecureBot)
3. Open the chat
4. Tap the [START] button that appears
5. Wait for bot to respond
```

**That's it! Their chat ID is now stored.**

---

## STEP 2: You Find the Contacts

**On the SheSecure Dashboard:**

```
1. Login to SheSecure
2. Go to DASHBOARD
3. Scroll to "Trusted Contacts" section
4. Click button: [Find Telegram Contacts]
5. Wait a few seconds...
```

---

## STEP 3: Auto-Fill & Save

**When contacts appear:**

```
✓ You'll see a list of people who tapped /start
✓ Click [Use This ID] on your contact
✓ The Telegram chat ID auto-fills
✓ Add phone number
✓ Click [Add Trusted Contact]
✓ DONE! Now can send emergency alerts via Telegram
```

---

## 📸 Visual Flow

```
┌─────────────────────────────────────────┐
│  Contact Action                          │
├─────────────────────────────────────────┤
│ 1. Search @YourBotName on Telegram      │
│ 2. Open chat                            │
│ 3. Tap [START] button                   │
│ 4. Wait (chat ID stored automatically) │
└─────────────────────────────────────────┘
           ↓ (5-10 seconds)
┌─────────────────────────────────────────┐
│  SheSecure Dashboard                    │
├─────────────────────────────────────────┤
│ 1. Click [Find Telegram Contacts]       │
│ 2. System checks who started the bot   │
│ 3. Shows list of discovered contacts   │
│ 4. Click [Use This ID]                 │
│ 5. Telegram chat ID auto-fills         │
└─────────────────────────────────────────┘
           ↓
┌─────────────────────────────────────────┐
│  ✅ READY!                               │
├─────────────────────────────────────────┤
│ Contact saved with Telegram ID         │
│ Can now send emergency alerts via TG   │
└─────────────────────────────────────────┘
```

---

## ❓ Still Not Finding Contacts?

### Check These:

1. **Did contact tap `/start`?** (Not just open chat, but TAP START)
2. **Did you wait?** (5-10 seconds after they tap START)
3. **Is Flask running?** (Server must be on: `python app.py`)
4. **Bot token set?** (File: `instance/telegram_bot.json`)

### Try This Debug:

```
1. Contact opens bot again
2. Contact sends ANY message (not just /start)
3. Wait 10 seconds
4. You click [Find Telegram Contacts]
5. Should appear now
```

---

## 📞 Manual Fallback (If Auto-Discovery Fails)

**If "Find Telegram Contacts" doesn't work:**

1. Contact can find their chat ID manually:
   - Message the bot: `/start` → Look for the ID in response
   - Or use this bot: `@userinfobot` → it shows your ID
   - Copy the number (e.g., 987654321)

2. In SheSecure, manually enter:
   - Name: Mom
   - Phone: +91XXXXXXXXXX
   - **Telegram Chat ID: 987654321** ← paste number here
   - Click [Add Trusted Contact]

---

## ✅ Test It Works

Once contact is saved:

1. Click [Send Emergency Message]
2. Type: "Test message from SheSecure"
3. Select the contact
4. Send
5. ✅ Message appears in contact's Telegram instantly

---

## 🆘 If STILL Not Working

**Check bot is active:**

1. Open Telegram
2. Message `@BotFather`
3. Type: `/mybot`
4. Select your bot
5. Should say "✅ Bot is online"

**If bot is offline:**
- Flask server crashed
- Restart: Close terminal → Run `python app.py`

---

## 📋 Checklist

- [ ] Contact found bot in Telegram
- [ ] Contact tapped `/start` button
- [ ] Waited 10 seconds
- [ ] Clicked "Find Telegram Contacts"
- [ ] Contact appeared in list
- [ ] Clicked "Use This ID"
- [ ] Contact name auto-filled
- [ ] Added phone number
- [ ] Clicked "Add Trusted Contact"
- [ ] Tested emergency message
- [ ] ✅ Message received in Telegram

---

## 💡 Pro Tips

- ✓ Have contact keep Telegram open when tapping START
- ✓ Both you and contact should be online during setup
- ✓ Use unique names so you remember who's who
- ✓ Test each contact with a message first
- ✓ If they delete chat, they need to tap /start again

---

**That's it! You're done.** Send emergency alerts via Telegram instantly! 🚀
