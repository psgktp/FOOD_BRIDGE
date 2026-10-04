import math
from datetime import datetime
from app.models.user import User, OrgProfile, UserAddress
from app.models.donation import Donation, FoodNeedRequest
from app.config import Config

def haversine_distance(lat1, lon1, lat2, lon2):
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees) in kilometers.
    """
    if lat1 is None or lon1 is None or lat2 is None or lon2 is None:
        return 999.0
        
    R = 6371.0 # Earth radius in kilometers
    
    d_lat = math.radians(lat2 - lat1)
    d_lon = math.radians(lon2 - lon1)
    
    a = (math.sin(d_lat / 2.0) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(d_lon / 2.0) ** 2)
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    
    return R * c


def calculate_match_score(donation: Donation, org_user: User, need_request: FoodNeedRequest = None):
    """
    Multi-Factor Algorithmic Score S_ij in [0, 100]:
    S_ij = w_d * f_dist + w_t * f_urgency + w_c * f_cap + w_p * f_pref
    """
    org_profile = org_user.org_profile
    if not org_profile or not org_profile.is_accepting_donations:
        return 0.0, 999.0, {}

    # 1. Geolocation & Distance Calculation
    # Fetch primary address of organization or use need_request coordinates
    if need_request:
        org_lat, org_lng = need_request.latitude, need_request.longitude
    else:
        addr = org_user.addresses.filter_by(is_default=True).first() or org_user.addresses.first()
        org_lat = addr.latitude if addr else 13.0827
        org_lng = addr.longitude if addr else 80.2707
        
    dist_km = haversine_distance(donation.pickup_latitude, donation.pickup_longitude, org_lat, org_lng)
    
    max_radius = Config.MAX_SEARCH_RADIUS_KM
    if dist_km > max_radius:
        f_dist = 0.0
    else:
        f_dist = max(0.0, 1.0 - (dist_km / max_radius))
        
    # 2. Urgency Factor
    hrs_rem = donation.hours_remaining
    if hrs_rem <= 0:
        f_urgency = 0.0
    elif hrs_rem < 1.0:
        f_urgency = 1.0 # Maximum urgency
    elif hrs_rem < 3.0:
        f_urgency = 0.85
    elif hrs_rem < 6.0:
        f_urgency = 0.60
    else:
        f_urgency = 0.35

    # 3. Capacity Compatibility
    unfilled_need = need_request.remaining_deficit if need_request else org_profile.remaining_capacity
    if unfilled_need <= 0:
        f_cap = 0.1
    else:
        # Ideal match if available donation can satisfy or fit comfortably into need
        f_cap = min(1.0, unfilled_need / max(1, donation.remaining_meals))
        if f_cap < 0.2:
            f_cap = 0.3

    # 4. Dietary and Category Compatibility
    f_pref = 1.0
    # Check dietary compatibility
    if need_request and need_request.dietary_preference != 'any':
        if need_request.dietary_preference != donation.dietary_type and donation.dietary_type != 'vegan':
            f_pref *= 0.4
            
    if org_profile.dietary_accepted != 'any' and org_profile.dietary_accepted != donation.dietary_type:
        f_pref *= 0.5
        
    # Check category acceptance
    if org_profile.accepted_categories and donation.food_category not in org_profile.accepted_categories:
        f_pref *= 0.4

    # Calculate Weighted Composite Score
    score = (
        Config.WEIGHT_DISTANCE * f_dist +
        Config.WEIGHT_URGENCY * f_urgency +
        Config.WEIGHT_CAPACITY * f_cap +
        Config.WEIGHT_PREFERENCE * f_pref
    ) * 100.0
    
    score = round(min(100.0, max(0.0, score)), 1)
    
    breakdown = {
        'distance_km': round(dist_km, 2),
        'dist_factor': round(f_dist * 100, 1),
        'urgency_factor': round(f_urgency * 100, 1),
        'capacity_factor': round(f_cap * 100, 1),
        'preference_factor': round(f_pref * 100, 1),
        'unfilled_need': unfilled_need
    }
    
    return score, dist_km, breakdown


def find_best_matches_for_donation(donation: Donation, max_results=5):
    """
    Ranks all verified active NGOs and their active need requests for a given donation.
    """
    active_orgs = User.query.filter_by(role='organization', is_active=True).all()
    results = []
    
    for org in active_orgs:
        # Check active need requests first
        open_needs = FoodNeedRequest.query.filter_by(organization_id=org.id, is_active=True).all()
        
        if open_needs:
            for need in open_needs:
                if need.remaining_deficit > 0:
                    score, dist, breakdown = calculate_match_score(donation, org, need_request=need)
                    results.append({
                        'org_user': org,
                        'org_profile': org.org_profile,
                        'need_request': need,
                        'score': score,
                        'distance_km': dist,
                        'breakdown': breakdown
                    })
        else:
            # Match against organization general profile
            score, dist, breakdown = calculate_match_score(donation, org, need_request=None)
            results.append({
                'org_user': org,
                'org_profile': org.org_profile,
                'need_request': None,
                'score': score,
                'distance_km': dist,
                'breakdown': breakdown
            })
            
    # Sort by highest match score descending
    results.sort(key=lambda x: x['score'], reverse=True)
    return results[:max_results]


def knapsack_aggregate_donations(need_request: FoodNeedRequest, max_radius_km=15.0):
    """
    Multi-Donor Resource Aggregation (N:1 Knapsack Heuristic).
    Given an NGO deficit (e.g. 200 meals), finds proximate surplus donations
    and builds an aggregated multi-stop rescue manifest.
    """
    target = need_request.remaining_deficit
    if target <= 0:
        return []
        
    available_donations = Donation.query.filter(
        Donation.status.in_(['available', 'allocated']),
        Donation.quantity_meals > Donation.allocated_meals
    ).all()
    
    candidates = []
    for don in available_donations:
        dist = haversine_distance(
            need_request.latitude, need_request.longitude,
            don.pickup_latitude, don.pickup_longitude
        )
        if dist <= max_radius_km and don.hours_remaining > 0:
            # Priority quotient: higher quantity, closer distance, higher urgency
            urgency_q = 1.0 / (don.hours_remaining + 0.1)
            priority = (don.remaining_meals / max(0.5, dist)) * urgency_q
            candidates.append({
                'donation': don,
                'distance_km': round(dist, 2),
                'available_meals': don.remaining_meals,
                'priority': priority
            })
            
    # Sort candidates by priority score descending
    candidates.sort(key=lambda x: x['priority'], reverse=True)
    
    selected_manifest = []
    accumulated_meals = 0
    
    for item in candidates:
        don = item['donation']
        needed = target - accumulated_meals
        claim_qty = min(needed, item['available_meals'])
        
        selected_manifest.append({
            'donation': don,
            'distance_km': item['distance_km'],
            'allocated_meals': claim_qty,
            'hours_remaining': round(don.hours_remaining, 1),
            'urgency_tier': don.urgency_tier,
            'is_campus_event': don.is_campus_event,
            'event_name': don.event_name
        })
        
        accumulated_meals += claim_qty
        if accumulated_meals >= target:
            break
            
    return {
        'manifest': selected_manifest,
        'total_pooled_meals': accumulated_meals,
        'target_meals': target,
        'is_fully_satisfied': accumulated_meals >= target
    }
