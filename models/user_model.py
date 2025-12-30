from models.base import db
from datetime import datetime

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)

    password_hash = db.Column(db.String(255), nullable=False)

    is_active = db.Column(db.Boolean, default=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


# ===============================
# Helper functions used by APIs
# ===============================

def create_user(name: str, email: str, password_hash: str) -> bool:
    """
    Create a new user.
    Returns True if created, False if user already exists.
    """
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return False

    user = User(
        name=name,
        email=email,
        password_hash=password_hash,
    )

    db.session.add(user)
    db.session.commit()
    return True


def get_user_by_email(email: str):
    """
    Fetch user by email.
    Returns User object or None.
    """
    return User.query.filter_by(email=email).first()
