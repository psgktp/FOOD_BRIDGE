# 🍱 FoodBridge: Smart Food Rescue & Need-Matching Platform

**FoodBridge** is an autonomous, demand-driven surplus food rescue and logistics coordination network featuring **$N:1$ multi-donor pooling**, **4-tier urgency decay timers**, **1-click campus event fast-track**, **live GIS food need heatmaps**, and **dual-stage cryptographic chain-of-custody (CoC)**.

---

## 🚀 Quick Start Guide

### 1. Activate Virtual Environment
```powershell
# Windows PowerShell
.\venv\Scripts\Activate.ps1
```

### 2. Run the Application
```powershell
python run.py
```
Open your browser and navigate to:
👉 **`http://127.0.0.1:5000`**

---

## 🔑 Pre-Configured Demo Credentials

The platform is pre-seeded with realistic campus, donor, NGO, and volunteer profiles:

| Role | Email | Password | Details |
| :--- | :--- | :--- | :--- |
| **Campus Donor** | `symposium@college.edu` | `donor123` | Anna University Tech Fest Coordinator |
| **Canteen Donor** | `mess@campus.edu` | `donor123` | Campus North Hostel Mess |
| **Hotel Donor** | `manager@grandpalace.com` | `donor123` | Grand Palace Banquets |
| **Shelter NGO** | `mercy@shelter.org` | `org123` | Mercy Community Shelter & Kitchen (Needs 200 Meals) |
| **City Food Bank**| `hope@foodbank.org` | `org123` | Hope City Food Bank & Pantry |
| **Volunteer** | `rahul@volunteer.org` | `vol123` | Student Courier (Two-Wheeler, 40 Meals) |
| **Volunteer (Car)**| `priya@volunteer.org` | `vol123` | Community Courier (Car, 120 Meals) |
| **System Admin** | `admin@foodbridge.org` | `admin123` | Platform KYC & Audit Suite |

*(Note: The login page includes **1-Click Quick Fill** buttons for instant testing!)*

---

## 🧠 The 5 Signature Technical Pillars

1. **Dynamic Need-to-Surplus Matching**: Multi-factor scoring balancing Haversine distance, urgency-to-spoilage, recipient capacity, and dietary constraints.
2. **Multi-Donor $N:1$ Pooling**: Knapsack algorithm pooling surplus from multiple small donors to fulfill large single-destination shelter requirements.
3. **4-Tier Food Urgency Decay**: Color-coded urgency clock (Green $\rightarrow$ Yellow $\rightarrow$ Orange $\rightarrow$ Red) dynamically expanding dispatch radiuses as food approaches safe consumption limits.
4. **Campus Event Fast-Track Mode**: 1-Click surplus declaration interface for symposiums, cultural fests, and messes.
5. **Dual-Stage QR/OTP Chain-of-Custody**: Dual-step handshake at pickup and delivery guaranteeing non-repudiation and food safety.

---

## 📁 Project Architecture

```
FOOD MANAGEMENT/
├── app/
│   ├── __init__.py          # Flask Application Factory
│   ├── config.py            # Parameters & EPA emission factors
│   ├── extensions.py        # SQLAlchemy & Flask-Login instances
│   ├── models/              # User, Donation, Logistics, Impact Models
│   ├── services/            # Matching Engine, Urgency Decay, QR & Impact
│   ├── routes/              # Auth, Donor, NGO, Volunteer, Finder, Admin & API
│   ├── static/              # CSS, JS, Leaflet maps & styling
│   ├── templates/           # Modern Jinja2 HTML Templates
│   └── seed_data.py         # Realistic demo seed data
├── venv/                    # Isolated Python Virtual Environment
├── foodbridge.db            # SQLite Database
├── run.py                   # Application Entry Point
├── test_app.py              # Verification Test Suite
├── requirements.txt         # Project Dependencies
└── PROJECT_DETAILS_FOODBRIDGE.md # Master Academic Specification
```
