# models.py

from flask_sqlalchemy import SQLAlchemy
from datetime import date, datetime
from sqlalchemy import CheckConstraint
from werkzeug.security import generate_password_hash, check_password_hash
import re

db = SQLAlchemy()

# Users table
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(50), nullable=True)
    income = db.Column(db.Float, nullable=True)
    goal = db.Column(db.String(50), nullable=True)  # e.g., "high_savings", "house", "retirement"
    risk_profile = db.Column(db.String(20), nullable=True)  # low/medium/high
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    expenses = db.relationship('Expense', backref='user', lazy=True, cascade='all, delete-orphan')
    
  
    
    def set_password(self, password):
        """Hash and set password"""
        self.password = generate_password_hash(password)
    
    def check_password(self, password):
        """Check password against hash"""
        return check_password_hash(self.password, password)
    
    def validate_email(self):
        """Validate email format"""
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(email_regex, self.email) is not None
    
    def validate_income(self):
        """Validate income is positive"""
        return self.income is None or self.income >= 0
    
    def to_dict(self):
        """Convert user to dictionary"""
        return {
            'id': self.id,
            'email': self.email,
            'name': self.name,
            'income': self.income,
            'goal': self.goal,
            'risk_profile': self.risk_profile,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'is_active': self.is_active
        }
    
    def __repr__(self):
        return f'<User {self.email}>'

# Expenses table
class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(200), nullable=True)
    created_at = db.Column(db.Date, nullable=False, default=date.today)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Constraints
    __table_args__ = (
        CheckConstraint('amount > 0', name='check_amount_positive'),
        CheckConstraint("category IN ('housing', 'food', 'transportation', 'utilities', 'healthcare', 'entertainment', 'shopping', 'education', 'savings', 'other')", name='check_category'),
    )
    
    def validate_amount(self):
        """Validate amount is positive"""
        return self.amount > 0
    
    def validate_category(self):
        """Validate category is valid"""
        valid_categories = ['housing', 'food', 'transportation', 'utilities', 
                          'healthcare', 'entertainment', 'shopping', 'education', 
                          'savings', 'other']
        return self.category in valid_categories
    
    def to_dict(self):
        """Convert expense to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'category': self.category,
            'amount': self.amount,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<Expense {self.category}: ${self.amount}>'
