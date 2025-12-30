from models.base import db

class Subscription(db.Model):
    __tablename__ = "subscriptions"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)

    plan_name = db.Column(db.String(50))
    price = db.Column(db.Float)

    start_date = db.Column(db.DateTime)
    end_date = db.Column(db.DateTime)

    status = db.Column(db.String(50))

    def to_dict(self):
        return {
            "id": self.id,
            "plan_name": self.plan_name,
            "price": self.price,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "status": self.status,
        }
