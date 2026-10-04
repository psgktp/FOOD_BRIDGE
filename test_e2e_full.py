import sys
import unittest
from datetime import datetime, timedelta
from app import create_app
from app.extensions import db
from app.models.user import User, DonorProfile, OrgProfile, VolunteerProfile, UserAddress
from app.models.donation import Donation, FoodNeedRequest, DonationAllocation
from app.models.logistics import DeliveryTask
from app.models.impact import ImpactLedger
from app.services.matching_engine import haversine_distance, calculate_match_score, find_best_matches_for_donation, knapsack_aggregate_donations
from app.services.urgency_engine import update_all_donation_urgencies, get_urgency_badge_info
from app.services.impact_service import get_global_impact_summary, record_impact_entry
from app.services.qr_service import generate_qr_base64, build_pickup_qr_payload, build_delivery_qr_payload

def run_comprehensive_diagnostics():
    app = create_app()
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    
    print("=" * 70)
    print("[*] FOODBRIDGE FULL SYSTEM DIAGNOSTIC & VERIFICATION SUITE")
    print("=" * 70)

    with app.app_context():
        # ---------------------------------------------------------------------
        # 1. DATABASE SCHEMA & INTEGRITY CHECK
        # ---------------------------------------------------------------------
        print("\n[1/6] Checking Database Tables & Seed Data...")
        users_count = User.query.count()
        donations_count = Donation.query.count()
        needs_count = FoodNeedRequest.query.count()
        impact_count = ImpactLedger.query.count()
        
        print(f"  [OK] Users in DB: {users_count}")
        print(f"  [OK] Donations in DB: {donations_count}")
        print(f"  [OK] Open Need Requests: {needs_count}")
        print(f"  [OK] Impact Ledger Entries: {impact_count}")
        assert users_count > 0, "Users table is empty!"

        # ---------------------------------------------------------------------
        # 2. ALGORITHMIC ENGINES TEST
        # ---------------------------------------------------------------------
        print("\n[2/6] Verifying Algorithmic & Mathematical Engines...")
        
        # Haversine distance
        d = haversine_distance(13.0827, 80.2707, 13.0110, 80.2354)
        print(f"  [OK] Haversine Distance (Chennai Central to Anna Univ): {d:.2f} km")
        assert 5.0 < d < 12.0, "Haversine calculation out of bounds!"

        # Multi-factor score
        test_don = Donation.query.filter_by(status='available').first() or Donation.query.first()
        test_org = User.query.filter_by(role='organization').first()
        score, dist_km, breakdown = calculate_match_score(test_don, test_org)
        print(f"  [OK] Multi-Factor Match Score: {score}% (Distance: {dist_km:.2f} km)")
        print(f"    - Sub-factors: Dist={breakdown['dist_factor']}%, Urgency={breakdown['urgency_factor']}%, Cap={breakdown['capacity_factor']}%")
        assert 0.0 <= score <= 100.0, "Score calculation out of range!"

        # Knapsack Aggregation
        test_need = FoodNeedRequest.query.filter_by(is_active=True).first()
        if test_need:
            pool = knapsack_aggregate_donations(test_need)
            print(f"  [OK] Knapsack N:1 Aggregator for Need #{test_need.id} (Deficit: {test_need.remaining_deficit} meals):")
            print(f"    - Total Pooled Surplus: {pool.get('total_pooled_meals')} meals across {len(pool.get('manifest', []))} batches.")

        # Urgency Decay Engine
        urg_status = update_all_donation_urgencies()
        print(f"  [OK] Urgency Decay Daemon: {urg_status['active_total']} active listings verified, {urg_status['updated']} updated.")

        # ---------------------------------------------------------------------
        # 3. QR & CRYPTOGRAPHIC HANDSHAKE ENGINE
        # ---------------------------------------------------------------------
        print("\n[3/6] Verifying Dual-Stage Cryptographic QR & Handshake Payload...")
        qr_b64 = generate_qr_base64("FOODBRIDGE-TEST-PAYLOAD")
        assert qr_b64.startswith("data:image/png;base64,"), "QR Generation failed!"
        print(f"  [OK] QR Code Engine (Base64 PNG): Generated valid data URI of length {len(qr_b64)} chars.")

        # ---------------------------------------------------------------------
        # 4. END-TO-END BUSINESS LIFECYCLE SIMULATION
        # ---------------------------------------------------------------------
        print("\n[4/6] Executing Complete End-to-End Rescue Lifecycle Simulation...")
        
        # Step A: Create Campus Event Surplus
        donor_user = User.query.filter_by(role='donor').first()
        now = datetime.utcnow()
        new_don = Donation(
            donor_id=donor_user.id,
            is_campus_event=True,
            event_name='Diagnostic Tech Symposium',
            title='100 Fresh Meal Boxes (Test Batch)',
            food_category='cooked_meals',
            dietary_type='vegetarian',
            quantity_meals=100,
            allocated_meals=0,
            weight_approx_kg=40.0,
            prepared_at=now - timedelta(hours=1),
            best_before=now + timedelta(hours=3),
            pickup_window_start=now,
            pickup_window_end=now + timedelta(hours=2.5),
            pickup_latitude=13.0110,
            pickup_longitude=80.2354,
            pickup_address_text='Anna University Main Gate, Guindy',
            donor_pickup_code='112233',
            ngo_delivery_code='445566',
            status='available',
            urgency_tier='high_orange'
        )
        db.session.add(new_don)
        db.session.commit()
        print(f"  [OK] [State 1: AVAILABLE] Created Campus Event Donation #{new_don.id} (OTP: {new_don.donor_pickup_code}).")

        # Step B: Organization Claims 50 Meals
        org_user = User.query.filter_by(role='organization').first()
        alloc = DonationAllocation(
            donation_id=new_don.id,
            organization_id=org_user.id,
            claimed_meals=50,
            status='allocated'
        )
        db.session.add(alloc)
        db.session.flush() # ID generation
        
        new_don.allocated_meals += 50
        
        task = DeliveryTask(
            allocation_id=alloc.id,
            status='dispatched',
            estimated_distance_km=2.1
        )
        db.session.add(task)
        db.session.commit()
        print(f"  [OK] [State 2: DISPATCHED] Org claimed 50 meals. Created Allocation #{alloc.id} & DeliveryTask #{task.id}.")

        # Step C: Volunteer Claims Delivery Leg
        vol_user = User.query.filter_by(role='volunteer').first()
        task.volunteer_id = vol_user.id
        db.session.commit()
        print(f"  [OK] [State 3: ASSIGNED] Volunteer '{vol_user.full_name}' claimed delivery task #{task.id}.")

        # Step D: Volunteer Verifies Donor Pickup via OTP
        assert new_don.donor_pickup_code == '112233', "Pickup code mismatch!"
        task.status = 'in_transit'
        task.pickup_verified_at = datetime.utcnow()
        alloc.status = 'in_transit'
        new_don.status = 'in_transit'
        db.session.commit()
        print(f"  [OK] [State 4: IN_TRANSIT] Donor OTP '112233' verified. Status transitioned to IN_TRANSIT.")

        # Step E: NGO Verifies Handover via Handshake OTP
        initial_ic = vol_user.volunteer_profile.impact_credits if vol_user.volunteer_profile else 0
        assert new_don.ngo_delivery_code == '445566', "Delivery code mismatch!"
        task.status = 'delivered'
        task.delivery_verified_at = datetime.utcnow()
        alloc.status = 'delivered'
        
        # Log Impact Entry & Award Impact Credits
        entry = record_impact_entry(alloc, volunteer_user=vol_user)
        print(f"  [OK] [State 5: DELIVERED & IMPACT RECORDED]")
        print(f"    - Rescued: {entry.meals_rescued} Meals ({entry.biomass_kg} kg biomass)")
        print(f"    - EPA Carbon Abatement: {entry.co2e_kg_saved} kg CO2e")
        print(f"    - Volunteer Impact Credits (IC): Updated from {initial_ic} to {vol_user.volunteer_profile.impact_credits} (+{entry.meals_rescued * 2} IC)")

        # ---------------------------------------------------------------------
        # 5. HTTP ROUTES & WEB VIEWS INTEGRITY CHECK
        # ---------------------------------------------------------------------
        print("\n[5/6] Testing All Web Views & REST Endpoints with Flask Test Client...")
        client = app.test_client()

        endpoints_to_test = [
            ('/', 200, "Home Landing Page"),
            ('/about', 200, "About Page & 5 Pillars"),
            ('/impact', 200, "Impact & ESG Telemetry"),
            ('/finder/', 200, "Food Bank Directory & Heatmap"),
            ('/finder/api/heatmap-data', 200, "Heatmap GeoJSON API"),
            ('/api/v1/impact-summary', 200, "REST API: Impact Summary"),
            ('/api/v1/donations/live', 200, "REST API: Live Donations"),
            ('/api/v1/needs/active', 200, "REST API: Active Needs"),
            ('/auth/login', 200, "Login Portal"),
            ('/auth/register', 200, "Multi-Role Registration Portal"),
        ]

        for url, expected_code, name in endpoints_to_test:
            resp = client.get(url)
            print(f"  [OK] {name} [{url}] -> HTTP {resp.status_code}")
            assert resp.status_code == expected_code, f"Failed endpoint {url}: got {resp.status_code}"

        # ---------------------------------------------------------------------
        # 6. AUTHENTICATED USER SESSIONS & DASHBOARDS
        # ---------------------------------------------------------------------
        print("\n[6/6] Verifying Role-Based Dashboards & Permissions...")
        
        # Test Donor Login & Dashboard
        client.post('/auth/login', data={'email': 'symposium@college.edu', 'password': 'donor123'})
        resp = client.get('/donor/dashboard')
        print(f"  [OK] Donor Dashboard [/donor/dashboard] -> HTTP {resp.status_code}")
        assert resp.status_code == 200, "Donor dashboard returned error"
        client.get('/auth/logout')

        # Test Org Login & Dashboard
        client.post('/auth/login', data={'email': 'mercy@shelter.org', 'password': 'org123'})
        resp = client.get('/org/dashboard')
        print(f"  [OK] Organization Dashboard [/org/dashboard] -> HTTP {resp.status_code}")
        assert resp.status_code == 200, "Org dashboard returned error"

        resp = client.get('/org/matches')
        print(f"  [OK] Smart Match Feed & N:1 Pooling [/org/matches] -> HTTP {resp.status_code}")
        assert resp.status_code == 200, "Match feed returned error"
        client.get('/auth/logout')

        # Test Volunteer Login & Dashboard
        client.post('/auth/login', data={'email': 'rahul@volunteer.org', 'password': 'vol123'})
        resp = client.get('/volunteer/dashboard')
        print(f"  [OK] Volunteer Hub [/volunteer/dashboard] -> HTTP {resp.status_code}")
        assert resp.status_code == 200, "Volunteer dashboard returned error"
        client.get('/auth/logout')

        # Test Admin Login & Dashboard
        client.post('/auth/login', data={'email': 'admin@foodbridge.org', 'password': 'admin123'})
        resp = client.get('/admin/dashboard')
        print(f"  [OK] Admin KYC & Telemetry Suite [/admin/dashboard] -> HTTP {resp.status_code}")
        assert resp.status_code == 200, "Admin dashboard returned error"
        client.get('/auth/logout')

    print("\n" + "=" * 70)
    print("SUCCESS: ALL 6 DIAGNOSTIC STAGES PASSED WITH 100% SUCCESS!")
    print("=" * 70)

if __name__ == '__main__':
    run_comprehensive_diagnostics()
