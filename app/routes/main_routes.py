from flask import Blueprint, render_template
from app.models.donation import Donation, FoodNeedRequest
from app.models.user import OrgProfile
from app.services.impact_service import get_global_impact_summary
from app.services.urgency_engine import get_urgency_badge_info, update_all_donation_urgencies

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    update_all_donation_urgencies()
    stats = get_global_impact_summary()
    
    # Active emergency needs
    urgent_needs = FoodNeedRequest.query.filter_by(is_active=True).order_by(FoodNeedRequest.needed_by.asc()).limit(4).all()
    
    # Recent live surplus postings
    live_surplus = Donation.query.filter(
        Donation.status.in_(['available', 'allocated'])
    ).order_by(Donation.created_at.desc()).limit(4).all()
    
    return render_template(
        'index.html',
        stats=stats,
        urgent_needs=urgent_needs,
        live_surplus=live_surplus,
        get_urgency_badge_info=get_urgency_badge_info
    )


@main_bp.route('/impact')
def impact_page():
    stats = get_global_impact_summary()
    return render_template('impact/index.html', stats=stats)


@main_bp.route('/about')
def about():
    return render_template('about.html')
