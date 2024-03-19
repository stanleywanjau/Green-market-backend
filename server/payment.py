import dbm
from shelve import DbfilenameShelf
from flask import Flask, jsonify, request
from flask_jwt_extended import jwt_required
from flask_restful import Api, Resource
import requests

from server.models import Payment
from datetime import datetime

app = Flask(__name__)
api = Api(app)

class TriggerPayment(Resource):
    @jwt_required()
    def post(self):
        # Extract data from the incoming JSON payload
        data = request.get_json()
        order_id = data.get("order_id")
        phone_number = data.get("phone_number")  # Extract phone number from the request

        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer lJ0G0H1EASGqvHvRhQHA4VjZEIyMlJ ",
        }

        # Use an f-string to dynamically insert the order_id into the CallBackURL
        callBackURL = f"https://mpesacallback.onrender.com/mycallback/{order_id}"

        payload = {
            "BusinessShortCode": 174379,
            "Password": "lJ0G0H1EASGqvHvRhQHA4VjZEIyMlJMTc0Mzc5YmZiMjc5ZjlhYTliZGJjZjE1OGU5N2RkNzFhNDY3Y2QyZTBjODkzMDU5YjEwZjc4ZTZiNzJhZGExZWQyYzkxOTIwMjQwMzE5MTgxMjUy",
            "Timestamp": "20240318181252",
            "TransactionType": "CustomerPayBillOnline",
            "Amount": 1,
            "PartyA": 254725929654,  # Use the extracted phone number here
            "PartyB": 174379,
            "PhoneNumber": 254725929654,  # And also here
            "CallBackURL": callBackURL,
            "AccountReference": "CompanyXLTD",
            "TransactionDesc": "Payment of X",
        }

        try:
            response = requests.post(
                "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest",
                headers=headers,
                json=payload,
            )
            response_data = response.text.encode("utf8")
            return jsonify({"success": True, "response": response_data.decode("utf-8")}), 200
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500

class MyCallback(Resource):
    @jwt_required()
    def post(self, order_id):
        # Parse the JSON data from the POST request
        data = request.get_json()

        try:
            items = data["Body"]["stkCallback"]["CallbackMetadata"]["Item"]
            extracted_data = {
                item["Name"]: item.get("Value", None) for item in items
            }  # Safely extract data

            # Extract relevant information
            mpesa_receipt_number = extracted_data.get("MpesaReceiptNumber")
            payment_amount = extracted_data.get("Amount")
            transaction_date = extracted_data.get("TransactionDate")

            # Convert transaction_date to datetime, keeping the time part
            payment_date = (
                datetime.strptime(str(transaction_date), "%Y%m%d%H%M%S")
                if transaction_date
                else None
            )

            # Use the provided order_id directly
            # Assuming Payment is a SQLAlchemy model
            new_payment = Payment(
                order_id=order_id,
                payment_amount=payment_amount,
                payment_date=payment_date,
                payment_method="M-Pesa",
                status="Completed",
                transaction_id=mpesa_receipt_number,
            )
            DbfilenameShelf.session.add(new_payment)
            dbm.session.commit()
        except Exception as e:
            # Handle any errors that might occur during the process
            return jsonify({"status": "error", "message": str(e)}), 400

        # Return a success response upon successful processing
        return (
            jsonify({"status": "success", "message": "Payment processed successfully"}),
            200,
        )

class Transactions(Resource):
    @jwt_required()
    def get(self):
        # Assuming Payment is a SQLAlchemy model
        transactions = Payment.query.all()
        transactions_data = [
            {
                "id": transaction.id,
                "order_id": transaction.order_id,
                "payment_amount": transaction.payment_amount,
                "payment_date": (
                    transaction.payment_date.strftime("%Y-%m-%d %H:%M:%S")
                    if transaction.payment_date
                    else None
                ),
                "payment_method": transaction.payment_method,
                "status": transaction.status,
                "transaction_id": transaction.transaction_id,
            }
            for transaction in transactions
        ]
        return jsonify(transactions_data), 200

api.add_resource(TriggerPayment, "/trigger-payment")
api.add_resource(MyCallback, "/mycallback/<int:order_id>")
api.add_resource(Transactions, "/transactions")


