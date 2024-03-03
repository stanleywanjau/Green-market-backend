from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import validates
from sqlalchemy import CheckConstraint
from marshmallow import validates_schema, ValidationError
from config import db, bcrypt




association_table_order_product = db.Table(
    'association_order_product',
    db.Column('order_id', db.Integer, db.ForeignKey('order.id')),
    db.Column('product_id', db.Integer, db.ForeignKey('product.id'))
)

association_table_product_review = db.Table(
    'association_product_review',
    db.Column('product_id', db.Integer, db.ForeignKey('product.id')),
    db.Column('review_id', db.Integer, db.ForeignKey('reviews.id'))
)

class User(db.Model, SerializerMixin):
    __tablename__ = "user"
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String,unique=True)
    email = db.Column(db.String,unique=True)
    password_hash = db.Column(db.String)  
    role = db.Column(db.String)
    registration_date = db.Column(db.Date)
    image = db.Column(db.String)
    farmer = db.relationship('Farmer', backref='user', uselist=False)
    orders = db.relationship('Order', backref='user')
    reviews = db.relationship('Reviews', backref='user', lazy='dynamic') 
    sent_messages = db.relationship('ChatMessage', foreign_keys='ChatMessage.sender_id', backref='sender', lazy='dynamic')
    received_messages = db.relationship('ChatMessage', foreign_keys='ChatMessage.receiver_id', backref='receiver', lazy='dynamic')
    
    
    @validates('email')
    def validate_email(self, key, email):
        if not email or '@' not in email:
            raise ValueError('Invalid email address format')
        return email

    @validates_schema
    def validate_schema(self, data):
        if 'role' in data and data['role'] not in ['Farmer', 'customer']:
            raise ValidationError('Invalid role. Must be either "Farmer" or "customer"')

class Farmer(db.Model, SerializerMixin):
    __tablename__ = "farmer"
    
    id = db.Column(db.Integer, primary_key=True)
    farm_name = db.Column(db.String,unique=True)
    location = db.Column(db.String)
    contact = db.Column(db.String)    
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True)
    products = db.relationship('Product', backref='farmer')

class Reviews(db.Model, SerializerMixin):
    __tablename__ = "reviews"
    
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    product_id = db.Column(db.Integer, db.ForeignKey('product.id')) 
    rating = db.Column(db.Integer)
    comments = db.Column(db.String)
    review_date = db.Column(db.Date)
    
    @validates('rating')
    def validate_rating(self, key, rating):
        if rating < 1 or rating > 5:
            raise ValueError('Rating must be between 1 and 5')
        return rating

class Product(db.Model, SerializerMixin):
    __tablename__ = "product"
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    price = db.Column(db.Integer)
    description = db.Column(db.String)
    quantity_available = db.Column(db.Integer)
    category = db.Column(db.String)
    image = db.Column(db.String)
    farmer_id = db.Column(db.Integer, db.ForeignKey('farmer.id'))
    reviews = db.relationship('Reviews', secondary=association_table_product_review, backref='products')  

class Order(db.Model, SerializerMixin):
    __tablename__ = "order"
    
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))  
    order_date = db.Column(db.Date)
    quantity_ordered = db.Column(db.Integer)
    total_price = db.Column(db.Integer)  
    order_status = db.Column(db.String)
    payments = db.relationship('Payment', backref='order')
    products = db.relationship('Product', secondary=association_table_order_product, backref='orders')  
    
    
    @validates('quantity_ordered')
    def validate_quantity_ordered(self, key, quantity_ordered):
        if quantity_ordered <= 0:
            raise ValueError('Quantity ordered must be greater than 0')
        return quantity_ordered

class Payment(db.Model, SerializerMixin):
    __tablename__ = "payment"
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'))
    payment_amount = db.Column(db.Integer)  
    payment_date = db.Column(db.Date)
    payment_method = db.Column(db.String)
    status = db.Column(db.String)
    transaction_id = db.Column(db.Integer)
    
    
    @validates('payment_amount')
    def validate_payment_amount(self, key, payment_amount):
        if payment_amount < 0:
            raise ValueError('Payment amount cannot be negative')
        return payment_amount

class ChatMessage(db.Model, SerializerMixin):
    __tablename__ = "chat_message"  
    
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id', name='fk_sender_id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id', name='fk_receiver_id'), nullable=False)
    message_text = db.Column(db.String)
    timestamp = db.Column(db.DateTime)  
    
    @validates('message_text')
    def validate_message_text(self, key, message_text):
        if not message_text:
            raise ValueError('Message text cannot be empty')
        return message_text
