Smart Women Safety — College project

Quick start

1. Create and activate a Python virtual environment (recommended).

Windows (PowerShell):
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2. Run the app:
```powershell
python "c:\Users\tanya\OneDrive\Documents\women_safety_control\app.py"
```

3. Open in browser:
- Home: http://127.0.0.1:5000/
- Predictor: http://127.0.0.1:5000/predictor
- Location & Safety: http://127.0.0.1:5000/location
- Helplines: http://127.0.0.1:5000/helpline

Notes
- Emergency alerts are simulated. The server prints recipients and returns JSON from `/alert`.
- Contacts are saved to `contacts.json` in the project root.
- Map uses OpenStreetMap embed (no API key).
- To allow LAN access change `app.run(host='0.0.0.0')` in `app.py`.

Files changed/added
- `app.py`: added `/contacts`, `/alert`, `/helpline`, `/location` routes and contact storage
- `templates/helpline.html`, `templates/location.html` added
- `templates/home.html`, `templates/index.html` updated (SOS button + JS)
- `static/js/app.js` added (client logic)
- `static/style.css` updated (SOS styles, layout)
- `contacts.json` added (initial empty list)
- `requirements.txt`, `README.md` added

If you want, I can run the server here and exercise the endpoints; tell me to proceed if you'd like that.