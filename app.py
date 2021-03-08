import os

from flask import Flask, jsonify
from flask_restful import Api
from flask_jwt_extended import JWTManager

from db import db
from blacklist import BLACKLIST
from resources.user import UserRegister, User, UserLogin, UserLogout
from resources.appointment import Appointment, AppointmentList, Schedule  

# must import all models where tables
# are defined because SQLAlchemy only creates the tables (line 27) that it sees


app = Flask(__name__)

# doesn't have to be sqlite in the next line. Can be mysql, postgresql, etc.
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///data.db')
# not changing the underlying behavior since there is still an implicit modification tracker
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['PROPAGATE_EXCEPTIONS'] = True
app.config['JWT_BLACKLIST_ENABLED'] = True
app.config['JWT_BLACKLIST_TOKEN_CHECKS'] = ['access',] # this might create a bug
app.secret_key = 'salon-reservation'
api = Api(app)

jwt = JWTManager(app) # JWT creates a new endpoint /auth, which
# when we call it, a username and password is sent to it.

@jwt.token_in_blacklist_loader
def check_if_token_in_blacklist(decrypted_token):
    return decrypted_token['jti'] in BLACKLIST

# function to see if we should add anything extra to JWT token response
@jwt.user_claims_loader
def add_claims_to_jwt(is_employee):
    # if it is the 1st user created, they are admin. Else not.
    # instead of hard-coding this, better to read from a config file or a database
    if is_employee:
        return {'is_employee': True}
    return {'is_employee': False}


# when user types in a random string in the authorization header instead of JWT token
@jwt.invalid_token_loader
def invalid_token_callback(error):
    return jsonify({
        'description': 'Signature verification failed.',
        'error': 'invalid_token'
    }), 401

# when user doesn't send a JWT at all
@jwt.unauthorized_loader
def missing_token_callback(error):
    return jsonify({
        'description': 'Request does not contain an access token.',
        'error': 'authorization required'
    }), 401


# remove an access token from a user (logging out someone so they have to input username/pass again)
@jwt.revoked_token_loader
def revoked_token_callback():
    return jsonify({
        'description': 'The token has been revoked.',
        'error': 'token_revoked'
    }), 401

@app.before_first_request
def create_tables():
    db.create_all()

api.add_resource(User, '/user/<int:user_id>')
api.add_resource(UserRegister, '/register')
api.add_resource(UserLogin, '/login')
api.add_resource(UserLogout, '/logout')
api.add_resource(AppointmentList, '/appointments')
api.add_resource(Appointment, '/appointment/<string:date>/<int:timeslot>')
api.add_resource(Schedule, '/schedule')

if __name__ == "__main__":
    # debug=True gives useful into in HTML format when things go wrong
    db.init_app(app)
    app.run(port=5000, debug=True)
