import uuid
from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import declarative_base, relationship, validates
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import re
import json
import typing
import sqlalchemy as sa

Base = declarative_base()

class BaseModel(Base):
    __abstract__ = True

    def __repr__(self):
        return str({column.name: getattr(self, column.name) for column in self.__table__.columns if hasattr(self, column.name)})
        
class Product(BaseModel):
    __tablename__ = 'products'

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    uuid = Column(String(36), default=lambda: str(uuid.uuid4()), unique=True, nullable=False)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(String(200))
    category_id = Column(Integer, ForeignKey('categories.id'))
    price = Column(Float)
    currency = Column(String(3), nullable=False)
    quantity = Column(Integer)
    creation_date = Column(DateTime, default=datetime.now(), nullable=False)
    changed_date = Column(DateTime, default=datetime.now(), nullable=False)
    
    category = relationship('Category', back_populates='products')

    @validates('price')
    def validate_price(self, key, price):
        if price < 0:
            raise ValueError("Price must be positive")
        return price
    
    @validates('quantity')
    def validate_quantity(self, key, quantity):
        if quantity <= 0:
            raise ValueError("Quantity must be 0 or more")
        return quantity
    
    @validates('currency')
    def validate_currency(self, key, currency):
        with open('../data/currencies.json', 'r') as f:
            data = json.load(f)
        allowed_currencies = data['allowed_currencies']
        currency = currency.lower()
        if currency not in allowed_currencies:
            raise ValueError(f"Invalid currency '{currency}', allowed currencies are {allowed_currencies}")
        return currency

class Category(BaseModel):
    __tablename__ = 'categories'
    
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(String(200))
    parent_id = Column(Integer, ForeignKey('categories.id')) # Parentid None means it's a top-level category
    
    parent = relationship('Category', remote_side=[id], backref='subcategories')
    products = relationship('Product', back_populates='category')

class Transaction(BaseModel):
    __tablename__ = 'transactions'
    
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    uuid = Column(String(36), default=lambda: str(uuid.uuid4()), unique=True, nullable=False)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    date = Column(DateTime, default=datetime.now(), nullable=False)
    profit = Column(Float, nullable=False)
    currency = Column(String(3), nullable=False)
    quantity = Column(Integer, nullable=False)
    transaction_type = Column(String(20), nullable=False)

    product = relationship('Product')
    user = relationship('User')

    @validates('transaction_type')
    def validate_transaction_type(self, key, transaction_type):
        allowed_types = ['purchase', 'refund', 'restock']
        if transaction_type not in allowed_types:
            raise ValueError(f"Invalid transaction type '{transaction_type}', allowed types are {allowed_types}")
        return transaction_type
    
    @validates('quantity')
    def validate_quantity(self, key, quantity):
        if quantity < 0:
            raise ValueError("Quantity must be positive")
        return quantity
    
    @validates('currency')
    def validate_currency(self, key, currency):
        with open('../data/currencies.json', 'r') as f:
            data = json.load(f)
        allowed_currencies = data['allowed_currencies']
        currency = currency.lower()
        if currency not in allowed_currencies:
            raise ValueError(f"Invalid currency '{currency}', allowed currencies are {allowed_currencies}")
        return currency

class User(BaseModel):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    uuid = Column(String(36), default=lambda: str(uuid.uuid4()), unique=True, nullable=False)
    username = Column(String(50), unique=True, nullable=False)
    password = Column(String(300), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    type = Column(String(50), default='user')  # admin_user, user

    __mapper_args__ = {
        'polymorphic_identity':'user',
        'polymorphic_on':type
    }

    def set_password(self, password):
        self.password = generate_password_hash(password)
    
    def set_username(self, username):
        self.username = username.lower()

    def set_email(self, email):
        self.email = email.lower()
    
    def check_password(self, password):
        return check_password_hash(self.password, password)

    @validates('username')
    def validate_username(self, key, username):
        if len(username) < 3:
            raise ValueError("Username must be at least 3 characters long")
        return username.lower()

    @validates('email')
    def validate_email(self, key, email):
        pattern = r"[^@]+@[^@]+\.[^@]+"
        if not re.match(pattern, email):
            raise ValueError("Invalid email")
        return email

class AdminUser(User):
    admin_status = Column(String(50), default='none')  # super, regular, etc.

    __mapper_args__ = {
        'polymorphic_identity':'admin_user',
    }

    @validates('admin_status')
    def validate_admin_status(self, key, status):
        allowed_statuses = ['none', 'regular', 'full']
        if status not in allowed_statuses:
            raise ValueError(f"Invalid admin status '{status}', allowed statuses are {allowed_statuses}")
        return status