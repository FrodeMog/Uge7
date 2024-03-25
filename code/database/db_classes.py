import uuid
from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, DateTime, Text
from sqlalchemy.orm import declarative_base, relationship, validates
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import re
import os
import json

# Get the directory of the current script
script_dir = os.path.dirname(os.path.abspath(__file__))

# Construct the path to the file
file_path = os.path.join(script_dir, '..', 'data', 'currencies.json')

with open(file_path, 'r') as f:
    currencies_data = json.load(f)

ALLOWED_CURRENCIES = currencies_data['allowed_currencies']
ALLOWED_TRANSACTION_TYPES = ['purchase', 'refund', 'restock']
ALLOWED_ADMIN_STATUSES = ['none', 'regular', 'full']

def validate_currency(currency):
    currency = currency.lower()
    if currency not in ALLOWED_CURRENCIES:
        raise ValueError(f"Invalid currency '{currency}', allowed currencies are {ALLOWED_CURRENCIES}")
    return currency

Base = declarative_base()

class BaseModel(Base):
    __abstract__ = True

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            if value is None and not self.__table__.c[key].nullable:
                raise ValueError(f"{key} cannot be null")
            if isinstance(self.__table__.c[key].type, String) and self.__table__.c[key].type.length is not None and len(value) > self.__table__.c[key].type.length:
                raise SQLAlchemyError(f"{key} must be less than {self.__table__.c[key].type.length} characters")
            setattr(self, key, value)

    def __repr__(self):
        return str({column.name: getattr(self, column.name) for column in self.__table__.columns if hasattr(self, column.name)})
class Log(BaseModel):
    __tablename__ = 'logs'
    
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    uuid = Column(String(36), default=lambda: str(uuid.uuid4()), unique=True, nullable=False)
    date = Column(DateTime, default=datetime.now(), nullable=False)
    func = Column(String(100), nullable=False)
    kwargs = Column(Text)
    status = Column(String(10), nullable=False)
    message = Column(Text)

class Product(BaseModel):
    __tablename__ = 'products'

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    uuid = Column(String(36), default=lambda: str(uuid.uuid4()), unique=True, nullable=False)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(Text)
    category_id = Column(Integer, ForeignKey('categories.id'))
    purchase_price = Column(Float)
    restock_price = Column(Float)
    currency = Column(String(3), nullable=False)
    quantity = Column(Integer)
    creation_date = Column(DateTime, default=datetime.now(), nullable=False)
    changed_date = Column(DateTime, default=datetime.now(), nullable=False)
    
    category = relationship('Category', back_populates='products')

    @validates('purchase_price', 'restock_price')
    def validate_price(self, key, price):
        if price < 0:
            raise ValueError("Price must be positive")
        return price
    
    @validates('quantity')
    def validate_quantity(self, key, quantity):
        if quantity < 0:
            raise ValueError("Quantity must be 0 or more")
        return quantity
    
    @validates('currency')
    def validate_currency(self, key, currency):
        return validate_currency(currency)

class Category(BaseModel):
    __tablename__ = 'categories'
    
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(Text)
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
    price = Column(Float, nullable=False)
    currency = Column(String(3), nullable=False)
    quantity = Column(Integer, nullable=False)
    transaction_type = Column(String(20), nullable=False)

    product = relationship('Product')
    user = relationship('User')

    @validates('transaction_type')
    def validate_transaction_type(self, key, transaction_type):
        if transaction_type not in ALLOWED_TRANSACTION_TYPES:
            raise ValueError(f"Invalid transaction type '{transaction_type}', allowed types are {ALLOWED_TRANSACTION_TYPES}")
        return transaction_type
    
    @validates('quantity')
    def validate_quantity(self, key, quantity):
        if quantity < 0:
            raise ValueError("Quantity must be positive")
        return quantity
    
    @validates('currency')
    def validate_currency(self, key, currency):
        return validate_currency(currency)

class User(BaseModel):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    uuid = Column(String(36), default=lambda: str(uuid.uuid4()), unique=True, nullable=False)
    username = Column(String(50), unique=True, nullable=False)
    password = Column(String(300), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    type = Column(String(20), default='user')  # admin_user, user

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
        if not re.match("^[A-Za-z0-9_]+$", username):
            raise ValueError("Username can only contain letters, numbers, and underscores")
        return username.lower()

    @validates('email')
    def validate_email(self, key, email):
        pattern = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
        if not re.match(pattern, email):
            raise ValueError("Invalid email address")
        return email

class AdminUser(User):
    admin_status = Column(String(50), default='none')

    __mapper_args__ = {
        'polymorphic_identity':'admin_user',
    }

    @validates('admin_status')
    def validate_admin_status(self, key, status):
        if status not in ALLOWED_ADMIN_STATUSES:
            raise ValueError(f"Invalid admin status")
        return status