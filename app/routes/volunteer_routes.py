from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from app.extensions import db
from app.models.logistics import DeliveryTask
from app.models.donation import DonationAllocation, Donation
from app.services.matching_engine import haversine_distance
from app.services.urgency_engine import get_urgency_badge_info, update_all_donation_urgencies
from app.services.impact_service import record_impact_entry

volunteer_bp = Blueprint('volunteer', __name__, url_prefix='/volunteer')

@volunteer_bp.before_request
@login_required
def check_volunteer_role():
    if not (current_user.is_volunteer or current_user.is_admin):
        flash('Access restricted to Registered Volunteers.', 'warning')
        return redirect(url_for('main.index'))


@volunteer_bp.route('/dashboard')
def dashboard():
    update_all_donation_urgencies()
    
    # Active delivery task currently claimed by this volunteer
    my_active_tasks = DeliveryTask.query.filter_by(
        volunteer_id=current_user.id
    ).filter(DeliveryTask.status.in_(['dispatched', 'in_transit'])).all()
    
    # Completed tasks
    completed_tasks = DeliveryTask.query.filter_by(
        volunteer_id=current_user.id, status='delivered'
    ).order_by(DeliveryTask.delivery_verified_at.desc()).all()
    
    # Available tasks waiting for volunteer pickup
    available_tasks = DeliveryTask.query.filter_by(
        volunteer_id=None, status='dispatched'
    ).all()
    
    # Calculate distance for each available task from volunteer location
    vol_lat = current_user.volunteer_profile.current_lat if current_user.volunteer_profile else 13.0827
    vol_lng = current_user.volunteer_profile.current_lng if current_user.volunteer_profile else 80.2707
    
    task_feed = []
    for task in available_tasks:
        don = task.allocation.donation
        dist_pickup = haversine_distance(vol_lat, vol_lng, don.pickup_latitude, don.pickup_longitude)
        task_feed.append({
            'task': task,
            'donation': don,
            'allocation': task.allocation,
            'dist_pickup_km': round(dist_pickup, 2),
            'urgency_info': get_urgency_badge_info(don.urgency_tier)
        })
        
    task_feed.sort(key=lambda x: x['dist_pickup_km'])
    
    return render_template(
        'volunteer/dashboard.html',
        my_active_tasks=my_active_tasks,
        completed_tasks=completed_tasks,
        available_tasks=task_feed,
        get_urgency_badge_info=get_urgency_badge_info
    )


@volunteer_bp.route('/task/<int:task_id>/claim', methods=['POST'])
def claim_task(task_id):
    task = DeliveryTask.query.get_or_404(task_id)
    if task.volunteer_id is not None:
        flash('This task has already been claimed by another volunteer.', 'warning')
        return redirect(url_for('volunteer.dashboard'))
        
    task.volunteer_id = current_user.id
    task.status = 'dispatched'
    task.transport_mode = current_user.volunteer_profile.transport_mode if current_user.volunteer_profile else 'two_wheeler'
    db.session.commit()
    
    flash(f'Delivery task #{task.id} claimed! Proceed to donor location for pickup.', 'success')
    return redirect(url_for('volunteer.track_task', task_id=task.id))


@volunteer_bp.route('/task/<int:task_id>/track')
def track_task(task_id):
    task = DeliveryTask.query.get_or_404(task_id)
    if task.volunteer_id != current_user.id and not current_user.is_admin:
        abort(403)
        
    allocation = task.allocation
    donation = allocation.donation
    org_user = allocation.organization
    
    org_addr = org_user.addresses.filter_by(is_default=True).first() or org_user.addresses.first()
    org_lat = org_addr.latitude if org_addr else (donation.pickup_latitude + 0.02)
    org_lng = org_addr.longitude if org_addr else (donation.pickup_longitude + 0.02)
    
    return render_template(
        'volunteer/track_task.html',
        task=task,
        donation=donation,
        allocation=allocation,
        org_user=org_user,
        org_lat=org_lat,
        org_lng=org_lng,
        urgency_info=get_urgency_badge_info(donation.urgency_tier)
    )


@volunteer_bp.route('/task/<int:task_id>/verify-pickup', methods=['POST'])
def verify_pickup(task_id):
    task = DeliveryTask.query.get_or_404(task_id)
    if task.volunteer_id != current_user.id and not current_user.is_admin:
        abort(403)
        
    entered_otp = request.form.get('otp', '').strip()
    donation = task.allocation.donation
    
    if entered_otp == donation.donor_pickup_code:
        task.status = 'in_transit'
        task.pickup_verified_at = datetime.utcnow()
        task.allocation.status = 'in_transit'
        donation.status = 'in_transit'
        db.session.commit()
        
        flash('Pickup verified successfully! Status is now IN_TRANSIT. Deliver food to the organization.', 'success')
    else:
        flash('Invalid Donor Pickup OTP. Please check with the food donor.', 'danger')
        
    return redirect(url_for('volunteer.track_task', task_id=task.id))


@volunteer_bp.route('/task/<int:task_id>/verify-delivery', methods=['POST'])
def verify_delivery(task_id):
    task = DeliveryTask.query.get_or_404(task_id)
    if task.volunteer_id != current_user.id and not current_user.is_admin:
        abort(403)
        
    entered_otp = request.form.get('otp', '').strip()
    donation = task.allocation.donation
    
    if entered_otp == donation.ngo_delivery_code:
        task.status = 'delivered'
        task.delivery_verified_at = datetime.utcnow()
        task.allocation.status = 'delivered'
        
        # Check if all allocations for this donation are delivered
        all_delivered = all(a.status == 'delivered' for a in donation.allocations)
        if all_delivered and donation.allocated_meals >= donation.quantity_meals:
            donation.status = 'delivered'
            
        # Log to Impact Ledger & Credit Impact Credits
        record_impact_entry(task.allocation, volunteer_user=current_user)
        
        flash('Delivery completed and verified! Impact Credits credited to your profile.', 'success')
        return redirect(url_for('volunteer.dashboard'))
    else:
        flash('Invalid NGO Delivery Handshake OTP. Please ask the NGO receiver.', 'danger')
        return redirect(url_for('volunteer.track_task', task_id=task.id))
