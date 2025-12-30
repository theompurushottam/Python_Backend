from flask import request, jsonify
from flask_restful import Resource, reqparse
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token
from models.user_model import create_user, get_user_by_email

class RegisterUser(Resource):
    def post(self):
        data = request.get_json()
        name = data.get("name")
        email = data.get("email")
        password = data.get("password")

        if not (name and email and password):
            return {"message": "All fields are required"}, 400

        password_hash = generate_password_hash(password)
        if create_user(name, email, password_hash):
            return {"message": "User registered successfully"}, 201
        return {"message": "User already exists"}, 409


class LoginUser(Resource):
    def post(self):
        # Parse the request data
        parser = reqparse.RequestParser()
        parser.add_argument("email", required=True, help="Email is required")
        parser.add_argument("password", required=True, help="Password is required")
        args = parser.parse_args()

        # Retrieve user from the database
        user = get_user_by_email(args["email"])  # Ensure this returns a User object
        print(f"args:{args}")
        print(f"user: {user}") 
        # Validate user and password
        if not user or not check_password_hash(user.password_hash, args["password"]):
            return {"message": "Invalid credentials"}, 401

        # Generate JWT access token
        access_token = create_access_token(identity=str(user.id))
        print(access_token)
        return {"access_token": access_token}, 200
