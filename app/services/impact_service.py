from sqlalchemy import func
from app.extensions import db
from app.models.impact import ImpactLedger
from app.models.donation import Donation
from app.models.user import User, DonorProfile, OrgProfile, VolunteerProfile
from app.config import Config

def record_impact_entry(allocation, volunteer_user=None):
    """
    Called upon successful delivery verification.
    Calculates biomass, CO2e abatement, and economic value.
    """
    donation = allocation.donation
    meals = allocation.claimed_meals
    biomass_kg = round(meals * Config.AVG_MEAL_WEIGHT_KG, 2)
    co2e_kg = round(biomass_kg * Config.CO2E_FACTOR_PER_KG, 2)
    econ_value = round(meals * 50.0, 2) # Est. 50 INR per meal
    
    inst_name = None
    if donation.donor and donation.donor.donor_profile:
        inst_name = donation.donor.donor_profile.institution_name
        donation.donor.donor_profile.total_meals_donated += meals
        donation.donor.donor_profile.total_donations_count += 1
        
    if volunteer_user and volunteer_user.volunteer_profile:
        volunteer_user.volunteer_profile.total_rescues_completed += 1
        volunteer_user.volunteer_profile.impact_credits += (meals * 2)
        
    entry = ImpactLedger(
        allocation_id=allocation.id,
        donor_id=donation.donor_id,
        organization_id=allocation.organization_id,
        volunteer_id=volunteer_user.id if volunteer_user else None,
        meals_rescued=meals,
        biomass_kg=biomass_kg,
        co2e_kg_saved=co2e_kg,
        economic_value_inr=econ_value,
        institution_credited=inst_name or "Individual Community Partner"
    )
    
    db.session.add(entry)
    db.session.commit()
    return entry


def get_global_impact_summary():
    """
    Aggregates platform-wide impact telemetry for live landing page and admin dashboards.
    """
    total_meals = db.session.query(func.sum(ImpactLedger.meals_rescued)).scalar() or 0
    total_biomass = db.session.query(func.sum(ImpactLedger.biomass_kg)).scalar() or 0.0
    total_co2e = db.session.query(func.sum(ImpactLedger.co2e_kg_saved)).scalar() or 0.0
    total_value = db.session.query(func.sum(ImpactLedger.economic_value_inr)).scalar() or 0.0
    
    total_donors = User.query.filter_by(role='donor').count()
    total_orgs = User.query.filter_by(role='organization').count()
    total_volunteers = User.query.filter_by(role='volunteer').count()
    total_rescues = ImpactLedger.query.count()
    
    # Campus Leaderboard
    campus_stats = db.session.query(
        ImpactLedger.institution_credited,
        func.sum(ImpactLedger.meals_rescued).label('meals'),
        func.sum(ImpactLedger.co2e_kg_saved).label('co2e')
    ).group_by(ImpactLedger.institution_credited).order_by(func.sum(ImpactLedger.meals_rescued).desc()).limit(5).all()
    
    leaderboard = [
        {
            'institution': item[0] or 'Community Partner',
            'meals': item[1] or 0,
            'co2e': round(item[2] or 0.0, 1)
        } for item in campus_stats
    ]
    
    return {
        'total_meals_rescued': int(total_meals),
        'total_biomass_kg': round(total_biomass, 1),
        'total_co2e_kg_saved': round(total_co2e, 1),
        'total_economic_value_inr': round(total_value, 2),
        'total_donors': total_donors,
        'total_orgs': total_orgs,
        'total_volunteers': total_volunteers,
        'total_completed_rescues': total_rescues,
        'campus_leaderboard': leaderboard
    }
