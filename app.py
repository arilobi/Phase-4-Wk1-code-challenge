from flask import Flask 
from flask_migrate import Migrate 
from models import db, TokenBlocklist
from flask_jwt_extended import JWTManager 
from datetime import timedelta

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///shop.db'
migrate = Migrate(app, db)
db.init_app(app)

#JWT EXTENDED configuration
app.config["JWT_SECRET_KEY"] = "supershy"
app.config["JWT_ACCESS_TOKEN_EXPIRE"] = timedelta(hours = 1)  #This is to tell the token to expire after 1 hour after registering / login in.
jwt = JWTManager(app)
# ---> Initializing 
jwt.init_app(app)

from views import *

app.register_blueprint(user_bp)
app.register_blueprint(products_bp)
app.register_blueprint(auth_bp)

# ---> This is for the logout function to work but I'm having issues with postman so I'm not entirley sure if it's working.
@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_payload: dict) -> bool:
    jti = jwt_payload["jti"]
    token = db.session.query(TokenBlocklist.id).filter_by(jti=jti).scalar()

    return token is not None

# ---> This is to run the app.
if __name__ == "__main__":
    app.run("localhost", debug=True)