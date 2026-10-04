from datetime import datetime
from app.extensions import db

class DeliveryTask(db.Model):
    __tablename__ = 'delivery_tasks'
    
    id = db.Column(db.Integer, primary_key=True)
    allocation_id = db.Column(db.Integer, db.ForeignKey('donation_allocations.id', ondelete='CASCADE'), nullable=False)
    volunteer_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    
    status = db.Column(db.String(40), default='dispatched') # 'dispatched', 'in_transit', 'delivered', 'failed', 'cancelled'
    transport_mode = db.Column(db.String(30), default='two_wheeler')
    
    # Handshake Timestamps
    dispatched_at = db.Column(db.DateTime, default=datetime.utcnow)
    pickup_verified_at = db.Column(db.DateTime, nullable=True)
    delivery_verified_at = db.Column(db.DateTime, nullable=True)
    
    # Telemetry
    estimated_distance_km = db.Column(db.Float, default=0.0)
    actual_duration_minutes = db.Column(db.Float, nullable=True)
    notes = db.Column(db.Text, nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
