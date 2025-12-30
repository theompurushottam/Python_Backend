from werkzeug.security import generate_password_hash
from app import app
from models.base import db
from models.user_model import User

with app.app_context():
    email = "priyanshneel@gmail.com"

    user = User.query.filter_by(email=email).first()
    if user:
        print("User already exists:", user.email)
    else:
        user = User(
            name="Priyansh",
            email=email,
            password_hash=generate_password_hash("munmun1973")
        )
        db.session.add(user)
        db.session.commit()
        print("User created successfully")
