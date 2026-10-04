from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from app.extensions import db
from app.models.user import User, OrgProfile, DonorProfile, VolunteerProfile
from app.models.donation import Donation, FoodNeedRequest
from app.models.logistics import DeliveryTask
from app.models.impact import ImpactLedger
from app.services.impact_service import get_global_impact_summary

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.before_request
@login_required
def check_admin_role():
    if not current_user.is_admin:
        flash('Administrator access required.', 'danger')
        return redirect(url_for('main.index'))


@admin_bp.route('/dashboard')
def dashboard():
    stats = get_global_impact_summary()
    
    pending_orgs = OrgProfile.query.filter_by(verification_status='pending').all()
    verified_orgs = OrgProfile.query.filter_by(verification_status='verified').all()
    
    recent_donations = Donation.query.order_by(Donation.created_at.desc()).limit(10).all()
    recent_deliveries = DeliveryTask.query.order_by(DeliveryTask.created_at.desc()).limit(10).all()
    
    return render_template(
        'admin/dashboard.html',
        stats=stats,
        pending_orgs=pending_orgs,
        verified_orgs=verified_orgs,
        recent_donations=recent_donations,
        recent_deliveries=recent_deliveries
    )


@admin_bp.route('/verify-org/<int:org_profile_id>/<action>', methods=['POST'])
def verify_org_action(org_profile_id, action):
    org_prof = OrgProfile.query.get_or_404(org_profile_id)
    if action == 'approve':
        org_prof.verification_status = 'verified'
        flash(f'Organization "{org_prof.org_name}" verified successfully!', 'success')
    elif action == 'reject':
        org_prof.verification_status = 'rejected'
        flash(f'Organization "{org_prof.org_name}" rejected.', 'warning')
        
    db.session.commit()
    return redirect(url_for('admin.dashboard'))
