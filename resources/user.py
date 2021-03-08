#import os

from werkzeug.security import safe_str_cmp
from flask_jwt_extended.utils import get_jwt_identity
from flask_jwt_extended.view_decorators import jwt_required
from flask_restful import Resource, reqparse

from models.user import UserModel
from blacklist import BLACKLIST

from flask_jwt_extended import (
    create_access_token,
    get_jwt_identity,
    get_raw_jwt,
    )


# use parser to get username and password for user trying to register
_user_parser = reqparse.RequestParser()
_user_parser.add_argument('username',
            type=str,
            required=True,
            help="This field cannot be left blank!"
)
_user_parser.add_argument('password',
            type=str,
            required=True,
            help="This field cannot be left blank!"
)
_user_parser.add_argument('full_name',
            type=str,
            required=False,
            help="This is the name that will show to others."
)
_user_parser.add_argument('employee_code',
            type=str,
            required=False,
            help="This field is only required for employees"
)

class UserRegister(Resource):
    def post(self):
        data = _user_parser.parse_args()

        if not data['full_name']: # if None
            return {'message': 'You must provide a full name in order to register'}

        if UserModel.find_by_username(data['username']): # if is not None
            return {'message': 'A user with that name already exists.'}, 400

        #TODO: make this use OS variable instead of hard coded
        #employee_code = os.environ.get('EMPLOYEE_CODE')
        employee_code = "cssi2019@tymmary"

        if data['employee_code']: # if not None
            if safe_str_cmp(employee_code, data['employee_code']):
                del data['employee_code']
                employee = UserModel(is_employee=True, **data)
                employee.save_to_db()
                return {'message': 'Employee created successfully.'}, 201

            return {'message': 'Employee secret code is incorrect.'}, 401

        del data['employee_code']
        customer = UserModel(**data)
        customer.save_to_db()

        return {'message': 'Customer created successfully.'}, 201


class User(Resource):

    @classmethod
    def get(cls, user_id):
        user = UserModel.find_by_id(user_id)
        if not user:
            return {'message': 'User not found.'}, 404
        return user.json()

    @classmethod
    def delete(cls, user_id):
        user = UserModel.find_by_id(user_id)
        if not user:
            return {'message': 'User not found.'}, 404
        user.delete_from_db()
        return {'message': 'User deleted.'}, 200


class UserLogin(Resource):
    @classmethod
    def post(cls):
        # get data from parser
        data = _user_parser.parse_args()

        # find user in database
        user = UserModel.find_by_username(data['username'])

        # check password
        if user and safe_str_cmp(user.password, data['password']):
            access_token = create_access_token(identity=user.json(), fresh=True)
            return {
                'access_token': access_token,
            }, 200

        return {'message': 'Invalid credentials.'}, 401


class UserLogout(Resource):
    # to log out users just blacklist their current access token so that it won't work and
    # they'll have to log in again!
    @jwt_required
    def post(self):
        # jti --> JWT id (a unique identifier for a JWT)
        jti = get_raw_jwt()['jti']
        BLACKLIST.add(jti)
        return {'message': 'Successfully logged out.'}
