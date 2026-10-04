from datetime import datetime, timedelta
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from app.extensions import db
from app.models.donation import Donation, FoodNeedRequest, DonationAllocation
from app.models.logistics import DeliveryTask
from app.services.matching_engine import calculate_match_score, knapsack_aggregate_donations
from app.services.urgency_engine import get_urgency_badge_info, update_all_donation_urgencies
from app.services.qr_service import generate_qr_base64, build_delivery_qr_payload
from app.services.impact_service import record_impact_entry

org_bp = Blueprint('org', __name__, url_prefix='/org')

@org_bp.before_request
@login_required
def check_org_role():
    if not (current_user.is_org or current_user.is_admin):
        flash('Access restricted to Verified Organizations / Food Banks.', 'warning')
        return redirect(url_for('main.index'))


@org_bp.route('/dashboard')
def dashboard():
    update_all_donation_urgencies()
    
    # Active open needs posted by this org
    open_needs = FoodNeedRequest.query.filter_by(
        organization_id=current_user.id, is_active=True
    ).order_by(FoodNeedRequest.created_at.desc()).all()
    
    # Active claims and allocations received
    allocations = DonationAllocation.query.filter_by(
        organization_id=current_user.id
    ).order_by(DonationAllocation.created_at.desc()).all()
    
    active_allocations = [a for a in allocations if a.status in ['allocated', 'in_transit']]
    completed_allocations = [a for a in allocations if a.status in ['delivered', 'completed']]
    
    total_meals_received = sum(a.claimed_meals for a in completed_allocations)
    
    return render_template(
        'org/dashboard.html',
        open_needs=open_needs,
        active_allocations=active_allocations,
        completed_allocations=completed_allocations,
        total_meals_received=total_meals_received,
        get_urgency_badge_info=get_urgency_badge_info
    )


@org_bp.route('/post-need', methods=['GET', 'POST'])
def post_need():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        target_meals = int(request.form.get('target_meals_required') or 50)
        food_cat = request.form.get('food_category', 'cooked_meals')
        dietary_pref = request.form.get('dietary_preference', 'any')
        hours_ahead = float(request.form.get('hours_ahead') or 3.0)
        
        needed_by = datetime.utcnow() + timedelta(hours=hours_ahead)
        
        addr = current_user.addresses.filter_by(is_default=True).first() or current_user.addresses.first()
        lat = float(request.form.get('latitude') or (addr.latitude if addr else 13.0827))
        lng = float(request.form.get('longitude') or (addr.longitude if addr else 80.2707))
        loc_name = request.form.get('location_name') or (addr.street_address if addr else "Shelter Distribution Center")
        
        need = FoodNeedRequest(
            organization_id=current_user.id,
            title=title,
            target_meals_required=target_meals,
            food_category=food_cat,
            dietary_preference=dietary_pref,
            needed_by=needed_by,
            latitude=lat,
            longitude=lng,
            location_name=loc_name
        )
        db.session.add(need)
        db.session.commit()
        
        flash(f'Food deficit request of {target_meals} meals published to the Food Need Heatmap!', 'success')
        return redirect(url_for('org.match_feed', need_id=need.id))
        
    return render_template('org/post_need.html')


@org_bp.route('/matches')
def match_feed():
    update_all_donation_urgencies()
    
    need_id = request.args.get('need_id')
    active_need = None
    if need_id:
        active_need = FoodNeedRequest.query.get(need_id)
        
    # Find all available donations
    available_donations = Donation.query.filter(
        Donation.status.in_(['available', 'allocated']),
        Donation.quantity_meals > Donation.allocated_meals
    ).all()
    
    scored_matches = []
    for don in available_donations:
        score, dist_km, breakdown = calculate_match_score(don, current_user, need_request=active_need)
        scored_matches.append({
            'donation': don,
            'score': score,
            'distance_km': dist_km,
            'breakdown': breakdown,
            'urgency_info': get_urgency_badge_info(don.urgency_tier)
        })
        
    scored_matches.sort(key=lambda x: x['score'], reverse=True)
    
    # Check Knapsack Multi-Donor Pool if an active need request is specified
    knapsack_pool = None
    if active_need and active_need.remaining_deficit > 0:
        knapsack_pool = knapsack_aggregate_donations(active_need)
        
    return render_template(
        'org/match_feed.html',
        matches=scored_matches,
        active_need=active_need,
        knapsack_pool=knapsack_pool,
        open_needs=current_user.need_requests.filter_by(is_active=True).all()
    )


@org_bp.route('/claim/<int:donation_id>', methods=['POST'])
def claim_donation(donation_id):
    donation = Donation.query.get_or_404(donation_id)
    if donation.remaining_meals <= 0:
        flash('Sorry, this donation has already been fully claimed.', 'warning')
        return redirect(url_for('org.match_feed'))
        
    need_id = request.form.get('need_request_id')
    need_req = FoodNeedRequest.query.get(need_id) if need_id else None
    
    requested_qty = int(request.form.get('claim_quantity') or donation.remaining_meals)
    claim_qty = min(requested_qty, donation.remaining_meals)
    
    allocation = DonationAllocation(
        donation_id=donation.id,
        organization_id=current_user.id,
        need_request_id=need_req.id if need_req else None,
        claimed_meals=claim_qty,
        status='allocated'
    )
    db.session.add(allocation)
    db.session.flush()
    
    donation.allocated_meals += claim_qty
    if donation.allocated_meals >= donation.quantity_meals:
        donation.status = 'allocated'
        
    if need_req:
        need_req.meals_fulfilled += claim_qty
        if need_req.meals_fulfilled >= need_req.target_meals_required:
            need_req.status = 'fulfilled'
            
    # Create Delivery Task for volunteer network
    delivery_task = DeliveryTask(
        allocation_id=allocation.id,
        status='dispatched',
        estimated_distance_km=2.5
    )
    
    db.session.add(delivery_task)
    
    # Update Org occupancy telemetry
    if current_user.org_profile:
        current_user.org_profile.current_occupancy += claim_qty
        
    db.session.commit()
    
    flash(f'Successfully claimed {claim_qty} meals from "{donation.title}"! Volunteer pickup request dispatched.', 'success')
    return redirect(url_for('org.dashboard'))


@org_bp.route('/claim-pool', methods=['POST'])
def claim_knapsack_pool():
    need_id = request.form.get('need_request_id')
    need_req = FoodNeedRequest.query.get_or_404(need_id)
    
    pool_result = knapsack_aggregate_donations(need_req)
    manifest = pool_result.get('manifest', [])
    
    if not manifest:
        flash('No available donations found in range to pool.', 'warning')
        return redirect(url_for('org.match_feed', need_id=need_id))
        
    total_allocated = 0
    for item in manifest:
        don = item['donation']
        claim_qty = item['allocated_meals']
        if claim_qty > 0 and don.remaining_meals > 0:
            actual_claim = min(claim_qty, don.remaining_meals)
            alloc = DonationAllocation(
                donation_id=don.id,
                organization_id=current_user.id,
                need_request_id=need_req.id,
                claimed_meals=actual_claim,
                status='allocated'
            )
            don.allocated_meals += actual_claim
            if don.allocated_meals >= don.quantity_meals:
                don.status = 'allocated'
                
            db.session.add(alloc)
            db.session.flush()
            
            task = DeliveryTask(
                allocation_id=alloc.id,
                status='dispatched',
                estimated_distance_km=item['distance_km']
            )
            db.session.add(task)
            total_allocated += actual_claim
            
    need_req.meals_fulfilled += total_allocated
    if need_req.meals_fulfilled >= need_req.target_meals_required:
        need_req.status = 'fulfilled'
        
    db.session.commit()
    flash(f'Multi-Donor Aggregation Successful! Pooled {total_allocated} meals across {len(manifest)} donors.', 'success')
    return redirect(url_for('org.dashboard'))


@org_bp.route('/update-capacity', methods=['POST'])
def update_capacity():
    max_cap = int(request.form.get('max_daily_capacity') or 250)
    current_occ = int(request.form.get('current_occupancy') or 0)
    is_accepting = bool(request.form.get('is_accepting_donations'))
    
    if current_user.org_profile:
        current_user.org_profile.max_daily_capacity = max_cap
        current_user.org_profile.current_occupancy = current_occ
        current_user.org_profile.is_accepting_donations = is_accepting
        db.session.commit()
        flash('Live intake capacity and storage telemetry updated.', 'success')
        
    return redirect(url_for('org.dashboard'))


@org_bp.route('/verify-receipt/<int:allocation_id>', methods=['GET', 'POST'])
def verify_receipt(allocation_id):
    allocation = DonationAllocation.query.get_or_404(allocation_id)
    if allocation.organization_id != current_user.id and not current_user.is_admin:
        abort(403)
        
    if request.method == 'POST':
        entered_otp = request.form.get('otp', '').strip()
        expected_otp = allocation.donation.ngo_delivery_code
        
        if entered_otp == expected_otp:
            allocation.status = 'delivered'
            if allocation.delivery_task:
                allocation.delivery_task.status = 'delivered'
                allocation.delivery_task.delivery_verified_at = datetime.utcnow()
                
            # Log to Impact Ledger
            vol_user = allocation.delivery_task.volunteer if allocation.delivery_task else None
            record_impact_entry(allocation, volunteer_user=vol_user)
            
            flash('Delivery handshake confirmed! Impact logged and green certificates generated.', 'success')
            return redirect(url_for('org.dashboard'))
        else:
            flash('Invalid Handshake Delivery OTP. Please verify with the volunteer.', 'danger')
            
    # Generate Delivery Handshake QR
    qr_payload = build_delivery_qr_payload(allocation, current_user)
    qr_image_b64 = generate_qr_base64(qr_payload)
    
    return render_template(
        'org/verify_receipt.html',
        allocation=allocation,
        qr_image_b64=qr_image_b64
    )
