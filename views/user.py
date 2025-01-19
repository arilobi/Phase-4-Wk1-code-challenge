from flask import jsonify, request, Blueprint 
from models import db, User
from werkzeug.security import generate_password_hash 

user_bp = Blueprint("user_bp", __name__)

# ---> CREATING THE CRUD FUNCTIONS

# ---> FETCHING A USER
@user_bp.route("/users", methods=["GET"])
def fetch_users():
    # ---> Fetching all the users in the db
    users = User.query.all()

    # ---> Fetching the user and their respective products that they own
    user_list = []
    for user in users:
        user_list.append({
            'id':user.id,
            'email':user.email,
            'is_admin': user.is_admin,
            'username':user.username,
            "products":[
                {
                    "id": product.id,
                    "name": product.name,
                    "price": product.price,
                    "stock": product.stock,
                } for product in user.products
            ]
        })
    return jsonify(user_list)

# ---> ADDING A USER / REGISTER
@user_bp.route("/users", methods=["POST"])
def add_users():
    data = request.get_json()

    username = data['username']
    email = data["email"]

    # ---> This is to make the password be hashed / scrypted 
    password = generate_password_hash(data['password'])

    # ---> Checking if the user already exists. If they do, it will bring the error in line 50 otherwise, it will create a new user in line 52
    check_username = User.query.filter_by(username=username).first()
    check_email = User.query.filter_by(email=email).first()

    if check_username or check_email:
        return jsonify({"error":"Username / Email already exists"})
    
    else:
        new_user = User(username=username, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()
        return jsonify({"success":"Added successfully"})
    
# ---> UPDATE A USER
@user_bp.route("/users/<int:user_id>", methods=["PATCH"])
def update_users(user_id):
    # ---> Using the get method to fetch the specific user to update their details
    user = User.query.get(user_id)

    if user:
        data = request.get_json()
        # ---> This is to get the user details from the database then check if the user exists in line 71 and 72 and afterwards, it will allow the user to update their details line 77
        username = data.get('username', user.username)
        email = data.get('email', user.email)
        password = data.get('password', user.password)

        check_username = User.query.filter_by(username=username and id!=user.id).first()
        check_email = User.query.filter_by(email=email and id!=user.id).first()

        if check_username or check_email:
            return jsonify({"error":"Username/email exists"}),406

        else:
            user.username=username
            user.email=email
            user.password=password
          
            db.session.commit()
            return jsonify({"success":"Updated successfully"}), 201
        
    else:
        return jsonify({"error": "User doesn't exist!"})

# ----> DELETE A USER
@user_bp.route("/users/<int:user_id>", methods=["DELETE"])
def delete_users(user_id):
    user = User.query.get(user_id)

    if user:
        db.session.delete(user)
        db.session.commit()
        return jsonify({"success": "Deleted successfully"})
    
    else:
        return jsonify({"error": "The User you are trying to delete doesn't exist!"})
    
