#!/usr/bin/env python3
"""
Convert PROJECT_ANALYSIS_FOR_TEACHER.md to PDF
Using reportlab library
"""

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.lib import colors
from datetime import datetime

# Create PDF
pdf_file = "SheSecure_Project_Analysis.pdf"
doc = SimpleDocTemplate(pdf_file, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)

# Story to add to PDF
story = []

# Styles
styles = getSampleStyleSheet()
title_style = ParagraphStyle(
    'CustomTitle',
    parent=styles['Title'],
    fontSize=24,
    textColor=colors.HexColor('#c04b84'),
    spaceAfter=12,
    alignment=TA_CENTER,
    fontName='Helvetica-Bold'
)

heading_style = ParagraphStyle(
    'CustomHeading',
    parent=styles['Heading1'],
    fontSize=16,
    textColor=colors.HexColor('#d04b84'),
    spaceAfter=8,
    spaceBefore=8,
    fontName='Helvetica-Bold'
)

subheading_style = ParagraphStyle(
    'CustomSubHeading',
    parent=styles['Heading2'],
    fontSize=13,
    textColor=colors.HexColor('#e46b9c'),
    spaceAfter=6,
    spaceBefore=6,
    fontName='Helvetica-Bold'
)

body_style = ParagraphStyle(
    'CustomBody',
    parent=styles['BodyText'],
    fontSize=10,
    alignment=TA_JUSTIFY,
    spaceAfter=6
)

# Title Page
story.append(Spacer(1, 1.5*inch))
story.append(Paragraph("🛡️ SheSecure", title_style))
story.append(Paragraph("Women Safety Application", subheading_style))
story.append(Spacer(1, 0.3*inch))
story.append(Paragraph("Comprehensive Project Analysis for Teachers", styles['Heading3']))
story.append(Spacer(1, 0.5*inch))
story.append(Paragraph(f"Generated: {datetime.now().strftime('%B %d, %Y')}", styles['Normal']))
story.append(Spacer(1, 0.2*inch))
story.append(Paragraph("Project Version: 3.0 (Real-time Messaging Enhanced)", styles['Normal']))
story.append(PageBreak())

# Table of Contents
story.append(Paragraph("Table of Contents", heading_style))
toc_items = [
    "1. Project Overview",
    "2. Technologies Used",
    "3. Code Structure Explanation",
    "4. APIs Used In Project",
    "5. Machine Learning Model",
    "6. Key Technologies & Concepts",
    "7. Working Flow",
    "8. Viva Questions & Answers",
    "9. Improvements & Enhancements",
    "10. File Requirements for Features",
    "11. Summary Table",
    "12. Conclusion"
]

for item in toc_items:
    story.append(Paragraph(item, body_style))

story.append(PageBreak())

# Section 1: PROJECT OVERVIEW
story.append(Paragraph("1. PROJECT OVERVIEW", heading_style))
story.append(Paragraph("<b>What the Project Does:</b>", subheading_style))
story.append(Paragraph(
    "SheSecure is a comprehensive web-based women's safety application designed to "
    "empower women by providing real-time safety information, emergency communication, "
    "and crime data analysis. It works as a 'Personal Safety Assistant' that tells users "
    "how safe an area is, helps contact trusted people instantly when in danger, shows "
    "safest routes to travel, and provides emergency helpline access.",
    body_style
))
story.append(Spacer(1, 0.2*inch))

story.append(Paragraph("<b>Main Features:</b>", subheading_style))
features_data = [
    ["Feature", "Purpose"],
    ["Crime Data Analysis", "Show crime statistics and hotspots"],
    ["Safety Prediction", "Use ML to assess risk level at any location"],
    ["Emergency Messaging", "Send instant messages to trusted contacts"],
    ["Location Sharing", "Share real-time location with family/friends"],
    ["Route Planning", "Suggest safer travel routes avoiding crime"],
    ["Emergency Helplines", "Direct access to 24/7 helpline numbers"],
    ["AI Chatbot", "Provide safety tips and guidance"],
    ["Offline Mode", "Access critical features without internet"],
]

features_table = Table(features_data, colWidths=[2*inch, 3.5*inch])
features_table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#d04b84')),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('FONTSIZE', (0, 0), (-1, 0), 11),
    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
    ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ('FONTSIZE', (0, 1), (-1, -1), 9),
    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#fff5f8')])
]))
story.append(features_table)
story.append(PageBreak())

# Section 2: TECHNOLOGIES USED
story.append(Paragraph("2. TECHNOLOGIES USED", heading_style))

story.append(Paragraph("<b>Backend Stack:</b>", subheading_style))
backend_tech = [
    "Python 3.8+ - Programming Language",
    "Flask 2.0+ - Web Framework",
    "Flask-SocketIO - Real-time WebSocket",
    "Flask-SQLAlchemy - Database ORM",
    "Flask-Login - User Authentication",
    "Werkzeug - Password Hashing (PBKDF2:SHA256)",
    "Pandas - Data Processing",
    "NumPy - Numerical Computing",
    "Scikit-learn - Machine Learning",
    "Joblib - Model Serialization"
]

for tech in backend_tech:
    story.append(Paragraph(f"• {tech}", body_style))

story.append(Spacer(1, 0.15*inch))
story.append(Paragraph("<b>Frontend Stack:</b>", subheading_style))
frontend_tech = [
    "HTML5 - Structure",
    "CSS3 - Styling & Animations",
    "JavaScript (Vanilla) - Client Logic",
    "Leaflet.js - Maps & Visualization",
    "Socket.IO - WebSocket Client",
    "Jinja2 - Template Engine"
]

for tech in frontend_tech:
    story.append(Paragraph(f"• {tech}", body_style))

story.append(Spacer(1, 0.15*inch))
story.append(Paragraph("<b>Database & Storage:</b>", subheading_style))
storage_tech = [
    "SQLite3 - Local Database",
    "SQLAlchemy ORM - Object Mapping",
    "CSV Files - Crime Datasets",
    "JSON Files - Configuration",
    "Browser LocalStorage - Client-side Data"
]

for tech in storage_tech:
    story.append(Paragraph(f"• {tech}", body_style))

story.append(Spacer(1, 0.15*inch))
story.append(Paragraph("<b>External Services:</b>", subheading_style))
services_tech = [
    "Twilio - SMS Gateway (for alerts)",
    "Telegram Bot API - Instant Messaging",
    "Leaflet.js - Open-source Mapping"
]

for tech in services_tech:
    story.append(Paragraph(f"• {tech}", body_style))

story.append(PageBreak())

# Section 3: CODE STRUCTURE
story.append(Paragraph("3. CODE STRUCTURE EXPLANATION", heading_style))

story.append(Paragraph("<b>Project Files (Most Important):</b>", subheading_style))

key_files = [
    ("app.py", "Main Flask application with all routes, database models, ML integration, and WebSocket handlers (1900+ lines)"),
    ("requirements.txt", "List of all Python dependencies (12 packages)"),
    ("templates/", "HTML pages using Jinja2 templating (14 main pages)"),
    ("static/", "CSS, JavaScript, and images for front-end"),
    ("*.csv files", "Crime datasets and training data (6 files)"),
    ("model.pkl", "Pre-trained RandomForest machine learning model"),
    ("instance/site.db", "SQLite database (auto-generated on first run)"),
]

for filename, description in key_files:
    story.append(Paragraph(f"<b>{filename}:</b> {description}", body_style))

story.append(Spacer(1, 0.15*inch))
story.append(Paragraph("<b>Database Models (SQLAlchemy):</b>", subheading_style))

db_models = [
    "User - Store usernames, emails, hashed passwords",
    "Contact - Store trusted contact information",
    "Message - Store real-time messages and alerts",
    "CrimeReport - 40,160+ crime records from India",
    "EnvironmentalCondition - Air quality and weather data",
    "WomenCrimeStat - Women-specific crime statistics"
]

for model in db_models:
    story.append(Paragraph(f"• {model}", body_style))

story.append(PageBreak())

# Section 4: VIVA QUESTIONS
story.append(Paragraph("4. VIVA QUESTIONS & ANSWERS", heading_style))

story.append(Paragraph("<b>Q1: What is SheSecure?</b>", subheading_style))
story.append(Paragraph(
    "SheSecure is a web-based women's safety application. It uses crime data and machine learning "
    "to assess area safety. Key features include: Real-time crime analysis, ML-based risk prediction, "
    "Emergency messaging with one-tap alerts, Route planning to avoid dangerous areas, and Access to "
    "emergency helplines. Women can check if an area is safe before traveling and alert loved ones instantly.",
    body_style
))

story.append(Spacer(1, 0.15*inch))
story.append(Paragraph("<b>Q2: What is the tech stack?</b>", subheading_style))
story.append(Paragraph(
    "<b>Backend:</b> Python + Flask + SQLAlchemy (database) + Flask-SocketIO (real-time messaging)<br/>"
    "<b>Frontend:</b> HTML5, CSS3, JavaScript + Leaflet.js (maps) + Socket.IO (WebSocket)<br/>"
    "<b>ML:</b> scikit-learn RandomForestClassifier for safety prediction<br/>"
    "<b>Database:</b> SQLite with 6 main tables for users, contacts, messages, and crime data",
    body_style
))

story.append(Spacer(1, 0.15*inch))
story.append(Paragraph("<b>Q3: How does ML model work?</b>", subheading_style))
story.append(Paragraph(
    "The model is a RandomForestClassifier trained on 1000+ records. It takes inputs: latitude, longitude, "
    "hour, and day of week. It queries crime database to extract features like crime_count and crowd_density. "
    "The model then predicts a risk score (0-100) and classifies as Low/Guarded/High/Critical. "
    "Why RandomForest? It handles non-linear relationships, needs no feature scaling, and is fast.",
    body_style
))

story.append(Spacer(1, 0.15*inch))
story.append(Paragraph("<b>Q4: How does real-time messaging work?</b>", subheading_style))
story.append(Paragraph(
    "Using WebSocket via Flask-SocketIO. Unlike HTTP (request-response), WebSocket provides bidirectional "
    "communication. When user sends urgent message: client sends via Socket.IO → server broadcasts to ALL "
    "connected clients INSTANTLY → message appears in real-time with no delay. This is critical for emergencies "
    "where delays can be fatal.",
    body_style
))

story.append(Spacer(1, 0.15*inch))
story.append(Paragraph("<b>Q5: How is password security ensured?</b>", subheading_style))
story.append(Paragraph(
    "We use PBKDF2:SHA256 hashing from werkzeug. Each password is salted (unique salt per user) and hashed "
    "200,000 times to slow down brute force attacks. When user logs in, we compare hashed versions, never "
    "storing or comparing plaintext. This prevents data breaches - even if database is stolen, passwords are safe.",
    body_style
))

story.append(PageBreak())

# More Viva Questions
story.append(Paragraph("<b>Q6: What is Haversine formula?</b>", subheading_style))
story.append(Paragraph(
    "It calculates distance between two GPS coordinates on Earth accounting for spherical shape. "
    "Formula: d = 2 × R × arcsin(√(sin²(Δφ/2) + cos(φ₁) × cos(φ₂) × sin²(Δλ/2))). Used in route "
    "planning to find nearest crimes to a path and for calculating distance between locations.",
    body_style
))

story.append(Spacer(1, 0.15*inch))
story.append(Paragraph("<b>Q7: How does route planning work?</b>", subheading_style))
story.append(Paragraph(
    "User enters start/end locations. System generates 6+ alternate routes (direct, north curve, south curve, etc.). "
    "For each route, it samples 100+ waypoints and calculates crime risk at each using database queries. Ranks routes "
    "by lowest risk score. Displays on map with dangerous hotspots marked. Final recommendation includes detour distance "
    "and estimated time.",
    body_style
))

story.append(Spacer(1, 0.15*inch))
story.append(Paragraph("<b>Q8: What is offline mode?</b>", subheading_style))
story.append(Paragraph(
    "Offline mode uses Browser LocalStorage to cache data locally. Critical features work without internet: "
    "Safety prediction (using cached ML model), Emergency alerts (queued for sync), and Helpline numbers "
    "(stored locally). When internet returns, queued messages auto-sync. Implemented using Service Workers "
    "and JavaScript offline detection.",
    body_style
))

story.append(Spacer(1, 0.15*inch))
story.append(Paragraph("<b>Q9: How are APIs protected?</b>", subheading_style))
story.append(Paragraph(
    "Using @login_required decorator from Flask-Login. Public APIs: /login, /signup (no auth needed). "
    "Protected APIs: /api/messages/send, /api/quick/danger-alert (require valid session). Session "
    "maintained via browser cookies. Unauthorized access redirects to login.",
    body_style
))

story.append(Spacer(1, 0.15*inch))
story.append(Paragraph("<b>Q10: What improvements can be made?</b>", subheading_style))
story.append(Paragraph(
    "Short-term: Add 2FA, improve mobile responsiveness. Medium-term: Build iOS/Android apps, "
    "add community features, integrate with police authorities. Long-term: AI chatbot with GPT-4, "
    "wearable device integration, drone emergency dispatch, blockchain for immutable incident records.",
    body_style
))

story.append(PageBreak())

# Data Requirements Table
story.append(Paragraph("5. FILE REQUIREMENTS FOR FEATURES", heading_style))

story.append(Paragraph("<b>Real-Time Messaging Feature Needs:</b>", subheading_style))
story.append(Paragraph(
    "Backend: app.py (Message model + routes + WebSocket handlers), "
    "requirements.txt (flask-socketio, python-socketio, python-engineio), "
    "Database: Message, Contact, User tables. "
    "Frontend: messaging.html template, style.css, Socket.IO JavaScript library.",
    body_style
))

story.append(Spacer(1, 0.15*inch))
story.append(Paragraph("<b>Safety Prediction Feature Needs:</b>", subheading_style))
story.append(Paragraph(
    "Data: women_safety_data.csv (training), crime_dataset_india.csv (crime records), "
    "Enviromental Conditions.csv (weather). "
    "Model: model.pkl (pre-trained RandomForest). "
    "Code: app.py predictor route, predictor.html template, app.js for visualization. "
    "Dependencies: scikit-learn, pandas, numpy, joblib.",
    body_style
))

story.append(Spacer(1, 0.15*inch))
story.append(Paragraph("<b>Route Planning Feature Needs:</b>", subheading_style))
story.append(Paragraph(
    "Data: delhi_crime_hotspots.csv (300+ areas). "
    "Code: app.py route algorithms (haversine_distance_km, build_safer_route_candidates). "
    "Frontend: location.html, Leaflet.js library, JavaScript for map interaction. "
    "Dependencies: pandas, numpy, math. Database: CrimeReport table.",
    body_style
))

story.append(Spacer(1, 0.15*inch))
story.append(Paragraph("<b>Emergency Alert Feature Needs:</b>", subheading_style))
story.append(Paragraph(
    "Setup: Twilio account (SMS) or Telegram Bot token. "
    "Backend: app.py /api/quick/danger-alert route, send_sms_via_gateway(), WebSocket broadcasting. "
    "Frontend: Dashboard.html button, JavaScript geolocation API, style.css. "
    "Database: Contact, Message, User tables. External: Flask-SocketIO.",
    body_style
))

story.append(PageBreak())

# Conclusion
story.append(Paragraph("CONCLUSION", heading_style))
story.append(Paragraph(
    "<b>SheSecure</b> demonstrates comprehensive full-stack web development including: "
    "✅ Backend with Flask and databases, ✅ Frontend with HTML/CSS/JavaScript, "
    "✅ Machine Learning integration, ✅ Real-time communication via WebSocket, "
    "✅ Geospatial calculations, ✅ Security best practices (password hashing), "
    "✅ API design and authentication.",
    body_style
))

story.append(Spacer(1, 0.2*inch))
story.append(Paragraph(
    "The project is <b>production-ready</b> and can be deployed to cloud platforms for scaling. "
    "It demonstrates practical application of computer science principles to solve real-world problems.",
    body_style
))

story.append(Spacer(1, 0.3*inch))
story.append(Paragraph("---", styles['Normal']))
story.append(Paragraph(f"Document Generated: {datetime.now().strftime('%B %d, %Y at %H:%M')}", styles['Normal']))
story.append(Paragraph("Project: SheSecure - Women Safety Application", styles['Normal']))
story.append(Paragraph("Version: 3.0", styles['Normal']))

# Build PDF
doc.build(story)
print(f"✅ PDF created successfully: {pdf_file}")
