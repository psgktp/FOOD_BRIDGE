import random
from datetime import datetime, timedelta
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from app.extensions import db
from app.models.donation import Donation, DonationAllocation
from app.models.user import UserAddress
from app.services.qr_service import generate_qr_base64, build_pickup_qr_payload
from app.services.matching_engine import find_best_matches_for_donation
from app.services.urgency_engine import get_urgency_badge_info, update_all_donation_urgencies

donor_bp = Blueprint('donor', __name__, url_prefix='/donor')

@donor_bp.before_request
@login_required
def check_donor_role():
    if not (current_user.is_donor or current_user.is_admin):
        flash('Access restricted to Food Donors.', 'warning')
        return redirect(url_for('main.index'))


@donor_bp.route('/dashboard')
def dashboard():
    update_all_donation_urgencies()
    
    my_donations = Donation.query.filter_by(donor_id=current_user.id).order_by(Donation.created_at.desc()).all()
    
    active_donations = [d for d in my_donations if d.status in ['available', 'allocated', 'in_transit']]
    past_donations = [d for d in my_donations if d.status in ['delivered', 'completed', 'expired', 'cancelled']]
    
    total_meals = sum(d.quantity_meals for d in past_donations if d.status in ['delivered', 'completed'])
    
    return render_template(
        'donor/dashboard.html',
        active_donations=active_donations,
        past_donations=past_donations,
        total_meals=total_meals,
        get_urgency_badge_info=get_urgency_badge_info
    )


@donor_bp.route('/post', methods=['GET', 'POST'])
def post_food():
    if request.method == 'POST':
        # Check campus fast track
        is_campus_event = request.form.get('is_campus_event') == 'true' or request.form.get('is_campus_event') == 'on'
        event_name = request.form.get('event_name', '').strip()
        
        title = request.form.get('title', '').strip()
        food_category = request.form.get('food_category', 'cooked_meals')
        dietary_type = request.form.get('dietary_type', 'vegetarian')
        quantity_meals = int(request.form.get('quantity_meals') or 10)
        weight_kg = float(request.form.get('weight_approx_kg') or (quantity_meals * 0.4))
        storage_condition = request.form.get('storage_condition', 'ambient')
        
        # Timestamps
        prep_hours_ago = float(request.form.get('prep_hours_ago') or 1.0)
        safe_hours_total = float(request.form.get('safe_hours_total') or 4.0)
        
        now = datetime.utcnow()
        prepared_at = now - timedelta(hours=prep_hours_ago)
        best_before = prepared_at + timedelta(hours=safe_hours_total)
        pickup_end = best_before - timedelta(minutes=30)
        
        if pickup_end <= now:
            flash('Error: The food has already expired or has less than 30 minutes remaining!', 'danger')
            return render_template('donor/post_food.html', is_fast_track=is_campus_event)
            
        # Coordinates
        addr = current_user.addresses.filter_by(is_default=True).first() or current_user.addresses.first()
        pickup_lat = float(request.form.get('pickup_latitude') or (addr.latitude if addr else 13.0827))
        pickup_lng = float(request.form.get('pickup_longitude') or (addr.longitude if addr else 80.2707))
        pickup_address_text = request.form.get('pickup_address_text') or (addr.street_address if addr else "Campus Canteen")
        pickup_instructions = request.form.get('pickup_instructions', '')
        
        # Multi-factor pickup & delivery codes
        pickup_otp = f"{random.randint(100000, 999999)}"
        delivery_otp = f"{random.randint(100000, 999999)}"
        
        donation = Donation(
            donor_id=current_user.id,
            is_campus_event=is_campus_event,
            event_name=event_name if is_campus_event else None,
            title=title,
            food_category=food_category,
            dietary_type=dietary_type,
            quantity_meals=quantity_meals,
            weight_approx_kg=weight_kg,
            storage_condition=storage_condition,
            prepared_at=prepared_at,
            best_before=best_before,
            pickup_window_start=now,
            pickup_window_end=pickup_end,
            pickup_latitude=pickup_lat,
            pickup_longitude=pickup_lng,
            pickup_address_text=pickup_address_text,
            pickup_instructions=pickup_instructions,
            donor_pickup_code=pickup_otp,
            ngo_delivery_code=delivery_otp,
            status='available'
        )
        donation.urgency_tier = donation.calculate_urgency_tier()
        
        db.session.add(donation)
        db.session.commit()
        
        flash(f'Surplus food listing activated successfully! ID: #{donation.id}. Generating smart match alerts...', 'success')
        return redirect(url_for('donor.donation_detail', donation_id=donation.id))
        
    is_fast_track = request.args.get('fast_track') == '1'
    return render_template('donor/post_food.html', is_fast_track=is_fast_track)


@donor_bp.route('/donation/<int:donation_id>')
def donation_detail(donation_id):
    donation = Donation.query.get_or_404(donation_id)
    if donation.donor_id != current_user.id and not current_user.is_admin:
        abort(403)
        
    # Generate Base64 QR Code for Pickup
    qr_payload = build_pickup_qr_payload(donation, current_user)
    qr_image_b64 = generate_qr_base64(qr_payload)
    
    # Calculate Candidate Smart Matches for this donation
    top_matches = find_best_matches_for_donation(donation, max_results=4)
    urgency_info = get_urgency_badge_info(donation.urgency_tier)
    
    return render_template(
        'donor/donation_detail.html',
        donation=donation,
        qr_image_b64=qr_image_b64,
        top_matches=top_matches,
        urgency_info=urgency_info
    )


@donor_bp.route('/donation/<int:donation_id>/cancel', methods=['POST'])
def cancel_donation(donation_id):
    donation = Donation.query.get_or_404(donation_id)
    if donation.donor_id != current_user.id and not current_user.is_admin:
        abort(403)
        
    if donation.status in ['in_transit', 'delivered', 'completed']:
        flash('Cannot cancel a donation that is already in transit or completed.', 'danger')
    else:
        donation.status = 'cancelled'
        db.session.commit()
        flash('Donation listing has been cancelled.', 'info')
        
    return redirect(url_for('donor.dashboard'))
