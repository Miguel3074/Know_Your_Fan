from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, PasswordField, BooleanField, TextAreaField, SelectField, DateField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length, URL, Optional, ValidationError
from models import User
import re

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[
        DataRequired(), 
        Length(min=3, max=64, message='Username must be between 3 and 64 characters')
    ])
    email = StringField('Email', validators=[
        DataRequired(), 
        Email(message='Please enter a valid email address')
    ])
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=8, message='Password must be at least 8 characters long')
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(),
        EqualTo('password', message='Passwords must match')
    ])
    agree_terms = BooleanField('I agree to the terms and conditions', validators=[
        DataRequired(message='You must agree to the terms and conditions')
    ])
    submit = SubmitField('Register')
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username is already taken. Please choose a different one.')
            
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email is already registered. Please use a different one.')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Login')

class BasicInfoForm(FlaskForm):
    full_name = StringField('Full Name', validators=[DataRequired(), Length(min=3, max=100)])
    cpf = StringField('CPF (Brazilian ID)', validators=[
        DataRequired(), 
        Length(min=11, max=14, message='CPF must be 11 digits')
    ])
    birthdate = DateField('Birth Date', validators=[DataRequired()], format='%Y-%m-%d')
    address = StringField('Address', validators=[DataRequired(), Length(max=200)])
    city = StringField('City', validators=[DataRequired(), Length(max=50)])
    state = StringField('State', validators=[DataRequired(), Length(max=30)])
    postal_code = StringField('Postal Code', validators=[DataRequired(), Length(max=10)])
    country = StringField('Country', validators=[DataRequired(), Length(max=50)], default="Brazil")
    phone = StringField('Phone Number', validators=[DataRequired(), Length(max=20)])
    submit = SubmitField('Save Basic Information')
    
    def validate_cpf(self, cpf):
        # Remove special characters
        digits = ''.join(re.findall('\d', cpf.data))
        
        if len(digits) != 11:
            raise ValidationError('CPF must contain 11 digits.')
            
        # Check if all digits are the same
        if digits == digits[0] * 11:
            raise ValidationError('Invalid CPF number.')
        
        # Validate CPF
        from utils import is_valid_cpf
        if not is_valid_cpf(cpf.data):
            raise ValidationError('Invalid CPF number.')

class InterestsForm(FlaskForm):
    interests = TextAreaField('What are your main interests in esports?', validators=[DataRequired()])
    favorite_games = TextAreaField('What are your favorite games?', validators=[DataRequired()])
    favorite_teams = TextAreaField('What are your favorite esports teams?', validators=[DataRequired()])
    gaming_experience = TextAreaField('Describe your gaming experience and history', validators=[DataRequired()])
    submit = SubmitField('Save Interests')

class DocumentUploadForm(FlaskForm):
    doc_type = SelectField('Document Type', validators=[DataRequired()], choices=[
        ('id', 'ID Card'),
        ('cpf', 'CPF Card'),
        ('passport', 'Passport'),
        ('drivers_license', 'Driver\'s License')
    ])
    doc_number = StringField('Document Number', validators=[DataRequired(), Length(max=50)])
    document_file = FileField('Upload Document', validators=[
        FileRequired(),
        FileAllowed(['jpg', 'jpeg', 'png', 'pdf'], 'Images and PDFs only!')
    ])
    submit = SubmitField('Upload Document')

class SocialMediaForm(FlaskForm):
    platform = SelectField('Platform', validators=[DataRequired()], choices=[
        ('twitter', 'Twitter/X'),
        ('instagram', 'Instagram'),
        ('facebook', 'Facebook'),
        ('tiktok', 'TikTok'),
        ('youtube', 'YouTube')
    ])
    username = StringField('Username', validators=[DataRequired(), Length(max=100)])
    profile_url = StringField('Profile URL', validators=[DataRequired(), URL()])
    submit = SubmitField('Link Social Media')

class EsportsProfileForm(FlaskForm):
    platform = SelectField('Platform', validators=[DataRequired()], choices=[
        ('steam', 'Steam'),
        ('battlenet', 'Battle.net'),
        ('riot', 'Riot Games'),
        ('epic', 'Epic Games'),
        ('ea', 'EA/Origin'),
        ('psn', 'PlayStation Network'),
        ('xbox', 'Xbox Live'),
        ('nintendo', 'Nintendo Account'),
        ('faceit', 'FACEIT'),
        ('esea', 'ESEA'),
        ('other', 'Other')
    ])
    username = StringField('Username', validators=[DataRequired(), Length(max=100)])
    profile_url = StringField('Profile URL', validators=[DataRequired(), URL()])
    submit = SubmitField('Add Esports Profile')
