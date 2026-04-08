# 👩‍💼 She Secure - Smart Women Safety Application

A comprehensive women safety application featuring crime data analysis, emergency alerts, offline safety mode, and community helplines.

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Installation Steps

#### 1. Clone the Repository
```bash
git clone https://github.com/Snehiljha1017/She_Secure.git
cd She_Secure
```

#### 2. Create and Activate Virtual Environment

**Windows (PowerShell):**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

**Windows (Command Prompt):**
```cmd
python -m venv .venv
.venv\Scripts\activate.bat
pip install -r requirements.txt
```

**macOS/Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

#### 3. Run the Application
```bash
python app.py
```

#### 4. Access in Browser
- **Home**: http://127.0.0.1:5000/
- **Dashboard**: http://127.0.0.1:5000/dashboard
- **Crime Predictor**: http://127.0.0.1:5000/predictor
- **Location & Safety**: http://127.0.0.1:5000/location
- **Helplines**: http://127.0.0.1:5000/helpline
- **Online Chat**: http://127.0.0.1:5000/chatbot

## ⚙️ Configuration

- **Emergency alerts** are simulated locally for testing purposes
- **Contacts** are saved to `contacts.json` in the project root
- **Maps** use OpenStreetMap embed (no API key required)
- **Local Network Access**: To allow access from other computers on your network, modify `app.py` and change:
  ```python
  app.run(host='0.0.0.0', debug=True)
  ```

## 📁 Project Structure

- `app.py` - Main Flask application
- `templates/` - HTML templates for different pages
- `static/` - CSS, JavaScript, and animations
- `requirements.txt` - Python dependencies
- `QUICK_START.md` - Testing guide

## 📝 Features

- ✅ Emergency SOS button with offline capability
- ✅ Crime hotspot analysis and prediction
- ✅ Real-time location sharing
- ✅ Emergency helplines directory
- ✅ Offline safety mode with alert queuing
- ✅ Trusted contacts management
- ✅ AI-powered safety chatbot

## 📊 Data Files

- `delhi_crime_hotspots.csv` - Crime hotspot data
- `women_crime_stats.csv` - Statistical analysis
- `women_safety_data.csv` - Safety indicators
- `crime_dataset_india.csv` - Comprehensive crime data

## 🔐 Security Notes

- Contacts are stored locally in JSON format
- Emergency data is queued offline and synced when connection is restored
- Configuration files (`.instance/`) are excluded from version control

Files changed/added
- `app.py`: added `/contacts`, `/alert`, `/helpline`, `/location` routes and contact storage
- `templates/helpline.html`, `templates/location.html` added
- `templates/home.html`, `templates/index.html` updated (SOS button + JS)
- `static/js/app.js` added (client logic)
- `static/style.css` updated (SOS styles, layout)
- `contacts.json` added (initial empty list)
- `requirements.txt`, `README.md` added

If you want, I can run the server here and exercise the endpoints; tell me to proceed if you'd like that.