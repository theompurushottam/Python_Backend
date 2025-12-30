from models.base import db

class Payment(db.Model):
    __tablename__ = "payments"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)

    order_id = db.Column(db.Integer, db.ForeignKey("orders.id"))

    amount = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(10), default="INR")

    payment_method = db.Column(db.String(50))
    payment_status = db.Column(db.String(50))
    transaction_id = db.Column(db.String(100))

    created_at = db.Column(db.DateTime)

    def to_dict(self):
        return {
            "id": self.id,
            "order_id": self.order_id,
            "amount": self.amount,
            "currency": self.currency,
            "payment_method": self.payment_method,
            "payment_status": self.payment_status,
            "transaction_id": self.transaction_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
