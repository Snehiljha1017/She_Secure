# SheSecure Project Handoff

This file is a quick guide for anyone joining the SheSecure project. It explains what the app does, how to run it, and where the important pieces live.

## What SheSecure Is

SheSecure is a Flask-based women safety web app. It combines:
- emergency SOS tools
- trusted contacts
- live location sharing
- safer-travel suggestions based on Delhi crime hotspot data
- crime analytics dashboards
- helplines and support pages
- offline emergency queueing

The goal is to help a user react quickly in unsafe situations and also make safer travel planning easier.

## Main Pages

- `/dashboard` - the main control center
- `/location` - live map, live sharing, and safer travel planner
- `/crime-data` - analytics and Delhi hotspot dataset view
- `/helplines` - emergency numbers and trusted contacts
- `/predictor` - safety risk predictor
- `/chatbot` - safety help chatbot
- `/counselling` - support and counselling page
- `/test-offline` - offline safety test page

## Key Features

### Emergency and SOS

- One-tap SOS support
- Emergency call action
- Emergency message action
- Offline queueing when network is unavailable
- Trusted-contact alerts

### Live Location

- Live tracking on the Location page
- Shareable live link for trusted contacts
- Live-share sessions update while the page stays open
- WhatsApp sharing for the live link

### Safer Travel Planner

- Uses the Delhi crime hotspot dataset
- Lets the user enter point A and point B
- Suggests a lower-risk route for women
- Prefers road-based routing instead of a straight line
- Shows direct route vs safer route
- Can open the route in Google Maps

### Crime Analytics

- Uses the India-wide crime dataset
- Shows charts and filters
- Includes a Delhi police-area hotspot section from the uploaded `crime.csv`

## Important Data Files

- `crime_dataset_india.csv` - main crime analytics dataset
- `women_crime_stats.csv` - women crime statistics
- `women_safety_data.csv` - model training data
- `Enviromental Conditions.csv` - environmental context data
- `delhi_crime_hotspots.csv` - Delhi hotspot dataset used for safer-travel planning

## How the Safer Travel Feature Works

The safer-travel planner does not try to guess with random lines. It:
- looks at the Delhi hotspot dataset
- scores nearby police areas using crime density, rape, gangrape, harassment, robbery, and total crime
- compares a direct path against safer alternatives
- then asks a road-routing service for the actual road geometry

If the routing service is unavailable, it falls back to the safer candidate geometry, but the goal is always a road-like route.

## How Live Sharing Works

The app creates a live-share token on the server and stores the current location in memory.

Important behavior:
- a new live-share link looks like `/live-share/<token>`
- if the server restarts, old live-share tokens become invalid
- the browser now clears stale tokens and creates a fresh one automatically

If you want to share the live link on WhatsApp:
- start live tracking first
- click `Send On WhatsApp`
- the app sends the current `/live-share/...` link to the saved trusted contacts

## Optional Messaging Integrations

The app has code paths for:
- WhatsApp fallback
- Telegram Bot API
- SMS gateway support

These integrations depend on external credentials or device support.

## How To Run Locally

1. Open the project folder.
2. Activate the virtual environment:

```powershell
.\.venv\Scripts\Activate.ps1
```

3. Start the app:

```powershell
python run_server.py
```

4. Open the browser at:

```text
http://127.0.0.1:5000
```

If you want the site reachable from another device on the same Wi-Fi, use the computer’s LAN IP address instead of `127.0.0.1`.

## Where The Main Logic Lives

- `app.py` - Flask routes, live-share API, safer-route API, dataset loading
- `templates/dashboard.html` - dashboard UI, trusted contacts, route planner, live actions
- `templates/location.html` - live map, WhatsApp live sharing, safer travel planner
- `templates/crime_data.html` - crime analytics and hotspot data display
- `static/js/app.js` - emergency actions, live-share logic, WhatsApp/Telegram helpers
- `static/js/offline-safety.js` - offline emergency behavior
- `static/js/sos-button.js` - direct SOS trigger button

## Notes For Future Changes

- Do not store real credentials in the repo.
- Restart the Flask server after changing backend route logic.
- Refresh the browser after changing live-share or map behavior.
- If the safer route feels wrong, check the route scoring in `app.py` and the Location page map rendering in `templates/location.html`.

## Short Summary

SheSecure is a women safety app with SOS, live location, trusted contacts, crime analytics, and a safer-travel planner based on Delhi hotspot data. The most important pages for daily use are the Dashboard and Location pages.
