from models.base import db

class Warehouse(db.Model):
    __tablename__ = "warehouses"

    id = db.Column(db.Integer, primary_key=True)

    # Owner of the warehouse (logged-in user)
    user_id = db.Column(db.Integer, nullable=False, index=True)

    # Basic warehouse details
    name = db.Column(db.String(150), nullable=False)
    code = db.Column(db.String(50), unique=True)

    address = db.Column(db.Text, nullable=False)
    district = db.Column(db.String(100))
    state = db.Column(db.String(100))
    pincode = db.Column(db.String(10))

    # Capacity & status
    total_capacity = db.Column(db.Integer)      # e.g. total boxes / pallets
    available_capacity = db.Column(db.Integer)
    status = db.Column(db.String(50), default="active")

    # Contact person
    contact_name = db.Column(db.String(100))
    contact_mobile = db.Column(db.String(20))
    contact_email = db.Column(db.String(100))

    # Metadata
    created_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime)

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "name": self.name,
            "code": self.code,
            "address": self.address,
            "district": self.district,
            "state": self.state,
            "pincode": self.pincode,
            "total_capacity": self.total_capacity,
            "available_capacity": self.available_capacity,
            "status": self.status,
            "contact_name": self.contact_name,
            "contact_mobile": self.contact_mobile,
            "contact_email": self.contact_email,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
