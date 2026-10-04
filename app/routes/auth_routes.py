from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app.extensions import db
from app.models.user import User, DonorProfile, OrgProfile, VolunteerProfile, UserAddress

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect_user_dashboard(current_user)
        
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        remember = bool(request.form.get('remember'))
        
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            if not user.is_active:
                flash('Your account has been deactivated. Please contact support.', 'danger')
                return render_template('auth/login.html')
                
            login_user(user, remember=remember)
            flash(f'Welcome back, {user.full_name}!', 'success')
            next_page = request.args.get('next')
            if next_page and next_page.startswith('/'):
                return redirect(next_page)
            return redirect_user_dashboard(user)
        else:
            flash('Invalid email or password. Please try again.', 'danger')
            
    return render_template('auth/login.html')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect_user_dashboard(current_user)
        
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        full_name = request.form.get('full_name', '').strip()
        phone = request.form.get('phone', '').strip()
        password = request.form.get('password', '')
        role = request.form.get('role', 'donor')
        
        # Address
        address_text = request.form.get('address_text', '').strip()
        city = request.form.get('city', 'Chennai').strip()
        lat = float(request.form.get('latitude') or 13.0827)
        lng = float(request.form.get('longitude') or 80.2707)
        
        # Validation
        if User.query.filter_by(email=email).first():
            flash('Email is already registered. Please log in.', 'warning')
            return render_template('auth/register.html')
            
        if User.query.filter_by(phone=phone).first():
            flash('Phone number is already registered.', 'warning')
            return render_template('auth/register.html')
            
        user = User(
            email=email,
            full_name=full_name,
            phone=phone,
            role=role
        )
        user.set_password(password)
        db.session.add(user)
        db.session.flush() # get user.id
        
        # Add primary address
        address = UserAddress(
            user_id=user.id,
            label='Primary Location',
            street_address=address_text or 'Campus / Headquarters',
            city=city,
            latitude=lat,
            longitude=lng,
            is_default=True
        )
        db.session.add(address)
        
        # Role-Specific Profiles
        if role == 'donor':
            donor_type = request.form.get('donor_type', 'college_canteen')
            inst_name = request.form.get('institution_name', full_name)
            fssai = request.form.get('fssai_license', '')
            donor_prof = DonorProfile(
                user_id=user.id,
                donor_type=donor_type,
                institution_name=inst_name,
                fssai_license=fssai
            )
            db.session.add(donor_prof)
            
        elif role == 'organization':
            org_name = request.form.get('org_name', full_name)
            org_type = request.form.get('org_type', 'food_bank')
            govt_reg = request.form.get('govt_reg_number', '')
            capacity = int(request.form.get('max_daily_capacity') or 250)
            desc = request.form.get('description', '')
            
            org_prof = OrgProfile(
                user_id=user.id,
                org_name=org_name,
                org_type=org_type,
                govt_reg_number=govt_reg,
                max_daily_capacity=capacity,
                description=desc,
                verification_status='verified' # Auto-verified for local dev
            )
            db.session.add(org_prof)
            
        elif role == 'volunteer':
            transport = request.form.get('transport_mode', 'two_wheeler')
            vol_prof = VolunteerProfile(
                user_id=user.id,
                transport_mode=transport,
                current_lat=lat,
                current_lng=lng
            )
            db.session.add(vol_prof)
            
        db.session.commit()
        login_user(user)
        flash(f'Account created successfully! Welcome to FoodBridge, {user.full_name}.', 'success')
        return redirect_user_dashboard(user)
        
    return render_template('auth/register.html')


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out safely.', 'info')
    return redirect(url_for('main.index'))


def redirect_user_dashboard(user):
    if user.is_donor:
        return redirect(url_for('donor.dashboard'))
    elif user.is_org:
        return redirect(url_for('org.dashboard'))
    elif user.is_volunteer:
        return redirect(url_for('volunteer.dashboard'))
    elif user.is_admin:
        return redirect(url_for('admin.dashboard'))
    return redirect(url_for('main.index'))
