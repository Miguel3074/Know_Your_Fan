from datetime import datetime
from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    verified = db.Column(db.Boolean, default=False)
    
    # Relationships
    profile = db.relationship('UserProfile', backref='user', uselist=False, cascade='all, delete-orphan')
    documents = db.relationship('Document', backref='user', lazy=True, cascade='all, delete-orphan')
    social_media = db.relationship('SocialMedia', backref='user', lazy=True, cascade='all, delete-orphan')
    esports_profiles = db.relationship('EsportsProfile', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'

class UserProfile(db.Model):
    __tablename__ = 'user_profiles'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    full_name = db.Column(db.String(100))
    cpf = db.Column(db.String(14))
    birthdate = db.Column(db.Date)
    address = db.Column(db.String(200))
    city = db.Column(db.String(50))
    state = db.Column(db.String(30))
    postal_code = db.Column(db.String(10))
    country = db.Column(db.String(50), default="Brazil")
    phone = db.Column(db.String(20))
    interests = db.Column(db.Text)
    favorite_games = db.Column(db.Text)
    favorite_teams = db.Column(db.Text)
    gaming_experience = db.Column(db.Text)
    completed = db.Column(db.Boolean, default=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<UserProfile {self.full_name}>'

class Document(db.Model):
    __tablename__ = 'documents'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    doc_type = db.Column(db.String(50), nullable=False)  # ID, CPF, passport, etc.
    doc_number = db.Column(db.String(50))
    doc_url = db.Column(db.String(255))  # Cloudinary URL
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    validated = db.Column(db.Boolean, default=False)
    validation_timestamp = db.Column(db.DateTime)
    validation_result = db.Column(db.Text)
    
    def __repr__(self):
        return f'<Document {self.doc_type}: {self.doc_number}>'

class SocialMedia(db.Model):
    __tablename__ = 'social_media'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    platform = db.Column(db.String(50), nullable=False)  # Twitter, Instagram, etc.
    username = db.Column(db.String(100))
    profile_url = db.Column(db.String(255))
    access_token = db.Column(db.String(255))
    refresh_token = db.Column(db.String(255))
    token_expires = db.Column(db.DateTime)
    verified = db.Column(db.Boolean, default=False)
    linked_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<SocialMedia {self.platform}: {self.username}>'

class EsportsProfile(db.Model):
    __tablename__ = 'esports_profiles'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    platform = db.Column(db.String(50), nullable=False)  # Steam, Battlenet, etc.
    username = db.Column(db.String(100))
    profile_url = db.Column(db.String(255))
    verified = db.Column(db.Boolean, default=False)
    relevance_score = db.Column(db.Float)  # AI validation score
    validation_result = db.Column(db.Text)
    added_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<EsportsProfile {self.platform}: {self.username}>'
