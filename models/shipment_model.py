from models.base import db

class Shipment(db.Model):
    __tablename__ = "shipments"

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("orders.id"), nullable=False)

    courier_name = db.Column(db.String(100))
    reference_number = db.Column(db.String(100))
    tracking_id = db.Column(db.String(100))

    shipment_status = db.Column(db.String(50))
    current_location = db.Column(db.String(100))
    estimated_delivery_date = db.Column(db.DateTime)

    district = db.Column(db.String(100))
    pincode = db.Column(db.String(10))

    created_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime)

    def to_dict(self):
        return {
            "id": self.id,
            "order_id": self.order_id,
            "courier_name": self.courier_name,
            "tracking_id": self.tracking_id,
            "shipment_status": self.shipment_status,
            "current_location": self.current_location,
            "estimated_delivery_date": self.estimated_delivery_date.isoformat() if self.estimated_delivery_date else None,
        }
