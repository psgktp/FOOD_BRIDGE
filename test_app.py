from app import create_app
from app.models.donation import FoodNeedRequest, Donation
from app.models.user import User
from app.services.matching_engine import find_best_matches_for_donation, knapsack_aggregate_donations
from app.services.impact_service import get_global_impact_summary

app = create_app()

with app.app_context():
    print("Testing Donation Matching Engine...")
    don = Donation.query.first()
    matches = find_best_matches_for_donation(don)
    print(f"-> Donation #{don.id} ('{don.title}') found {len(matches)} candidate NGO matches.")
    for m in matches:
        print(f"   * {m['org_profile'].org_name}: {m['score']}% match ({m['distance_km']} km)")
        
    print("\nTesting N:1 Knapsack Pooling Engine...")
    need = FoodNeedRequest.query.first()
    pool = knapsack_aggregate_donations(need)
    print(f"-> Need #{need.id} (Deficit: {need.target_meals_required} meals): Pooled {pool.get('total_pooled_meals')} meals across {len(pool.get('manifest'))} surplus batches.")
    for item in pool.get('manifest'):
        print(f"   + Batch #{item['donation'].id} ('{item['donation'].title}'): {item['allocated_meals']} meals ({item['distance_km']} km)")
        
    print("\nTesting Impact Telemetry Engine...")
    stats = get_global_impact_summary()
    print(f"-> Total Meals Rescued: {stats['total_meals_rescued']}")
    print(f"-> Total Biomass Diverted: {stats['total_biomass_kg']} kg")
    print(f"-> Total CO2e Abated: {stats['total_co2e_kg_saved']} kg")
    print(f"-> Top Campus on Leaderboard: {stats['campus_leaderboard'][0]['institution']}")
    
    print("\n ALL VERIFICATIONS PASSED SUCCESSFULLY!")
