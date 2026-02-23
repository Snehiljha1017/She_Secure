from flask import Flask, render_template, request, jsonify
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
import json
import os
from datetime import datetime

app = Flask(__name__)
app.config['APP_NAME'] = 'SheSecure'

# Emergency queue for offline actions
emergency_queue = []

# Load & Train ML Model
df = pd.read_csv("women_safety_data.csv")
X = df[["crime_count", "hour", "crowd_density", "weather"]]
y = df["risk"]
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X, y)

# ==================== MAIN ROUTES ====================

@app.route("/")
def landing():
    """Landing page - home/intro"""
    return render_template("landing.html")

@app.route("/login")
def login():
    """Login page"""
    return render_template("login.html")

@app.route("/signup")
def signup():
    """Signup page"""
    return render_template("signup.html")

@app.route("/dashboard")
def dashboard():
    """Main dashboard - feature hub"""
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

# ==================== LEGACY ROUTES ====================

@app.route("/home")
def home():
    """Legacy home page redirect"""
    return render_template("home.html") if os.path.exists("templates/home.html") else landing()

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
    app.run(debug=True)
