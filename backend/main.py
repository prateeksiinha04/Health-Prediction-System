import os
import joblib
import numpy as np
from datetime import datetime
from bson import ObjectId
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from database import users_collection, predictions_collection

app = FastAPI(title="HealthPredict AI Backend")

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 🤖 MACHINE LEARNING MODEL LOAD ---
MODEL_PATH = "heart_model.pkl"
svc_model = None
scaler = None
imputer = None

if os.path.exists(MODEL_PATH):
    try:
        loaded_data = joblib.load(MODEL_PATH)
        svc_model = loaded_data["model"]
        scaler = loaded_data["scaler"]
        imputer = loaded_data["imputer"]
        print("✅ Success: ML Pipeline successfully loaded!")
    except Exception as e:
        print(f"❌ Model load karne me error: {e}")
else:
    print("⚠️ Warning: heart_model.pkl file nahi mili!")

# --- 📝 PYDANTIC SCHEMAS ---
class SignupModel(BaseModel):
    name: str
    email: EmailStr
    password: str

class LoginModel(BaseModel):
    email: EmailStr
    password: str

class PredictionModel(BaseModel):
    user_id: str
    age: int
    sex: int
    cp: int          
    trestbps: int    
    chol: int        
    fbs: int         
    restecg: int     
    thalach: int     
    exang: int       
    oldpeak: float   
    slope: int       
    ca: int          
    thal: int        

class ManualRecordModel(BaseModel):
    user_id: str
    record_type: str
    date: str
    heart_rate: str
    blood_pressure: str
    notes: str

# --- 🔌 API ENDPOINTS ---

@app.post("/api/auth/signup")
def signup(data: SignupModel):
    if users_collection.find_one({"email": data.email}):
        raise HTTPException(status_code=400, detail="Email already registered!")
    inserted = users_collection.insert_one(data.model_dump())
    return {"message": "Account created!", "user_id": str(inserted.inserted_id)}

@app.post("/api/auth/login")
def login(data: LoginModel):
    user = users_collection.find_one({"email": data.email, "password": data.password})
    if not user:
        raise HTTPException(status_code=400, detail="Invalid Email or Password!")
    return {"user_id": str(user["_id"]), "name": user["name"]}

@app.post("/api/add-record")
def add_manual_record(data: ManualRecordModel):
    try:
        record = {
            "user_id": ObjectId(data.user_id),
            "timestamp": data.date, 
            "record_type": data.record_type,
            "is_manual": True,
            "vitals": {
                "hr": data.heart_rate,
                "bp": data.blood_pressure
            },
            "risk_status": data.notes,
            "probability": "N/A"
        }
        predictions_collection.insert_one(record)
        return {"message": "Manual record saved successfully!"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Database error: {str(e)}")

@app.post("/api/predict")
def predict(data: PredictionModel):
    if svc_model is None or scaler is None:
        raise HTTPException(status_code=500, detail="ML Pipeline is not loaded.")
    
    try:
        # Feature Engineering
        age_thalach_ratio = data.age / data.thalach if data.thalach > 0 else 0
        bp_chol_product = data.trestbps * data.chol
        age_group = 1 if 40 <= data.age < 55 else (2 if data.age >= 55 else 0)

        raw_features = np.array([[
            data.age, data.sex, data.cp, data.trestbps, data.chol,
            data.fbs, data.restecg, data.thalach, data.exang,
            data.oldpeak, data.slope, data.ca, data.thal,
            age_thalach_ratio, bp_chol_product, age_group
        ]])
        
        imputed = imputer.transform(raw_features)
        scaled = scaler.transform(imputed)
        
        prediction = svc_model.predict(scaled)[0]
        
        # Save to DB
        record = {
            "user_id": ObjectId(data.user_id),
            "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
            "metrics": data.model_dump(),
            "risk_status": "HIGH RISK" if prediction == 1 else "LOW RISK",
            "is_manual": False
        }
        predictions_collection.insert_one(record)
        
        return {"risk_status": record["risk_status"]}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/history/{user_id}")
def get_history(user_id: str):
    cursor = predictions_collection.find({"user_id": ObjectId(user_id)}).sort("timestamp", -1)
    return [{
        "date": item.get("timestamp"),
        "risk": item.get("risk_status"),
        "vitals": item.get("vitals"),
        "is_manual": item.get("is_manual", False)
    } for item in cursor]