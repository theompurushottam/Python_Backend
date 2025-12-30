import logging
from flask import jsonify
import requests
from flask_restful import Resource

logging.basicConfig(level=logging.DEBUG)

class TrackingResource(Resource):
    def get(self, tracking_number):
        # Get authentication token
        print('Sunny')
       
        token = self.get_auth_token()
       
        if not token:
            return jsonify({"error": "Unable to authenticate"}), 403
        
        # Fetch tracking details using the token
        tracking_data = self.get_tracking_details(token, tracking_number)
        print('tracking_data')
        print(tracking_data)
        if tracking_data is not None:
            print('tracking_data11')
            logging.debug(f"Tracking Data: {tracking_data}")  # Log the tracking data
            return jsonify(tracking_data)
        else:
            print('tracking_data22')
            return {"message": "Data not found"}, 400

    def get_auth_token(self):
        url = "https://ltl-clients-api.delhivery.com/ums/login"
        payload = {
            "username": "DVCEXPRESSLOGB2BC",
            "password": "Vinay@1234"
        }
        headers = {"Content-Type": "application/json"}
        
        response = requests.post(url, json=payload, headers=headers)
       
        
        if response.status_code == 200:
            token = response.json().get("data", {}).get("jwt", None)
            logging.debug(f"Auth Token: {token}")  # Log the token
            return token
        return None

    def get_tracking_details(self, token, tracking_number):
        url = f"https://ltl-clients-api.delhivery.com/lrn/track?lrnum={tracking_number}"
        headers = {"Authorization": f"Bearer {token}"}
        
        response = requests.get(url, headers=headers)
        print(response.status_code)
        print(response.json())
        if response.status_code == 200:
            tracking_data = response.json()  # This returns the JSON response as a dictionary
            logging.debug(f"Received Tracking Data: {tracking_data}")  # Log the tracking data
            return tracking_data
        return None
