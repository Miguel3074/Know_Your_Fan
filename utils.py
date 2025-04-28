import base64
import os
import re
import uuid
from functools import wraps
from flask import request, redirect, url_for, flash, current_app
from flask_login import current_user

def is_valid_cpf(cpf):
    """Validate Brazilian CPF number."""
    # Remove special characters
    cpf = ''.join(re.findall('\d', str(cpf)))
    
    # Check if has 11 digits
    if len(cpf) != 11:
        return False
    
    # Check if all digits are the same
    if cpf == cpf[0] * 11:
        return False
    
    # Calculate first verification digit
    sum_of_products = 0
    for i in range(9):
        sum_of_products += int(cpf[i]) * (10 - i)
    
    expected_digit = (sum_of_products * 10) % 11
    if expected_digit == 10:
        expected_digit = 0
    
    # Check first verification digit
    if expected_digit != int(cpf[9]):
        return False
    
    # Calculate second verification digit
    sum_of_products = 0
    for i in range(10):
        sum_of_products += int(cpf[i]) * (11 - i)
    
    expected_digit = (sum_of_products * 10) % 11
    if expected_digit == 10:
        expected_digit = 0
    
    # Check second verification digit
    if expected_digit != int(cpf[10]):
        return False
    
    return True

def generate_unique_filename(filename):
    """Generate a unique filename for uploaded files."""
    file_extension = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
    unique_filename = f"{uuid.uuid4()}.{file_extension}"
    return unique_filename

def allowed_file(filename, allowed_extensions=None):
    """Check if the file extension is allowed."""
    if allowed_extensions is None:
        allowed_extensions = current_app.config.get('ALLOWED_EXTENSIONS', {'png', 'jpg', 'jpeg', 'gif', 'pdf'})
    
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

def encode_image_to_base64(file_path):
    """Convert an image file to base64 string."""
    with open(file_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def profile_required(view_func):
    """Decorator to ensure user has completed their basic profile."""
    @wraps(view_func)
    def wrapped_view(*args, **kwargs):
        if current_user.is_authenticated and current_user.profile and current_user.profile.completed:
            return view_func(*args, **kwargs)
        else:
            flash('Please complete your basic profile information first.', 'warning')
            return redirect(url_for('profile.basic_info'))
    return wrapped_view

def format_social_data(platform, data):
    """Format social media data for display."""
    formatted_data = {
        'profile_url': '',
        'followers': 0,
        'following': 0,
        'posts': 0,
        'verified': False,
        'interests': []
    }
    
    if platform == 'twitter':
        formatted_data['profile_url'] = data.get('profile_url', '')
        formatted_data['followers'] = data.get('followers_count', 0)
        formatted_data['following'] = data.get('friends_count', 0)
        formatted_data['posts'] = data.get('statuses_count', 0)
        formatted_data['verified'] = data.get('verified', False)
    
    elif platform == 'instagram':
        formatted_data['profile_url'] = data.get('profile_url', '')
        formatted_data['followers'] = data.get('followers_count', 0)
        formatted_data['following'] = data.get('following_count', 0)
        formatted_data['posts'] = data.get('media_count', 0)
        formatted_data['verified'] = data.get('is_verified', False)
    
    elif platform == 'facebook':
        formatted_data['profile_url'] = data.get('link', '')
        formatted_data['followers'] = data.get('fan_count', 0)
        formatted_data['verified'] = data.get('verification_status', '') != ''
    
    return formatted_data
