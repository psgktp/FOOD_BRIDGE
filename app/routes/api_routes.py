from flask import Blueprint, jsonify, request
from app.extensions import db
from app.models.donation import Donation, FoodNeedRequest
from app.models.user import User
from app.services.matching_engine import find_best_matches_for_donation, knapsack_aggregate_donations
from app.services.impact_service import get_global_impact_summary

api_bp = Blueprint('api', __name__, url_prefix='/api/v1')

@api_bp.route('/impact-summary', methods=['GET'])
def impact_summary():
    return jsonify({'status': 'success', 'data': get_global_impact_summary()})

@api_bp.route('/donations/live', methods=['GET'])
def live_donations():
    donations = Donation.query.filter(Donation.status.in_(['available', 'allocated'])).all()
    results = []
    for d in donations:
        results.append({
            'id': d.id,
            'title': d.title,
            'quantity_meals': d.quantity_meals,
            'remaining_meals': d.remaining_meals,
            'food_category': d.food_category,
            'dietary_type': d.dietary_type,
            'urgency_tier': d.urgency_tier,
            'hours_remaining': round(d.hours_remaining, 1),
            'latitude': d.pickup_latitude,
            'longitude': d.pickup_longitude,
            'is_campus_event': d.is_campus_event,
            'event_name': d.event_name
        })
    return jsonify({'status': 'success', 'count': len(results), 'data': results})

@api_bp.route('/needs/active', methods=['GET'])
def active_needs():
    needs = FoodNeedRequest.query.filter_by(is_active=True).all()
    results = []
    for n in needs:
        results.append({
            'id': n.id,
            'title': n.title,
            'target_meals': n.target_meals_required,
            'meals_fulfilled': n.meals_fulfilled,
            'remaining_deficit': n.remaining_deficit,
            'dietary_preference': n.dietary_preference,
            'latitude': n.latitude,
            'longitude': n.longitude,
            'location_name': n.location_name,
            'urgency_level': n.urgency_level
        })
    return jsonify({'status': 'success', 'count': len(results), 'data': results})

@api_bp.route('/match/pool-need/<int:need_id>', methods=['GET'])
def pool_need(need_id):
    need_req = FoodNeedRequest.query.get_or_404(need_id)
    pool = knapsack_aggregate_donations(need_req)
    
    clean_manifest = []
    for m in pool.get('manifest', []):
        clean_manifest.append({
            'donation_id': m['donation'].id,
            'title': m['donation'].title,
            'distance_km': m['distance_km'],
            'allocated_meals': m['allocated_meals'],
            'hours_remaining': m['hours_remaining'],
            'urgency_tier': m['urgency_tier'],
            'is_campus_event': m['is_campus_event']
        })
        
    return jsonify({
        'status': 'success',
        'target_meals': pool['target_meals'],
        'total_pooled_meals': pool['total_pooled_meals'],
        'is_fully_satisfied': pool['is_fully_satisfied'],
        'manifest': clean_manifest
    })
