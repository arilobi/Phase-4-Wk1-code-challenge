from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData

metaData = MetaData()

db = SQLAlchemy(metadata=metaData)

# ---> CREATING THE USER TABLE
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(128), nullable=False)
    password = db.Column(db.String(128), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    
    products = db.relationship("Products", backref="user", lazy=True)

# ---> CREATING THE PRODUCTS TABLE
class Products(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    price = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, nullable=False)

    # ---> One user can have many products
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

# ---> CREATING A LOGOUT TABLE TO HOLD DATA OF USERS WHO HAVE LOGGED OUT
class TokenBlocklist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(36), nullable=False, index=True)
    created_at = db.Column(db.DateTime, nullable=False)
