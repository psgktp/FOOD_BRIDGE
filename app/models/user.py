from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(150), nullable=False)
    phone = db.Column(db.String(25), nullable=False)
    role = db.Column(db.String(30), nullable=False) # 'donor', 'organization', 'volunteer', 'admin'
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    donor_profile = db.relationship('DonorProfile', backref='user', uselist=False, cascade="all, delete-orphan")
    org_profile = db.relationship('OrgProfile', backref='user', uselist=False, cascade="all, delete-orphan")
    volunteer_profile = db.relationship('VolunteerProfile', backref='user', uselist=False, cascade="all, delete-orphan")
    addresses = db.relationship('UserAddress', backref='user', lazy='dynamic', cascade="all, delete-orphan")
    donations = db.relationship('Donation', backref='donor', lazy='dynamic')
    need_requests = db.relationship('FoodNeedRequest', backref='organization', lazy='dynamic')
    delivery_tasks = db.relationship('DeliveryTask', backref='volunteer', lazy='dynamic')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    @property
    def is_donor(self):
        return self.role == 'donor'
    
    @property
    def is_org(self):
        return self.role == 'organization'
    
    @property
    def is_volunteer(self):
        return self.role == 'volunteer'
    
    @property
    def is_admin(self):
        return self.role == 'admin'


class UserAddress(db.Model):
    __tablename__ = 'user_addresses'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    label = db.Column(db.String(100), default='Primary Location')
    street_address = db.Column(db.Text, nullable=False)
    city = db.Column(db.String(100), nullable=False, default='Chennai')
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    is_default = db.Column(db.Boolean, default=True)


class DonorProfile(db.Model):
    __tablename__ = 'donor_profiles'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, unique=True)
    donor_type = db.Column(db.String(50), nullable=False) # 'college_canteen', 'event_organizer', 'restaurant', 'hotel', 'individual'
    institution_name = db.Column(db.String(200))
    fssai_license = db.Column(db.String(100))
    total_meals_donated = db.Column(db.Integer, default=0)
    total_donations_count = db.Column(db.Integer, default=0)


class OrgProfile(db.Model):
    __tablename__ = 'org_profiles'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, unique=True)
    org_name = db.Column(db.String(200), nullable=False)
    org_type = db.Column(db.String(50), nullable=False) # 'food_bank', 'ngo', 'shelter', 'community_kitchen'
    govt_reg_number = db.Column(db.String(100))
    description = db.Column(db.Text)
    
    # Real-time Capacity & Live Telemetry
    max_daily_capacity = db.Column(db.Integer, default=250, nullable=False)
    current_occupancy = db.Column(db.Integer, default=0)
    is_accepting_donations = db.Column(db.Boolean, default=True)
    
    # Verification & Visibility
    verification_status = db.Column(db.String(30), default='verified') # 'pending', 'verified', 'rejected'
    is_public_in_finder = db.Column(db.Boolean, default=True)
    operating_hours_start = db.Column(db.String(10), default='08:00')
    operating_hours_end = db.Column(db.String(10), default='21:00')
    
    # Accepted categories (comma-separated string or helper)
    accepted_categories = db.Column(db.String(255), default='cooked_meals,raw_groceries,packaged')
    dietary_accepted = db.Column(db.String(100), default='any') # 'vegetarian', 'non_vegetarian', 'any'

    @property
    def capacity_percentage(self):
        if self.max_daily_capacity <= 0:
            return 0
        return min(100, int((self.current_occupancy / self.max_daily_capacity) * 100))

    @property
    def remaining_capacity(self):
        return max(0, self.max_daily_capacity - self.current_occupancy)


class VolunteerProfile(db.Model):
    __tablename__ = 'volunteer_profiles'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, unique=True)
    transport_mode = db.Column(db.String(30), default='two_wheeler') # 'walking', 'bicycle', 'two_wheeler', 'car', 'van'
    max_carrying_meals = db.Column(db.Integer, default=50)
    is_available = db.Column(db.Boolean, default=True)
    current_lat = db.Column(db.Float, nullable=True)
    current_lng = db.Column(db.Float, nullable=True)
    max_travel_radius_km = db.Column(db.Float, default=10.0)
    total_rescues_completed = db.Column(db.Integer, default=0)
    impact_credits = db.Column(db.Integer, default=100)

    @property
    def karma_points(self):
        return self.impact_credits

    @karma_points.setter
    def karma_points(self, value):
        self.impact_credits = value
