from models.base import db

class Order(db.Model):
    __tablename__ = "orders"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)

    source_address = db.Column(db.Text)
    destination_address = db.Column(db.Text)

    district = db.Column(db.String(100))
    pincode = db.Column(db.String(10))

    item_description = db.Column(db.Text)
    weight = db.Column(db.Float)
    dimensions = db.Column(db.String(100))
    nember_of_items = db.Column(db.Integer)

    order_date = db.Column(db.DateTime)
    order_status = db.Column(db.String(50))
    payment_status = db.Column(db.String(50))

    primary_contact_name = db.Column(db.String(100))
    primary_contact_mobile = db.Column(db.String(20))
    primary_contact_email = db.Column(db.String(100))

    secondary_contact_name = db.Column(db.String(100))
    secondary_contact_mobile = db.Column(db.String(20))
    secondary_contact_email = db.Column(db.String(100))

    created_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime)

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "source_address": self.source_address,
            "destination_address": self.destination_address,
            "district": self.district,
            "pincode": self.pincode,
            "item_description": self.item_description,
            "weight": self.weight,
            "dimensions": self.dimensions,
            "nember_of_items": self.nember_of_items,
            "order_date": self.order_date.isoformat() if self.order_date else None,
            "order_status": self.order_status,
            "payment_status": self.payment_status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
