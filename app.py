from flask import Flask
from flask_restful import Api
from flask_cors import CORS
from flask_jwt_extended import JWTManager

from models.base import db

# IMPORTANT: import models so SQLAlchemy registers them
from models.user_model import User
from models.order_model import Order
from models.shipment_model import Shipment
from models.payment_model import Payment
from models.subscription_model import Subscription
from models.notification_model import Notification
from models.warehouse_model import Warehouse

from resources.user_resource import RegisterUser, LoginUser
from resources.dashboard_resource import (
    Dashboard,
    OrdersResource,
    ShipmentsResource,
    PaymentsResource,
    SubscriptionsResource,
    NotificationsResource,
    WarehouseResource,
)

app = Flask(__name__)

# CONFIG
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["JWT_SECRET_KEY"] = "super-secret-key"


# INIT
db.init_app(app)
jwt = JWTManager(app)
api = Api(app)
CORS(app)

# ROUTES
api.add_resource(RegisterUser, "/api/register")
api.add_resource(LoginUser, "/api/login")
api.add_resource(Dashboard, "/api/dashboard")
api.add_resource(OrdersResource, "/api/orders")
api.add_resource(ShipmentsResource, "/api/shipments")
api.add_resource(PaymentsResource, "/api/payments")
api.add_resource(SubscriptionsResource, "/api/subscriptions")
api.add_resource(NotificationsResource, "/api/notifications")
api.add_resource(WarehouseResource, "/api/warehouses")

# CREATE TABLES
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000,debug=True)
