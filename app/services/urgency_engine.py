from datetime import datetime
from app.extensions import db
from app.models.donation import Donation

def update_all_donation_urgencies():
    """
    Scans all active donations and updates their urgency tier in real-time.
    Auto-expires donations that have passed their safe consumption threshold.
    """
    active_donations = Donation.query.filter(
        Donation.status.in_(['available', 'allocated'])
    ).all()
    
    updated_count = 0
    expired_count = 0
    
    now = datetime.utcnow()
    for donation in active_donations:
        old_tier = donation.urgency_tier
        new_tier = donation.calculate_urgency_tier()
        
        if new_tier == 'expired':
            donation.status = 'expired'
            donation.urgency_tier = 'expired'
            expired_count += 1
        elif old_tier != new_tier:
            donation.urgency_tier = new_tier
            updated_count += 1
            
    if updated_count > 0 or expired_count > 0:
        db.session.commit()
        
    return {
        'updated': updated_count,
        'expired': expired_count,
        'active_total': len(active_donations)
    }


def get_urgency_badge_info(tier: str):
    """
    Returns visual badge classes, label, and radius escalation text for UI.
    """
    mapping = {
        'low_green': {
            'label': 'Normal Urgency (>4h)',
            'badge_class': 'badge bg-success',
            'border_class': 'border-success',
            'radius_km': 5.0,
            'color': '#198754',
            'glow_class': 'glow-green'
        },
        'moderate_yellow': {
            'label': 'Moderate Urgency (2-4h)',
            'badge_class': 'badge bg-warning text-dark',
            'border_class': 'border-warning',
            'radius_km': 10.0,
            'color': '#ffc107',
            'glow_class': 'glow-yellow'
        },
        'high_orange': {
            'label': 'High Urgency (1-2h)',
            'badge_class': 'badge bg-orange text-white',
            'border_class': 'border-orange',
            'radius_km': 15.0,
            'color': '#fd7e14',
            'glow_class': 'glow-orange'
        },
        'critical_red': {
            'label': 'CRITICAL URGENT (<1h)',
            'badge_class': 'badge bg-danger text-white pulse-badge',
            'border_class': 'border-danger',
            'radius_km': 25.0,
            'color': '#dc3545',
            'glow_class': 'glow-red'
        },
        'expired': {
            'label': 'Expired',
            'badge_class': 'badge bg-secondary',
            'border_class': 'border-secondary',
            'radius_km': 0.0,
            'color': '#6c757d',
            'glow_class': ''
        }
    }
    return mapping.get(tier, mapping['low_green'])
