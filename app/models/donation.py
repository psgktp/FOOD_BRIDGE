import uuid
from datetime import datetime, timedelta
from app.extensions import db

class FoodNeedRequest(db.Model):
    __tablename__ = 'food_need_requests'
    
    id = db.Column(db.Integer, primary_key=True)
    organization_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    target_meals_required = db.Column(db.Integer, nullable=False)
    meals_fulfilled = db.Column(db.Integer, default=0)
    food_category = db.Column(db.String(50), default='cooked_meals') # 'cooked_meals', 'raw_groceries', 'packaged'
    dietary_preference = db.Column(db.String(30), default='any') # 'vegetarian', 'vegan', 'non_vegetarian', 'any'
    
    needed_by = db.Column(db.DateTime, nullable=False)
    urgency_level = db.Column(db.String(20), default='moderate_yellow') # 'low_green', 'moderate_yellow', 'high_orange', 'critical_red'
    
    # Geolocation for Heatmap & Matching
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    location_name = db.Column(db.String(200), nullable=False)
    
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    allocations = db.relationship('DonationAllocation', backref='need_request', lazy='dynamic')
    
    @property
    def remaining_deficit(self):
        return max(0, self.target_meals_required - self.meals_fulfilled)
    
    @property
    def fulfillment_percentage(self):
        if self.target_meals_required <= 0:
            return 100
        return min(100, int((self.meals_fulfilled / self.target_meals_required) * 100))


class Donation(db.Model):
    __tablename__ = 'donations'
    
    id = db.Column(db.Integer, primary_key=True)
    donor_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    
    # Event Context
    is_campus_event = db.Column(db.Boolean, default=False)
    event_name = db.Column(db.String(200), nullable=True)
    
    title = db.Column(db.String(200), nullable=False)
    food_category = db.Column(db.String(50), default='cooked_meals') # 'cooked_meals', 'raw_groceries', 'packaged_goods', 'bakery_items', 'produce'
    dietary_type = db.Column(db.String(30), default='vegetarian') # 'vegetarian', 'vegan', 'non_vegetarian', 'halal', 'jain'
    
    quantity_meals = db.Column(db.Integer, nullable=False)
    allocated_meals = db.Column(db.Integer, default=0)
    weight_approx_kg = db.Column(db.Float, default=0.0)
    storage_condition = db.Column(db.String(30), default='ambient') # 'ambient', 'refrigerated', 'frozen', 'hot_insulated'
    
    # Time Constraints & Safe Consumption
    prepared_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    best_before = db.Column(db.DateTime, nullable=False)
    pickup_window_start = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    pickup_window_end = db.Column(db.DateTime, nullable=False)
    
    # Pickup Geolocation
    pickup_latitude = db.Column(db.Float, nullable=False)
    pickup_longitude = db.Column(db.Float, nullable=False)
    pickup_address_text = db.Column(db.Text, nullable=False)
    pickup_instructions = db.Column(db.Text, nullable=True)
    
    # Safety Affirmation & Status
    food_safety_guaranteed = db.Column(db.Boolean, default=True)
    status = db.Column(db.String(40), default='available') # 'available', 'allocated', 'in_transit', 'delivered', 'completed', 'expired', 'cancelled'
    urgency_tier = db.Column(db.String(20), default='low_green') # 'low_green', 'moderate_yellow', 'high_orange', 'critical_red'
    
    # Cryptographic Tokens & Multi-Factor Verification
    donor_pickup_code = db.Column(db.String(6), nullable=False)
    ngo_delivery_code = db.Column(db.String(6), nullable=False)
    qr_secret_token = db.Column(db.String(64), default=lambda: str(uuid.uuid4()))
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    allocations = db.relationship('DonationAllocation', backref='donation', lazy='dynamic', cascade="all, delete-orphan")
    
    @property
    def remaining_meals(self):
        return max(0, self.quantity_meals - self.allocated_meals)
    
    @property
    def is_fully_allocated(self):
        return self.allocated_meals >= self.quantity_meals
    
    @property
    def hours_remaining(self):
        diff = self.best_before - datetime.utcnow()
        return max(0.0, diff.total_seconds() / 3600.0)
    
    def calculate_urgency_tier(self):
        hrs = self.hours_remaining
        if hrs <= 0:
            return 'expired'
        elif hrs < 1.0:
            return 'critical_red'
        elif hrs < 2.5:
            return 'high_orange'
        elif hrs < 4.5:
            return 'moderate_yellow'
        else:
            return 'low_green'


class DonationAllocation(db.Model):
    """Handles N:1 Pooling where multiple donations satisfy an NGO need request, or 1 donation is divided."""
    __tablename__ = 'donation_allocations'
    
    id = db.Column(db.Integer, primary_key=True)
    donation_id = db.Column(db.Integer, db.ForeignKey('donations.id', ondelete='CASCADE'), nullable=False)
    organization_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    need_request_id = db.Column(db.Integer, db.ForeignKey('food_need_requests.id', ondelete='SET NULL'), nullable=True)
    
    claimed_meals = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(40), default='allocated') # 'allocated', 'in_transit', 'delivered', 'cancelled'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    organization = db.relationship('User', foreign_keys=[organization_id], backref='allocations_received')
    delivery_task = db.relationship('DeliveryTask', backref='allocation', uselist=False, cascade="all, delete-orphan")
    impact_entry = db.relationship('ImpactLedger', backref='allocation', uselist=False, cascade="all, delete-orphan")
