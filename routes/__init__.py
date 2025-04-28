from flask import render_template, redirect, url_for
from app import app

# Main routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('index.html', section='about')

@app.route('/privacy')
def privacy():
    return render_template('index.html', section='privacy')

@app.route('/terms')
def terms():
    return render_template('index.html', section='terms')

# For easier imports
from routes.auth import auth_bp
from routes.profile import profile_bp
from routes.social import social_bp
from routes.dashboard import dashboard_bp

# Initialize main routes through app context
main_routes = "initialized"
