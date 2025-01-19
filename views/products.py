from flask import jsonify, request, Blueprint
from models import db, Products
from flask_jwt_extended import jwt_required, get_jwt_identity

products_bp = Blueprint("products_bp", __name__)

# ---> CREATING THE CRUD FUNCTIONS

# ---> FETCH ALL PRODUCTS
@products_bp.route("/products", methods=["GET"])
@jwt_required()
def fetch_products(): 
    current_user_id = get_jwt_identity()

    # ---> Fetching all the products in the db that belongs to the current user
    products = Products.query.filter_by(user_id=current_user_id)

    # ---> This will list all the product details after fetching it.
    product_list = [
        {
            "id": product.id,
            "name": product.name,
            "price": product.price,
            "stock": product.stock,
            "user_id": product.user_id,
            "user": {"id":product.user.id, "username": product.user.username, "email": product.user.email},
           
        } for product in products
    ]    
    return jsonify(product_list), 200

# ---> GET Product BY ID
@products_bp.route("/product/<int:product_id>", methods=["GET"])
@jwt_required()
def get_product(product_id):
    # ---> This will show the product details and the user id that owns the products
    current_user_id = get_jwt_identity()

    product = Products.query.filter_by(id=product_id, user_id=current_user_id).first()
    if product:
        product_details = {
            "id": product.id,
            "name": product.name,
            "price": product.price,
            "stock": product.stock,
            "user_id": product.user_id
        }
        return jsonify(product_details), 200
    
    else:
        return jsonify({"error": "Product not found"}), 406


# ---> ADD A PRODUCT
@products_bp.route("/products", methods=["POST"])
@jwt_required()
def add_products():
    data = request.get_json()
    current_user_id = get_jwt_identity()

    name = data['name']
    price = data["price"]
    stock = data['stock']

    # ---> Check if the product name already exists
    check_name = Products.query.filter_by(name=name).first()

    if check_name:
        return jsonify({"error": "Product already exists"}), 400
    
    # ---> I had to pass this because it's not allowing me to add a product without passing a user id even when I have an access token
    if not current_user_id:
        return jsonify({"error": "User ID is required"}), 400

    # ----> Create a new product and associate it with the user
    new_product = Products(name=name, price=price, stock=stock, user_id=current_user_id)
    db.session.add(new_product)
    db.session.commit()
    return jsonify({"success": "Added successfully"}), 201

# ---> UPDATE A PRODUCT
@products_bp.route("/products/<int:product_id>", methods=["PUT"])
@jwt_required()
def update_products(product_id):
    product = Products.query.get(product_id)
    current_user_id = get_jwt_identity()
    
    # ---> If the product and the product user id is equal to the current user logged in, the user will be allowed to update their product.
    if product and product.user_id==current_user_id:
        data = request.get_json()

        name = data.get('name', product.name)
        price = data.get('price', product.price)
        stock = data.get('stock', product.stock)

        # ---> This is to check if there's any product with the same name but with a different id, helping to avoid duplication while updating products.
        check_name = Products.query.filter(Products.name == name, Products.id != product.id).first()

        if check_name:
            return jsonify({"error":"Product already exists"}),406

        else:
            product.name = name
            product.price = price
            product.stock = stock
          
            db.session.commit()
            return jsonify({"success":"Updated successfully"}), 201
        
    else:
        return jsonify({"error": "Product doesn't exist!"})

# ---> DELETE A PRODUCT
@products_bp.route("/products/<int:product_id>", methods=["DELETE"])
@jwt_required()
def delete_products(product_id):
    current_user_id = get_jwt_identity()

    # ---> We're filtering the product by the product id with it's associated current user id so that the current user can be able to delete their product.
    product = Products.query.filter_by(id=product_id, user_id=current_user_id).first()

    if not product:
        return jsonify({"error": "Product not found/Unauthorized"}), 406
    
    db.session.delete(product)
    db.session.commit()
    return jsonify({"success": "Product deleted successfully"}), 200
