from flask_restful import Resource
from flask import jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.order_model import Order
from models.shipment_model import Shipment
from models.payment_model import Payment
from models.subscription_model import Subscription
from models.notification_model import Notification
from models.warehouse_model import Warehouse

class Dashboard(Resource):
    @jwt_required()
    def get(self):
        """
        Fetch all dashboard data for the logged-in user.
        """
        try:
            user_id = get_jwt_identity()
            if not user_id:
                return {"error": "Invalid or missing user ID in token"}, 401

            # Fetch all data for the user
            orders = Order.query.filter_by(user_id=user_id).all()
            shipments = Shipment.query.filter(Shipment.order_id.in_([o.id for o in orders])).all()
            payments = Payment.query.filter_by(user_id=user_id).all()
            subscriptions = Subscription.query.filter_by(user_id=user_id).all()
            notifications = Notification.query.filter_by(user_id=user_id).all()

            # Construct response
            return jsonify({
                "orders": [order.to_dict() for order in orders],
                "shipments": [shipment.to_dict() for shipment in shipments],
                "payments": [payment.to_dict() for payment in payments],
                "subscriptions": [subscription.to_dict() for subscription in subscriptions],
                "notifications": [notification.to_dict() for notification in notifications],
            })
        except Exception as e:
            return {"error": str(e)}, 500


class OrdersResource(Resource):
    @jwt_required()
    def get(self):
        """
        Fetch orders for the logged-in user.
        """
        try:
            user_id = get_jwt_identity()
            if not user_id:
                return {"error": "Invalid or missing user ID in token"}, 401

            orders = Order.query.filter_by(user_id=user_id).all()
            return jsonify([order.to_dict() for order in orders])
        except Exception as e:
            return {"error": str(e)}, 500


class ShipmentsResource(Resource):
    @jwt_required()
    def get(self):
        """
        Fetch shipments for the logged-in user.
        """
        try:
            user_id = get_jwt_identity()
            if not user_id:
                return {"error": "Invalid or missing user ID in token"}, 401

            shipments = Shipment.query.filter(Shipment.order_id.in_(
                [o.id for o in Order.query.filter_by(user_id=user_id).all()]
            )).all()
            return jsonify([shipment.to_dict() for shipment in shipments])
        except Exception as e:
            return {"error": str(e)}, 500


class PaymentsResource(Resource):
    @jwt_required()
    def get(self):
        """
        Fetch payments for the logged-in user.
        """
        try:
            user_id = get_jwt_identity()
            if not user_id:
                return {"error": "Invalid or missing user ID in token"}, 401

            payments = Payment.query.filter_by(user_id=user_id).all()
            return jsonify([payment.to_dict() for payment in payments])
        except Exception as e:
            return {"error": str(e)}, 500


class SubscriptionsResource(Resource):
    @jwt_required()
    def get(self):
        """
        Fetch subscriptions for the logged-in user.
        """
        try:
            user_id = get_jwt_identity()
            if not user_id:
                return {"error": "Invalid or missing user ID in token"}, 401

            subscriptions = Subscription.query.filter_by(user_id=user_id).all()
            return jsonify([subscription.to_dict() for subscription in subscriptions])
        except Exception as e:
            return {"error": str(e)}, 500


class NotificationsResource(Resource):
    @jwt_required()
    def get(self):
        """
        Fetch notifications for the logged-in user.
        """
        try:
            user_id = get_jwt_identity()
            if not user_id:
                return {"error": "Invalid or missing user ID in token"}, 401

            notifications = Notification.query.filter_by(user_id=user_id).all()
            return jsonify([notification.to_dict() for notification in notifications])
        except Exception as e:
            return {"error": str(e)}, 500

class WarehouseResource(Resource):
    @jwt_required()
    def get(self):
        """
        Fetch subscriptions for the logged-in user.
        """
        try:
            user_id = get_jwt_identity()
            if not user_id:
                return {"error": "Invalid or missing user ID in token"}, 401

            warehouse = Warehouse.query.filter_by(user_id=user_id).all()
            return jsonify([subscription.to_dict() for subscription in warehouse])
        except Exception as e:
            return {"error": str(e)}, 500       

        
