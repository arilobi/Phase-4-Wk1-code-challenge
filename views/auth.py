from flask import jsonify, request, Blueprint 
from models import db, User, TokenBlocklist
from werkzeug.security import check_password_hash
from datetime import datetime
from datetime import timedelta
from datetime import timezone
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, get_jwt

auth_bp = Blueprint("auth_bp", __name__)

# Login Function
@auth_bp.route("/login", methods=["POST"])
def login():
    # ---> getting data from the request
    data = request.get_json()
    # ---> The email and password that are in the database are required for one to login.
    if not data or "email" not in data or "password" not in data:
        return jsonify({"error": "Email and password are required"}), 400
    
    email = data["email"]
    password = data["password"]

    # ---> Checking if the user exists
    user = User.query.filter_by(email=email).first()

    # ---> if the user exists and the password hash from User.py and the one in line 21 match, it will give me the access token. 
    if user and check_password_hash(user.password, password):
        # ---> Creating a token and converted it into a string because my postman was telling me that a string was necessary for it to work. It couldn't work without it.
        access_token = create_access_token(identity=str(user.id))
        return jsonify({"access_token": access_token}), 200
    else:
        return jsonify({"error": "Either email/password is incorrect"}), 404

# ---> getting the current user
@auth_bp.route("/current_user", methods=["GET"])
@jwt_required()  # ---> this is what will be required in the Authorization header.
def current_user():
    # ---> Get the current user's ID from the JWT token
    current_user_id = get_jwt_identity()

    # ---> Fetching the user from the database by their ID and if the user is not there, it will give me a message in line 45.
    user = User.query.get(current_user_id)

    if not user:
        return jsonify({"error": "User not found"}), 404

    # ---> This will return the user information
    user_data = {
        "id": user.id,
        "email": user.email,
        "username": user.username
    }

    return jsonify(user_data), 200


# ---> LOGOUT function. I'm not entirely sure if this works because my postman refused to load. 
@auth_bp.route("/logout", methods=["DELETE"])
@jwt_required()
def logout():
    jti = get_jwt()["jti"]
    now = datetime.now(timezone.utc)
    db.session.add(TokenBlocklist(jti=jti, created_at=now))
    db.session.commit()
    return jsonify({"success": "Logged out successfully"})
