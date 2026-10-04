import os

BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'foodbridge-super-secret-key-2026-prod'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or f"sqlite:///{os.path.join(BASE_DIR, 'foodbridge.db')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Matching Engine Parameters
    MAX_SEARCH_RADIUS_KM = 25.0
    DEFAULT_TRANSIT_SPEED_KMH = 20.0
    
    # Weight Coefficients for Matching Engine (Sum = 1.0)
    WEIGHT_DISTANCE = 0.35
    WEIGHT_URGENCY = 0.30
    WEIGHT_CAPACITY = 0.20
    WEIGHT_PREFERENCE = 0.15
    
    # Carbon Abatement Factor (EPA standard: 2.5 kg CO2e per kg food waste diverted)
    CO2E_FACTOR_PER_KG = 2.5
    AVG_MEAL_WEIGHT_KG = 0.40 # 400 grams per meal box on average
