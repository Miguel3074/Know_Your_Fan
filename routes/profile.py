import os
import base64
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from app import db
from models import UserProfile, Document
from forms import BasicInfoForm, InterestsForm, DocumentUploadForm
from utils import allowed_file, generate_unique_filename, profile_required
from ai_validation import validate_document
from werkzeug.utils import secure_filename

profile_bp = Blueprint('profile', __name__, url_prefix='/profile')

@profile_bp.route('/basic-info', methods=['GET', 'POST'])
@login_required
def basic_info():
    # Create or get user profile
    profile = current_user.profile or UserProfile(user=current_user)
    
    form = BasicInfoForm(obj=profile)
    
    if form.validate_on_submit():
        form.populate_obj(profile)
        
        # Save to database
        if not profile.id:
            db.session.add(profile)
        
        db.session.commit()
        
        flash('Basic information saved successfully!', 'success')
        return redirect(url_for('profile.interests'))
    
    return render_template('profile/basic_info.html', form=form)

@profile_bp.route('/interests', methods=['GET', 'POST'])
@login_required
def interests():
    # Ensure profile exists
    if not current_user.profile:
        flash('Please complete your basic information first.', 'warning')
        return redirect(url_for('profile.basic_info'))
    
    profile = current_user.profile
    form = InterestsForm(obj=profile)
    
    if form.validate_on_submit():
        form.populate_obj(profile)
        
        # Mark profile as completed
        profile.completed = True
        db.session.commit()
        
        flash('Interest information saved successfully!', 'success')
        return redirect(url_for('profile.documents'))
    
    return render_template('profile/basic_info.html', form=form, section='interests')

@profile_bp.route('/documents', methods=['GET', 'POST'])
@login_required
def documents():
    form = DocumentUploadForm()
    
    if form.validate_on_submit():
        # Check if file was uploaded
        if 'document_file' not in request.files:
            flash('No file part', 'danger')
            return redirect(request.url)
        
        file = request.files['document_file']
        
        if file.filename == '':
            flash('No selected file', 'danger')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            # Secure filename and create unique one
            filename = secure_filename(file.filename)
            unique_filename = generate_unique_filename(filename)
            
            # Create upload directory if it doesn't exist
            upload_dir = os.path.join(current_app.root_path, 'uploads')
            os.makedirs(upload_dir, exist_ok=True)
            
            # Save file
            file_path = os.path.join(upload_dir, unique_filename)
            file.save(file_path)
            
            # Convert to base64 for AI validation
            with open(file_path, "rb") as image_file:
                base64_image = base64.b64encode(image_file.read()).decode('utf-8')
            
            # Get user info for validation
            user_info = {
                'full_name': current_user.profile.full_name,
                'doc_number': form.doc_number.data
            }
            
            # Validate document with AI
            validation_result = validate_document(base64_image, form.doc_type.data, user_info)
            
            # Create document record
            document = Document(
                user_id=current_user.id,
                doc_type=form.doc_type.data,
                doc_number=form.doc_number.data,
                doc_url=file_path,  # In production, this would be a Cloudinary URL
                validated=validation_result.get('validation_score', 0) > 0.7,
                validation_result=str(validation_result)
            )
            
            db.session.add(document)
            db.session.commit()
            
            # Check validation result
            if document.validated:
                flash('Document uploaded and validated successfully!', 'success')
            else:
                flash('Document uploaded but could not be validated. Please try another document.', 'warning')
            
            # Remove local file after processing (in production we'd use Cloudinary)
            os.remove(file_path)
            
            return redirect(url_for('profile.documents'))
        else:
            flash('File type not allowed', 'danger')
    
    # Get user documents
    user_documents = Document.query.filter_by(user_id=current_user.id).all()
    
    return render_template('profile/documents.html', form=form, documents=user_documents)
