# Quick Start: Testing Offline Safety Mode

## 🚀 Immediate Testing Steps

### 1. Access the Application
Open your browser and go to: **http://127.0.0.1:5000/dashboard**

### 2. Add Test Contacts (Required)
1. Click "Emergency Helplines" in the navigation
2. Scroll down to "Manage Trusted Contacts"
3. Click "Add Contact"
4. Add at least one contact:
   - Name: Test Contact
   - Phone: 1234567890
5. Save the contact

### 3. Test Offline Mode (Easy Method)
1. Go back to the Dashboard
2. Click the **"🧪 Test Offline Mode"** button
3. You'll see the offline indicator appear at top-right
4. Now click the red **SOS** button
5. You should see/hear:
   - ✅ Loud alarm (beeping sound)
   - ✅ Alert message with details
   - ✅ Queue badge showing pending alerts
   - ✅ Offline indicator pulsing

### 4. Test Offline Mode (Browser Method)
1. Open Developer Tools (Press F12)
2. Go to the **Network** tab
3. Click the dropdown that says "No throttling"
4. Select **"Offline"**
5. You'll see: "📡 Offline Safety Mode" indicator appear
6. Click the SOS button
7. Watch the magic happen!

### 5. View Queue Status
1. Click the **"📋 View Queue"** button on the Dashboard
2. You'll see:
   - Pending alerts count
   - Evidence recorded
   - Last known location
   - Connection status

### 6. Test Auto-Sync
1. While still in offline mode with queued alerts
2. Go back to Network tab in DevTools
3. Change "Offline" back to **"No throttling"**
4. Watch for the success notification
5. Check queue - pending count should be 0

## 🎯 What Each Feature Does

### Offline Indicator (Top-Right)
- **Purple/Red**: You're offline, safety mode active
- **Green with ✅**: You're online

### SOS Button (Red, Center)
- Click once to trigger emergency
- Works online or offline
- Automatic alarm + recording + queue

### Test Button
- Simulates offline mode for 20 seconds
- Perfect for testing without going offline
- Safe to use anytime

### Queue Button
- Shows detailed status
- Pending/sent counts
- Location accuracy
- Evidence details

## 📱 Features You'll Experience

### When You Click SOS:

1. **Immediate Actions** (works offline):
   - 🔊 Loud beeping alarm (30 seconds)
   - 📳 Vibration pattern (if supported)
   - 📍 Location captured
   - 📹 Recording starts (camera + mic permissions needed)

2. **Alert Dialog Shows**:
   ```
   🚨 OFFLINE SOS ACTIVATED!
   
   ✅ Queued for X contacts
   📍 Current Location (±15m)
   🔊 Alarm triggered
   📹 Evidence recording started
   
   Alerts will be sent when connectivity is restored.
   
   💡 Queue Status: Check dashboard for details
   ```

3. **Visual Indicators**:
   - Emergency notification (persistent, red, pulsing)
   - Queue badge at bottom-left
   - Recording indicator (if recording)

4. **When Back Online**:
   - Automatic processing starts
   - All SMS alerts sent to contacts
   - Success notification appears
   - Queue cleared

## 🔧 Permissions You May Need

### First Time Only:
- **Location**: Click "Allow" when prompted
- **Microphone**: Click "Allow" for audio recording
- **Camera**: Click "Allow" for video evidence

*All recordings stay on your device until you manually clear them.*

## ⚡ Quick Tips

1. **No Contacts?** → Go to Helplines page and add some
2. **No Alarm?** → Check browser volume, grant audio permissions
3. **No Location?** → Grant location permission in browser settings
4. **Queue Not Sending?** → Check if you're actually back online
5. **Want to Stop Alarm?** → Wait 30 seconds (auto-stops)

## 📊 Testing Checklist

- [ ] Dashboard loads with offline safety info
- [ ] Can add test contacts
- [ ] Test button triggers offline mode
- [ ] SOS button shows alert
- [ ] Alarm plays (beeping sound)
- [ ] Queue badge appears
- [ ] View queue shows status
- [ ] Browser offline mode works
- [ ] Auto-sync when back online
- [ ] Queue clears after processing

## 🐛 Troubleshooting

### "No contacts found"
→ Add contacts in the Helplines page first

### Alarm not playing
→ Check browser volume, unmute tab, grant permissions

### Offline indicator not showing
→ Manually set browser to offline mode (F12 → Network → Offline)

### Queue not processing
→ Refresh page after going back online

### Location shows 0,0
→ Grant location permission and move around (GPS needs signal)

## 💡 Advanced Testing

### Test Recording:
1. Grant camera/mic permissions
2. Trigger SOS
3. Wait 2 minutes for recording
4. Check localStorage: 
   ```javascript
   localStorage.getItem('emergency_evidence')
   ```

### Test Queue Persistence:
1. Trigger SOS offline
2. Close browser completely
3. Reopen and check queue
4. Go online and watch it process

### Test Location Tracking:
1. Open console (F12)
2. Watch for location updates every 30 seconds
3. Move around to see accuracy changes

## 🎊 Success Indicators

You know it's working when:
- ✅ Offline indicator appears/disappears correctly
- ✅ Alarm plays loud and clear
- ✅ Queue badge shows pending count
- ✅ Notifications appear with details
- ✅ Auto-sync happens when back online
- ✅ Contact count updates on dashboard

## 🚨 Real Emergency Use

**IMPORTANT**: In a real emergency:
1. Click SOS immediately - don't wait
2. Let the alarm play out (attracts attention)
3. Get to safety - app handles the rest
4. Always call emergency services (100/911) as well

---

## Quick Test Script

Copy and run this in your browser console to test everything:

```javascript
// Quick test script
console.log('Testing Offline Safety Mode...');

// 1. Check if loaded
console.log('Offline safety loaded:', typeof offlineSafety !== 'undefined');

// 2. Check contacts
const contacts = JSON.parse(localStorage.getItem('contacts') || '[]');
console.log('Contacts found:', contacts.length);

// 3. Check queue
const queue = JSON.parse(localStorage.getItem('emergency_queue') || '[]');
console.log('Queue items:', queue.length);

// 4. Check location
const location = JSON.parse(localStorage.getItem('last_known_location') || '{}');
console.log('Last location:', location.lat, location.lon);

// 5. Connection status
console.log('Online:', navigator.onLine);

console.log('✅ Test complete! Check results above.');
```

---

**Ready to test!** Go to the dashboard and click the "Test Offline Mode" button! 🎉
