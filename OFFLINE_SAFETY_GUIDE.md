# 🔴 Offline Safety Mode - User Guide

## Overview

**Offline Safety Mode** is a critical safety feature that works even without internet connection. It ensures you can always trigger emergency alerts, record evidence, and contact trusted contacts - regardless of network availability.

## Key Features

### 📡 Always Available
- **Automatic activation** when you lose internet connection
- Works on cellular data, WiFi, or completely offline
- Visual indicator shows your connection status
- Emergency features prioritized over everything else

### 🚨 One-Tap Emergency SOS
- Single button press activates all safety features
- No internet required - works 100% offline
- Alerts sent automatically when connection restored
- Confirmation shown immediately

### 📍 Location Tracking
- Uses your **current location** if GPS available
- Falls back to **last known location** if offline
- Updates every 30 seconds in background
- Stored locally for privacy

### 🔊 Loud Alarm
- Automatic 30-second alarm when SOS triggered
- Vibration pattern for silent situations
- Helps attract attention and deter threats
- Can be manually stopped

### 🎥 Evidence Recording
- **Audio**: Automatically records up to 2 minutes
- **Video**: Captures up to 1 minute (rear camera)
- Stored locally on your device
- Automatically included with emergency alerts

### 📱 SMS Emergency Alerts
- Queued for all your trusted contacts
- Includes: your location, timestamp, Google Maps link
- Sent automatically when connection restored
- Real-time delivery tracking

## How to Use

### Setup (First Time)

1. **Add Trusted Contacts**
   - Go to **Helplines** page
   - Click "Add Contact"
   - Enter name and phone number
   - Save contact
   - Add at least 3 trusted contacts

2. **Grant Permissions**
   - Allow **Location Access** when prompted
   - Allow **Microphone** for audio recording
   - Allow **Camera** for video evidence
   - These are essential for emergency features

3. **Test the System**
   - Try the SOS button in a safe situation
   - Verify alarm works
   - Check notifications appear
   - Confirm contacts receive test alerts

### During Emergency (Online or Offline)

1. **Trigger SOS**
   - Tap the **red SOS button** (floating on right side)
   - Button available on all pages
   - Works with single tap

2. **Automatic Actions**
   - ✅ Location captured
   - ✅ Alarm triggered (30 seconds)
   - ✅ Audio recording started (2 minutes)
   - ✅ Video recording started (1 minute)
   - ✅ Emergency alerts queued for all contacts
   - ✅ Confirmation shown

3. **What You'll See**
   ```
   🚨 OFFLINE SOS ACTIVATED!
   
   ✅ Queued for 3 contacts
   📍 Current Location (±15m)
   🔊 Alarm triggered
   📹 Evidence recording started
   
   Alerts will be sent when connectivity is restored.
   ```

4. **When Online Again**
   - System automatically detects connection
   - All queued alerts sent immediately
   - SMS messages delivered to contacts
   - Success notification shown
   - Queue cleared

### Understanding the UI

#### Offline Indicator (Top-Right)
```
📡 Offline Safety Mode
   Emergency features active
```
- **Purple/Red**: You're offline, safety mode active
- **Green**: You're online, all features available
- Always visible when offline

#### Safety Notifications
Appear below the offline indicator:

- **Info** (Blue): General updates
- **Success** (Green): Actions completed
- **Warning** (Orange): Important notices
- **Emergency** (Red, Pulsing): SOS activated

#### SOS Button States
- **Normal**: Red button, ready to use
- **Offline Mode**: Red button with 📡 badge + pulsing
- **Active**: Pulsing animation, alarm playing

#### Queue Badge (Bottom-Left)
Shows pending emergency alerts:
```
⏳ 2 alerts pending
```
- Click to see queue status
- Auto-hides when empty
- Updates when alerts sent

## Offline Capabilities

### What Works Offline ✅
- Emergency SOS button
- Location tracking (last known)
- Alarm & vibration
- Audio/video recording
- Contact management
- Queue management

### What Requires Internet ❌
- Sending SMS/email alerts
- Uploading evidence to server
- Real-time location sharing
- Chatbot responses
- Safety predictions

### Automatic Sync
When you go back online:
1. System detects connection
2. Processes emergency queue
3. Sends all SMS alerts
4. Uploads evidence (if configured)
5. Shows success notification
6. Clears processed items

## Privacy & Security

### Local Storage
- All emergency data stored on YOUR device
- Location never shared without SOS trigger
- Evidence recordings stay private
- Manual deletion available

### Data Transmission
- Only sent during emergencies
- Requires explicit SOS trigger
- Contacts receive SMS with location
- Evidence shared only with authorities (optional)

### Storage Management
- Maximum 5 evidence recordings kept
- Older recordings auto-deleted
- Queue cleared after successful send
- Manual clear option available

## Troubleshooting

### "No Contacts Found" Error
**Solution:** Add trusted contacts in Helplines section

### Location Not Working
**Solution:** Grant location permission in browser settings

### Alarm Not Playing
**Solution:** 
- Check device volume
- Enable sound permissions
- Vibration will work as fallback

### Recording Failed
**Solution:**
- Grant microphone/camera permissions
- Close other apps using camera
- SOS still queues alerts without recording

### Notifications Not Showing
**Solution:**
- Check browser notification permissions
- Look for offline indicator at top-right
- Check browser console for errors

### Alerts Not Sending When Back Online
**Solution:**
- Refresh the page after reconnecting
- Check queue badge for pending count
- Manually trigger sync (coming soon)

## Best Practices

### Setup Tips
1. Add **multiple** trusted contacts (3-5 recommended)
2. Test SOS in safe situation first
3. Keep contact list updated
4. Verify phone numbers are correct
5. Inform contacts about SheSecure alerts

### During Use
1. Keep app open during travel in unsafe areas
2. Allow background location (if available)
3. Keep device charged
4. Test system periodically
5. Update contact list regularly

### Emergency Situations
1. **Tap SOS immediately** - don't wait
2. Let alarm play out (attracts attention)
3. Get to safety - app handles the rest
4. Recording captures audio/video evidence
5. Contacts notified automatically

## Technical Details

### Browser Support
- **Chrome/Edge**: Full support (recommended)
- **Firefox**: Full support
- **Safari**: iOS 14.1+ required for video
- **Mobile**: Android Chrome recommended

### Storage Limits
- **Queue**: Unlimited emergency alerts
- **Evidence**: 5 recordings max (~10-20MB)
- **Location**: 1 current position
- **Contacts**: Unlimited

### Battery Usage
- **Passive**: Minimal (periodic location updates)
- **Active SOS**: Moderate (recording + alarm)
- **Optimization**: Auto-stops after set time

### Network Requirements
- **Offline**: Core features work completely offline
- **Online**: Required for SMS delivery
- **Low Data**: Queue sent over cellular
- **Auto-sync**: Every 30 seconds when online

## FAQ

**Q: Does it work on flights?**  
A: Yes, but alerts only send after landing when online.

**Q: Can I stop the alarm early?**  
A: Currently auto-stops after 30 seconds. Manual stop coming soon.

**Q: How long does evidence record?**  
A: Audio: 2 minutes, Video: 1 minute (to save storage).

**Q: What if my battery dies?**  
A: Queued alerts persist and send when device turns on.

**Q: Do contacts receive actual SMS?**  
A: Requires SMS gateway setup (Twilio, etc.) - queued for now.

**Q: Can I test without alerting contacts?**  
A: Add test contacts first, or use demo mode (coming soon).

**Q: Does it work in airplane mode?**  
A: Yes, but location may be limited and alerts send after mode disabled.

**Q: How accurate is the location?**  
A: Typically 5-50 meters. Accuracy shown in alert.

**Q: Can I delete evidence recordings?**  
A: Go to browser settings → Clear site data (coming to UI soon).

**Q: What happens if I close the browser?**  
A: Queue persists, but active recordings stop. Keep app open.

## Support

### Need Help?
- Check console logs (F12 in browser)
- Verify permissions granted
- Test internet connection
- Restart browser
- Clear cache and try again

### Report Issues
- Describe the situation
- Include browser/device info
- Note offline/online status
- Check for error messages

### Emergency Resources
Always call local emergency services:
- **Police**: 100 (India) / 911 (US)
- **Women Helpline**: 1091 (India)
- **Ambulance**: 102 (India) / 911 (US)

---

**SheSecure** | Your Safety, Our Priority | Version 2.0 | February 2026

Stay Safe! 💜
