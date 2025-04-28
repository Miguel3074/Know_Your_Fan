from flask import Blueprint, render_template, jsonify
from flask_login import login_required, current_user
from utils import profile_required
from models import Document, SocialMedia, EsportsProfile

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')

@dashboard_bp.route('/')
@login_required
@profile_required
def overview():
    """Main dashboard overview showing all collected fan information."""
    # Get user profile
    profile = current_user.profile
    
    # Get document verification status
    documents = Document.query.filter_by(user_id=current_user.id).all()
    verified_documents = sum(1 for doc in documents if doc.validated)
    
    # Get social media accounts
    social_accounts = SocialMedia.query.filter_by(user_id=current_user.id).all()
    
    # Get esports profiles
    esports_profiles = EsportsProfile.query.filter_by(user_id=current_user.id).all()
    
    # Calculate completion percentage
    total_sections = 4  # Basic info, interests, documents, social/esports
    completed_sections = 0
    
    if profile and profile.completed:
        completed_sections += 2  # Basic info and interests
    
    if verified_documents > 0:
        completed_sections += 1  # Document verification
    
    if len(social_accounts) > 0 or len(esports_profiles) > 0:
        completed_sections += 1  # Social/esports profiles
    
    completion_percentage = int((completed_sections / total_sections) * 100)
    
    # Calculate fan score based on profile completeness and engagement
    base_score = 50  # Starting score
    
    # Add points for verified documents
    document_score = min(20, verified_documents * 10)
    
    # Add points for social accounts
    social_score = min(15, len(social_accounts) * 5)
    
    # Add points for esports profiles with relevance
    esports_score = 0
    for profile in esports_profiles:
        relevance = getattr(profile, 'relevance_score', 0) or 0
        esports_score += int(relevance * 10)
    esports_score = min(15, esports_score)
    
    fan_score = base_score + document_score + social_score + esports_score
    fan_score = min(100, fan_score)  # Cap at 100
    
    return render_template(
        'dashboard/overview.html',
        profile=profile,
        documents=documents,
        verified_documents=verified_documents,
        social_accounts=social_accounts,
        esports_profiles=esports_profiles,
        completion_percentage=completion_percentage,
        fan_score=fan_score
    )

@dashboard_bp.route('/data')
@login_required
@profile_required
def profile_data():
    """API endpoint to get profile data for charts and visualizations."""
    # Simple data for demo charts
    interests = current_user.profile.interests.split(',') if current_user.profile.interests else []
    favorite_games = current_user.profile.favorite_games.split(',') if current_user.profile.favorite_games else []
    favorite_teams = current_user.profile.favorite_teams.split(',') if current_user.profile.favorite_teams else []
    
    # Count documents by type
    documents = Document.query.filter_by(user_id=current_user.id).all()
    doc_types = {}
    for doc in documents:
        doc_types[doc.doc_type] = doc_types.get(doc.doc_type, 0) + 1
    
    # Count social media by platform
    social_accounts = SocialMedia.query.filter_by(user_id=current_user.id).all()
    social_platforms = {}
    for account in social_accounts:
        social_platforms[account.platform] = social_platforms.get(account.platform, 0) + 1
    
    # Count esports profiles by platform
    esports_profiles = EsportsProfile.query.filter_by(user_id=current_user.id).all()
    esports_platforms = {}
    for profile in esports_profiles:
        esports_platforms[profile.platform] = esports_platforms.get(profile.platform, 0) + 1
    
    # Get average relevance score
    relevance_scores = [getattr(profile, 'relevance_score', 0) or 0 for profile in esports_profiles]
    avg_relevance = sum(relevance_scores) / len(relevance_scores) if relevance_scores else 0
    
    return jsonify({
        'interests': interests,
        'favorite_games': favorite_games,
        'favorite_teams': favorite_teams,
        'document_types': doc_types,
        'social_platforms': social_platforms,
        'esports_platforms': esports_platforms,
        'average_relevance': avg_relevance
    })
