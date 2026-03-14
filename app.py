from flask import Flask, render_template, request, jsonify, flash, redirect, url_for
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
import json
import os
from datetime import datetime
import joblib
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, UserMixin, login_user, current_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['APP_NAME'] = 'SheSecure'
app.config['SECRET_KEY'] = 'your_secret_key_here'  # Change this to a random secret key
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'

db = SQLAlchemy(app)
migrate = Migrate(app, db)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Emergency queue for offline actions
emergency_queue = []

# Load & Train ML Model
model_file = 'model.pkl'
if os.path.exists(model_file):
    model = joblib.load(model_file)
else:
    df = pd.read_csv("women_safety_data.csv")
    X = df[["crime_count", "hour", "crowd_density", "weather"]]
    y = df["risk"]
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X, y)
    joblib.dump(model, model_file)

# Database Models
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    contacts = db.relationship('Contact', backref='user', lazy=True)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"

class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class CrimeReport(db.Model):
    """Crime dataset from India"""
    id = db.Column(db.Integer, primary_key=True)
    report_number = db.Column(db.Integer)
    date_reported = db.Column(db.String(100))
    city = db.Column(db.String(100))
    crime_code = db.Column(db.Integer)
    crime_description = db.Column(db.String(200))
    victim_age = db.Column(db.Integer)
    victim_gender = db.Column(db.String(10))
    weapon_used = db.Column(db.String(100))
    crime_domain = db.Column(db.String(100))
    police_deployed = db.Column(db.Integer)
    case_closed = db.Column(db.String(10))

class EnvironmentalCondition(db.Model):
    """Environmental and air quality conditions"""
    id = db.Column(db.Integer, primary_key=True)
    city = db.Column(db.String(100))
    date = db.Column(db.String(100))
    pm25 = db.Column(db.Float)
    pm10 = db.Column(db.Float)
    no2 = db.Column(db.Float)
    so2 = db.Column(db.Float)
    co = db.Column(db.Float)
    o3 = db.Column(db.Float)
    temperature = db.Column(db.Float)
    humidity = db.Column(db.Float)

class WomenCrimeStat(db.Model):
    """Women-centric crime statistics by district"""
    id = db.Column(db.Integer, primary_key=True)
    year = db.Column(db.Integer)
    state_name = db.Column(db.String(100))
    district_name = db.Column(db.String(100))
    rape_women_above_18 = db.Column(db.Float)
    rape_girls_below_18 = db.Column(db.Float)
    dowry_deaths = db.Column(db.Float)
    assaults = db.Column(db.Float)
    cruelty_by_husband = db.Column(db.Float)
    kidnapping_abduction = db.Column(db.Float)
    human_trafficking = db.Column(db.Float)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ==================== DATA IMPORT FUNCTIONS ====================

def import_crime_data():
    """Import crime dataset from CSV"""
    try:
        if CrimeReport.query.first() is None:
            crime_df = pd.read_csv("crime_dataset_india.csv")
            for _, row in crime_df.iterrows():
                crime = CrimeReport(
                    report_number=row.get('Report Number'),
                    date_reported=str(row.get('Date Reported')),
                    city=row.get('City'),
                    crime_code=row.get('Crime Code'),
                    crime_description=row.get('Crime Description'),
                    victim_age=row.get('Victim Age'),
                    victim_gender=row.get('Victim Gender'),
                    weapon_used=row.get('Weapon Used'),
                    crime_domain=row.get('Crime Domain'),
                    police_deployed=row.get('Police Deployed'),
                    case_closed=row.get('Case Closed')
                )
                db.session.add(crime)
            db.session.commit()
    except Exception as e:
        print(f"Error importing crime data: {e}")

def import_environmental_data():
    """Import environmental conditions from CSV"""
    try:
        if EnvironmentalCondition.query.first() is None:
            env_df = pd.read_csv("Enviromental Conditions.csv")
            for _, row in env_df.iterrows():
                env = EnvironmentalCondition(
                    city=row.get('City'),
                    date=str(row.get('Date')),
                    pm25=row.get('PM2.5'),
                    pm10=row.get('PM10'),
                    no2=row.get('NO2'),
                    so2=row.get('SO2'),
                    co=row.get('CO'),
                    o3=row.get('O3'),
                    temperature=row.get('Temperature'),
                    humidity=row.get('Humidity')
                )
                db.session.add(env)
            db.session.commit()
    except Exception as e:
        print(f"Error importing environmental data: {e}")

def import_women_crime_stats():
    """Import women crime statistics from CSV"""
    try:
        if WomenCrimeStat.query.first() is None:
            women_df = pd.read_csv("women_crime_stats.csv")
            for _, row in women_df.iterrows():
                women = WomenCrimeStat(
                    year=row.get('year'),
                    state_name=row.get('state_name'),
                    district_name=row.get('district_name'),
                    rape_women_above_18=row.get('rape_women_above_18'),
                    rape_girls_below_18=row.get('rape_girls_below_18'),
                    dowry_deaths=row.get('dowry_deaths'),
                    assaults=row.get('assault_on_womenabove_18'),
                    cruelty_by_husband=row.get('cruelty_by_husband_or_his_relatives'),
                    kidnapping_abduction=row.get('kidnapping_and_abduction'),
                    human_trafficking=row.get('human_trafficking')
                )
                db.session.add(women)
            db.session.commit()
    except Exception as e:
        print(f"Error importing women crime stats: {e}")

# ==================== MAIN ROUTES ====================

@app.route("/")
def landing():
    """Landing page with dataset impact metrics"""
    try:
        total_crimes = CrimeReport.query.count()
        cities_count = db.session.query(func.count(distinct(CrimeReport.city))).scalar()
        crime_types_count = db.session.query(func.count(distinct(CrimeReport.crime_description))).scalar()
        dataset_stats = {
            'total_crimes': total_crimes,
            'cities': cities_count,
            'crime_types': crime_types_count
        }
    except Exception:
        dataset_stats = {'total_crimes': 0, 'cities': 0, 'crime_types': 0}

    # landing.html now handles rendering the metrics section
    return render_template("home.html", dataset_stats=dataset_stats)

@app.route("/login", methods=['GET', 'POST'])
def login():
    """Login page"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Login unsuccessful. Please check username and password', 'danger')
    return render_template("login.html")

@app.route("/signup", methods=['GET', 'POST'])
def signup():
    """Signup page"""
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Check if user already exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists. Please choose a different one.', 'danger')
            return render_template("signup.html")
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered. Please use a different email or login.', 'danger')
            return render_template("signup.html")
        
        try:
            hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
            user = User(username=username, email=email, password=hashed_password)
            db.session.add(user)
            db.session.commit()
            flash('Your account has been created! You can now log in', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating account: {str(e)}', 'danger')
            return render_template("signup.html")
    return render_template("signup.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('landing'))

@app.route("/dashboard")
@login_required
def dashboard():
    """Main dashboard - feature hub"""
    return render_template("dashboard.html")

@app.route("/crime-data")
@login_required
def crime_data():
    """Crime data analytics dashboard"""
    try:
        # Get statistics
        total_crimes = CrimeReport.query.count()
        cities_count = db.session.query(CrimeReport.city).distinct().count()
        crime_types_count = db.session.query(CrimeReport.crime_description).distinct().count()

        # Calculate average police deployed
        avg_police_result = db.session.query(db.func.avg(CrimeReport.police_deployed)).scalar()
        avg_police = round(avg_police_result, 1) if avg_police_result else 0

        # Get initial data (first 25 records)
        crimes = CrimeReport.query.limit(25).all()

        # Get filter options
        cities = [row[0] for row in db.session.query(CrimeReport.city).distinct().all()]
        crime_types = [row[0] for row in db.session.query(CrimeReport.crime_description).distinct().all()]

        stats = {
            'total_crimes': total_crimes,
            'cities': cities_count,
            'crime_types': crime_types_count,
            'avg_police': avg_police
        }

        return render_template("crime_data.html",
                             stats=stats,
                             crimes=crimes,
                             cities=sorted(cities),
                             crime_types=sorted(crime_types))
    except Exception as e:
        print(f"Error loading crime data page: {e}")
        return render_template("dashboard.html")

@app.route("/test-offline")
def test_offline():
    """Offline Safety Mode test page"""
    return render_template("test_offline.html")

@app.route("/counselling")
def counselling():
    """Secure counselling & mental health support portal"""
    return render_template("counselling.html")

# ==================== FEATURE PAGES ====================

@app.route("/predictor")
def predictor():
    """Safety prediction page"""
    return render_template("predictor.html")

@app.route("/location")
def location():
    """Location sharing page"""
    return render_template("location.html")

@app.route("/helplines")
def helplines():
    """Emergency helplines & contacts"""
    return render_template("helpline.html")

@app.route("/chatbot")
def chatbot():
    """Smart chatbot page"""
    return render_template("chatbot.html")

# ==================== API ENDPOINTS ====================

@app.route("/predict", methods=["POST"])
def predict():
    """API for safety prediction"""
    try:
        crime = int(request.form.get("crime", 0))
        hour = int(request.form.get("hour", 12))
        crowd = float(request.form.get("crowd", 0.5))
        weather = int(request.form.get("weather", 0))
        
        sample = np.array([[crime, hour, crowd, weather]])
        prediction = model.predict(sample)[0]
        risk_level = "HIGH RISK" if prediction == 1 else "LOW RISK"
        
        return jsonify({"status": "ok", "risk": risk_level})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route("/emergency/sms", methods=["POST"])
def send_emergency_sms():
    """API to send emergency SMS (placeholder - integrate with SMS gateway)"""
    try:
        data = request.get_json()
        contacts = data.get("contacts", [])
        location = data.get("location", {})
        timestamp = data.get("timestamp", datetime.now().isoformat())
        
        # In production, integrate with SMS gateway (Twilio, AWS SNS, etc.)
        # For now, log the emergency
        emergency_data = {
            "timestamp": timestamp,
            "contacts": contacts,
            "location": location,
            "status": "queued"
        }
        emergency_queue.append(emergency_data)
        
        print(f"EMERGENCY SMS QUEUED: {len(contacts)} contacts at {location}")
        
        return jsonify({
            "status": "success",
            "message": f"Emergency alert queued for {len(contacts)} contacts",
            "queue_id": len(emergency_queue) - 1
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route("/emergency/process-queue", methods=["POST"])
def process_emergency_queue():
    """Process queued emergency actions when connectivity is restored"""
    try:
        processed = 0
        for item in emergency_queue:
            if item["status"] == "queued":
                # Process each queued emergency
                # In production: send actual SMS, email, push notifications
                print(f"Processing emergency from {item['timestamp']}")
                item["status"] = "sent"
                item["processed_at"] = datetime.now().isoformat()
                processed += 1
        
        return jsonify({
            "status": "success",
            "processed": processed,
            "message": f"Processed {processed} emergency alerts"
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route("/emergency/queue-status", methods=["GET"])
def get_queue_status():
    """Get status of emergency queue"""
    queued = sum(1 for item in emergency_queue if item["status"] == "queued")
    sent = sum(1 for item in emergency_queue if item["status"] == "sent")
    
    return jsonify({
        "status": "success",
        "queued": queued,
        "sent": sent,
        "total": len(emergency_queue)
    })

# ==================== DATA API ENDPOINTS ====================

@app.route("/api/crime-data", methods=["GET"])
def get_crime_data():
    """Get crime data by city and optional crime type"""
    city = request.args.get('city')
    crime_type = request.args.get('crime_type')
    limit = request.args.get('limit', 10, type=int)
    try:
        query = CrimeReport.query
        if city:
            query = query.filter_by(city=city)
        if crime_type:
            query = query.filter_by(crime_description=crime_type)
        crimes = query.limit(limit).all()
        data = [{
            'id': c.id,
            'city': c.city,
            'crime_description': c.crime_description,
            'victim_age': c.victim_age,
            'victim_gender': c.victim_gender,
            'weapon': c.weapon_used,
            'police_deployed': c.police_deployed
        } for c in crimes]
        return jsonify({'status': 'success', 'data': data})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400

@app.route("/api/environmental-data", methods=["GET"])
def get_environmental_data():
    """Get environmental conditions by city"""
    city = request.args.get('city')
    limit = request.args.get('limit', 10, type=int)
    try:
        if city:
            envs = EnvironmentalCondition.query.filter_by(city=city).limit(limit).all()
        else:
            envs = EnvironmentalCondition.query.limit(limit).all()
        data = [{
            'id': e.id,
            'city': e.city,
            'date': e.date,
            'pm25': float(e.pm25) if e.pm25 else None,
            'pm10': float(e.pm10) if e.pm10 else None,
            'temperature': float(e.temperature) if e.temperature else None,
            'humidity': float(e.humidity) if e.humidity else None
        } for e in envs]
        return jsonify({'status': 'success', 'data': data})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400

@app.route("/api/women-crime-stats", methods=["GET"])
def get_women_crime_stats():
    """Get women crime statistics by state/district"""
    state = request.args.get('state')
    district = request.args.get('district')
    limit = request.args.get('limit', 10, type=int)
    try:
        query = WomenCrimeStat.query
        if state:
            query = query.filter_by(state_name=state)
        if district:
            query = query.filter_by(district_name=district)
        stats = query.limit(limit).all()
        data = [{
            'id': s.id,
            'year': s.year,
            'state': s.state_name,
            'district': s.district_name,
            'rape_women': float(s.rape_women_above_18) if s.rape_women_above_18 else 0,
            'rape_girls': float(s.rape_girls_below_18) if s.rape_girls_below_18 else 0,
            'dowry_deaths': float(s.dowry_deaths) if s.dowry_deaths else 0,
            'cruelty': float(s.cruelty_by_husband) if s.cruelty_by_husband else 0,
            'human_trafficking': float(s.human_trafficking) if s.human_trafficking else 0
        } for s in stats]
        return jsonify({'status': 'success', 'data': data})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400

@app.route("/api/cities", methods=["GET"])
def get_cities():
    """Get all available cities"""
    try:
        crime_cities = [c.city for c in db.session.query(CrimeReport.city).distinct()]
        return jsonify({'status': 'success', 'cities': list(set(crime_cities))})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400

# ==================== LEGACY ROUTES ====================

@app.route("/home")
def home():
    """Legacy home page redirect"""
    return render_template("home.html") if os.path.exists("templates/home.html") else landing()

# duplicate landing route removed; use the primary definition above

@app.route("/index")
def index_page():
    """Legacy index page redirect"""
    return predictor()

@app.route("/all")
def combined():
    """Combined view page"""
    try:
        return render_template("combined.html")
    except:
        return dashboard()

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        print("Creating databases and importing CSV data...")
        # ensure a demo user exists for quick login
        if not User.query.filter_by(username='teacher').first():
            demo = User(username='teacher', email='teacher@example.com',
                        password=generate_password_hash('secret123'))
            db.session.add(demo)
            db.session.commit()
            print("Inserted demo user: teacher / secret123")
        import_crime_data()
        import_environmental_data()
        import_women_crime_stats()
        print("Data import complete!")
    app.run(debug=True)
