# db_models.py

from flask_sqlalchemy import SQLAlchemy
from enum import Enum

db = SQLAlchemy()

class TransportType(Enum):
    PICKUP = "PICKUP"
    TRUCK = "TRUCK"
    COURIER = "COURIER"

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

    # Nowa kolumna – domyślnie False
    is_admin = db.Column(db.Boolean, default=False)

    def __init__(self, username, email, password, is_admin=False):
        self.username = username
        self.email = email
        self.password = password
        self.is_admin = is_admin

class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Float, nullable=False)
    image = db.Column(db.LargeBinary, nullable=True)

class Province(Enum):
    DOLNOSLASKIE = "dolnośląskie"
    KUJAWSKOPOMORSKIE = "kujawsko-pomorskie"
    LUBELSKIE = "lubelskie"
    LUBUSKIE = "lubuskie"
    LODZKIE = "łódzkie"
    MAŁOPOLSKIE = "małopolskie"
    MAZOWIECKIE = "mazowieckie"
    OPOLE = "opolskie"
    PODKARPACKIE = "podkarpackie"
    PODLASKIE = "podlaskie"
    POMORSKIE = "pomorskie"
    SLASKIE = "śląskie"
    SWIETOKRZYSKIE = "świętokrzyskie"
    WARMINSKOMAZURSKIE = "warmińsko-mazurskie"
    WIELKOPOLSKIE = "wielkopolskie"
    ZACHODNIOPOMORSKIE = "zachodniopomorskie"

class Order(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    delivery_date = db.Column(db.String(50), nullable=False)  # Możesz użyć db.Date lub db.DateTime
    address = db.Column(db.String(200), nullable=False)
    transport_type = db.Column(db.Enum(TransportType), nullable=False)
    province = db.Column(db.Enum(Province), nullable=False)  # Nowe pole

    def __init__(self, user_id, product_id, delivery_date, address, transport_type, province):
        self.user_id = user_id
        self.product_id = product_id
        self.delivery_date = delivery_date
        self.address = address
        self.transport_type = transport_type
        self.province = province