import requests
from flask import Flask, jsonify

app = Flask(__name__)

# Get authentication token
def get_auth_token_for_delhivery():
    url = "https://ltl-clients-api.delhivery.com/ums/login"
    payload = {
        "username": "DVCEXPRESSLOGB2BC",
        "password": "Vinay@1234"
    }
    headers = {"Content-Type": "application/json"}
    
    response = requests.post(url, json=payload, headers=headers)
    
    if response.status_code == 200:
        return response.json().get("token")
    return None

# Get tracking details from Delhivery API
@app.route("/track_shipment/<tracking_number>", methods=["GET"])
def track_shipment_for_delhivery(tracking_number):
    token = get_auth_token_for_delhivery()
    if not token:
        return jsonify({"error": "Unable to authenticate"}), 403

    url = f"https://ltl-clients-api.delhivery.com/lrn/track?lrnum={tracking_number}"
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        return jsonify(response.json())
    else:
        return jsonify({"error": "Failed to fetch tracking details"}), 500
    


# Check serviceability
@app.route("/api/check_serviceability", methods=["POST"])
def check_serviceability():
    data = requests.json
    pincode = data.get("pincode")
    weight = data.get("weight", 0)
    token = get_auth_token_for_delhivery()
    if not token:
        return jsonify({"error": "Authentication failed"}), 403

    url = f"https://ltl-clients-api.delhivery.com/pincode-service/{pincode}"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers, params={"weight": weight})
    return jsonify(response.json())

# Estimate freight charges
@app.route("/api/freight_estimate", methods=["POST"])
def freight_estimate():
    data = requests.json
    payload = {
        "dimensions": data["dimensions"],
        "weight_g": data["weight_g"],
        "source_pin": data["source_pin"],
        "consignee_pin": data["consignee_pin"],
        "payment_mode": data["payment_mode"],
        "inv_amount": data["inv_amount"]
    }
    token = get_auth_token_for_delhivery()
    if not token:
        return jsonify({"error": "Authentication failed"}), 403

    url = "https://ltl-clients-api.delhivery.com/freight/estimate"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    response = requests.post(url, headers=headers, json=payload)
    return jsonify(response.json())

# Create warehouse
@app.route("/api/create_warehouse", methods=["POST"])
def create_warehouse():
    data = requests.json
    print(f"create_warehouse data: {data}")
    token = get_auth_token_for_delhivery()
    if not token:
        return jsonify({"error": "Authentication failed"}), 403

    url = "https://ltl-clients-api.delhivery.com/client-warehouse/create/"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    response = requests.post(url, headers=headers, json=data)
    return jsonify(response.json())

# Create pickup request
@app.route("/api/create_pickup", methods=["POST"])
def create_pickup():
    data = requests.json
    token = get_auth_token_for_delhivery()
    if not token:
        return jsonify({"error": "Authentication failed"}), 403

    url = "https://ltl-clients-api.delhivery.com/pickup_requests/"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    response = requests.post(url, headers=headers, json=data)
    return jsonify(response.json())

# Manifest order
@app.route("/api/manifest_order", methods=["POST"])
def manifest_order():
    data = requests.json
    token = get_auth_token_for_delhivery()
    if not token:
        return jsonify({"error": "Authentication failed"}), 403

    url = "https://ltl-clients-api.delhivery.com/manifest"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    response = requests.post(url, headers=headers, json=data)
    return jsonify(response.json())

if __name__ == "__main__":
    app.run(debug=True)
