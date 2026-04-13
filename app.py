from flask import Flask, render_template, request, jsonify, flash, redirect, url_for, session
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
import json
import os
import socket
import math
from datetime import datetime
import base64
from urllib import parse, request as urlrequest, error as urlerror
from uuid import uuid4
import joblib
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, UserMixin, login_user, current_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from flask_socketio import SocketIO, emit, join_room, leave_room

app = Flask(__name__, instance_path=os.path.join(os.path.dirname(__file__), 'instance'))
app.config['APP_NAME'] = 'SheSecure'
app.config['SECRET_KEY'] = os.urandom(16).hex() if os.getenv('SECRET_KEY') is None else os.getenv('SECRET_KEY')

# Ensure instance path exists
os.makedirs(app.instance_path, exist_ok=True)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(app.instance_path, 'site.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
socketio = SocketIO(app, cors_allowed_origins="*")

# Emergency queue for offline actions
emergency_queue = []
live_share_sessions = {}
telegram_live_sessions = {}


def detect_local_network_ip():
    """Best-effort detection of the local LAN IP address."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.connect(("8.8.8.8", 80))
            return sock.getsockname()[0]
    except Exception:
        return "127.0.0.1"


def build_public_base_url():
    """Return a shareable base URL, preferring an explicit public URL or LAN IP."""
    explicit_public_url = os.getenv("PUBLIC_BASE_URL", "").strip()
    if explicit_public_url:
        return explicit_public_url.rstrip("/")

    request_host = request.host.split(":")[0]
    request_scheme = request.scheme
    request_port = request.host.split(":")[1] if ":" in request.host else None

    if request_host in {"127.0.0.1", "localhost"}:
        local_ip = detect_local_network_ip()
        port = request_port or "5000"
        return f"{request_scheme}://{local_ip}:{port}"

    return request.host_url.rstrip("/")


def load_sms_gateway_settings():
    """Load SMS gateway settings from environment variables or a local instance config."""
    settings = {
        "account_sid": os.getenv("TWILIO_ACCOUNT_SID", "").strip(),
        "auth_token": os.getenv("TWILIO_AUTH_TOKEN", "").strip(),
        "from_number": os.getenv("TWILIO_FROM_NUMBER", "").strip()
    }

    if all(settings.values()):
        return settings

    config_path = os.path.join(app.instance_path, "sms_gateway.json")
    if os.path.exists(config_path):
        try:
            with open(config_path, "r", encoding="utf-8") as config_file:
                config_data = json.load(config_file)
            settings["account_sid"] = settings["account_sid"] or str(config_data.get("TWILIO_ACCOUNT_SID", "")).strip()
            settings["auth_token"] = settings["auth_token"] or str(config_data.get("TWILIO_AUTH_TOKEN", "")).strip()
            settings["from_number"] = settings["from_number"] or str(config_data.get("TWILIO_FROM_NUMBER", "")).strip()
        except Exception:
            pass

    return settings


def load_telegram_bot_settings():
    """Load Telegram bot settings from environment variables or local instance config."""
    settings = {
        "bot_token": os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
    }

    if settings["bot_token"]:
        return settings

    config_path = os.path.join(app.instance_path, "telegram_bot.json")
    if os.path.exists(config_path):
        try:
            with open(config_path, "r", encoding="utf-8") as config_file:
                config_data = json.load(config_file)
            settings["bot_token"] = str(config_data.get("TELEGRAM_BOT_TOKEN", "")).strip()
        except Exception:
            pass

    return settings


def telegram_bot_configured():
    settings = load_telegram_bot_settings()
    return bool(settings["bot_token"])


def telegram_api_request(method_name, payload):
    """Call the Telegram Bot API using JSON."""
    settings = load_telegram_bot_settings()
    bot_token = settings["bot_token"]

    if not bot_token:
        raise RuntimeError("Telegram bot is not configured. Set TELEGRAM_BOT_TOKEN first.")

    api_request = urlrequest.Request(
        f"https://api.telegram.org/bot{bot_token}/{method_name}",
        data=json.dumps(payload).encode("utf-8"),
        method="POST",
        headers={"Content-Type": "application/json"}
    )

    try:
        with urlrequest.urlopen(api_request, timeout=20) as response:
            response_body = response.read().decode("utf-8")
            response_data = json.loads(response_body)
            if not response_data.get("ok"):
                raise RuntimeError(response_data.get("description", "Telegram request failed."))
            return response_data.get("result")
    except urlerror.HTTPError as exc:
        error_body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Telegram rejected the request: {error_body}") from exc
    except urlerror.URLError as exc:
        raise RuntimeError(f"Could not reach Telegram: {exc.reason}") from exc


def telegram_api_get(method_name, query=None):
    """Call a Telegram Bot API GET endpoint."""
    settings = load_telegram_bot_settings()
    bot_token = settings["bot_token"]

    if not bot_token:
        raise RuntimeError("Telegram bot is not configured. Set TELEGRAM_BOT_TOKEN first.")

    query_string = ""
    if query:
        query_string = "?" + parse.urlencode(query)

    api_url = f"https://api.telegram.org/bot{bot_token}/{method_name}{query_string}"

    try:
        with urlrequest.urlopen(api_url, timeout=20) as response:
            response_body = response.read().decode("utf-8")
            response_data = json.loads(response_body)
            if not response_data.get("ok"):
                raise RuntimeError(response_data.get("description", "Telegram request failed."))
            return response_data.get("result")
    except urlerror.HTTPError as exc:
        error_body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Telegram rejected the request: {error_body}") from exc
    except urlerror.URLError as exc:
        raise RuntimeError(f"Could not reach Telegram: {exc.reason}") from exc


def get_contact_telegram_chat_id(contact):
    """Return a Telegram chat ID from either a model object or a dict."""
    if isinstance(contact, dict):
        return str(contact.get("telegram_chat_id") or contact.get("telegramChatId") or "").strip()

    return str(getattr(contact, "telegram_chat_id", "") or "").strip()


def build_telegram_location_suffix(location):
    """Append a map link when a coordinate pair is available."""
    if not isinstance(location, dict):
        return ""

    lat = location.get("lat")
    lon = location.get("lon")
    if lat is None or lon is None:
        return ""

    return (
        f"\n\n📍 Location: {lat}, {lon}"
        f"\n🗺️ https://maps.google.com/?q={lat},{lon}"
    )


def build_telegram_message_text(message, location=None):
    """Combine the caller's text with location details when available."""
    base_message = str(message or "").strip()
    location_suffix = build_telegram_location_suffix(location)

    if not location_suffix:
        return base_message

    if "maps.google.com" in base_message or "Location:" in base_message:
        return base_message

    return f"{base_message}{location_suffix}"


def send_telegram_live_location(contact, location, intro_message=None, live_period=3600):
    """Send a live Telegram location pin, optionally preceded by a text note."""
    chat_id = get_contact_telegram_chat_id(contact)
    if not chat_id:
        raise RuntimeError("Missing Telegram chat ID.")

    lat = location.get("lat") if isinstance(location, dict) else None
    lon = location.get("lon") if isinstance(location, dict) else None
    if lat is None or lon is None:
        raise RuntimeError("Live location coordinates are required.")

    if intro_message:
        telegram_api_request("sendMessage", {
            "chat_id": chat_id,
            "text": str(intro_message).strip()
        })

    return telegram_api_request("sendLocation", {
        "chat_id": chat_id,
        "latitude": lat,
        "longitude": lon,
        "live_period": live_period
    })


def sms_gateway_configured():
    """Check whether Twilio SMS credentials are available."""
    settings = load_sms_gateway_settings()
    return all(settings.values())


def send_sms_via_gateway(phone, message):
    """Send a real SMS through Twilio when credentials are configured."""
    settings = load_sms_gateway_settings()
    account_sid = settings["account_sid"]
    auth_token = settings["auth_token"]
    from_number = settings["from_number"]

    if not all([account_sid, auth_token, from_number]):
        raise RuntimeError(
            "SMS gateway is not configured. Set TWILIO_ACCOUNT_SID, "
            "TWILIO_AUTH_TOKEN, and TWILIO_FROM_NUMBER."
        )

    payload = parse.urlencode({
        "To": phone,
        "From": from_number,
        "Body": message
    }).encode("utf-8")

    auth_header = base64.b64encode(f"{account_sid}:{auth_token}".encode("utf-8")).decode("utf-8")
    sms_request = urlrequest.Request(
        f"https://api.twilio.com/2010-04-01/Accounts/{account_sid}/Messages.json",
        data=payload,
        method="POST",
        headers={
            "Authorization": f"Basic {auth_header}",
            "Content-Type": "application/x-www-form-urlencoded"
        }
    )

    try:
        with urlrequest.urlopen(sms_request, timeout=20) as response:
            response_body = response.read().decode("utf-8")
            return json.loads(response_body)
    except urlerror.HTTPError as exc:
        error_body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Gateway rejected the SMS request: {error_body}") from exc
    except urlerror.URLError as exc:
        raise RuntimeError(f"Could not reach the SMS gateway: {exc.reason}") from exc

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
    password = db.Column(db.String(255), nullable=False)
    contacts = db.relationship('Contact', backref='user', lazy=True)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"

class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    telegram_chat_id = db.Column(db.String(100), nullable=True)  # Telegram user ID for alerts
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class Message(db.Model):
    """Real-time emergency messages between users and contacts"""
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    receiver_phone = db.Column(db.String(20), nullable=True)  # For sending to non-registered contacts
    message_text = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    is_read = db.Column(db.Boolean, default=False)
    message_type = db.Column(db.String(20), default='text')  # text, emergency_alert, location_share
    is_emergency = db.Column(db.Boolean, default=False)
    sender = db.relationship('User', foreign_keys=[sender_id], backref='sent_messages')

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


def load_delhi_hotspot_data():
    """Load the merged police-area crime dataset from the uploaded CSV."""
    try:
        hotspot_path = "delhi_crime_hotspots.csv"
        if not os.path.exists(hotspot_path):
            return pd.DataFrame()

        hotspot_df = pd.read_csv(hotspot_path)
        hotspot_df.columns = [str(column).strip() for column in hotspot_df.columns]

        numeric_columns = [
            "murder", "rape", "gangrape", "robbery", "theft",
            "assualt murders", "sexual harassement", "totarea",
            "totalcrime", "long", "lat", "crime/area", "area"
        ]
        for column in numeric_columns:
            if column in hotspot_df.columns:
                hotspot_df[column] = pd.to_numeric(hotspot_df[column], errors="coerce").fillna(0)

        if not hotspot_df.empty:
            density_max = max(float(hotspot_df["crime/area"].max()), 1.0)
            totalcrime_max = max(float(hotspot_df["totalcrime"].max()), 1.0)
            rape_max = max(float(hotspot_df["rape"].max()), 1.0)
            gangrape_max = max(float(hotspot_df["gangrape"].max()), 1.0)
            harassment_max = max(float(hotspot_df["sexual harassement"].max()), 1.0)
            robbery_max = max(float(hotspot_df["robbery"].max()), 1.0)

            hotspot_df["women_risk_score"] = (
                hotspot_df["crime/area"] / density_max * 32
                + hotspot_df["totalcrime"] / totalcrime_max * 20
                + hotspot_df["rape"] / rape_max * 18
                + hotspot_df["gangrape"] / gangrape_max * 10
                + hotspot_df["sexual harassement"] / harassment_max * 12
                + hotspot_df["robbery"] / robbery_max * 8
            )

            hotspot_df["risk_band"] = pd.cut(
                hotspot_df["women_risk_score"],
                bins=[-0.01, 18, 34, 52, 1000],
                labels=["Lower", "Guarded", "High", "Critical"]
            ).astype(str)

        return hotspot_df
    except Exception as e:
        print(f"Error loading Delhi hotspot data: {e}")
        return pd.DataFrame()


def load_merged_crime_travel_data():
    """Load the merged crime dataset for travel route planning."""
    try:
        travel_path = "merged_crime_travel_data.csv"
        if not os.path.exists(travel_path):
            return pd.DataFrame()
        
        travel_df = pd.read_csv(travel_path)
        return travel_df
    except Exception as e:
        print(f"Error loading merged crime travel data: {e}")
        return pd.DataFrame()


def clamp_number(value, minimum, maximum):
    return max(minimum, min(maximum, value))


def haversine_distance_km(lat1, lon1, lat2, lon2):
    earth_radius_km = 6371.0088
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)

    lat_delta = lat2_rad - lat1_rad
    lon_delta = lon2_rad - lon1_rad

    arc = (
        math.sin(lat_delta / 2) ** 2
        + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(lon_delta / 2) ** 2
    )
    return 2 * earth_radius_km * math.asin(math.sqrt(arc))


def interpolate_coordinate(start_value, end_value, ratio):
    return start_value + (end_value - start_value) * ratio


def build_route_hotspot_options(hotspot_df):
    if hotspot_df.empty:
        return []

    route_columns = ["nm_pol", "lat", "long", "women_risk_score", "totalcrime", "crime/area", "risk_band"]
    route_df = hotspot_df[route_columns].copy()
    route_df = route_df.sort_values(by="nm_pol")
    route_df = route_df.rename(columns={"nm_pol": "name", "long": "lon"})
    route_df["women_risk_score"] = route_df["women_risk_score"].round(2)
    route_df["crime/area"] = route_df["crime/area"].round(2)
    return route_df.to_dict("records")


def build_delhi_bounds(hotspot_df):
    if hotspot_df.empty:
        return {
            "lat_min": 28.45,
            "lat_max": 28.86,
            "lon_min": 76.90,
            "lon_max": 77.34
        }

    return {
        "lat_min": float(hotspot_df["lat"].min()) - 0.01,
        "lat_max": float(hotspot_df["lat"].max()) + 0.01,
        "lon_min": float(hotspot_df["long"].min()) - 0.01,
        "lon_max": float(hotspot_df["long"].max()) + 0.01
    }


def clamp_point_to_bounds(lat, lon, bounds):
    return (
        clamp_number(lat, bounds["lat_min"], bounds["lat_max"]),
        clamp_number(lon, bounds["lon_min"], bounds["lon_max"])
    )


def build_hotspot_records(hotspot_df):
    if hotspot_df.empty:
        return []

    records = []
    for row in hotspot_df.to_dict("records"):
        records.append({
            "name": str(row.get("nm_pol", "Unknown")).strip(),
            "lat": float(row.get("lat", 0)),
            "lon": float(row.get("long", 0)),
            "totalcrime": float(row.get("totalcrime", 0)),
            "crime_density": float(row.get("crime/area", 0)),
            "rape": float(row.get("rape", 0)),
            "gangrape": float(row.get("gangrape", 0)),
            "harassment": float(row.get("sexual harassement", 0)),
            "robbery": float(row.get("robbery", 0)),
            "women_risk_score": float(row.get("women_risk_score", 0)),
            "risk_band": str(row.get("risk_band", "Guarded"))
        })
    return records


def polyline_length_km(points):
    total_distance = 0.0
    for index in range(len(points) - 1):
        start = points[index]
        end = points[index + 1]
        total_distance += haversine_distance_km(start["lat"], start["lon"], end["lat"], end["lon"])
    return total_distance


def sample_route_points(points, samples_per_segment=12):
    if len(points) <= 1:
        return points

    samples = []
    for index in range(len(points) - 1):
        start = points[index]
        end = points[index + 1]
        for step in range(samples_per_segment):
            ratio = step / samples_per_segment
            samples.append({
                "lat": interpolate_coordinate(start["lat"], end["lat"], ratio),
                "lon": interpolate_coordinate(start["lon"], end["lon"], ratio)
            })
    samples.append(points[-1])
    return samples


def point_route_risk(lat, lon, hotspot_records):
    if not hotspot_records:
        return 0.0

    weighted_risk = 0.0
    weight_total = 0.0
    immediate_penalty = 0.0

    for hotspot in hotspot_records:
        distance_km = haversine_distance_km(lat, lon, hotspot["lat"], hotspot["lon"])
        weight = math.exp(-distance_km / 2.4)
        weighted_risk += hotspot["women_risk_score"] * weight
        weight_total += weight

        if distance_km <= 1.2:
            immediate_penalty = max(
                immediate_penalty,
                hotspot["women_risk_score"] * (1.25 - distance_km) / 1.25
            )

    base_risk = weighted_risk / max(weight_total, 1e-9)
    return base_risk + immediate_penalty * 0.5


def minimum_hotspot_distance_km(hotspot, route_samples):
    return min(
        haversine_distance_km(hotspot["lat"], hotspot["lon"], sample["lat"], sample["lon"])
        for sample in route_samples
    )


def nearest_hotspot_area(lat, lon, hotspot_records):
    if not hotspot_records:
        return None

    nearest = min(
        hotspot_records,
        key=lambda hotspot: haversine_distance_km(lat, lon, hotspot["lat"], hotspot["lon"])
    )
    return {
        "name": nearest["name"],
        "distance_km": round(haversine_distance_km(lat, lon, nearest["lat"], nearest["lon"]), 2),
        "risk_band": nearest["risk_band"]
    }


def risk_label_from_score(score):
    if score >= 58:
        return "High-risk"
    if score >= 40:
        return "Guarded"
    if score >= 24:
        return "Moderate"
    return "Lower-risk"


def format_waypoint_label(point, hotspot_records):
    nearest = nearest_hotspot_area(point["lat"], point["lon"], hotspot_records)
    if nearest and nearest["distance_km"] <= 2.2:
        return f"{nearest['name']} side"
    return "Route checkpoint"


def evaluate_route_candidate(name, points, hotspot_records, direct_distance_km):
    route_samples = sample_route_points(points)
    point_risks = [point_route_risk(point["lat"], point["lon"], hotspot_records) for point in route_samples]
    distance_km = polyline_length_km(points)
    detour_ratio = distance_km / max(direct_distance_km, 0.25)
    route_score = (
        float(np.mean(point_risks)) * 0.58
        + float(np.max(point_risks)) * 0.32
        + max(0.0, detour_ratio - 1.0) * 22
    )

    hotspots_along_route = []
    for hotspot in hotspot_records:
        min_distance_km = minimum_hotspot_distance_km(hotspot, route_samples)
        if min_distance_km <= 2.4:
            hotspot_copy = dict(hotspot)
            hotspot_copy["distance_km"] = round(min_distance_km, 2)
            hotspots_along_route.append(hotspot_copy)

    hotspots_along_route = sorted(
        hotspots_along_route,
        key=lambda hotspot: (hotspot["distance_km"], -hotspot["women_risk_score"])
    )

    return {
        "name": name,
        "points": points,
        "distance_km": round(distance_km, 2),
        "avg_point_risk": round(float(np.mean(point_risks)), 2),
        "peak_point_risk": round(float(np.max(point_risks)), 2),
        "route_score": round(route_score, 2),
        "risk_label": risk_label_from_score(route_score),
        "detour_ratio": round(detour_ratio, 3),
        "nearby_hotspots": hotspots_along_route[:6]
    }


def build_safer_route_candidates(start_point, end_point, hotspot_records, bounds):
    start_lat = start_point["lat"]
    start_lon = start_point["lon"]
    end_lat = end_point["lat"]
    end_lon = end_point["lon"]

    lat_delta = end_lat - start_lat
    lon_delta = end_lon - start_lon
    straight_line_degrees = math.hypot(lat_delta, lon_delta)
    direct_route = [{"lat": start_lat, "lon": start_lon}, {"lat": end_lat, "lon": end_lon}]

    if straight_line_degrees < 1e-5:
        return [{"name": "Direct route", "points": direct_route}]

    perpendicular_lat = lon_delta / straight_line_degrees
    perpendicular_lon = -lat_delta / straight_line_degrees
    base_offset = clamp_number(straight_line_degrees * 0.55, 0.02, 0.09)

    def shifted_point(ratio, offset_multiplier, direction):
        base_lat = interpolate_coordinate(start_lat, end_lat, ratio)
        base_lon = interpolate_coordinate(start_lon, end_lon, ratio)
        shifted_lat = base_lat + perpendicular_lat * base_offset * offset_multiplier * direction
        shifted_lon = base_lon + perpendicular_lon * base_offset * offset_multiplier * direction
        safe_lat, safe_lon = clamp_point_to_bounds(shifted_lat, shifted_lon, bounds)
        return {"lat": safe_lat, "lon": safe_lon}

    candidates = [
        {"name": "Direct route", "points": direct_route},
        {
            "name": "North arc",
            "points": [direct_route[0], shifted_point(0.33, 0.7, 1), shifted_point(0.5, 1.0, 1), shifted_point(0.66, 0.7, 1), direct_route[1]]
        },
        {
            "name": "South arc",
            "points": [direct_route[0], shifted_point(0.33, 0.7, -1), shifted_point(0.5, 1.0, -1), shifted_point(0.66, 0.7, -1), direct_route[1]]
        },
        {
            "name": "Wide north arc",
            "points": [direct_route[0], shifted_point(0.28, 0.9, 1), shifted_point(0.5, 1.35, 1), shifted_point(0.72, 0.9, 1), direct_route[1]]
        },
        {
            "name": "Wide south arc",
            "points": [direct_route[0], shifted_point(0.28, 0.9, -1), shifted_point(0.5, 1.35, -1), shifted_point(0.72, 0.9, -1), direct_route[1]]
        }
    ]

    denominator = lat_delta ** 2 + lon_delta ** 2
    corridor_candidates = []
    for hotspot in sorted(hotspot_records, key=lambda item: item["women_risk_score"]):
        if denominator <= 0:
            break

        projection_ratio = (
            ((hotspot["lat"] - start_lat) * lat_delta) + ((hotspot["lon"] - start_lon) * lon_delta)
        ) / denominator
        if projection_ratio < 0.2 or projection_ratio > 0.8:
            continue

        projection_point = {
            "lat": interpolate_coordinate(start_lat, end_lat, projection_ratio),
            "lon": interpolate_coordinate(start_lon, end_lon, projection_ratio)
        }
        corridor_distance_km = haversine_distance_km(
            hotspot["lat"],
            hotspot["lon"],
            projection_point["lat"],
            projection_point["lon"]
        )
        if corridor_distance_km > 7:
            continue

        corridor_candidates.append(hotspot)
        if len(corridor_candidates) == 2:
            break

    for hotspot in corridor_candidates:
        candidates.append({
            "name": f"Lower-risk corridor via {hotspot['name']}",
            "points": [
                direct_route[0],
                {"lat": hotspot["lat"], "lon": hotspot["lon"]},
                direct_route[1]
            ]
        })

    return candidates


def build_route_narrative(best_route, direct_route, avoided_hotspots):
    if best_route["name"] == "Direct route":
        return (
            "The straight route already scores as the lowest-risk option against the current Delhi hotspot map, "
            "so the app is recommending that direct path instead of forcing a detour."
        )

    hotspot_names = ", ".join(hotspot["name"] for hotspot in avoided_hotspots[:3])
    if hotspot_names:
        return (
            f"The recommended path bends away from higher-pressure areas such as {hotspot_names}, "
            "trading a small detour for lower exposure to rape, harassment, robbery, and overall crime density."
        )

    return (
        "The route shifts into a lower-risk corridor based on the Delhi police-area crime map, "
        "keeping distance from denser hotspot clusters while still staying practical."
    )


def build_safer_route_response(start_lat, start_lon, end_lat, end_lon):
    hotspot_df = load_delhi_hotspot_data()
    if hotspot_df.empty:
        raise ValueError("Delhi hotspot data is not available yet.")

    hotspot_records = build_hotspot_records(hotspot_df)
    bounds = build_delhi_bounds(hotspot_df)

    start_point = {"lat": float(start_lat), "lon": float(start_lon)}
    end_point = {"lat": float(end_lat), "lon": float(end_lon)}

    candidate_routes = build_safer_route_candidates(start_point, end_point, hotspot_records, bounds)
    direct_distance_km = polyline_length_km(candidate_routes[0]["points"])
    evaluated_routes = [
        evaluate_route_candidate(candidate["name"], candidate["points"], hotspot_records, direct_distance_km)
        for candidate in candidate_routes
    ]
    evaluated_routes = sorted(evaluated_routes, key=lambda candidate: candidate["route_score"])

    best_route = evaluated_routes[0]
    direct_route = next(
        (route for route in evaluated_routes if route["name"] == "Direct route"),
        evaluated_routes[0]
    )

    best_route_samples = sample_route_points(best_route["points"])
    direct_route_samples = sample_route_points(direct_route["points"])

    avoided_hotspots = []
    for hotspot in hotspot_records:
        direct_distance = minimum_hotspot_distance_km(hotspot, direct_route_samples)
        best_distance = minimum_hotspot_distance_km(hotspot, best_route_samples)
        if direct_distance <= 1.8 and best_distance >= direct_distance + 0.7:
            avoided_hotspots.append({
                "name": hotspot["name"],
                "risk_band": hotspot["risk_band"],
                "women_risk_score": round(hotspot["women_risk_score"], 2),
                "totalcrime": int(hotspot["totalcrime"]),
                "direct_distance_km": round(direct_distance, 2),
                "safer_route_distance_km": round(best_distance, 2)
            })

    avoided_hotspots = sorted(avoided_hotspots, key=lambda hotspot: hotspot["women_risk_score"], reverse=True)[:5]
    direct_score = max(direct_route["route_score"], 1.0)
    score_improvement = max(0.0, direct_route["route_score"] - best_route["route_score"])
    risk_reduction_pct = round((score_improvement / direct_score) * 100, 1)

    start_nearest = nearest_hotspot_area(start_point["lat"], start_point["lon"], hotspot_records)
    end_nearest = nearest_hotspot_area(end_point["lat"], end_point["lon"], hotspot_records)

    waypoint_data = []
    for index, point in enumerate(best_route["points"]):
        if index == 0:
            label = "Start"
        elif index == len(best_route["points"]) - 1:
            label = "Destination"
        else:
            label = format_waypoint_label(point, hotspot_records)

        waypoint_data.append({
            "label": label,
            "lat": round(point["lat"], 5),
            "lon": round(point["lon"], 5)
        })

    outside_delhi = not (
        bounds["lat_min"] <= start_point["lat"] <= bounds["lat_max"]
        and bounds["lon_min"] <= start_point["lon"] <= bounds["lon_max"]
        and bounds["lat_min"] <= end_point["lat"] <= bounds["lat_max"]
        and bounds["lon_min"] <= end_point["lon"] <= bounds["lon_max"]
    )

    return {
        "status": "success",
        "mode": "hotspot-aware-routing",
        "message": "Safer route suggestion ready.",
        "warning": (
            "One or both points sit outside the Delhi hotspot bounds, so this is a best-effort suggestion."
            if outside_delhi else None
        ),
        "start": {
            "lat": round(start_point["lat"], 5),
            "lon": round(start_point["lon"], 5),
            "nearest_area": start_nearest
        },
        "destination": {
            "lat": round(end_point["lat"], 5),
            "lon": round(end_point["lon"], 5),
            "nearest_area": end_nearest
        },
        "recommended_route": {
            "name": best_route["name"],
            "risk_label": best_route["risk_label"],
            "route_score": best_route["route_score"],
            "distance_km": best_route["distance_km"],
            "extra_distance_km": round(max(0.0, best_route["distance_km"] - direct_route["distance_km"]), 2),
            "estimated_minutes": max(4, int(round(best_route["distance_km"] / 24 * 60))),
            "risk_reduction_pct": risk_reduction_pct,
            "summary": build_route_narrative(best_route, direct_route, avoided_hotspots),
            "waypoints": waypoint_data,
            "points": best_route["points"],
            "nearby_hotspots": best_route["nearby_hotspots"]
        },
        "direct_route": {
            "distance_km": direct_route["distance_km"],
            "route_score": direct_route["route_score"],
            "risk_label": direct_route["risk_label"],
            "points": direct_route["points"]
        },
        "alternatives": [
            {
                "name": route["name"],
                "distance_km": route["distance_km"],
                "route_score": route["route_score"],
                "risk_label": route["risk_label"]
            }
            for route in evaluated_routes[:4]
        ],
        "avoided_hotspots": avoided_hotspots,
        "display_hotspots": sorted(
            hotspot_records,
            key=lambda hotspot: hotspot["women_risk_score"],
            reverse=True
        )[:14]
    }

# ==================== MAIN ROUTES ====================

@app.route("/")
def landing():
    """Start on signup for new users, or send signed-in users to the dashboard."""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('signup'))

@app.route("/login", methods=['GET', 'POST'])
def login():
    """Login page"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        if not username or not password:
            flash('Please provide both username and password.', 'danger')
            return render_template("login.html")
        
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password, password):
            login_user(user, remember=True)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('dashboard'))
        else:
            flash('Login unsuccessful. Please check your username and password.', 'danger')
    
    return render_template("login.html")

@app.route("/signup", methods=['GET', 'POST'])
def signup():
    """Signup page"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        password_confirm = request.form.get('password_confirm', '')
        
        # Validate inputs
        if not username or len(username) < 3 or len(username) > 20:
            flash('Username must be between 3-20 characters long.', 'danger')
            return render_template("signup.html")
        
        if not email or '@' not in email:
            flash('Please provide a valid email address.', 'danger')
            return render_template("signup.html")
        
        if not password or len(password) < 6:
            flash('Password must be at least 6 characters long.', 'danger')
            return render_template("signup.html")
        
        if password != password_confirm:
            flash('Passwords do not match. Please try again.', 'danger')
            return render_template("signup.html")
        
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
            flash('Your account has been created! You can now log in.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating account. Please try again.', 'danger')
            print(f"Signup error: {str(e)}")
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
    hotspot_df = load_delhi_hotspot_data()
    route_hotspots = build_route_hotspot_options(hotspot_df)
    return render_template("dashboard.html", route_hotspots=route_hotspots)

@app.route("/crime-data")
@login_required
def crime_data():
    """Crime data analytics dashboard"""
    try:
        hotspot_df = load_delhi_hotspot_data()

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

        hotspot_stats = {
            'total_areas': 0,
            'highest_totalcrime_area': 'Not available',
            'highest_totalcrime_value': 0,
            'highest_density_area': 'Not available',
            'highest_density_value': 0
        }
        hotspot_rows = []

        if not hotspot_df.empty:
            hotspot_sorted = hotspot_df.sort_values(by="totalcrime", ascending=False)
            density_sorted = hotspot_df.sort_values(by="crime/area", ascending=False)
            hotspot_stats = {
                'total_areas': int(len(hotspot_df.index)),
                'highest_totalcrime_area': str(hotspot_sorted.iloc[0].get("nm_pol", "Unknown")),
                'highest_totalcrime_value': int(hotspot_sorted.iloc[0].get("totalcrime", 0)),
                'highest_density_area': str(density_sorted.iloc[0].get("nm_pol", "Unknown")),
                'highest_density_value': round(float(density_sorted.iloc[0].get("crime/area", 0)), 2)
            }

            hotspot_rows = hotspot_sorted.head(10).to_dict("records")

        return render_template("crime_data.html",
                             stats=stats,
                             crimes=crimes,
                             cities=sorted(cities),
                             crime_types=sorted(crime_types),
                             hotspot_stats=hotspot_stats,
                             hotspot_rows=hotspot_rows)
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
    hotspot_df = load_delhi_hotspot_data()
    travel_df = load_merged_crime_travel_data()
    route_hotspots = build_route_hotspot_options(hotspot_df)
    
    # Get top safe and risky cities
    travel_cities = []
    if not travel_df.empty:
        # Sort by risk - get highest and lowest
        travel_cities = travel_df[['City', 'Risk_Score', 'Risk_Level']].to_dict('records')
    
    return render_template("location.html", route_hotspots=route_hotspots, travel_cities=travel_cities)

@app.route("/live-share/<token>")
def live_share_view(token):
    """Public live tracking page for trusted contacts."""
    session = live_share_sessions.get(token)
    return render_template("live_share.html", token=token, session=session)

@app.route("/helplines")
def helplines():
    """Emergency helplines & contacts"""
    return render_template("helpline.html")

@app.route("/chatbot")
def chatbot():
    """Smart chatbot page"""
    return render_template("chatbot.html")

# ==================== API ENDPOINTS ====================

@app.route("/api/live-share/start", methods=["POST"])
def start_live_share():
    """Start a live-sharing session and return a shareable tracking link."""
    try:
        data = request.get_json() or {}
        location = data.get("location", {})
        token = str(uuid4())
        session = {
            "token": token,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "location": location
        }
        live_share_sessions[token] = session
        share_url = f"{build_public_base_url()}{url_for('live_share_view', token=token)}"
        return jsonify({
            "status": "success",
            "token": token,
            "share_url": share_url,
            "location": location
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route("/api/live-share/<token>/update", methods=["POST"])
def update_live_share(token):
    """Update the latest location for an existing live-sharing session."""
    try:
        session = live_share_sessions.get(token)
        if not session:
            return jsonify({"status": "error", "message": "Live-share session not found."}), 404

        data = request.get_json() or {}
        location = data.get("location", {})
        session["location"] = location
        session["updated_at"] = datetime.now().isoformat()
        share_url = f"{build_public_base_url()}{url_for('live_share_view', token=token)}"
        return jsonify({
            "status": "success",
            "token": token,
            "share_url": share_url,
            "location": location
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route("/api/live-share/<token>", methods=["GET"])
def get_live_share(token):
    """Fetch the current location for a live-sharing session."""
    session = live_share_sessions.get(token)
    if not session:
        return jsonify({"status": "error", "message": "Live-share session not found."}), 404

    return jsonify({
        "status": "success",
        "token": token,
        "updated_at": session.get("updated_at"),
        "location": session.get("location", {})
    })


@app.route("/api/telegram/message", methods=["POST"])
def send_telegram_message():
    """Send a Telegram text message to trusted contacts."""
    try:
        if not telegram_bot_configured():
            return jsonify({
                "status": "error",
                "message": "Telegram bot is not configured."
            }), 400

        data = request.get_json() or {}
        contacts = data.get("contacts", [])
        message = data.get("message", "").strip()
        location = data.get("location", {})

        if not contacts:
            return jsonify({"status": "error", "message": "No Telegram contacts were provided."}), 400
        if not message:
            return jsonify({"status": "error", "message": "Message text is required."}), 400

        sent = []
        failed = []

        for contact in contacts:
            chat_id = get_contact_telegram_chat_id(contact)
            name = contact.get("name", "Trusted Contact")
            if not chat_id:
                failed.append({"name": name, "error": "Missing Telegram chat ID."})
                continue

            try:
                result = telegram_api_request("sendMessage", {
                    "chat_id": chat_id,
                    "text": build_telegram_message_text(message, location)
                })
                sent.append({
                    "name": name,
                    "chat_id": chat_id,
                    "message_id": result.get("message_id")
                })
            except Exception as exc:
                failed.append({
                    "name": name,
                    "chat_id": chat_id,
                    "error": str(exc)
                })

        return jsonify({
            "status": "success" if not failed else "partial",
            "delivery": "telegram",
            "message": f"Telegram alerts sent to {len(sent)} contact(s).",
            "sent": sent,
            "failed": failed,
            "telegram_configured": True
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400


@app.route("/api/telegram/discovered-chats", methods=["GET"])
def get_telegram_discovered_chats():
    """List chats that have already started the configured Telegram bot."""
    try:
        if not telegram_bot_configured():
            return jsonify({
                "status": "error",
                "message": "Telegram bot is not configured."
            }), 400

        updates = telegram_api_get("getUpdates", {"timeout": 1})
        discovered = {}

        for update in updates or []:
            message = update.get("message") or update.get("edited_message") or {}
            chat = message.get("chat") or {}
            chat_id = chat.get("id")
            if not chat_id:
                continue

            username = chat.get("username") or message.get("from", {}).get("username") or ""
            first_name = chat.get("first_name") or message.get("from", {}).get("first_name") or ""
            last_name = chat.get("last_name") or message.get("from", {}).get("last_name") or ""
            display_name = " ".join(part for part in [first_name, last_name] if part).strip() or username or str(chat_id)

            discovered[str(chat_id)] = {
                "chat_id": str(chat_id),
                "username": username,
                "name": display_name
            }

        return jsonify({
            "status": "success",
            "telegram_configured": True,
            "contacts": list(discovered.values())
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400


@app.route("/api/telegram/live/start", methods=["POST"])
def start_telegram_live():
    """Start a Telegram live location session for trusted contacts."""
    try:
        if not telegram_bot_configured():
            return jsonify({
                "status": "error",
                "message": "Telegram bot is not configured."
            }), 400

        data = request.get_json() or {}
        contacts = data.get("contacts", [])
        location = data.get("location", {})
        intro_message = data.get("message", "").strip()
        live_period = int(data.get("live_period", 3600))

        lat = location.get("lat")
        lon = location.get("lon")
        if lat is None or lon is None:
            return jsonify({"status": "error", "message": "Live location coordinates are required."}), 400

        session_id = str(uuid4())
        recipients = []
        failed = []

        for contact in contacts:
            chat_id = get_contact_telegram_chat_id(contact)
            name = contact.get("name", "Trusted Contact")
            if not chat_id:
                failed.append({"name": name, "error": "Missing Telegram chat ID."})
                continue

            try:
                if intro_message:
                    telegram_api_request("sendMessage", {
                        "chat_id": chat_id,
                        "text": intro_message
                    })

                live_result = telegram_api_request("sendLocation", {
                    "chat_id": chat_id,
                    "latitude": lat,
                    "longitude": lon,
                    "live_period": live_period
                })

                recipients.append({
                    "name": name,
                    "chat_id": chat_id,
                    "message_id": live_result.get("message_id")
                })
            except Exception as exc:
                failed.append({
                    "name": name,
                    "chat_id": chat_id,
                    "error": str(exc)
                })

        telegram_live_sessions[session_id] = {
            "session_id": session_id,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "recipients": recipients,
            "location": location
        }

        return jsonify({
            "status": "success" if not failed else "partial",
            "delivery": "telegram",
            "session_id": session_id,
            "message": f"Telegram live location started for {len(recipients)} contact(s).",
            "recipients": recipients,
            "failed": failed
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400


@app.route("/api/telegram/live/<session_id>/update", methods=["POST"])
def update_telegram_live(session_id):
    """Update Telegram live location for an active session."""
    try:
        if not telegram_bot_configured():
            return jsonify({
                "status": "error",
                "message": "Telegram bot is not configured."
            }), 400

        session = telegram_live_sessions.get(session_id)
        if not session:
            return jsonify({"status": "error", "message": "Telegram live session not found."}), 404

        data = request.get_json() or {}
        location = data.get("location", {})
        lat = location.get("lat")
        lon = location.get("lon")
        if lat is None or lon is None:
            return jsonify({"status": "error", "message": "Live location coordinates are required."}), 400

        updated = []
        failed = []

        for recipient in session.get("recipients", []):
            try:
                telegram_api_request("editMessageLiveLocation", {
                    "chat_id": recipient["chat_id"],
                    "message_id": recipient["message_id"],
                    "latitude": lat,
                    "longitude": lon
                })
                updated.append({
                    "name": recipient.get("name"),
                    "chat_id": recipient.get("chat_id")
                })
            except Exception as exc:
                failed.append({
                    "name": recipient.get("name"),
                    "chat_id": recipient.get("chat_id"),
                    "error": str(exc)
                })

        session["updated_at"] = datetime.now().isoformat()
        session["location"] = location

        return jsonify({
            "status": "success" if not failed else "partial",
            "session_id": session_id,
            "message": f"Telegram live location updated for {len(updated)} contact(s).",
            "updated": updated,
            "failed": failed
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

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
    """API to send emergency SMS to trusted contacts."""
    try:
        data = request.get_json() or {}
        contacts = data.get("contacts", [])
        location = data.get("location", {})
        message = data.get("message", "").strip()
        mode = data.get("mode", "emergency")
        timestamp = data.get("timestamp", datetime.now().isoformat())

        if not contacts:
            return jsonify({
                "status": "error",
                "message": "No trusted contacts were provided."
            }), 400

        if not message:
            return jsonify({
                "status": "error",
                "message": "Message text is required."
            }), 400

        emergency_data = {
            "timestamp": timestamp,
            "contacts": contacts,
            "location": location,
            "message": message,
            "mode": mode,
            "status": "queued"
        }
        emergency_queue.append(emergency_data)

        sent = []
        failed = []

        if sms_gateway_configured():
            for contact in contacts:
                contact_name = contact.get("name", "Trusted Contact")
                phone = contact.get("phone", "").strip()
                if not phone:
                    failed.append({
                        "name": contact_name,
                        "phone": phone,
                        "error": "Missing phone number."
                    })
                    continue

                try:
                    gateway_response = send_sms_via_gateway(phone, message)
                    sent.append({
                        "name": contact_name,
                        "phone": phone,
                        "sid": gateway_response.get("sid")
                    })
                except Exception as exc:
                    failed.append({
                        "name": contact_name,
                        "phone": phone,
                        "error": str(exc)
                    })

            emergency_data["status"] = "sent" if not failed else "partial"
            emergency_data["sent"] = sent
            emergency_data["failed"] = failed
        else:
            emergency_data["status"] = "queued"
            print(f"EMERGENCY SMS QUEUED: {len(contacts)} contacts at {location}")

        return jsonify({
            "status": "success" if not failed else "partial",
            "delivery": "gateway" if sms_gateway_configured() else "queued",
            "message": (
                f"Sent alerts to {len(sent)} contact(s)."
                if sms_gateway_configured()
                else f"Direct server SMS is not configured yet for {len(contacts)} contact(s)."
            ),
            "queue_id": len(emergency_queue) - 1,
            "sent": sent,
            "failed": failed,
            "gateway_configured": sms_gateway_configured()
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
                if sms_gateway_configured():
                    sent = []
                    failed = []

                    for contact in item.get("contacts", []):
                        phone = contact.get("phone", "").strip()
                        name = contact.get("name", "Trusted Contact")
                        if not phone:
                            failed.append({"name": name, "phone": phone, "error": "Missing phone number."})
                            continue

                        try:
                            gateway_response = send_sms_via_gateway(phone, item.get("message", "Emergency alert from SheSecure."))
                            sent.append({
                                "name": name,
                                "phone": phone,
                                "sid": gateway_response.get("sid")
                            })
                        except Exception as exc:
                            failed.append({
                                "name": name,
                                "phone": phone,
                                "error": str(exc)
                            })

                    item["status"] = "sent" if not failed else "partial"
                    item["sent"] = sent
                    item["failed"] = failed
                else:
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

# ==================== QUICK EMERGENCY ENDPOINT ====================

@app.route("/api/test-telegram", methods=["GET"])
@login_required
def test_telegram():
    """Test if Telegram is working - debugging endpoint"""
    try:
        settings = load_telegram_bot_settings()
        bot_token = settings["bot_token"]
        
        # Get all user's contacts
        contacts = Contact.query.filter_by(user_id=current_user.id).all()
        
        config_exists = os.path.exists(os.path.join(app.instance_path, "telegram_bot.json"))
        
        return jsonify({
            "status": "success",
            "telegram_configured": telegram_bot_configured(),
            "bot_token_exists": bool(bot_token),
            "bot_token_preview": f"{bot_token[:20]}..." if bot_token else "None",
            "config_file_exists": config_exists,
            "config_path": os.path.join(app.instance_path, "telegram_bot.json"),
            "contacts_total": len(contacts),
            "contacts_with_telegram": sum(1 for c in contacts if c.telegram_chat_id),
            "contacts_list": [
                {
                    "id": c.id,
                    "name": c.name,
                    "phone": c.phone,
                    "telegram_chat_id": c.telegram_chat_id,
                    "has_tg": bool(c.telegram_chat_id)
                }
                for c in contacts
            ]
        }), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/api/emergency/danger", methods=["POST"])
@login_required
def emergency_danger():
    """
    ONE-TAP EMERGENCY: Send "I'm in Danger" alert + live location to all trusted contacts
    (both SMS and Telegram simultaneously)
    """
    try:
        data = request.get_json() or {}
        location = data.get("location", {})
        lat = location.get("lat")
        lon = location.get("lon")
        
        # Get all user's contacts
        contacts = Contact.query.filter_by(user_id=current_user.id).all()
        
        if not contacts:
            return jsonify({"status": "error", "message": "No trusted contacts found"}), 400
        
        sent_sms = 0
        failed_sms = 0
        sent_telegram = 0
        failed_telegram = 0
        sms_errors = []
        telegram_errors = []
        
        # Emergency message
        emergency_msg = f"🚨 EMERGENCY: {current_user.username} is in danger!"
        if lat and lon:
            emergency_msg += f"\n📍 Location: {lat}, {lon}"
            emergency_msg += f"\n🗺️ https://maps.google.com/?q={lat},{lon}"
        
        # Send SMS to phone contacts
        for contact in contacts:
            if contact.phone:
                try:
                    # Queue for SMS gateway
                    emergency_queue.append({
                        "id": str(uuid4()),
                        "timestamp": datetime.utcnow(),
                        "phone": contact.phone,
                        "message": emergency_msg,
                        "status": "queued"
                    })
                    sent_sms += 1
                except Exception as e:
                    failed_sms += 1
                    sms_errors.append(f"{contact.name}: {str(e)}")
        
        # Send Telegram to Telegram contacts - DIRECT AND VERIFIED
        settings = load_telegram_bot_settings()
        bot_token = settings.get("bot_token", "").strip()
        
        if bot_token:
            for contact in contacts:
                chat_id = str(contact.telegram_chat_id or "").strip()
                
                if chat_id and chat_id.isdigit():
                    try:
                        print(f"\n[TELEGRAM] Attempting send...")
                        print(f"[TELEGRAM] Chat ID: {chat_id}")
                        print(f"[TELEGRAM] Message: {emergency_msg}")
                        print(f"[TELEGRAM] Bot Token: {bot_token[:20]}...")
                        
                        # Make direct API request
                        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
                        payload = {
                            "chat_id": chat_id,
                            "text": emergency_msg
                        }
                        
                        api_request = urlrequest.Request(
                            url,
                            data=json.dumps(payload).encode("utf-8"),
                            method="POST",
                            headers={"Content-Type": "application/json"}
                        )
                        
                        with urlrequest.urlopen(api_request, timeout=10) as response:
                            response_body = response.read().decode("utf-8")
                            response_data = json.loads(response_body)
                            
                            print(f"[TELEGRAM] Response: {response_data}")
                            
                            if response_data.get("ok"):
                                print(f"[TELEGRAM] ✅ SUCCESS - Message sent!")
                                sent_telegram += 1
                            else:
                                error_desc = response_data.get("description", "Unknown error")
                                print(f"[TELEGRAM] ❌ FAILED - {error_desc}")
                                failed_telegram += 1
                                telegram_errors.append(f"{contact.name}: {error_desc}")
                    
                    except urlerror.HTTPError as e:
                        error_body = e.read().decode("utf-8", errors="replace")
                        print(f"[TELEGRAM] ❌ HTTP ERROR: {error_body}")
                        failed_telegram += 1
                        telegram_errors.append(f"{contact.name}: HTTP {e.code}")
                    
                    except urlerror.URLError as e:
                        print(f"[TELEGRAM] ❌ CONNECTION ERROR: {str(e)}")
                        failed_telegram += 1
                        telegram_errors.append(f"{contact.name}: {str(e.reason)}")
                    
                    except Exception as e:
                        print(f"[TELEGRAM] ❌ UNEXPECTED ERROR: {str(e)}")
                        failed_telegram += 1
                        telegram_errors.append(f"{contact.name}: {str(e)}")
        else:
            print("[TELEGRAM] ⚠️ Bot token not configured")
        
        print(f"\n[RESULT] SMS: {sent_sms} sent, {failed_sms} failed")
        print(f"[RESULT] Telegram: {sent_telegram} sent, {failed_telegram} failed")
        
        return jsonify({
            "status": "success",
            "message": f"Alert sent to {sent_sms + sent_telegram} contacts",
            "sms_sent": sent_sms,
            "sms_failed": failed_sms,
            "telegram_sent": sent_telegram,
            "telegram_failed": failed_telegram,
            "errors": sms_errors + telegram_errors
        }), 200
    
    except Exception as e:
        print(f"[EMERGENCY] ❌ CRITICAL ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"status": "error", "message": str(e)}), 500

# ==================== QUICK EMERGENCY ENDPOINT ====================

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


@app.route("/api/travel-risk", methods=["GET"])
@login_required
def get_travel_risk_data():
    """Get consolidated crime risk data for travel route planning"""
    try:
        travel_df = load_merged_crime_travel_data()
        
        if travel_df.empty:
            return jsonify({'status': 'error', 'message': 'Travel data not available'}), 400
        
        # Convert dataframe to dictionary format
        cities_data = []
        for _, row in travel_df.iterrows():
            city_info = {
                'city': str(row['City']),
                'risk_score': float(row['Risk_Score']),
                'risk_level': str(row['Risk_Level']),
                'total_incidents': int(row['Total_Incidents']),
                'women_target_percentage': float(row['Women_Target_Percentage']),
                'primary_crime_type': str(row['Primary_Crime_Type']),
                'crime_severity_score': float(row['Crime_Severity_Score']),
                'top_crimes': str(row['Top_3_Crime_Types'])
            }
            cities_data.append(city_info)
        
        return jsonify({
            'status': 'success',
            'cities': cities_data,
            'summary': {
                'total_cities': len(cities_data),
                'average_risk': float(travel_df['Risk_Score'].mean()),
                'highest_risk_city': str(travel_df.iloc[0]['City']),
                'lowest_risk_city': str(travel_df.iloc[-1]['City'])
            }
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400


@app.route("/api/safer-route", methods=["POST"])
@login_required
def get_safer_route():
    """Suggest a lower-risk route across Delhi using hotspot data."""
    try:
        data = request.get_json() or {}
        start = data.get("start") or {}
        destination = data.get("destination") or {}

        start_lat = float(start.get("lat"))
        start_lon = float(start.get("lon"))
        end_lat = float(destination.get("lat"))
        end_lon = float(destination.get("lon"))

        return jsonify(build_safer_route_response(start_lat, start_lon, end_lat, end_lon))
    except (TypeError, ValueError):
        return jsonify({
            "status": "error",
            "message": "Enter valid start and destination coordinates first."
        }), 400
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400

# ==================== LEGACY ROUTES ====================

@app.route("/home")
def home():
    """Legacy home page redirect"""
    if current_user.is_authenticated and os.path.exists("templates/home.html"):
        return render_template("home.html")
    return landing()

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

# ==================== MESSAGING ROUTES ====================

# ==================== CONTACT MANAGEMENT APIS ====================

@app.route("/api/contacts", methods=["GET"])
@login_required
def get_contacts():
    """Retrieve all contacts for the current user"""
    try:
        contacts = Contact.query.filter_by(user_id=current_user.id).all()
        return jsonify({
            "status": "success",
            "contacts": [{
                "id": c.id,
                "name": c.name,
                "phone": c.phone,
                "telegram_chat_id": c.telegram_chat_id or "",
                "telegramChatId": c.telegram_chat_id or ""
            } for c in contacts]
        }), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/api/contacts", methods=["POST"])
@login_required
def add_contact():
    """Add a new trusted contact"""
    try:
        data = request.get_json() or {}
        name = (data.get("name") or "").strip()
        phone = (data.get("phone") or "").strip()
        telegram_chat_id = (data.get("telegram_chat_id") or data.get("telegramChatId") or "").strip()

        if not name or not phone:
            return jsonify({"status": "error", "message": "Name and phone are required"}), 400

        # Check for duplicates
        existing = Contact.query.filter_by(user_id=current_user.id, phone=phone).first()
        if existing:
            return jsonify({"status": "error", "message": "Contact with this phone already exists"}), 400

        contact = Contact(
            name=name,
            phone=phone,
            telegram_chat_id=telegram_chat_id if telegram_chat_id else None,
            user_id=current_user.id
        )
        db.session.add(contact)
        db.session.commit()

        return jsonify({
            "status": "success",
            "message": f"{name} added to trusted contacts",
            "contact": {
                "id": contact.id,
                "name": contact.name,
                "phone": contact.phone,
                "telegram_chat_id": contact.telegram_chat_id or ""
            }
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/api/contacts/<int:contact_id>", methods=["PUT"])
@login_required
def update_contact(contact_id):
    """Update an existing contact"""
    try:
        contact = Contact.query.filter_by(id=contact_id, user_id=current_user.id).first()
        if not contact:
            return jsonify({"status": "error", "message": "Contact not found"}), 404

        data = request.get_json() or {}
        if "name" in data:
            contact.name = (data["name"] or "").strip()
        if "phone" in data:
            contact.phone = (data["phone"] or "").strip()
        if "telegram_chat_id" in data or "telegramChatId" in data:
            contact.telegram_chat_id = (data.get("telegram_chat_id") or data.get("telegramChatId") or "").strip()
            if not contact.telegram_chat_id:
                contact.telegram_chat_id = None

        db.session.commit()
        return jsonify({
            "status": "success",
            "message": "Contact updated",
            "contact": {
                "id": contact.id,
                "name": contact.name,
                "phone": contact.phone,
                "telegram_chat_id": contact.telegram_chat_id or ""
            }
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/api/contacts/<int:contact_id>", methods=["DELETE"])
@login_required
def delete_contact(contact_id):
    """Delete a trusted contact"""
    try:
        contact = Contact.query.filter_by(id=contact_id, user_id=current_user.id).first()
        if not contact:
            return jsonify({"status": "error", "message": "Contact not found"}), 404

        contact_name = contact.name
        db.session.delete(contact)
        db.session.commit()

        return jsonify({
            "status": "success",
            "message": f"{contact_name} removed from trusted contacts"
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/messaging")
@login_required
def messaging():
    """Real-time emergency messaging interface"""
    conversations = db.session.query(
        Message.sender_id, Message.receiver_id, db.func.max(Message.timestamp).label('last_message')
    ).filter(
        (Message.sender_id == current_user.id) | (Message.receiver_id == current_user.id)
    ).group_by(Message.sender_id, Message.receiver_id).all()
    
    contacts = Contact.query.filter_by(user_id=current_user.id).all()
    return render_template("messaging.html", contacts=contacts, conversations=conversations)

@app.route("/api/messages/<int:contact_id>", methods=["GET"])
@login_required
def get_messages(contact_id):
    """Fetch conversation history with a specific contact"""
    try:
        contact = Contact.query.filter_by(id=contact_id, user_id=current_user.id).first()
        if not contact:
            return jsonify({"status": "error", "message": "Contact not found"}), 404
        
        messages = Message.query.filter(
            ((Message.sender_id == current_user.id) & (Message.receiver_phone == contact.phone)) |
            ((Message.receiver_id == current_user.id) & (Message.sender_id == current_user.id))
        ).order_by(Message.timestamp).all()
        
        # Mark messages as read
        for msg in messages:
            if msg.receiver_id == current_user.id:
                msg.is_read = True
        db.session.commit()
        
        return jsonify({
            "status": "success",
            "contact": {
                "id": contact.id,
                "name": contact.name,
                "phone": contact.phone
            },
            "messages": [{
                "id": m.id,
                "sender_id": m.sender_id,
                "message": m.message_text,
                "timestamp": m.timestamp.isoformat(),
                "is_emergency": m.is_emergency,
                "message_type": m.message_type
            } for m in messages]
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route("/api/messages/send", methods=["POST"])
@login_required
def send_message():
    """Send an instant message to a contact"""
    try:
        data = request.get_json() or {}
        contact_id = data.get("contact_id")
        message_text = data.get("message", "").strip()
        is_emergency = data.get("is_emergency", False)
        message_type = data.get("message_type", "text")
        
        if not contact_id or not message_text:
            return jsonify({"status": "error", "message": "Contact ID and message are required"}), 400
        
        contact = Contact.query.filter_by(id=contact_id, user_id=current_user.id).first()
        if not contact:
            return jsonify({"status": "error", "message": "Contact not found"}), 404
        
        msg = Message(
            sender_id=current_user.id,
            receiver_phone=contact.phone,
            message_text=message_text,
            is_emergency=is_emergency,
            message_type=message_type,
            timestamp=datetime.utcnow()
        )
        db.session.add(msg)
        db.session.commit()
        
        # Emit via WebSocket for instant delivery
        socketio.emit('new_message', {
            'sender_id': current_user.id,
            'sender_name': current_user.username,
            'contact_id': contact_id,
            'contact_name': contact.name,
            'message': message_text,
            'timestamp': msg.timestamp.isoformat(),
            'is_emergency': is_emergency,
            'message_type': message_type
        }, broadcast=True)
        
        return jsonify({
            "status": "success",
            "message_id": msg.id,
            "timestamp": msg.timestamp.isoformat()
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

# ==================== QUICK ACTION ENDPOINTS ====================

@app.route("/api/quick/share-location", methods=["POST"])
@login_required
def quick_share_location():
    """Single-tap to share location to all trusted contacts"""
    try:
        data = request.get_json() or {}
        location = data.get("location", {})
        
        if not location or not location.get("lat") or not location.get("lon"):
            return jsonify({"status": "error", "message": "Location required"}), 400
        
        contacts = Contact.query.filter_by(user_id=current_user.id).all()
        if not contacts:
            return jsonify({"status": "error", "message": "No trusted contacts found"}), 400
        
        message_text = f"📍 Check my location: {location['lat']}, {location['lon']}"
        
        sent_to = []
        for contact in contacts:
            msg = Message(
                sender_id=current_user.id,
                receiver_phone=contact.phone,
                message_text=message_text,
                is_emergency=False,
                message_type='location_share',
                timestamp=datetime.utcnow()
            )
            db.session.add(msg)
            sent_to.append(contact.name)
        
        db.session.commit()
        
        # Broadcast via WebSocket
        socketio.emit('location_shared', {
            'from_user': current_user.username,
            'location': location,
            'message': message_text,
            'timestamp': datetime.utcnow().isoformat(),
            'sent_to': sent_to
        }, broadcast=True)
        
        return jsonify({
            "status": "success",
            "message": f"Location shared with {len(sent_to)} contact(s)",
            "contacts": sent_to
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route("/api/quick/danger-alert", methods=["POST"])
@login_required
def quick_danger_alert():
    """Single-tap emergency alert to all trusted contacts"""
    try:
        data = request.get_json() or {}
        location = data.get("location", {})
        
        contacts = Contact.query.filter_by(user_id=current_user.id).all()
        if not contacts:
            return jsonify({"status": "error", "message": "No trusted contacts found"}), 400
        
        message_text = "🚨 I'M IN DANGER! Please help me immediately!"
        if location and location.get("lat") and location.get("lon"):
            message_text += f"\n📍 Location: {location['lat']}, {location['lon']}"
        
        sent_to = []
        for contact in contacts:
            msg = Message(
                sender_id=current_user.id,
                receiver_phone=contact.phone,
                message_text=message_text,
                is_emergency=True,
                message_type='emergency_alert',
                timestamp=datetime.utcnow()
            )
            db.session.add(msg)
            sent_to.append(contact.name)
        
        db.session.commit()
        
        # Broadcast emergency alert via WebSocket
        socketio.emit('danger_alert', {
            'from_user': current_user.username,
            'message': message_text,
            'location': location,
            'timestamp': datetime.utcnow().isoformat(),
            'sent_to': sent_to
        }, broadcast=True)
        
        return jsonify({
            "status": "success",
            "message": f"Emergency alert sent to {len(sent_to)} contact(s)",
            "contacts": sent_to,
            "timestamp": datetime.utcnow().isoformat()
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

# ==================== WEBSOCKET HANDLERS ====================

@socketio.on('connect')
def handle_connect():
    """Handle WebSocket connection"""
    if current_user.is_authenticated:
        join_room(f'user_{current_user.id}')
        emit('connection_response', {
            'data': 'Connected to messaging server',
            'user_id': current_user.id,
            'username': current_user.username
        })

@socketio.on('disconnect')
def handle_disconnect():
    """Handle WebSocket disconnection"""
    if current_user.is_authenticated:
        leave_room(f'user_{current_user.id}')

@socketio.on('send_instant_message')
def handle_instant_message(data):
    """Handle instant message via WebSocket for real-time delivery"""
    if not current_user.is_authenticated:
        return {'status': 'error', 'message': 'Not authenticated'}
    
    try:
        contact_id = data.get('contact_id')
        message_text = data.get('message', '').strip()
        is_emergency = data.get('is_emergency', False)
        location = data.get('location', {})
        
        if not contact_id or not message_text:
            emit('message_error', {'error': 'Contact ID and message are required'})
            return
        
        contact = Contact.query.filter_by(id=contact_id, user_id=current_user.id).first()
        if not contact:
            emit('message_error', {'error': 'Contact not found'})
            return
        
        # Store in database
        msg = Message(
            sender_id=current_user.id,
            receiver_phone=contact.phone,
            message_text=message_text,
            is_emergency=is_emergency,
            message_type='text' if not location else 'location_share',
            timestamp=datetime.utcnow()
        )
        db.session.add(msg)
        db.session.commit()
        
        # Emit instantly to all connected clients
        emit('instant_message', {
            'id': msg.id,
            'sender_id': current_user.id,
            'sender_name': current_user.username,
            'contact_id': contact_id,
            'contact_name': contact.name,
            'message': message_text,
            'location': location,
            'timestamp': msg.timestamp.isoformat(),
            'is_emergency': is_emergency
        }, broadcast=True)
        
        # Acknowledgment
        emit('message_sent', {
            'status': 'success',
            'message_id': msg.id,
            'timestamp': msg.timestamp.isoformat()
        })
        
    except Exception as e:
        emit('message_error', {'error': str(e)})

@socketio.on('emergency_alert')
def handle_emergency_alert(data):
    """Handle instant emergency alert to all trusted contacts"""
    if not current_user.is_authenticated:
        return {'status': 'error', 'message': 'Not authenticated'}
    
    try:
        message_text = data.get('message', 'EMERGENCY ALERT!').strip()
        location = data.get('location', {})
        contact_ids = data.get('contact_ids', [])
        
        contacts = Contact.query.filter(
            Contact.user_id == current_user.id,
            Contact.id.in_(contact_ids) if contact_ids else True
        ).all()
        
        sent_to = []
        for contact in contacts:
            msg = Message(
                sender_id=current_user.id,
                receiver_phone=contact.phone,
                message_text=message_text,
                is_emergency=True,
                message_type='emergency_alert',
                timestamp=datetime.utcnow()
            )
            db.session.add(msg)
            sent_to.append(contact.name)
        
        db.session.commit()
        
        # Broadcast emergency alert
        emit('emergency_alert_received', {
            'from_user': current_user.username,
            'message': message_text,
            'location': location,
            'timestamp': datetime.utcnow().isoformat(),
            'sent_to': sent_to
        }, broadcast=True)
        
        emit('emergency_sent', {
            'status': 'success',
            'contacts_notified': len(sent_to),
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        emit('message_error', {'error': str(e)})

def initialize_app_data():
    """Initialize database tables and seed data used by the app."""
    with app.app_context():
        db.create_all()
        print("Creating databases and importing CSV data...")
        import_crime_data()
        import_environmental_data()
        import_women_crime_stats()
        print("Data import complete!")

if __name__ == "__main__":
    initialize_app_data()
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
