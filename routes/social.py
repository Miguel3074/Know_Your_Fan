from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app import db
from models import SocialMedia, EsportsProfile
from forms import SocialMediaForm, EsportsProfileForm
from utils import profile_required
from ai_validation import validate_esports_profile, analyze_social_media
import random

social_bp = Blueprint('social', __name__, url_prefix='/social')


twitter_follows = ['FURIA', 'Cloud9', 'FaZeClan', 'TeamLiquid', 'NAVI', 'G2 Esports']
twitter_interests = ['CSGO', 'Valorant', 'LeagueOfLegends', 'Overwatch', 'Apex Legends']

instagram_follows = ['furiagg', 'navi_gaming', 'teamliquid', 'g2esports', 'cloud9gg']
instagram_interests = ['CSGO', 'Dota2', 'Valorant', 'PUBG', 'Rainbow6']

facebook_likes = ['FURIA Esports', 'ESL Gaming', 'DreamHack', 'Red Bull Gaming', 'EVO Championship']
facebook_interests = ['gaming', 'esports', 'streaming', 'competitive gaming', 'pro players']


def random_subset(lst):
    chance = random.random()
    if chance < 0.2:
        k = 0
    elif chance < 0.5:
        k = 1
    elif chance < 0.8:
        k = random.randint(2, min(3, len(lst)))
    else:
        k = len(lst)
    return random.sample(lst, k) if k > 0 else []

def compute_engagement(follows, interests, max_items):
    """Calcula engajamento com base no percentual de itens usados."""
    max_total = max_items * 2  # total possível (follows + interests)
    actual_total = len(follows) + len(interests)
    base_score = actual_total / max_total if max_total > 0 else 0
    noise = random.uniform(-0.05, 0.05)  # variação para parecer natural
    return round(min(1.0, max(0.0, base_score + noise)), 2)

def generate_mock_data():
    twitter_f = random_subset(twitter_follows)
    twitter_i = random_subset(twitter_interests)

    insta_f = random_subset(instagram_follows)
    insta_i = random_subset(instagram_interests)

    fb_likes = random_subset(facebook_likes)
    fb_i = random_subset(facebook_interests)

    return {
        'twitter': {
            'follows': twitter_f,
            'interests': twitter_i,
            'engagement': compute_engagement(twitter_f, twitter_i, 5)
        },
        'instagram': {
            'follows': insta_f,
            'interests': insta_i,
            'engagement': compute_engagement(insta_f, insta_i, 5)
        },
        'facebook': {
            'likes': fb_likes,
            'interests': fb_i,
            'engagement': compute_engagement(fb_likes, fb_i, 5)
        }
    }


@social_bp.route('/media', methods=['GET', 'POST'])
@login_required
@profile_required
def social_media():
    form = SocialMediaForm()
    
    if form.validate_on_submit():
        # Check if this platform is already linked
        existing = SocialMedia.query.filter_by(
            user_id=current_user.id, 
            platform=form.platform.data
        ).first()
        
        if existing:
            flash(f'You already have a {form.platform.data} account linked.', 'warning')
            return redirect(url_for('social.social_media'))
        
        # In a real app, this would initiate OAuth flow
        # For demo purposes, we'll just save the profile info
        social_media = SocialMedia(
            user_id=current_user.id,
            platform=form.platform.data,
            username=form.username.data,
            profile_url=form.profile_url.data,
            verified=False  # Would be verified through OAuth
        )
        
        db.session.add(social_media)
        db.session.commit()
        
        flash(f'Your {form.platform.data} profile has been linked!', 'success')
        return redirect(url_for('social.social_media'))
    
    # Get user's linked social media
    social_media_accounts = SocialMedia.query.filter_by(user_id=current_user.id).all()
    
    return render_template(
        'profile/social_media.html', 
        form=form, 
        social_accounts=social_media_accounts
    )

@social_bp.route('/media/<int:id>/remove', methods=['POST'])
@login_required
def remove_social_media(id):
    social_media = SocialMedia.query.get_or_404(id)
    
    # Ensure the social media belongs to the current user
    if social_media.user_id != current_user.id:
        flash('You do not have permission to remove this social media account.', 'danger')
        return redirect(url_for('social.social_media'))
    
    platform = social_media.platform
    db.session.delete(social_media)
    db.session.commit()
    
    flash(f'Your {platform} account has been unlinked.', 'success')
    return redirect(url_for('social.social_media'))

@social_bp.route('/esports', methods=['GET', 'POST'])
@login_required
@profile_required
def esports_profiles():
    form = EsportsProfileForm()
    
    if form.validate_on_submit():
        # Check if this platform/username combo is already linked
        existing = EsportsProfile.query.filter_by(
            user_id=current_user.id,
            platform=form.platform.data,
            username=form.username.data
        ).first()
        
        if existing:
            flash(f'You already have this {form.platform.data} profile linked.', 'warning')
            return redirect(url_for('social.esports_profiles'))
        
        # Validate profile with AI
        validation_result = validate_esports_profile(
            form.profile_url.data,
            form.platform.data,
            form.username.data
        )
        
        # Create new esports profile
        esports_profile = EsportsProfile(
            user_id=current_user.id,
            platform=form.platform.data,
            username=form.username.data,
            profile_url=form.profile_url.data,
            verified=validation_result.get('is_valid_url', False),
            relevance_score=validation_result.get('relevance_score', 0.0),
            validation_result=str(validation_result)
        )
        
        db.session.add(esports_profile)
        db.session.commit()
        
        # Show appropriate message based on validation
        if esports_profile.relevance_score > 0.7:
            flash(f'Your {form.platform.data} profile has been verified and shows strong esports relevance!', 'success')
        elif esports_profile.relevance_score > 0.4:
            flash(f'Your {form.platform.data} profile has been added with moderate esports relevance.', 'info')
        else:
            flash(f'Your {form.platform.data} profile has been added, but shows limited esports relevance.', 'warning')
        
        return redirect(url_for('social.esports_profiles'))
    
    # Get user's linked esports profiles
    esports_profiles = EsportsProfile.query.filter_by(user_id=current_user.id).all()
    
    return render_template(
        'profile/esports_profiles.html',
        form=form,
        esports_profiles=esports_profiles
    )

@social_bp.route('/esports/<int:id>/remove', methods=['POST'])
@login_required
def remove_esports_profile(id):
    profile = EsportsProfile.query.get_or_404(id)
    
    # Ensure the profile belongs to the current user
    if profile.user_id != current_user.id:
        flash('You do not have permission to remove this profile.', 'danger')
        return redirect(url_for('social.esports_profiles'))
    
    platform = profile.platform
    db.session.delete(profile)
    db.session.commit()
    
    flash(f'Your {platform} profile has been removed.', 'success')
    return redirect(url_for('social.esports_profiles'))

@social_bp.route('/analyze/<platform>/<int:id>', methods=['POST'])
@login_required
def analyze_social_platform(platform, id):
    """Analyze a linked social media account with AI to identify esports interests."""
    social = SocialMedia.query.get_or_404(id)
    
    # Ensure the social media belongs to the current user
    if social.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized access'}), 403
    
    # In a real app, we would fetch actual data from the platform's API
    # For demo purposes, we'll simulate some data
    mock_data = generate_mock_data()
    
    # Get mock data for the platform or default to empty
    platform_data = mock_data.get(social.platform, {})
    
    # In a real app, we would analyze actual data with AI
    analysis_result = analyze_social_media(platform_data, social.platform)
    
    print(analysis_result)

    return jsonify(analysis_result)
