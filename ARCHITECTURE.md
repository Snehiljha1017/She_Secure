# 🛡️ SheSecure - Application Architecture

## Project Overview

**SheSecure** is a comprehensive women's safety application built with Flask, featuring real-time crime prediction, location tracking, emergency helplines, and an AI chatbot.

## Technology Stack

- **Backend**: Python Flask
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **ML/Data**: Pandas, scikit-learn (RandomForestClassifier)
- **Templating**: Jinja2
- **Storage**: LocalStorage (client-side), JSON files (server-side)

## Directory Structure

```
women_safety_control/
├── app.py                      # Flask application & routes
├── requirements.txt            # Python dependencies
├── women_safety_data.csv       # Training data for ML model
├── contacts.json               # Persistent contacts storage
├── chat.json                   # Chat history
│
├── static/
│   ├── style.css              # Core styling
│   ├── animations.css         # Reusable animations
│   ├── logos.css              # Logo styling
│   └── js/
│       └── app.js             # Client-side logic
│
├── templates/
│   ├── base.html              # Base template (navbar, footer)
│   ├── landing.html           # Landing/intro page
│   ├── login.html             # Login form
│   ├── signup.html            # Signup form
│   ├── dashboard.html         # Main feature hub
│   ├── predictor.html         # Safety prediction
│   ├── location.html          # Location sharing
│   ├── helpline.html          # Emergency contacts
│   ├── chatbot.html           # AI chatbot
│   └── (legacy)
│       ├── home.html
│       ├── index.html
│       └── combined.html
│
└── README.md                   # Project documentation
```

## Application Architecture

### Page Hierarchy

```
Entry Point (/)
    ↓
Landing Page (Intro)
    ↓
User chooses: Login or Continue as Guest
    ↓
Dashboard (Feature Hub)
    ├── Safety Predictor (/predictor)
    ├── Location Sharing (/location)
    ├── Emergency Helplines (/helplines)
    └── Smart Chatbot (/chatbot)
```

### Core Pages

#### 1. **Landing Page** (`landing.html`)
- Beautiful hero section with SheSecure logo
- Feature preview (4 main features)
- Call-to-action buttons
- Animations: fade-in-up, slide-in-left

#### 2. **Authentication Pages**
- **Login** (`login.html`): Email/password form
- **Signup** (`signup.html`): Multi-field registration form
- Stores user session in localStorage
- Redirects to dashboard on success

#### 3. **Dashboard** (`dashboard.html`)
- Stats cards: Trusted Contacts, Emergency Status, Location
- SOS emergency button with pulse animation
- 4 Feature cards (clickable links):
  - Safety Predictor
  - Location Sharing
  - Emergency Helplines
  - Smart Chatbot

#### 4. **Safety Predictor** (`predictor.html`)
- Input: Latitude, Longitude, Hour, Day of Week
- ML Model: RandomForestClassifier
- Output: Safety Score (0-100), Risk Level, Safety Tips
- Risk visualization with color-coded meter

#### 5. **Location Sharing** (`location.html`)
- Fetch current GPS location
- Generate shareable link
- Set safety radius (100-5000m)
- Real-time status display

#### 6. **Emergency Helplines** (`helpline.html`)
- 4 Emergency contacts (Police, Women Helpline, Ambulance, Childline)
- Trusted Contacts Management:
  - Add contacts
  - Edit contacts
  - Delete contacts
  - Quick call buttons

#### 7. **Smart Chatbot** (`chatbot.html`)
- Conversational AI interface
- Keywords: safe, hospital, police, help, contact
- Contextual responses
- Scrollable message history
- Real-time message rendering

#### 8. **Base Template** (`base.html`)
- Navbar with SheSecure logo + navigation
- Floating chatbot button
- Footer with copyright & links
- CSS & JS imports

### Styling System

#### CSS Files
- **style.css**: Core styles (colors, typography, layout)
- **animations.css**: 15+ reusable animation classes
- **logos.css**: Logo styling for navbar and hero

#### Color Scheme
- Primary (Accent): `#6366f1` (Indigo)
- Secondary (Accent-2): `#ff4081` (Pink)
- Gradients: Indigo → Pink

#### Responsive Breakpoints
- Desktop: 1024px+
- Tablet: 768px - 1023px
- Mobile: <768px

### JavaScript Architecture

#### Main Functions (`app.js`)
- `loadContactsList()`: Fetch contacts from localStorage
- `renderContacts()`: Display contact list dynamically
- `addContact()`: Save new contact
- `editContact()`: Modify existing contact
- `deleteContact()`: Remove contact
- `toggleMenu()`: Mobile hamburger menu
- `switchTheme()`: Theme switching (light/dark/high-contrast)

#### Data Storage
- **localStorage**: User data, contacts, preferences
- **JSON files**: Server-side persistent storage
- **Session**: User authentication state

### Flask Routes

#### Page Routes
- `GET /` - Landing page
- `GET /login` - Login form
- `GET /signup` - Signup form
- `GET /dashboard` - Main dashboard
- `GET /predictor` - Safety predictor
- `GET /location` - Location sharing
- `GET /helplines` - Emergency helplines
- `GET /chatbot` - AI chatbot

#### API Endpoints
- `POST /predict` - ML prediction API
- `GET/POST /contacts` - Contact management (legacy)
- `POST /alert` - Emergency alert (legacy)

### Machine Learning Model

**Model Type**: RandomForestClassifier
**Features**: 
- crime_count: Number of crimes in area
- hour: Hour of day (0-23)
- crowd_density: Population density (0-1)
- weather: Weather condition (0-2)

**Target**: Risk level (0=Low, 1=High)
**Training**: women_safety_data.csv (pre-trained)

### Animation Library

```
Fade: fadeIn, fadeInDown, fadeInUp
Slide: slideInLeft, slideInRight, slideInUp
Scale: scaleIn
Effects: bounce, pulse
Stagger: stagger-1 through stagger-4
Timing: 0.5s - 0.8s ease-out
```

### Features Summary

| Feature | Page | Functionality |
|---------|------|---------------|
| **Safety Predictor** | /predictor | ML-based crime risk analysis |
| **Location Sharing** | /location | GPS + map integration |
| **Helplines** | /helplines | Emergency contacts + management |
| **Chatbot** | /chatbot | AI conversation interface |
| **SOS Button** | /dashboard | One-tap emergency alert |
| **Dashboard** | /dashboard | Stats + feature hub |
| **Auth** | /login, /signup | User authentication |

### Performance Considerations

- Static file caching with CSS/JS bundling
- Client-side rendering for contacts
- LocalStorage for instant data access
- Lightweight animations (CSS-based)
- Optimized SVG logos (inline)
- Offline-first architecture with service worker ready

### Security Notes

- Client-side auth (localStorage) - for demo purposes
- CSRF protection should be added for production
- Sensitive data should use secure backend sessions
- SMS/Email backends should be implemented for real alerts
- Evidence encryption recommended for production

## 🔴 Offline Safety Mode

### Overview

**Offline Safety Mode** is a critical feature that ensures user safety even without internet connectivity. It provides emergency functionality through local device capabilities, queued actions, and automatic synchronization when connectivity is restored.

### Key Features

#### 1. **Automatic Offline Detection**
- Real-time monitoring of network connectivity
- Visual indicator showing online/offline status
- Persistent status badge at top-right of screen
- Automatic activation of offline features when disconnected

#### 2. **One-Tap SOS (Offline)**
When SOS is triggered offline:
- Uses **last known location** or attempts to get current location
- Queues emergency alerts for all trusted contacts
- Triggers **loud alarm** (audio + vibration)
- Starts **audio/video evidence recording**
- Stores all data locally until connectivity restored
- Shows confirmation with queued contact count

#### 3. **Emergency SMS Queue**
- Emergency alerts queued locally when offline
- Automatic sending via server when back online
- Includes: location (Google Maps link), timestamp, accuracy
- Backend endpoint: `/emergency/sms` (POST)
- Queue management: `/emergency/process-queue` (POST)
- Status check: `/emergency/queue-status` (GET)

#### 4. **Local Evidence Recording**
- **Audio Recording**: Up to 2 minutes (automatically saved)
- **Video Recording**: Up to 1 minute (rear camera)
- Stored as Base64 in localStorage
- Maximum 5 evidence items kept (storage optimization)
- Auto-cleanup of older evidence

#### 5. **Alarm System**
- Loud beep sound (embedded in code for offline availability)
- 30-second automatic stop
- SOS vibration pattern: long-short-long
- Fallback to vibration if audio fails

#### 6. **Auto-Sync on Reconnect**
- Detects when connectivity is restored
- Automatically processes queued emergencies
- Sends all pending SMS/email alerts
- Updates queue status
- Shows success notification

### Technical Implementation

#### Files Structure
```
static/
├── js/
│   ├── offline-safety.js       # Core offline functionality
│   └── app.js                  # Integration & legacy support
├── offline-safety.css          # Offline UI styling
└── ...

app.py                          # Backend emergency endpoints
```

#### JavaScript Class: `OfflineSafetyMode`

**Key Methods:**
- `setupOnlineDetection()` - Monitor network status
- `triggerOfflineSOS()` - One-tap emergency activation
- `attemptEmergencySMS()` - Queue SMS for contacts
- `triggerAlarm()` - Sound + vibration alerts
- `startRecordingEvidence()` - Audio/video capture
- `processQueuedEmergencies()` - Sync when online
- `saveEvidence()` - Local evidence storage

**Local Storage Keys:**
- `emergency_queue` - Pending emergency actions
- `last_known_location` - GPS coordinates with timestamp
- `emergency_evidence` - Audio/video recordings
- `trusted_contacts` - Emergency contact list

#### Backend Endpoints

**POST /emergency/sms**
```json
{
  "contacts": [{"name": "...", "phone": "..."}],
  "location": {"lat": 0, "lon": 0, "accuracy": 0},
  "timestamp": "2026-02-19T..."
}
```

**POST /emergency/process-queue**
- Processes all queued emergencies
- Returns: `{processed: count, status: "success"}`

**GET /emergency/queue-status**
- Returns: `{queued: count, sent: count, total: count}`

### UI Components

#### 1. **Offline Indicator**
- Fixed position: top-right (below navbar)
- Shows: "Offline Safety Mode" with pulsing icon
- Automatically appears when offline
- Color-coded: Purple (offline), Green (online)

#### 2. **Safety Notifications**
- Toast-style notifications
- Types: info, success, warning, emergency
- Auto-dismiss after 5 seconds (except emergency)
- Emergency notifications pulse and persist

#### 3. **SOS Button Enhancements**
- Adds offline mode badge (📡) when disconnected
- Pulsing animation for better visibility
- Works identically online or offline

#### 4. **Emergency Queue Badge**
- Bottom-left corner indicator
- Shows count of pending emergency alerts
- Clickable to view queue status
- Only visible when queue has items

### User Flow

**Scenario: User triggers SOS while offline**

1. User taps SOS button
2. System detects offline status
3. Gets current location (or uses last known)
4. Loads trusted contacts from localStorage
5. Creates emergency payload with timestamp
6. Queues SMS alerts for all contacts
7. Triggers loud alarm (30 seconds)
8. Starts recording audio (2 min) + video (1 min)
9. Shows confirmation: "SOS ACTIVATED! Queued for X contacts"
10. Saves evidence to localStorage
11. **When connectivity restored:**
    - Detects online status
    - Processes queue automatically
    - Sends all SMS/email alerts
    - Shows success notification
    - Clears processed queue items

### Browser Compatibility

- **Offline Detection**: All modern browsers
- **Geolocation**: All modern browsers
- **MediaRecorder API**: Chrome, Firefox, Edge, Safari 14.1+
- **Vibration API**: Android Chrome, Firefox
- **localStorage**: Universal support

### Storage Limits

- **Queue**: Unlimited (JSON array)
- **Evidence**: 5 items max (~10-20MB typical)
- **Location History**: 1 item (current/last)
- **Contacts**: Unlimited

### Privacy & Security

- All data stored locally on device
- Evidence automatically limited to conserve space
- Queue cleared after successful transmission
- Location stored with accuracy rating
- No data sent to server until user triggers SOS

### Testing Offline Mode

1. Open DevTools → Network tab
2. Set throttling to "Offline"
3. Observe offline indicator appears
4. Trigger SOS button
5. Check console for queue status
6. Verify alarm plays
7. Set back to "Online"
8. Verify automatic queue processing

### Configuration

**Alarm Duration:** 30 seconds (configurable in code)
**Audio Recording:** 2 minutes max
**Video Recording:** 1 minute max
**Queue Check Interval:** 30 seconds
**Location Update:** 30 seconds
**Evidence Limit:** 5 items

### Production Considerations

1. **SMS Gateway Integration**
   - Implement Twilio, AWS SNS, or similar
   - Update `/emergency/sms` endpoint
   - Add authentication & rate limiting

2. **Evidence Encryption**
   - Encrypt recorded media before storage
   - Use Web Crypto API
   - Secure transmission to backend

3. **Service Worker**
   - Add PWA functionality
   - Cache critical assets
   - Enable true offline operation

4. **Backend Queue Persistence**
   - Move from in-memory to database
   - Add queue retry logic
   - Track delivery status

5. **Battery Optimization**
   - Limit recording duration
   - Optimize location polling
   - Reduce wake locks

### Future Enhancements

- Backend user authentication (SQLite/PostgreSQL)
- Real SMS/Email integration for alerts ✅ **IMPLEMENTED**
- Advanced ML models (XGBoost, Neural Networks)
- Push notifications
- Multi-language support
- Progressive Web App (PWA) capabilities
- Bluetooth emergency beacons
- Peer-to-peer offline messaging

---

**Version**: 2.0 (Offline Safety Mode) | **Last Updated**: February 2026 | **Branding**: SheSecure
