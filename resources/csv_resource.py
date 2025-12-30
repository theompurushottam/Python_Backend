import pandas as pd
from flask import request, jsonify
from flask_restful import Resource
from models.order_model import Order
from models.shipment_model import Shipment
from models.base import db
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime

class CSVUploadResource(Resource):
    @jwt_required()
    def post(self):
        try:
            current_user = get_jwt_identity() 
            # Get CSV data from the request body
            data = request.json.get('data')  # Ensure the payload has 'data' field
            
            # Validate data
            if not data or len(data) == 0:
                return {'message': 'No CSV data provided or the data is empty'}, 400
            
            # Convert the received data into a pandas DataFrame
            df = pd.DataFrame(data)
            print(df)
            
            # Debugging: Print columns before cleaning
            print("Columns before cleaning:", df.columns.tolist())
            
            # Clean column names by stripping spaces and unwanted characters (e.g., remove quotes, trim extra spaces)
            df.columns = df.columns.str.strip().str.replace("'", "").str.replace('"', "").str.replace(' ', '_')
            
            # Debugging: Print columns after cleaning
            print("Columns after cleaning:", df.columns.tolist())
            
            # Check if all necessary columns are present
            required_columns = [
                'Sr No', 'District Name', '1st level Contcat Name/ DM Name', '1st level Contcat No/ DM contcat no', 
                '2nd level Contcat Name', '2nd level Contcat No', 'Address for Delivery', 'Pincode', 'Date', 
                'Courier', 'Parcel', 'No Of Box', 'Ref', 'Awb', 'Status'
            ]
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            #if missing_columns:
            #    return {'message': f'Missing required columns: {", ".join(missing_columns)}'}, 400
            print(f"Missing columns: {missing_columns}")  # Debugging

            # Process each row from the CSV data
            count = 0
            success_count = 0
            failure_count = 0
            for _, row in df.iterrows():
                # Log the row data to ensure it's correctly parsed
                print(f"Processing row: {row}")
                print(f"count row: {count}")
                
                # Increment the count variable
               
                count += 1
                try: 
                    order_date = pd.to_datetime(row['order_date'], errors='raise')
                    estimated_delivery_date = pd.to_datetime(row['estimated_delivery_date'], errors='raise')
                    current_datetime = datetime.utcnow()
                    
                    
                    
                    order_data = {
                        
                        'user_id': current_user,
                        'source_address' : row['source_address'],
                        'destination_address' : row['destination_address'],
                        'district' : row['district'],
                        'pincode' : row['pincode'],
                        'item_description' : row['item_description'],
                        'weight' : row['weight'],
                        'dimensions' : row['dimensions'],
                        'nember_of_items' : row['nember_of_items'],
                        'order_date' :order_date,
                        'order_status' : row['order_status'],
                        'payment_status' : row['payment_status'],
                        'primary_contact_name' : row['primary_contact_name'],
                        'primary_contact_mobile' : row['primary_contact_number'],
                        'primary_contact_email' : row['primary_contact_email'],
                        'secondary_contact_name' : row['secondary_contact_name'],
                        'secondary_contact_mobile' : row['secondary_contact_number'],
                        'secondary_contact_email' : row['secondary_contact_email'],
                        'created_at': current_datetime, 
                        'updated_at': current_datetime,
                    }
                   

                    # Create the order and save it
                    order = Order(**order_data)
                    db.session.add(order)
                    db.session.flush()
                

                    # Now create the shipment related to this order
                    shipment_data = {
                        'order_id': order.id,
                        'courier_name' : row['courier_name'],
                        'reference_number' : row['reference_number'],
                        'tracking_id' : row['awb'],
                        'shipment_status' : row['shipment_status'],
                        'current_location' : row['current_location'],
                        'estimated_delivery_date' : estimated_delivery_date,
                        'primary_contact_name' : row['primary_contact_name'],
                        'primary_contact_mobile' : row['primary_contact_number'],
                        'primary_contact_email' : row['primary_contact_email'],
                        'secondary_contact_name' : row['secondary_contact_name'],
                        'secondary_contact_mobile' : row['secondary_contact_number'],
                        'secondary_contact_email' : row['secondary_contact_email'],
                        'district' : row['district'],
                        'pincode' : row['pincode'],
                        'created_at': current_datetime, 
                        'updated_at': current_datetime,
                    }

                    shipment = Shipment(**shipment_data)
                    db.session.add(shipment)

                    # Commit all new shipments to the DB
                    db.session.commit()

                    # Return success response
                    success_count += 1
                    print(f"Order ID {order.id} and Shipment created successfully.")
                except Exception as e:
                    db.session.rollback()
                    failure_count += 1
                    print(f"Error processing row {row['sr_no']}: {str(e)}")
            # Return success or failure message based on the result
            return {
                'message': f'{success_count} rows successfully processed, {failure_count} rows failed.',
                'status': 'success' if failure_count == 0 else 'partial_success'
            }, 200        

        except Exception as e:
            # Log the error and return a failure message
            print(f"Error processing CSV data: {str(e)}")
            return {'message': f'Error processing CSV data: {str(e)}'}, 500
