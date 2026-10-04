from datetime import datetime
from app.extensions import db

class ImpactLedger(db.Model):
    __tablename__ = 'impact_ledger'
    
    id = db.Column(db.Integer, primary_key=True)
    allocation_id = db.Column(db.Integer, db.ForeignKey('donation_allocations.id', ondelete='SET NULL'), nullable=True)
    
    donor_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    organization_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    volunteer_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    
    meals_rescued = db.Column(db.Integer, nullable=False)
    biomass_kg = db.Column(db.Float, nullable=False)
    co2e_kg_saved = db.Column(db.Float, nullable=False) # EPA conversion factor = biomass_kg * 2.5
    economic_value_inr = db.Column(db.Float, default=0.0) # Calculated @ ~50 INR per meal box
    
    institution_credited = db.Column(db.String(200), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    donor = db.relationship('User', foreign_keys=[donor_id])
    organization = db.relationship('User', foreign_keys=[organization_id])
    volunteer = db.relationship('User', foreign_keys=[volunteer_id])


class SystemNotification(db.Model):
    __tablename__ = 'system_notifications'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    title = db.Column(db.String(150), nullable=False)
    message = db.Column(db.Text, nullable=False)
    notification_type = db.Column(db.String(50), default='info') # 'urgent_match', 'pickup_assigned', 'delivered', 'kyc'
    is_read = db.Column(db.Boolean, default=False)
    reference_url = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref=db.backref('notifications', lazy='dynamic', cascade="all, delete-orphan"))
