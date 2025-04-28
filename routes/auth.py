from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.security import check_password_hash
from app import db
from models import User, UserProfile
from forms import RegistrationForm, LoginForm

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.overview'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        # Create new user
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        
        # Add user to database
        db.session.add(user)
        
        # Create empty profile
        profile = UserProfile(user=user)
        db.session.add(profile)
        
        # Commit changes
        db.session.commit()
        
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html', form=form)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.overview'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        
        if user and user.check_password(form.password.data):
            # Login successful
            login_user(user, remember=form.remember_me.data)
            
            # Redirect to requested page or dashboard
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            
            # Check if profile is complete
            if user.profile and user.profile.completed:
                return redirect(url_for('dashboard.overview'))
            else:
                return redirect(url_for('profile.basic_info'))
        else:
            flash('Login failed. Please check your email and password.', 'danger')
    
    return render_template('auth/login.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@auth_bp.route('/reset_password', methods=['GET', 'POST'])
def reset_password_request():
    # This would normally implement a password reset flow
    # For this demo, we'll just show a message
    flash('Password reset functionality would be implemented here.', 'info')
    return redirect(url_for('auth.login'))
