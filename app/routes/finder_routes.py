from flask import Blueprint, render_template, request, jsonify
from app.models.user import User, OrgProfile, UserAddress
from app.models.donation import FoodNeedRequest, Donation
from app.services.matching_engine import haversine_distance

finder_bp = Blueprint('finder', __name__, url_prefix='/finder')

@finder_bp.route('/')
def index():
    query_text = request.args.get('q', '').strip().lower()
    category_filter = request.args.get('category', 'all')
    
    # Query verified organizations that are public in finder
    org_users = User.query.filter_by(role='organization', is_active=True).all()
    
    food_banks = []
    for user in org_users:
        prof = user.org_profile
        if prof and prof.is_public_in_finder:
            # Filter matches
            if query_text and (query_text not in prof.org_name.lower() and query_text not in (prof.description or '').lower()):
                continue
                
            addr = user.addresses.filter_by(is_default=True).first() or user.addresses.first()
            lat = addr.latitude if addr else 13.0827
            lng = addr.longitude if addr else 80.2707
            street = addr.street_address if addr else "Chennai Central"
            
            # Active open need count
            open_needs_count = FoodNeedRequest.query.filter_by(organization_id=user.id, is_active=True).count()
            
            food_banks.append({
                'id': user.id,
                'name': prof.org_name,
                'type': prof.org_type.replace('_', ' ').title(),
                'address': street,
                'latitude': lat,
                'longitude': lng,
                'capacity_pct': prof.capacity_percentage,
                'remaining_cap': prof.remaining_capacity,
                'max_cap': prof.max_daily_capacity,
                'is_accepting': prof.is_accepting_donations,
                'accepted_categories': prof.accepted_categories,
                'operating_hours': f"{prof.operating_hours_start} - {prof.operating_hours_end}",
                'open_needs_count': open_needs_count,
                'description': prof.description or "Verified hunger-relief partner in the FoodBridge network."
            })
            
    return render_template('finder/index.html', food_banks=food_banks, query_text=query_text)


@finder_bp.route('/api/heatmap-data')
def get_heatmap_points():
    """
    Returns JSON array of active food deficit request points with weights for Leaflet.heat
    [lat, lng, intensity]
    """
    active_needs = FoodNeedRequest.query.filter_by(is_active=True).all()
    points = []
    
    for need in active_needs:
        if need.remaining_deficit > 0:
            # Normalized intensity between 0.3 and 1.0 based on deficit size
            intensity = min(1.0, max(0.3, need.remaining_deficit / 200.0))
            points.append({
                'lat': need.latitude,
                'lng': need.longitude,
                'intensity': intensity,
                'title': need.title,
                'meals_needed': need.remaining_deficit,
                'location': need.location_name,
                'urgency': need.urgency_level
            })
            
    return jsonify({'points': points})
