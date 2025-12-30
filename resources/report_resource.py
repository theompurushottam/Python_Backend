from flask_restful import Resource
from flask import jsonify
from models.order_model import Order
from models.shipment_model import Shipment
from models.base import db
from sqlalchemy import func
from datetime import datetime, timedelta

class ReportResource(Resource):
    def get(self):
        try:
            # Current date and date 1 month ago
            current_date = datetime.utcnow()
            one_month_ago = current_date - timedelta(days=30)
            print('current_date')
            print(current_date)

            # Total Orders Count in the last 30 days
            total_orders_count = db.session.query(func.count(Order.id)).filter(Order.order_date >= one_month_ago).scalar()

            # Total Shipments Count in the last 30 days
            total_shipments_count = db.session.query(func.count(Shipment.id)).filter(Shipment.created_at >= one_month_ago).scalar()

            # Orders Status Distribution
            orders_status = db.session.query(Order.order_status, func.count(Order.id)).filter(Order.order_date >= one_month_ago).group_by(Order.order_status).all()

            # Shipments Status Distribution
            shipments_status = db.session.query(Shipment.shipment_status, func.count(Shipment.id)).filter(Shipment.created_at >= one_month_ago).group_by(Shipment.shipment_status).all()

            # Revenue Estimate (Total weight in last 30 days as a simple example)
            total_weight = db.session.query(func.sum(Order.weight)).filter(Order.order_date >= one_month_ago).scalar()

            # Top 5 Districts by Orders
            top_districts = db.session.query(Order.destination_address, func.count(Order.id).label('order_count')).filter(Order.order_date >= one_month_ago).group_by(Order.destination_address).order_by(func.count(Order.id).desc()).limit(5).all()

            # Convert all results to JSON-serializable format
            orders_status = [{"order_status": status, "count": count} for status, count in orders_status]
            shipments_status = [{"shipment_status": status, "count": count} for status, count in shipments_status]
            top_districts = [{"district": district, "order_count": order_count} for district, order_count in top_districts]

            # Print debug information
            print(total_orders_count)
            print(total_shipments_count)
            print(orders_status)
            print(shipments_status)
            print(total_weight)
            print(top_districts)

            return jsonify({
                'total_orders_count': total_orders_count,
                'total_shipments_count': total_shipments_count,
                'orders_status': orders_status,
                'shipments_status': shipments_status,
                'total_weight': total_weight,
                'top_districts': top_districts
            })

        except Exception as e:
            return {'message': f'Error generating reports: {str(e)}'}, 500
