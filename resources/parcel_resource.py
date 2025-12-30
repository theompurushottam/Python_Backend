import logging
import random
import string
import json
from models.base import db
from flask import jsonify, request,make_response
import requests
from flask_restful import Resource
from models.warehouse_model import Warehouse
from models.warehouse_model import create_warehouse 

from models.pickup_model import Pickup
from models.order_model import Order
from models.shipment_model import Shipment  # Assuming you have a shipment_model.py

from flask_jwt_extended import jwt_required, get_jwt_identity

logging.basicConfig(level=logging.DEBUG)

class ParcelResourceBase(Resource):
    """Base class for Parcel-related resources with common methods."""

    def get_auth_token(self):
        """Fetch authentication token from the Delhivery API."""
        url = "https://ltl-clients-api.delhivery.com/ums/login"
        payload = {
            "username": "DVCEXPRESSLOGB2BC",
            "password": "Vinay@1234"
        }
        headers = {"Content-Type": "application/json"}

        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            token = response.json().get("data", {}).get("jwt", None)
            logging.debug(f"Auth Token: {token}")
            return token
        logging.error("Failed to authenticate")
        return None


class CheckServiceabilityResource(ParcelResourceBase):
    def post(self):
        """Check serviceability for a given pincode and weight."""
        data = request.json
        pincode = data.get("pincode")
        weight = data.get("weight", 0)
        token = self.get_auth_token()

        if not token:
            return jsonify({"error": "Unable to authenticate"}), 403

        url = f"https://ltl-clients-api.delhivery.com/pincode-service/{pincode}"
        headers = {"Authorization": f"Bearer {token}"}
        params = {"weight": weight}

        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            return jsonify(response.json())
        logging.error(f"Serviceability check failed: {response.text}")
        return {"message": "Failed to check serviceability"}, response.status_code


class FreightEstimateResource(ParcelResourceBase):
    def post(self):
        """Get freight estimation for a shipment."""
        data = request.json
        logging.debug(f"Incoming payload for freight estimation: {data}")
        
        print('data')
        print(data)
        print(data.get("dimensions"))
        

        # Validate payload before proceeding
        if not data.get("dimensions"):
            return {"message": "Validation Error: 'dimensions' field is required"}, 401
        for dimension in data["dimensions"]:
            print('dimension....')
            print(dimension)
            if not all(k in dimension for k in ("length_cm", "width_cm", "height_cm")):
                return {
                    "message": "Validation Error: 'length_cm', 'width_cm', and 'height_cm' are required in dimensions"
                }, 402

        token = self.get_auth_token()
        if not token:
            return jsonify({"error": "Unable to authenticate"}), 403

        url = "https://ltl-clients-api.delhivery.com/freight/estimate"
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            return jsonify(response.json())
        logging.error(f"Freight estimation failed: {response.text}")
        return {"message": "Failed to estimate freight"}, response.status_code



class CreateWarehouseResource(ParcelResourceBase):
    @jwt_required()  # ✅ Ensure JWT is required before extracting user identity
    def post(self):
        """Create a new warehouse via Delhivery API and save it in the database if successful."""
        data = request.json
        token = self.get_auth_token()
        print(f"create_warehouse data: {data}")

        if not token:
            return jsonify({"error": "Unable to authenticate"}), 403

        # ✅ Extract `user_id` from JWT token after verifying authentication
        user_id = get_jwt_identity()
        if not user_id:
            return jsonify({"error": "User ID not found in token"}), 403

        # Call external API (Delhivery)
        url = "https://ltl-clients-api.delhivery.com/client-warehouse/create/"
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        response = requests.post(url, headers=headers, json=data)

        if response.status_code == 200:
            delhivery_response = response.json()

            # Extract necessary fields for local storage
            address_details = data.get("address_details", {})
            warehouse_data = {
                "name": data.get("name"),
                "pin_code": data.get("pin_code"),
                "city": data.get("city"),
                "state": data.get("state"),
                "country": data.get("country"),
                "address": address_details.get("address", ""),
                "contact_person": address_details.get("contact_person", ""),
                "phone_number": address_details.get("phone_number", ""),
                "email": address_details.get("email", ""),
            }

            # ✅ Pass `user_id` when creating the warehouse
            warehouse_response, status_code = create_warehouse(warehouse_data, user_id)

            return jsonify({
                "success": True,
                "message": "Warehouse created successfully",
                "delhivery_response": delhivery_response,
                "warehouse_response": warehouse_response
            }), status_code
        else:
            # Log the error message from Delhivery's response
            error_message = response.json().get('error', {}).get('message', 'Unknown error')
            logging.error(f"Warehouse creation failed: {error_message}")
            print(f"Warehouse creation failed: {error_message}")
            status_code = response.status_code 
            logging.error(f"Warehouse creation failed: {status_code}")
            if status_code ==400:
                return jsonify({"message": f"Failed to create warehouse: Warehouse with same name already exist"})
            else:
                return jsonify({"message": f"Failed to create warehouse: Unknow Error"})




class CreatePickupResource(ParcelResourceBase):
    @jwt_required()
    def post(self):
        """Create a new shipment and Pickup via Delhivery API and save it in the database if successful."""
        data = request.json
        token = self.get_auth_token()
        print(f"create_shipment and pickup data: {data}")

        if not token:
            return jsonify({"error": "Unable to authenticate"}), 403

        user_id = get_jwt_identity()
        if not user_id:
            return jsonify({"error": "User ID not found in token"}), 403

       # url = "https://ltl-clients-api.delhivery.com/pickup_requests/"
        url = "https://run.mocky.io/v3/c9787b2b-806a-4014-aaa2-105bbb5f46e6"
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

        # Construct the Delhivery request payload as per the requirements
        pickup_data = data.get('pickupdata')
        shipment_data = data.get('shipmentdata')
        
        delhivery_payload = {
            "client_warehouse": pickup_data.get("client_warehouse"),
            "pickup_date": pickup_data.get("pickup_date"),
            "start_time": pickup_data.get("pickup_time")+":00",
            "expected_package_count": pickup_data.get("package_count")
        }

        response = requests.post(url, headers=headers, json=delhivery_payload)
        print(f"create pick up response: {response.json()}")
        if response.status_code == 200:
            print(f"create_shipment and pickup data: {data}")
            try:
                delhivery_response_data = response.json()
                external_pickup_id = delhivery_response_data.get('data', {}).get('pickup_id') 
                order_data = {
                    "user_id": user_id,
                    "source_address": shipment_data.get('source_address') if shipment_data.get('source_address') else "TEST",
                    "destination_address": shipment_data.get('destination_address'),
                    "item_description": shipment_data.get('item_description'),
                    "weight": float(shipment_data.get('weight')) if shipment_data.get('weight') else 10,
                    "dimensions": shipment_data.get('dimensions') if shipment_data.get('dimensions') else "10",
                    "order_status": "Pending",
                    "payment_status": "Pending",
                    "primary_contact_name": shipment_data.get('primary_contact_name'),
                    "primary_contact_mobile": shipment_data.get('primary_contact_mobile'),
                    "primary_contact_email": shipment_data.get('primary_contact_email'),
                    "secondary_contact_name": shipment_data.get('secondary_contact_name'),
                    "secondary_contact_mobile": shipment_data.get('secondary_contact_mobile'),
                    "secondary_contact_email": shipment_data.get('secondary_contact_email'),
                    "district": shipment_data.get('district'),
                    "pincode": shipment_data.get('pincode'),
                }
                print(f"order_data: {order_data}")
                order_result = Order.create_order(order_data, user_id)
                if not order_result.get('success'):
                    db.session.rollback()
                    return jsonify(order_result), order_result.get('status_code') if 'status_code' in order_result else 500

                order_id = order_result['order_id']
                print(f"order_id: {order_id}")

                # 2. Create Shipment
                shipment_data['order_id'] = order_id
                shipment_data['tracking_id'] = generate_tracking_id()
                shipment_data['courier_name'] = shipment_data.get('courier_name') or "Delhiwery"
                shipment_data['shipment_status'] = "Pending"
                print(f"shipment_data: {shipment_data}")
                shipment_result = Shipment.create_shipment(shipment_data, user_id)
                if not shipment_result.get('success'):
                    db.session.rollback()
                    return jsonify(shipment_result), shipment_result.get('status_code') if 'status_code' in shipment_result else 500
                shipment_id = shipment_result['shipment_id']

                # 3. Create Pickup
                pickup_data['shipment_id'] = shipment_id
                pickup_data['warehouse_id'] = pickup_data.get('client_warehouse_id')
                pickup_data["external_pickup_id"]=external_pickup_id
                pickup_result = Pickup.create_pickup(pickup_data, user_id)
                if not pickup_result.get('success'):
                    db.session.rollback()
                    print(f"pickup_result: {pickup_result}")
                    return {
                        "success": False,
                        "message": pickup_result.get('message'),
                        "status_code": pickup_result.get('status_code') if 'status_code' in pickup_result else 500
                    }

                db.session.commit()     
                print(f"pickup_result: {pickup_result}")
                print(f"pickup_result: {shipment_result}")           
                print(f"pickup_result: {order_result}")           
                return {
                    "success": True,
                    "message": "Shipment, order, and pickup created successfully",
                    "pickup_result": pickup_result,
                    "shipment_result": shipment_result,
                    "order_result": order_result
                }
                #return {"success": True,"message": "Shipment, order, and pickup created successfully", "shipment_id": shipment_id, "order_id": order_id, "pickup_id": pickup_data.get('external_pickup_id')}
            except Exception as e:
                db.session.rollback()
                print(f"Error in CreatePickupResource: {e}")
                return jsonify({"message": str(e)}), 500
        else:
            error_message = response.json().get('error', {}).get('message', 'Unknown error')
            logging.error(f"Warehouse creation failed: {error_message}")
            print(f"Pickup creation failed: {error_message}")
            status_code = response.status_code
            logging.error(f"Pickup creation failed: {status_code}")
            return jsonify({"message": f"Failed to create Pickup. Delhivery API Error: {error_message}"})


class ManifestOrderResource(ParcelResourceBase):
    def post(self):
        """Manifest an order."""
        data = request.json
        token = self.get_auth_token()

        if not token:
            return jsonify({"error": "Unable to authenticate"}), 403

        url = "https://ltl-clients-api.delhivery.com/manifest"
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            return jsonify(response.json())
        logging.error(f"Order manifestation failed: {response.text}")
        return {"message": "Failed to manifest order"}, response.status_code
class ManifestOrderResource(ParcelResourceBase):
    @jwt_required()
    def post(self):
        """Manifest an order via Delhivery API and save the manifest details in the database if successful."""
        data = request.json
        token = self.get_auth_token()
        print(f"manifest_order data: {data}")

        if not token:
            return jsonify({"error": "Unable to authenticate"}), 403

        user_id = get_jwt_identity()
        if not user_id:
            return jsonify({"error": "User ID not found in token"}), 403

        url = "https://ltl-clients-api.delhivery.com/manifest"
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}


        # Prepare the multipart/form-data payload
        files = {}  # For file uploads, if needed
        payload = {
            "lrn": data.get("lrn"),
            "pickup_location_name": data.get("pickup_location_name"),
            "pickup_location_id": data.get("pickup_location_id"),
            "payment_mode": data.get("payment_mode"),
            "weight": data.get("weight"),
            "dropoff_store_code": data.get("dropoff_store_code"),
            "dropoff_location": data.get("dropoff_location"),
            "shipment_details": json.dumps(data.get("shipment_details")),
            "dimensions": json.dumps(data.get("dimensions")),
            "invoices": json.dumps(data.get("invoices")),
            "freight_mode": data.get("freight_mode"),
            "fm_pickup": data.get("fm_pickup"),
            "billing_address": json.dumps(data.get("billing_address")),
        }

        # Conditionally add cod_amount
        if data.get("payment_mode") == "cod":
            payload["cod_amount"] = data.get("cod_amount")

        # Conditionally add return_address
        if data.get("dropoff_store_code") or data.get("dropoff_location"):
            payload["return_address"] = json.dumps(data.get("return_address"))

        #Conditionally add rov_insurance
        if data.get("rov_insurance") is not None:
            payload["rov_insurance"] = data.get("rov_insurance")

        #Conditionally add enable_paperless_movement
        if data.get("enable_paperless_movement") is not None:
            payload["enable_paperless_movement"] = data.get("enable_paperless_movement")

        #Conditionally add callback
        if data.get("callback") is not None:
            payload["callback"] = json.dumps(data.get("callback"))

        # Add doc_file and doc_data conditionally (Retail client)
        if data.get("is_retail_client"):  # Add is_retail_client to your data
            if data.get("doc_file"):
                files["doc_file"] = data.get("doc_file")  # Handle file upload
                payload["doc_data"] = json.dumps(data.get("doc_data"))
            else:
                return jsonify({"message": "doc_file is required for retail clients"}), 400

        response = requests.post(url, headers=headers, data=payload, files=files)

        if response.status_code == 202:  # Assuming 202 for success
            delhivery_response = response.json()

            # Extract necessary fields for local storage
            manifest_data = {
                "user_id": user_id,
                "job_id": delhivery_response.get("job_id"),
                "request_id": delhivery_response.get("request_id"),
                # Add other relevant fields from the Delhivery response
            }

            # Save manifest data to the database
            #try:
                #manifest_response, status_code = Manifest.create_manifest(manifest_data, user_id)
            #except Exception as e:
             #   logging.error(f"Error saving manifest to database: {e}")
             #   return jsonify({"message": "Error saving manifest to database"}), 500

            return jsonify({
                "success": True,
                "message": "Order manifested successfully",
                "delhivery_response": delhivery_response,
                "manifest_response": manifest_data,
            }), status_code

        else:
            # Log the error message from Delhivery's response
            error_message = response.json().get('error', {}).get('message', 'Unknown error')
            logging.error(f"Manifest order failed: {error_message}")
            print(f"Manifest order failed: {error_message}")
            status_code = response.status_code
            logging.error(f"Manifest order failed: {status_code}")
            return jsonify({"message": f"Failed to manifest order: {error_message}"}), status_code
class CancelPickupResource(ParcelResourceBase):
    def post(self):
        """Cancel a pickup request."""
        data = request.json
        token = self.get_auth_token()
        if not token:
            return jsonify({"error": "Unable to authenticate"}), 403

        url = "https://ltl-clients-api.delhivery.com/pickup/cancel"
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            return jsonify(response.json())
        logging.error(f"Cancel pickup failed: {response.text}")
        return {"message": "Failed to cancel pickup"}, response.status_code


class OrderManifestationStatusResource(ParcelResourceBase):
    def get(self, order_id):
        """Check order manifestation status."""
        token = self.get_auth_token()
        if not token:
            return jsonify({"error": "Unable to authenticate"}), 403

        url = f"https://ltl-clients-api.delhivery.com/manifest/status?order_id={order_id}"
        headers = {"Authorization": f"Bearer {token}"}

        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return jsonify(response.json())
        logging.error(f"Order manifestation status failed: {response.text}")
        return {"message": "Failed to fetch manifestation status"}, response.status_code


class EditLRResource(ParcelResourceBase):
    def post(self):
        """Edit LR details."""
        data = request.json
        token = self.get_auth_token()
        if not token:
            return jsonify({"error": "Unable to authenticate"}), 403

        url = "https://ltl-clients-api.delhivery.com/lr/edit"
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            return jsonify(response.json())
        logging.error(f"Edit LR failed: {response.text}")
        return {"message": "Failed to edit LR"}, response.status_code


class ShippingLabelResource(ParcelResourceBase):
    def post(self):
        """Get shipping label URLs."""
        data = request.json
        token = self.get_auth_token()
        if not token:
            return jsonify({"error": "Unable to authenticate"}), 403

        url = "https://ltl-clients-api.delhivery.com/shipping-label"
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            return jsonify(response.json())
        logging.error(f"Fetching shipping labels failed: {response.text}")
        return {"message": "Failed to fetch shipping labels"}, response.status_code


class TrackShipmentResource(ParcelResourceBase):
    def get(self, tracking_number):
        """Track a shipment."""
        token = self.get_auth_token()
        if not token:
            return jsonify({"error": "Unable to authenticate"}), 403

        url = f"https://ltl-clients-api.delhivery.com/lrn/track?lrnum={tracking_number}"
        headers = {"Authorization": f"Bearer {token}"}

        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return jsonify(response.json())
        logging.error(f"Tracking shipment failed: {response.text}")
        return {"message": "Failed to track shipment"}, response.status_code
class EditLRStatusResource(ParcelResourceBase):
    def post(self):
        """Edit LR status."""
        data = request.json
        token = self.get_auth_token()
        if not token:
            return jsonify({"error": "Unable to authenticate"}), 403

        url = "https://ltl-clients-api.delhivery.com/lr/edit-status"
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            return jsonify(response.json())
        logging.error(f"Edit LR status failed: {response.text}")
        return {"message": "Failed to edit LR status"}, response.status_code
class GetLabelURLsResource(ParcelResourceBase):
    def get(self):
        """Get label URLs."""
        token = self.get_auth_token()
        if not token:
            return jsonify({"error": "Unable to authenticate"}), 403

        url = "https://ltl-clients-api.delhivery.com/labels/urls"
        headers = {"Authorization": f"Bearer {token}"}

        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return jsonify(response.json())
        logging.error(f"Fetching label URLs failed: {response.text}")
        return {"message": "Failed to fetch label URLs"}, response.status_code
class GenerateDocumentsResource(ParcelResourceBase):
    def post(self):
        """Generate documents for a shipment."""
        data = request.json
        token = self.get_auth_token()
        if not token:
            return jsonify({"error": "Unable to authenticate"}), 403

        url = "https://ltl-clients-api.delhivery.com/documents/generate"
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            return jsonify(response.json())
        logging.error(f"Document generation failed: {response.text}")
        return {"message": "Failed to generate documents"}, response.status_code
class GenerateDocumentsStatusResource(ParcelResourceBase):
    def get(self, request_id):
        """Get the status of generated documents."""
        token = self.get_auth_token()
        if not token:
            return jsonify({"error": "Unable to authenticate"}), 403

        url = f"https://ltl-clients-api.delhivery.com/documents/status?request_id={request_id}"
        headers = {"Authorization": f"Bearer {token}"}

        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return jsonify(response.json())
        logging.error(f"Document status fetch failed: {response.text}")
        return {"message": "Failed to fetch document status"}, response.status_code
class PrintLRCopyResource(ParcelResourceBase):
    def post(self):
        """Print LR copy."""
        data = request.json
        print(data)
        token = self.get_auth_token()
        print('token')
        print(token)
        if not token:
            return jsonify({"error": "Unable to authenticate"}), 403
        
        url = "https://ltl-clients-api.delhivery.com/lr/print"
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            return jsonify(response.json())
        logging.error(f"Print LR copy failed: {response.text}")
        return {"message": "Failed to print LR copy"}, response.status_code
class CancelShipmentResource(ParcelResourceBase):
    def post(self):
        """Cancel a shipment."""
        data = request.json
        token = self.get_auth_token()
        if not token:
            return jsonify({"error": "Unable to authenticate"}), 403

        url = "https://ltl-clients-api.delhivery.com/shipment/cancel"
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            return jsonify(response.json())
        logging.error(f"Cancel shipment failed: {response.text}")
        return {"message": "Failed to cancel shipment"}, response.status_code
class FreightChargesResource(ParcelResourceBase):
    def post(self):
        """Fetch freight charges."""
        data = request.json
        token = self.get_auth_token()
        if not token:
            return jsonify({"error": "Unable to authenticate"}), 403

        url = "https://ltl-clients-api.delhivery.com/freight/charges"
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            return jsonify(response.json())
        logging.error(f"Fetching freight charges failed: {response.text}")
        return {"message": "Failed to fetch freight charges"}, response.status_code
class DocumentDownloadResource(ParcelResourceBase):
    def get(self, document_id):
        """Download document."""
        token = self.get_auth_token()
        if not token:
            return jsonify({"error": "Unable to authenticate"}), 403

        url = f"https://ltl-clients-api.delhivery.com/documents/download?document_id={document_id}"
        headers = {"Authorization": f"Bearer {token}"}

        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return jsonify(response.json())
        logging.error(f"Document download failed: {response.text}")
        return {"message": "Failed to download document"}, response.status_code
    


def generate_tracking_id():
    """Generates a tracking ID in the format 'DEL' + 6 random digits."""

    digits = ''.join(random.choices(string.digits, k=6))  # Generate 6 random digits
    return 'DEL' + digits
