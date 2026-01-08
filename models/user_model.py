from models.base import db
from datetime import datetime


class User(db.Model):
    __tablename__ = "register_users"

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    
    business_name = db.Column(db.String(200), nullable=False)
    store_type = db.Column(db.String(50), nullable=False)

    phone = db.Column(db.String(20), nullable=False)
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
            "full_name": self.full_name,
            "email": self.email,
            "business_name": self.business_name,
            "store_type": self.store_type,
            "phone": self.phone,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


# ===============================
# Updated helper function
# ===============================

def create_user(
    full_name: str,
    email: str,
    business_name: str,
    store_type: str,
    phone: str,
    password_hash: str
) -> bool:
    """
    Create a new user with all details.
    Returns True if created, False if user already exists.
    """
    print("1")
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return False

    user = User(
        full_name=full_name,
        email=email,
        business_name=business_name,
        store_type=store_type,
        phone=phone,
        password_hash=password_hash,
    )

    print("2")
    db.session.add(user)
    db.session.commit()
    return True


# Keep get_user_by_email as is
def get_user_by_email(email: str):
    return User.query.filter_by(email=email).first()