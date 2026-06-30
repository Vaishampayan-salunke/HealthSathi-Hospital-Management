"""
CityCare Hospital Management System - FastAPI Backend
A production-ready backend for accessible, low-cost healthcare platform.

INSTALLATION (Windows PowerShell):
python -m pip install fastapi uvicorn sqlalchemy pyjwt python-multipart pydantic python-dotenv

Run: python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000

Required ENV variables (optional - defaults provided):
- DATABASE_URL=sqlite:///./hospital.db
- JWT_SECRET=your-secret-key-change-in-production
"""

from fastapi import FastAPI, HTTPException, Depends, status, WebSocket, WebSocketDisconnect, File, UploadFile, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy import create_engine, Column, String, Float, Boolean, Integer, JSON, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from fastapi import Query
import jwt
import hashlib
import uuid
import json
import os
import random
import re
from pathlib import Path
import logging
from contextlib import asynccontextmanager

# Configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./hospital.db")
JWT_SECRET = os.getenv("JWT_SECRET", "change-this-secret-in-production")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Supported Languages Configuration
SUPPORTED_LANGUAGES = {
    "en": {"name": "English", "native": "English"},
    "hi": {"name": "Hindi", "native": "हिंदी"},
    "kn": {"name": "Kannada", "native": "ಕನ್ನಡ"},
    "ta": {"name": "Tamil", "native": "தமிழ்"},
    "te": {"name": "Telugu", "native": "తెలుగు"},
    "bn": {"name": "Bengali", "native": "বাংলা"},
    "mr": {"name": "Marathi", "native": "मराठी"},
    "gu": {"name": "Gujarati", "native": "ગુજરાતી"},
    "ml": {"name": "Malayalam", "native": "മലയാളം"},
    "pa": {"name": "Punjabi", "native": "ਪੰਜਾਬੀ"}
}

# Translation Dictionary for Common Phrases
TRANSLATIONS = {
    "en": {
        "welcome": "Welcome to CityCare Hospital",
        "appointment_booked": "Appointment booked successfully",
        "appointment_cancelled": "Appointment cancelled",
        "invalid_otp": "Invalid OTP",
        "user_not_found": "User not found",
        "rest_hydration": "Rest, hydration. Consult doctor if persists.",
        "emergency_call": "CALL AMBULANCE IMMEDIATELY",
        "consult_doctor": "Consult healthcare provider",
        "sos_sent": "SOS alert sent successfully"
    },
    "hi": {
        "welcome": "सिटीकेयर अस्पताल में आपका स्वागत है",
        "appointment_booked": "अपॉइंटमेंट सफलतापूर्वक बुक किया गया",
        "appointment_cancelled": "अपॉइंटमेंट रद्द किया गया",
        "invalid_otp": "अमान्य ओटीपी",
        "user_not_found": "उपयोगकर्ता नहीं मिला",
        "rest_hydration": "आराम करें, पानी पिएं। यदि समस्या जारी रहे तो डॉक्टर से परामर्श करें।",
        "emergency_call": "तुरंत एम्बुलेंस बुलाएं",
        "consult_doctor": "स्वास्थ्य सेवा प्रदाता से परामर्श करें",
        "sos_sent": "SOS अलर्ट सफलतापूर्वक भेजा गया"
    },
    "kn": {
        "welcome": "ಸಿಟಿಕೇರ್ ಆಸ್ಪತ್ರೆಗೆ ಸ್ವಾಗತ",
        "appointment_booked": "ಅಪಾಯಿಂಟ್ಮೆಂಟ್ ಯಶಸ್ವಿಯಾಗಿ ಬುಕ್ ಆಗಿದೆ",
        "appointment_cancelled": "ಅಪಾಯಿಂಟ್ಮೆಂಟ್ ರದ್ದುಗೊಂಡಿದೆ",
        "invalid_otp": "ಅಮಾನ್ಯ OTP",
        "user_not_found": "ಬಳಕೆದಾರ ಕಂಡುಬಂದಿಲ್ಲ",
        "rest_hydration": "ವಿಶ್ರಾಂತಿ, ನೀರು ಕುಡಿಯಿರಿ। ಮುಂದುವರಿದರೆ ವೈದ್ಯರನ್ನು ಸಂಪರ್ಕಿಸಿ.",
        "emergency_call": "ತಕ್ಷಣ ಆಂಬುಲೆನ್ಸ್ ಕರೆ ಮಾಡಿ",
        "consult_doctor": "ಆರೋಗ್ಯ ಸೇವಾ ಪೂರೈಕೆದಾರರನ್ನು ಸಂಪರ್ಕಿಸಿ",
        "sos_sent": "SOS ಎಚ್ಚರಿಕೆ ಯಶಸ್ವಿಯಾಗಿ ಕಳುಹಿಸಲಾಗಿದೆ"
    },
    "ta": {
        "welcome": "சிட்டிகேர் மருத்துவமனைக்கு வரவேற்கிறோம்",
        "appointment_booked": "அப்பாயின்மென்ட் வெற்றிகரமாக பதிவு செய்யப்பட்டது",
        "appointment_cancelled": "அப்பாயின்மென்ட் ரத்து செய்யப்பட்டது",
        "invalid_otp": "தவறான OTP",
        "user_not_found": "பயனர் கண்டுபிடிக்கப்படவில்லை",
        "rest_hydration": "ஓய்வு, தண்ணீர் குடிக்கவும். தொடர்ந்தால் மருத்துவரை அணுகவும்.",
        "emergency_call": "உடனடியாக ஆம்புலன்ஸ் அழைக்கவும்",
        "consult_doctor": "சுகாதார வழங்குநரை அணுகவும்",
        "sos_sent": "SOS எச்சரிக்கை வெற்றிகரமாக அனுப்பப்பட்டது"
    },
    "te": {
        "welcome": "సిటీకేర్ హాస్పిటల్‌కు స్వాగతం",
        "appointment_booked": "అపాయింట్‌మెంట్ విజయవంతంగా బుక్ చేయబడింది",
        "appointment_cancelled": "అపాయింట్‌మెంట్ రద్దు చేయబడింది",
        "invalid_otp": "చెల్లని OTP",
        "user_not_found": "వినియోగదారు కనుగొనబడలేదు",
        "rest_hydration": "విశ్రాంతి, నీరు తాగండి. కొనసాగితే వైద్యుడిని సంప్రదించండి.",
        "emergency_call": "వెంటనే అంబులెన్స్‌ని పిలవండి",
        "consult_doctor": "ఆరోగ్య సేవా ప్రదాతను సంప్రదించండి",
        "sos_sent": "SOS హెచ్చరిక విజయవంతంగా పంపబడింది"
    }
}

# Database Setup
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Models
class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    phone = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    language_pref = Column(String, default="en")
    created_at = Column(DateTime, default=datetime.utcnow)
    last_seen = Column(DateTime, default=datetime.utcnow)
    consent_flags = Column(JSON, default=dict)
    jwt_revoked = Column(Boolean, default=False)
    role = Column(String, default="patient")

class SymptomQuery(Base):
    __tablename__ = "symptom_queries"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, nullable=True)
    text = Column(Text, nullable=False)
    transcript = Column(Text, nullable=True)
    language = Column(String, default="en")
    suggestions = Column(JSON, default=list)
    model_used = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class DirectoryEntry(Base):
    __tablename__ = "directory_entries"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)
    lat = Column(Float, nullable=False)
    lng = Column(Float, nullable=False)
    phone = Column(String, nullable=True)
    address = Column(String, nullable=True)
    open_24_7 = Column(Boolean, default=False)
    source = Column(String, default="manual")
    last_updated = Column(DateTime, default=datetime.utcnow)

class SOS(Base):
    __tablename__ = "sos_requests"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, nullable=False)
    lat = Column(Float, nullable=False)
    lng = Column(Float, nullable=False)
    location_text = Column(String, nullable=True)
    message = Column(Text, nullable=False)
    contacts = Column(JSON, default=list)
    share_with = Column(JSON, default=list)
    status = Column(String, default="pending")
    notified_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

class ContentVersion(Base):
    __tablename__ = "content_versions"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    version = Column(String, unique=True, nullable=False)
    checksum = Column(String, nullable=False)
    payload = Column(JSON, nullable=False)
    changelog = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Appointment(Base):
    __tablename__ = "appointments"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    patient_name = Column(String, nullable=False)
    gender = Column(String, nullable=False)
    age = Column(Integer, nullable=False)
    phone = Column(String, nullable=False)
    email = Column(String, nullable=False)
    department = Column(String, nullable=False)
    doctor = Column(String, nullable=False)
    date = Column(String, nullable=False)
    time = Column(String, nullable=False)
    status = Column(String, default="scheduled")
    created_at = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(bind=engine)

# Pydantic Schemas
class RegisterRequest(BaseModel):
    phone: str
    name: str
    language: str = "en"

class VerifyRequest(BaseModel):
    phone: str
    otp: str

class SymptomRequest(BaseModel):
    text: str
    language: str = "en"

class TTSRequest(BaseModel):
    text: str
    language: str = "en"
    voice: str = "female"

class SOSRequest(BaseModel):
    lat: float
    lng: float
    location_text: Optional[str] = None
    contacts: List[str] = []
    message: str
    share_with: List[str] = ["volunteer", "nearby_doctors", "hospital_admin"]

class AppointmentRequest(BaseModel):
    name: str
    gender: str
    age: int
    phone: str
    email: str
    dept: str
    doctor: str
    date: str
    time: str
# ==================== ADD THIS TO YOUR main.py (after imports) ====================

from fastapi import Query

# Translation dictionary (easily extendable to more languages)
TRANSLATIONS = {
    "en": {
        "welcome": "Welcome to CityCare Hospital",
        "subtitle": "Choose a department to get started",
        "cardiology": "Cardiology",
        "cardiology_desc": "Specialized heart care — consultations, angiography and rehab services.",
        "orthopedics": "Orthopedics",
        "orthopedics_desc": "Bone & joint treatments including arthroscopy and joint replacement.",
        "dentistry": "Dentistry",
        "dentistry_desc": "Complete dental care: checkups, cosmetic dentistry and emergency extraction.",
        "neurology": "Neurology",
        "neurology_desc": "Diagnosis and treatment for brain & nervous system disorders.",
        "dermatology": "Dermatology",
        "dermatology_desc": "Skin treatments, mole removal, and allergy testing.",
        "gynecology": "Gynecology",
        "gynecology_desc": "Women's health, prenatal care and obstetrics services.",
        "pediatrics": "Pediatrics",
        "pediatrics_desc": "Child health, immunizations and growth monitoring.",
        "general": "General Medicine",
        "general_desc": "Primary care, diagnostics and chronic disease management.",
        "appointments": "Appointments",
        "departments": "Departments",
        "pharmacy": "Pharmacy",
        "lab": "Lab",
        "billing": "Billing",
        "chatbot": "AI Chatbot",
        "emergency": "Emergency",
        "logout": "Logout",
        "language": "Language"
    },
    "hi": {
        "welcome": "सिटीकेयर अस्पताल में आपका स्वागत है",
        "subtitle": "शुरू करने के लिए एक विभाग चुनें",
        "cardiology": "हृदय रोग",
        "cardiology_desc": "विशेष हृदय देखभाल — परामर्श, एंजियोग्राफी और पुनर्वास सेवाएँ।",
        "orthopedics": "हड्डी रोग",
        "orthopedics_desc": "हड्डी और जोड़ों का इलाज जिसमें आर्थ्रोस्कोपी और जोड़ प्रतिस्थापन शामिल है।",
        "dentistry": "दंत चिकित्सा",
        "dentistry_desc": "पूर्ण दंत देखभाल: जांच, कॉस्मेटिक दंत चिकित्सा और आपात निष्कर्षण।",
        "neurology": "न्यूरोलॉजी",
        "neurology_desc": "मस्तिष्क और तंत्रिका तंत्र विकारों का निदान और उपचार।",
        "dermatology": "त्वचा रोग",
        "dermatology_desc": "त्वचा उपचार, तिल हटाना और एलर्जी परीक्षण।",
        "gynecology": "स्त्री रोग",
        "gynecology_desc": "महिला स्वास्थ्य, प्रसव पूर्व देखभाल और प्रसूति सेवाएँ।",
        "pediatrics": "बाल रोग",
        "pediatrics_desc": "बच्चों का स्वास्थ्य, टीकाकरण और विकास निगरानी।",
        "general": "सामान्य चिकित्सा",
        "general_desc": "प्राथमिक देखभाल, निदान और पुरानी बीमारियों का प्रबंधन।",
        "appointments": "नियुक्तियाँ",
        "departments": "विभाग",
        "pharmacy": "फार्मेसी",
        "lab": "लैब",
        "billing": "बिलिंग",
        "chatbot": "एआई चैटबॉट",
        "emergency": "आपातकाल",
        "logout": "लॉग आउट",
        "language": "भाषा"
    },
    "ta": {  # Tamil
        "welcome": "சிட்டிகேர் மருத்துவமனைக்கு வரவேற்கிறோம்",
        "subtitle": "தொடங்க ஒரு துறையைத் தேர்வு செய்க",
        "cardiology": "இதயவியல்",
        "cardiology_desc": "சிறப்பு இதய பராமரிப்பு — ஆலோசனை, ஆஞ்சியோகிராபி மற்றும் மறுவாழ்வு சேவைகள்.",
        # ... add others similarly
    },
    "te": {  # Telugu
        "welcome": "సిటీకేర్ హాస్పిటల్‌కు స్వాగతం",
        "subtitle": "ప్రారంభించడానికి ఒక విభాగాన్ని ఎంచుకోండి",
        "cardiology": "కార్డియాలజీ",
        "cardiology_desc": "ప్రత్యేక గుండె సంరక్షణ — సంప్రదింపులు, ఆంజియోగ్రఫీ మరియు పునరావాస సేవలు.",
        # ... add rest
    },
    "kn": {  # Kannada
        "welcome": "ಸಿಟಿಕೇರ್ ಆಸ್ಪತ್ರೆಗೆ ಸ್ವಾಗತ",
        "subtitle": "ಪ್ರಾರಂಭಿಸಲು ಒಂದು ಇಲಾಖೆಯನ್ನು ಆಯ್ಕೆಮಾಡಿ",
        "cardiology": "ಹೃದ್ರೋಗ ತಜ್ಞ",
        "cardiology_desc": "ವಿಶೇಷ ಹೃದಯ ಆರೈಕೆ — ಸಮಾಲೋಚನೆ, ಆಂಜಿಯೋಗ್ರಫಿ ಮತ್ತು ಪುನರ್ವಸತಿ ಸೇವೆಗಳು.",
        # ... add rest
    }
    # Add Marathi, Bengali, Gujarati, Punjabi, Malayalam etc. the same way
}

# Default to English if language not found
def t(text_key: str, lang: str = "en") -> str:
    return TRANSLATIONS.get(lang, TRANSLATIONS["en"]).get(text_key, text_key)

# New endpoint to get translations (optional – you can also serve from frontend JSON)
@app.get("/api/translations")
async def get_translations(lang: str = Query("en", max_length=5)):
    lang = lang.lower()
    if lang not in TRANSLATIONS:
        lang = "en"
    return TRANSLATIONS[lang]
# Dependencies
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

security = HTTPBearer()

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    try:
        token = credentials.credentials
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
        user = db.query(User).filter(User.id == user_id, User.jwt_revoked == False).first()
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        return user
    except:
        raise HTTPException(status_code=401, detail="Invalid token")

# AI Adapters
class MockLLMAdapter:
    CONDITIONS_DB = {
        "fever": {"condition": "Viral Fever", "confidence": 0.75, "advice": "Rest, hydration. Consult doctor if persists."},
        "headache": {"condition": "Tension Headache", "confidence": 0.70, "advice": "Rest in dark room, take paracetamol."},
        "cough": {"condition": "Upper Respiratory Infection", "confidence": 0.72, "advice": "Steam, warm fluids, rest."},
        "chest pain": {"condition": "EMERGENCY", "confidence": 0.95, "advice": "CALL AMBULANCE IMMEDIATELY"},
    }
    
    def analyze_symptoms(self, text: str, language: str):
        text_lower = text.lower()
        suggestions = []
        for keyword, data in self.CONDITIONS_DB.items():
            if keyword in text_lower:
                suggestions.append(data)
        if not suggestions:
            suggestions.append({"condition": "General Concern", "confidence": 0.50, "advice": "Consult healthcare provider"})
        return {
            "suggestions": suggestions[:3],
            "follow_up": ["How long have you had symptoms?"],
            "model_used": "mock_llm_v1",
            "provenance": "Rule-based mock"
        }

# Helper Functions
OTP_STORAGE = {}

def generate_otp(phone: str) -> str:
    otp = str(random.randint(100000, 999999))
    OTP_STORAGE[phone] = {"otp": otp, "expires": datetime.utcnow() + timedelta(minutes=5)}
    return otp

def verify_otp(phone: str, otp: str) -> bool:
    stored = OTP_STORAGE.get(phone)
    if not stored or datetime.utcnow() > stored["expires"]:
        return False
    return stored["otp"] == otp

def calculate_distance(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    from math import radians, sin, cos, sqrt, atan2
    R = 6371
    lat1, lng1, lat2, lng2 = map(radians, [lat1, lng1, lat2, lng2])
    dlat = lat2 - lat1
    dlng = lng2 - lng1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlng/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    return R * c

# WebSocket Manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}
    
    async def connect(self, sos_id: str, websocket: WebSocket):
        await websocket.accept()
        if sos_id not in self.active_connections:
            self.active_connections[sos_id] = []
        self.active_connections[sos_id].append(websocket)
    
    def disconnect(self, sos_id: str, websocket: WebSocket):
        if sos_id in self.active_connections:
            self.active_connections[sos_id].remove(websocket)
    
    async def broadcast(self, sos_id: str, message: dict):
        if sos_id in self.active_connections:
            for connection in self.active_connections[sos_id]:
                try:
                    await connection.send_json(message)
                except:
                    pass

manager = ConnectionManager()

# FastAPI App
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting CityCare Hospital Backend...")
    db = SessionLocal()
    try:
        if db.query(DirectoryEntry).count() == 0:
            sample_entries = [
                DirectoryEntry(name="CityCare Hospital", type="hospital", lat=12.9716, lng=77.5946, 
                              phone="+919876543210", address="MG Road, Bangalore", open_24_7=True),
            ]
            db.add_all(sample_entries)
            db.commit()
        
        if db.query(ContentVersion).count() == 0:
            content = {
                "first_aid": {"burns": "Cool with water. Cover with clean cloth.", "bleeding": "Apply pressure. Elevate wound."},
                "emergency_numbers": {"ambulance": "108", "police": "100"}
            }
            checksum = hashlib.sha256(json.dumps(content).encode()).hexdigest()
            db.add(ContentVersion(version="1.0.0", checksum=checksum, payload=content))
            db.commit()
    finally:
        db.close()
    yield
    logger.info("Shutting down...")

app = FastAPI(title="CityCare Hospital API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static HTML files
static_path = Path(__file__).parent / "static"
if static_path.exists():
    app.mount("/static", StaticFiles(directory=str(static_path), html=True), name="static")

# API Endpoints
@app.get("/")
async def root():
    return {"message": "CityCare Hospital API", "docs": "/docs", "health": "/health"}

@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    db_status = False
    try:
        db.execute("SELECT 1")
        db_status = True
    except:
        pass
    return {"status": "ok" if db_status else "degraded", "services": {"db": db_status, "cache": True}}

@app.post("/auth/register")
async def register(req: RegisterRequest, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.phone == req.phone).first()
    if existing:
        otp = generate_otp(req.phone)
        return {"user_id": existing.id, "otp_sent": True, "otp": otp}
    
    user = User(phone=req.phone, name=req.name, language_pref=req.language)
    db.add(user)
    db.commit()
    db.refresh(user)
    otp = generate_otp(req.phone)
    return {"user_id": user.id, "otp_sent": True, "otp": otp}

@app.post("/auth/verify")
async def verify(req: VerifyRequest, db: Session = Depends(get_db)):
    if not verify_otp(req.phone, req.otp):
        raise HTTPException(status_code=400, detail="Invalid OTP")
    
    user = db.query(User).filter(User.phone == req.phone).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    token_data = {"sub": user.id, "phone": user.phone, "exp": datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS)}
    token = jwt.encode(token_data, JWT_SECRET, algorithm=JWT_ALGORITHM)
    
    if req.phone in OTP_STORAGE:
        del OTP_STORAGE[req.phone]
    
    return {"access_token": token, "token_type": "bearer", "user": {"id": user.id, "name": user.name, "phone": user.phone}}

@app.post("/api/appointments")
async def create_appointment(req: AppointmentRequest, db: Session = Depends(get_db)):
    appointment = Appointment(
        patient_name=req.name,
        gender=req.gender,
        age=req.age,
        phone=req.phone,
        email=req.email,
        department=req.dept,
        doctor=req.doctor,
        date=req.date,
        time=req.time
    )
    db.add(appointment)
    db.commit()
    db.refresh(appointment)
    return {"success": True, "appointment_id": appointment.id, "message": "Appointment booked successfully"}

@app.get("/api/appointments")
async def get_appointments(db: Session = Depends(get_db)):
    appointments = db.query(Appointment).order_by(Appointment.created_at.desc()).all()
    return {
        "appointments": [
            {
                "id": a.id,
                "name": a.patient_name,
                "gender": a.gender,
                "age": a.age,
                "phone": a.phone,
                "email": a.email,
                "dept": a.department,
                "doctor": a.doctor,
                "date": a.date,
                "time": a.time,
                "status": a.status
            }
            for a in appointments
        ]
    }

@app.delete("/api/appointments/{appointment_id}")
async def delete_appointment(appointment_id: str, db: Session = Depends(get_db)):
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    db.delete(appointment)
    db.commit()
    return {"success": True, "message": "Appointment cancelled"}

@app.post("/ai/symptoms")
async def analyze_symptoms(req: SymptomRequest, db: Session = Depends(get_db)):
    query_id = str(uuid.uuid4())
    llm = MockLLMAdapter()
    result = llm.analyze_symptoms(req.text, req.language)
    
    query = SymptomQuery(id=query_id, text=req.text, language=req.language, suggestions=result["suggestions"], model_used=result["model_used"])
    db.add(query)
    db.commit()
    
    return {
        "query_id": query_id,
        "language": req.language,
        "suggestions": result["suggestions"],
        "follow_up": result.get("follow_up", []),
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/content/essentials")
async def get_essentials(db: Session = Depends(get_db)):
    latest = db.query(ContentVersion).order_by(ContentVersion.created_at.desc()).first()
    if not latest:
        raise HTTPException(status_code=404, detail="No content available")
    return {"version": latest.version, "checksum": latest.checksum, "content": latest.payload}

@app.get("/directory/nearby")
async def find_nearby_facilities(lat: float, lng: float, radius: float = 5.0, type: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(DirectoryEntry)
    if type:
        query = query.filter(DirectoryEntry.type == type)
    
    all_entries = query.all()
    nearby = []
    for entry in all_entries:
        distance = calculate_distance(lat, lng, entry.lat, entry.lng)
        if distance <= radius:
            nearby.append({
                "id": entry.id,
                "name": entry.name,
                "type": entry.type,
                "lat": entry.lat,
                "lng": entry.lng,
                "phone": entry.phone,
                "address": entry.address,
                "open_24_7": entry.open_24_7,
                "distance_km": round(distance, 2)
            })
    nearby.sort(key=lambda x: x["distance_km"])
    return {"count": len(nearby), "facilities": nearby}

@app.post("/sos")
async def create_sos(req: SOSRequest, user: User = Depends(verify_token), db: Session = Depends(get_db)):
    sos = SOS(
        user_id=user.id,
        lat=req.lat,
        lng=req.lng,
        location_text=req.location_text,
        message=req.message,
        contacts=req.contacts,
        share_with=req.share_with,
        status="sent",
        notified_count=len(req.contacts)
    )
    db.add(sos)
    db.commit()
    db.refresh(sos)
    
    logger.info(f"SOS created: {sos.id}")
    return {"sos_id": sos.id, "status": "sent", "notified": sos.notified_count}

@app.websocket("/ws/sos/{sos_id}")
async def websocket_sos(websocket: WebSocket, sos_id: str):
    await manager.connect(sos_id, websocket)
    try:
        while True:
            data = await websocket.receive_json()
            await manager.broadcast(sos_id, data)
    except WebSocketDisconnect:
        manager.disconnect(sos_id, websocket)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)