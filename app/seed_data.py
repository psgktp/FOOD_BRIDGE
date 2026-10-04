from datetime import datetime, timedelta
from app.extensions import db
from app.models.user import User, UserAddress, DonorProfile, OrgProfile, VolunteerProfile
from app.models.donation import Donation, FoodNeedRequest, DonationAllocation
from app.models.logistics import DeliveryTask
from app.models.impact import ImpactLedger

def seed_database():
    """Seeds the database with rich demo data if empty."""
    if User.query.first():
        print("Database already contains data. Skipping seed.")
        return

    print("Seeding FoodBridge with demo data...")
    
    # Coordinates centered around Chennai Metro / Campus area
    BASE_LAT = 13.0827
    BASE_LNG = 80.2707

    # =========================================================================
    # 1. ADMIN USER
    # =========================================================================
    admin = User(
        email='admin@foodbridge.org',
        full_name='FoodBridge System Admin',
        phone='+91 98765 00001',
        role='admin'
    )
    admin.set_password('admin123')
    db.session.add(admin)

    # =========================================================================
    # 2. FOOD DONORS
    # =========================================================================
    # Donor 1: Campus Symposium Coordinator (Event Fast-Track)
    donor1 = User(
        email='symposium@college.edu',
        full_name='Prof. Ramesh (Symposium Chair)',
        phone='+91 98765 11001',
        role='donor'
    )
    donor1.set_password('donor123')
    db.session.add(donor1)
    db.session.flush()

    addr1 = UserAddress(
        user_id=donor1.id,
        label='University Auditorium',
        street_address='College Campus, Main Tech Block, Sardar Patel Road',
        city='Chennai',
        latitude=BASE_LAT + 0.005,
        longitude=BASE_LNG - 0.004
    )
    prof1 = DonorProfile(
        user_id=donor1.id,
        donor_type='event_organizer',
        institution_name='Anna University Tech Fest',
        fssai_license='FSSAI-UNIV-2026-09',
        total_meals_donated=480,
        total_donations_count=4
    )
    db.session.add_all([addr1, prof1])

    # Donor 2: Campus Hostel Mess
    donor2 = User(
        email='mess@campus.edu',
        full_name='Campus North Mess Incharge',
        phone='+91 98765 11002',
        role='donor'
    )
    donor2.set_password('donor123')
    db.session.add(donor2)
    db.session.flush()

    addr2 = UserAddress(
        user_id=donor2.id,
        label='North Hostel Dining Hall',
        street_address='Block 4 Hostel Campus Dining Facility',
        city='Chennai',
        latitude=BASE_LAT - 0.008,
        longitude=BASE_LNG + 0.006
    )
    prof2 = DonorProfile(
        user_id=donor2.id,
        donor_type='college_canteen',
        institution_name='Campus Hostel Central Kitchen',
        fssai_license='FSSAI-MESS-2026-44',
        total_meals_donated=320,
        total_donations_count=3
    )
    db.session.add_all([addr2, prof2])

    # Donor 3: Grand Palace Banquets
    donor3 = User(
        email='manager@grandpalace.com',
        full_name='Grand Palace Banquets',
        phone='+91 98765 11003',
        role='donor'
    )
    donor3.set_password('donor123')
    db.session.add(donor3)
    db.session.flush()

    addr3 = UserAddress(
        user_id=donor3.id,
        label='Main Banquet Kitchen',
        street_address='45 Mount Road, Guindy',
        city='Chennai',
        latitude=BASE_LAT + 0.015,
        longitude=BASE_LNG + 0.012
    )
    prof3 = DonorProfile(
        user_id=donor3.id,
        donor_type='hotel',
        institution_name='Grand Palace Luxury Hotel',
        fssai_license='FSSAI-HOTEL-2025-88',
        total_meals_donated=1200,
        total_donations_count=8
    )
    db.session.add_all([addr3, prof3])

    # =========================================================================
    # 3. ORGANIZATIONS / FOOD BANKS
    # =========================================================================
    # Org 1: Mercy Shelter Home
    org1 = User(
        email='mercy@shelter.org',
        full_name='Sister Theresa (Director)',
        phone='+91 98765 22001',
        role='organization'
    )
    org1.set_password('org123')
    db.session.add(org1)
    db.session.flush()

    org_addr1 = UserAddress(
        user_id=org1.id,
        label='Shelter Distribution Wing',
        street_address='12 St. Thomas Road, Saidapet',
        city='Chennai',
        latitude=BASE_LAT + 0.009,
        longitude=BASE_LNG + 0.003
    )
    org_prof1 = OrgProfile(
        user_id=org1.id,
        org_name='Mercy Shelter Home & Community Kitchen',
        org_type='shelter',
        govt_reg_number='TN-NGO-2018-9921',
        max_daily_capacity=300,
        current_occupancy=90,
        is_accepting_donations=True,
        verification_status='verified',
        description='Provides warm evening meals and shelter to homeless seniors and migrant workers.'
    )
    db.session.add_all([org_addr1, org_prof1])

    # Org 2: Hope City Food Bank
    org2 = User(
        email='hope@foodbank.org',
        full_name='David Raj (Coordinator)',
        phone='+91 98765 22002',
        role='organization'
    )
    org2.set_password('org123')
    db.session.add(org2)
    db.session.flush()

    org_addr2 = UserAddress(
        user_id=org2.id,
        label='Central Pantry Depot',
        street_address='88 Poonamallee High Road',
        city='Chennai',
        latitude=BASE_LAT - 0.012,
        longitude=BASE_LNG - 0.010
    )
    org_prof2 = OrgProfile(
        user_id=org2.id,
        org_name='Hope City Food Bank',
        org_type='food_bank',
        govt_reg_number='TN-FB-2020-4412',
        max_daily_capacity=500,
        current_occupancy=180,
        is_accepting_donations=True,
        verification_status='verified',
        description='Distributes packaged rations and recovered cooked meals to local slums.'
    )
    db.session.add_all([org_addr2, org_prof2])

    # =========================================================================
    # 4. VOLUNTEERS
    # =========================================================================
    vol1 = User(
        email='rahul@volunteer.org',
        full_name='Rahul Sharma (Student Volunteer)',
        phone='+91 98765 33001',
        role='volunteer'
    )
    vol1.set_password('vol123')
    db.session.add(vol1)
    db.session.flush()

    v_prof1 = VolunteerProfile(
        user_id=vol1.id,
        transport_mode='two_wheeler',
        max_carrying_meals=40,
        current_lat=BASE_LAT + 0.002,
        current_lng=BASE_LNG - 0.001,
        total_rescues_completed=14,
        impact_credits=380
    )
    db.session.add(v_prof1)

    vol2 = User(
        email='priya@volunteer.org',
        full_name='Priya V (Community Hero)',
        phone='+91 98765 33002',
        role='volunteer'
    )
    vol2.set_password('vol123')
    db.session.add(vol2)
    db.session.flush()

    v_prof2 = VolunteerProfile(
        user_id=vol2.id,
        transport_mode='car',
        max_carrying_meals=120,
        current_lat=BASE_LAT + 0.010,
        current_lng=BASE_LNG + 0.005,
        total_rescues_completed=22,
        impact_credits=640
    )
    db.session.add(v_prof2)

    db.session.commit()

    # =========================================================================
    # 5. DEMAND SIDE (ORGANIZATION LIVE FOOD DEFICITS)
    # =========================================================================
    now = datetime.utcnow()

    need1 = FoodNeedRequest(
        organization_id=org1.id,
        title='Evening Community Dinner Drive (200 Meals Required)',
        target_meals_required=200,
        meals_fulfilled=0,
        food_category='cooked_meals',
        dietary_preference='vegetarian',
        needed_by=now + timedelta(hours=3.5),
        latitude=BASE_LAT + 0.009,
        longitude=BASE_LNG + 0.003,
        location_name='Mercy Shelter Saidapet Center',
        urgency_level='high_orange'
    )

    need2 = FoodNeedRequest(
        organization_id=org2.id,
        title='Night Ration Distribution for Daily Wage Workers',
        target_meals_required=120,
        meals_fulfilled=0,
        food_category='cooked_meals',
        dietary_preference='any',
        needed_by=now + timedelta(hours=5.0),
        latitude=BASE_LAT - 0.012,
        longitude=BASE_LNG - 0.010,
        location_name='Hope City Central Pantry',
        urgency_level='moderate_yellow'
    )
    db.session.add_all([need1, need2])

    # =========================================================================
    # 6. SURPLUS DONATIONS (Active for Demo & N:1 Pooling)
    # =========================================================================
    # Donation A: Campus Tech Fest (120 meals - Yellow/Orange Urgency)
    don1 = Donation(
        donor_id=donor1.id,
        is_campus_event=True,
        event_name='National AI & Web Symposium 2026',
        title='Fresh Veg Biryani & Paneer Gravy Meal Boxes',
        food_category='cooked_meals',
        dietary_type='vegetarian',
        quantity_meals=120,
        allocated_meals=0,
        weight_approx_kg=48.0,
        prepared_at=now - timedelta(hours=1.5),
        best_before=now + timedelta(hours=2.5),
        pickup_window_start=now,
        pickup_window_end=now + timedelta(hours=2.0),
        pickup_latitude=BASE_LAT + 0.005,
        pickup_longitude=BASE_LNG - 0.004,
        pickup_address_text='Main Auditorium Dining Lawn, College Campus',
        pickup_instructions='Collect from catering coordinator near Gate 2',
        donor_pickup_code='482910',
        ngo_delivery_code='719342',
        status='available',
        urgency_tier='high_orange'
    )

    # Donation B: Campus North Mess (70 meals)
    don2 = Donation(
        donor_id=donor2.id,
        is_campus_event=False,
        event_name=None,
        title='Steamed Rice, Dal, Poriyal & Chapati Packets',
        food_category='cooked_meals',
        dietary_type='vegetarian',
        quantity_meals=70,
        allocated_meals=0,
        weight_approx_kg=28.0,
        prepared_at=now - timedelta(hours=1.0),
        best_before=now + timedelta(hours=3.5),
        pickup_window_start=now,
        pickup_window_end=now + timedelta(hours=3.0),
        pickup_latitude=BASE_LAT - 0.008,
        pickup_longitude=BASE_LNG + 0.006,
        pickup_address_text='North Mess Dispatch Counter, Hostel Area',
        pickup_instructions='Call mess supervisor on arrival',
        donor_pickup_code='391024',
        ngo_delivery_code='820491',
        status='available',
        urgency_tier='moderate_yellow'
    )

    # Donation C: Grand Palace Banquets (50 meals)
    don3 = Donation(
        donor_id=donor3.id,
        is_campus_event=False,
        event_name='Corporate Gala Dinner',
        title='Buffet Surplus Meals (Rotis, Pulao & Mix Veg)',
        food_category='cooked_meals',
        dietary_type='vegetarian',
        quantity_meals=50,
        allocated_meals=0,
        weight_approx_kg=20.0,
        prepared_at=now - timedelta(hours=2.0),
        best_before=now + timedelta(hours=2.0),
        pickup_window_start=now,
        pickup_window_end=now + timedelta(hours=1.5),
        pickup_latitude=BASE_LAT + 0.015,
        pickup_longitude=BASE_LNG + 0.012,
        pickup_address_text='Grand Palace Banquet Loading Bay 3',
        pickup_instructions='Ask for Banquet Manager Mr. Rajesh',
        donor_pickup_code='904812',
        ngo_delivery_code='651038',
        status='available',
        urgency_tier='high_orange'
    )

    db.session.add_all([don1, don2, don3])
    db.session.commit()

    # =========================================================================
    # 7. HISTORICAL IMPACT DATA (For Impact Dashboard and Leaderboards)
    # =========================================================================
    hist_entries = [
        ImpactLedger(
            donor_id=donor1.id,
            organization_id=org1.id,
            volunteer_id=vol1.id,
            meals_rescued=240,
            biomass_kg=96.0,
            co2e_kg_saved=240.0,
            economic_value_inr=12000.0,
            institution_credited='Anna University Tech Fest',
            created_at=now - timedelta(days=3)
        ),
        ImpactLedger(
            donor_id=donor2.id,
            organization_id=org2.id,
            volunteer_id=vol2.id,
            meals_rescued=180,
            biomass_kg=72.0,
            co2e_kg_saved=180.0,
            economic_value_inr=9000.0,
            institution_credited='Campus Hostel Central Kitchen',
            created_at=now - timedelta(days=2)
        ),
        ImpactLedger(
            donor_id=donor3.id,
            organization_id=org1.id,
            volunteer_id=vol1.id,
            meals_rescued=350,
            biomass_kg=140.0,
            co2e_kg_saved=350.0,
            economic_value_inr=17500.0,
            institution_credited='Grand Palace Luxury Hotel',
            created_at=now - timedelta(days=1)
        )
    ]
    db.session.add_all(hist_entries)
    db.session.commit()

    print("FoodBridge database seeded successfully with realistic campus, donor, NGO, and volunteer profiles!")
