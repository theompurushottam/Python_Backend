from flask import request, jsonify
from flask_restful import Resource, reqparse
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token
from models.user_model import create_user, get_user_by_email

class RegisterUser(Resource):
    def post(self):
        print("=== BACKEND: Received request ===")  
        data = request.get_json()
        print("=== BACKEND: Received data ===", data) 

        full_name = data.get("fullName") 
        email = data.get("email")
        business_name = data.get("businessName")
        store_type = data.get("storeType")
        phone = data.get("phone")
        password = data.get("password")

        if not (full_name and email and business_name and store_type and phone and password):
            return {"message": "All fields are required"}, 400

        password_hash = generate_password_hash(password)

        if create_user(
            full_name=full_name,
            email=email,
            business_name=business_name,
            store_type=store_type,
            phone=phone,
            password_hash=password_hash
        ):
            return {"message": "User registered successfully"}, 201
        return {"message": "User already exists"}, 409
    


class LoginUser(Resource):
    def post(self):
        # Parse the request data
        parser = reqparse.RequestParser()
        parser.add_argument("email", required=True, help="Email is required")
        parser.add_argument("password", required=True, help="Password is required")
        args = parser.parse_args()

        print(f"Login attempt for email: {args['email']}")
        
        user = get_user_by_email(args["email"])
        
        # Debug print
        print(f"User found: {user is not None}")
        if user:
            print(f"User ID: {user.id}, Email: {user.email}")
            print(f"Password hash in DB: {user.password_hash[:50]}...")
        
        if not user:
            print("User not found")
            return {"message": "Invalid credentials"}, 401

        password_valid = check_password_hash(user.password_hash, args["password"])
        print(f"Password valid: {password_valid}")
        
        if not password_valid:
            print("Password incorrect")
            return {"message": "Invalid credentials"}, 401

        # Generate JWT access token
        access_token = create_access_token(identity=str(user.id))
        print(f"Generated token: {access_token[:50]}...")
        
        return {
            "message": "Login successful",
            "access_token": access_token,
            "user": user.to_dict() 
        }, 200
