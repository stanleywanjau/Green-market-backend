from flask import  jsonify, request, make_response
from flask_restful import Resource
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
import random
import smtplib

from config import db, api, app
from models import User,Farmer,Order,Product

# Add a dictionary to store email-OTP mappings
signup_otp_map = {}

class Signup(Resource):
    def post(self):
        username = request.json.get('username')
        email = request.json.get('email')
        password = request.json.get('password')
        image = request.json.get('image')
        role = request.json.get('role')

        if not (username and email and password and role):
            return {'error': '422: Unprocessable Entity'}, 422
        if role not in ['farmer', 'customer']:
            return {'error': '422: Unprocessable Entity', 'message': 'Invalid role value'}, 422

        # Generate OTP
        otp = ''.join([str(random.randint(0, 9)) for _ in range(6)])

        # Store OTP in the dictionary
        signup_otp_map[email] = otp

        # Send OTP via Email
        send_otp_email(email, otp)

        # Return the email for verification
        return {'email': email}, 200

class Verify(Resource):
    def post(self):
        email = request.json.get('email')
        otp_user = request.json.get('otp')

        # Retrieve OTP from the dictionary
        stored_otp = signup_otp_map.get(email)

        if stored_otp and verify_otp(stored_otp, otp_user):
            # Create a new user instance
            username = request.json.get('username')
            password = request.json.get('password')
            image = request.json.get('image')
            role = request.json.get('role')
            new_user = User(username=username, email=email, image=image, role=role)
            new_user.password_hash = password
            
            # Commit the new user to the database
            db.session.add(new_user)
            db.session.commit()

            # Create an access token
            access_token = create_access_token(identity=new_user.id)

            # Return the access token
            return {'access_token': access_token, 'message': 'User registered successfully'}, 201
        else:
            return {'error': '401 Unauthorized', 'message': 'Invalid OTP'}, 401

def send_otp_email(email, otp):
    # This function sends the OTP via email using SMTP
    
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587
    sender_email = 'stanley.muiruri@student.moringaschool.com'
    sender_password = 'imei myuf vudn zvah'

    subject = 'OTP Verification'
    body = f'Your OTP for email verification is: {otp}'

    message = f'Subject: {subject}\n\n{body}'

    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, email, message)

def verify_otp(stored_otp, otp_user):
    # Compare the stored OTP with the OTP provided by the user
    return stored_otp == otp_user
class CheckSession(Resource):
    @jwt_required()
    def get(self):
        current_user_id = get_jwt_identity()
        
        user = User.query.filter_by(id=current_user_id).first()
        if not user:
            return {'error': '404 Not Found', 'message': 'User not found'}, 404

        user_data = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role,
            "image": user.image,
            "sent_messages": [],
            "received_messages": [],
            "orders": [],
            "reviews": [],
            "farmer": {}
        }
        
        for sent_msg in user.sent_messages:
            user_data["sent_messages"].append({
                "id": sent_msg.id,
                "message_text": sent_msg.message_text,
                "timestamp": sent_msg.timestamp
            })
        
        for received_msg in user.received_messages:
            user_data["received_messages"].append({
                "id": received_msg.id,
                "message_text": received_msg.message_text,
                "timestamp": received_msg.timestamp
            })

        for order in user.orders:
            user_data["orders"].append({
                "id": order.id,
                "order_date": order.order_date,
                "quantity_ordered": order.quantity_ordered,
                "total_price": order.total_price,
                "order_status": order.order_status,
                
            })

        for review in user.reviews:
            user_data["reviews"].append({
                "id": review.id,
                "product_id": review.product_id,
                "rating": review.rating,
                "comments": review.comments,
                "review_date": review.review_date,
                
            })

        if user.role == "farmer":
            farmer_data = {
                "id": user.farmer.id,
                "farm_name": user.farmer.farm_name,
                "location": user.farmer.location,
                "contact": user.farmer.contact
                
            }
            user_data["farmer"] = farmer_data

        return make_response(jsonify(user_data), 200)
class Login(Resource):
    def post(self):
        username = request.json.get('username')
        password = request.json.get('password')
        
        user = User.query.filter_by(username=username).first()
        if not user:
            return {'error': '404: Not Found', 'message': 'User not found'}, 404

        if not user.authenticate(password):
            return {'error': '401: Unauthorized', 'message': 'Invalid password'}, 401

        access_token = create_access_token(identity=user.id)
        return {'access_token': access_token}, 200
class FarmerDetails(Resource):
    @jwt_required()
    def post(self):
        current_user_id = get_jwt_identity()
        user = User.query.filter_by(id=current_user_id).first()

        if not user:
            return {'error': '404 Not Found', 'message': 'User not found'}, 404

        if user.role != "farmer":
            return {'error': '403 Forbidden', 'message': 'User is not a farmer'}, 403

        
        farm_name = request.json.get('farm_name')
        location = request.json.get('location')
        contact = request.json.get('contact')

        if not (farm_name and location and contact):
            return {'error': '422 Unprocessable Entity', 'message': 'Missing farmer details'}, 422

        
        if user.farmer:
            user.farmer.farm_name = farm_name
            user.farmer.location = location
            user.farmer.contact = contact
        else:
            farmer = Farmer(farm_name=farm_name, location=location, contact=contact)
            user.farmer = farmer

        db.session.commit()

        return {'message': 'Farmer details added successfully'}, 201


# Routes
class Orders(Resource):
    @jwt_required()
    def get(self):
        current_user_id = get_jwt_identity()
        user = User.query.filter_by(id=current_user_id).first()
        if not user:
            return {'error': '404 Not Found', 'message': 'User not found'}, 404

        if user.role == "customer":
            orders = Order.query.filter_by(customer_id=current_user_id).all()
        elif user.role == "farmer":
            products = Product.query.filter_by(farmer_id=user.farmer.id).all()
            product_ids = [product.id for product in products]
            orders = Order.query.filter(Order.product_id.in_(product_ids)).all()
        else:
            return {'error': '403 Forbidden', 'message': 'User role not supported for orders'}, 403

        # Serialize orders data as needed before returning
        return jsonify([order.serialize() for order in orders]), 200

    @jwt_required()
    def post(self):
        current_user_id = get_jwt_identity()
        user = User.query.filter_by(id=current_user_id).first()
        if not user:
            return {'error': '404 Not Found', 'message': 'User not found'}, 404

        # Extract order data from the request
        order_data = request.json
        product_id = order_data.get('product_id')
        quantity_ordered = order_data.get('quantity_ordered')

        # Validate the input data
        if not (product_id and quantity_ordered):
            return {'error': '422 Unprocessable Entity', 'message': 'Product ID and quantity are required'}, 422

        # Check if the product exists
        product = Product.query.get(product_id)
        if not product:
            return {'error': '404 Not Found', 'message': 'Product not found'}, 404

        # Check if the user is a customer
        if user.role != "customer":
            return {'error': '403 Forbidden', 'message': 'Only customers can place orders'}, 403

        # Create the order
        order = Order(
            customer_id=current_user_id,
            product_id=product_id,
            quantity_ordered=quantity_ordered,
            total_price=product.price * quantity_ordered,
            order_date=datetime.utcnow(),  # Assuming the current time is used as the order date
            order_status="pending"  # Assuming the initial status is "pending"
        )

        # Add the order to the database
        db.session.add(order)
        db.session.commit()

        # Serialize the order data before returning
        return jsonify(order.serialize()), 201

    @jwt_required()
    def put(self, order_id):
        current_user_id = get_jwt_identity()
        user = User.query.filter_by(id=current_user_id).first()
        if not user:
            return {'error': '404 Not Found', 'message': 'User not found'}, 404

        # Extract updated order data from the request
        updated_order_data = request.json
        quantity_ordered = updated_order_data.get('quantity_ordered')

        # Validate the input data
        if not quantity_ordered:
            return {'error': '422 Unprocessable Entity', 'message': 'Quantity is required'}, 422

        # Fetch the order to be updated
        order = Order.query.filter_by(id=order_id, customer_id=current_user_id).first()
        if not order:
            return {'error': '404 Not Found', 'message': 'Order not found or unauthorized'}, 404

        # Update the order data
        order.quantity_ordered = quantity_ordered
        order.total_price = order.product.price * quantity_ordered

        # Commit the changes to the database
        db.session.commit()

        # Serialize the updated order data before returning
        return jsonify(order.serialize()), 200

    @jwt_required()
    def delete(self, order_id):
        current_user_id = get_jwt_identity()
        user = User.query.filter_by(id=current_user_id).first()
        if not user:
            return {'error': '404 Not Found', 'message': 'User not found'}, 404

        # Fetch the order to be deleted
        order = Order.query.filter_by(id=order_id, customer_id=current_user_id).first()
        if not order:
            return {'error': '404 Not Found', 'message': 'Order not found or unauthorized'}, 404

        # Delete the order from the database
        db.session.delete(order)
        db.session.commit()

        return {'message': 'Order deleted successfully'}, 200




api.add_resource(Signup, '/signup', endpoint='signup')
api.add_resource(Verify, '/verify')
api.add_resource(CheckSession,'/checksession')
api.add_resource(Login,'/login')
api.add_resource(FarmerDetails, '/farmer-details')
api.add_resource(Orders, '/orders/<int:order_id>', endpoint='orders')

if __name__ == "__main__":
    app.run(port=5555, debug=True)
