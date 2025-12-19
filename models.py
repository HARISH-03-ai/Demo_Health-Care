from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(200), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    is_blocked = db.Column(db.Boolean, default=False)
    phone = db.Column(db.String(20), unique=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    reviews = db.relationship("Review", backref="user", lazy=True)
    is_verified = db.Column(db.Boolean, default=False)
    verification_token = db.Column(db.String(200))
    reset_token = db.Column(db.String(200))
    reset_token_expiry = db.Column(db.DateTime)
    profile_pic = db.Column(db.String(300), default="/static/images/default_pfp.png")

    def __repr__(self):
        return f"<User {self.email}>"
    

class HeroSection(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image_url = db.Column(db.String(500))
    product_name = db.Column(db.String(200))
    product_desc = db.Column(db.String(300))
    offer_text = db.Column(db.String(300))
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(50))
    price = db.Column(db.Float, nullable=False)
    image_url = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # NEW
    description = db.Column(db.String(500))
    details = db.Column(db.Text)
    refund_policy = db.Column(db.Text)
    shipping_info = db.Column(db.Text)



class ContactMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150))
    gender = db.Column(db.String(20))
    email = db.Column(db.String(200))
    phone = db.Column(db.String(20))
    message = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    review_text = db.Column(db.String(500), nullable=False)
    admin_reply = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# models.py

class Highlight(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    video_file = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)