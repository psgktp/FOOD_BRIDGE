from app import create_app
from app.extensions import db
from app.models.donation import Donation, FoodNeedRequest, DonationAllocation
from app.models.user import User
from app.models.logistics import DeliveryTask
from app.services.matching_engine import knapsack_aggregate_donations

app = create_app()

with app.app_context():
    org = User.query.filter_by(role='organization').first()
    don = Donation.query.filter(Donation.quantity_meals > Donation.allocated_meals).first()
    need = FoodNeedRequest.query.filter_by(is_active=True).first()
    
    print(f"Testing claim of donation #{don.id} for org '{org.full_name}'...")
    
    claim_qty = 10
    allocation = DonationAllocation(
        donation_id=don.id,
        organization_id=org.id,
        need_request_id=need.id if need else None,
        claimed_meals=claim_qty,
        status='allocated'
    )
    db.session.add(allocation)
    db.session.flush() # ID is generated
    
    task = DeliveryTask(
        allocation_id=allocation.id,
        status='dispatched',
        estimated_distance_km=1.5
    )
    db.session.add(task)
    don.allocated_meals += claim_qty
    db.session.commit()
    
    print(f"SUCCESS: Claimed {claim_qty} meals! Created Allocation #{allocation.id} and DeliveryTask #{task.id}.")
    
    # Test Knapsack Pool Claim
    if need and need.remaining_deficit > 0:
        print(f"\nTesting Knapsack Pool claim for need #{need.id}...")
        pool = knapsack_aggregate_donations(need)
        manifest = pool.get('manifest', [])
        print(f"Manifest has {len(manifest)} items.")
        for item in manifest:
            d = item['donation']
            q = min(5, d.remaining_meals)
            if q > 0:
                a = DonationAllocation(
                    donation_id=d.id,
                    organization_id=org.id,
                    need_request_id=need.id,
                    claimed_meals=q,
                    status='allocated'
                )
                db.session.add(a)
                db.session.flush()
                t = DeliveryTask(
                    allocation_id=a.id,
                    status='dispatched',
                    estimated_distance_km=item['distance_km']
                )
                db.session.add(t)
        db.session.commit()
        print("SUCCESS: Knapsack pool claim verified without errors!")
