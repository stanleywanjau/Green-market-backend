from sqlite3 import IntegrityError
from sqlite3 import IntegrityError
from flask import  jsonify, request, make_response
from flask_restful import Resource
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from _datetime import datetime
import random
from datetime import datetime
from datetime import datetime
import smtplib
from models import ChatMessage, User
import logging


# app = Flask(__name__)

from config import db, api, app
from models import User,Farmer,CustomerOrder,Product

# Add a dictionary to store email-OTP mappings
signup_otp_map = {}
reset_otp_map ={}

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
        
        existing_user_email = User.query.filter_by(email=email).first()
        existing_user_username = User.query.filter_by(username=username).first()

        if existing_user_email:
            return {'error': '409 Conflict', 'message': 'Email already exists'}, 409
        if existing_user_username:
            return {'error': '409 Conflict', 'message': 'Username already exists'}, 409

        # Generate OTP
        otp = ''.join([str(random.randint(0, 9)) for _ in range(6)])

        # Store OTP in the dictionary
        signup_otp_map[email] = otp

        # Send OTP via Email
        send_otp_email(email, otp)

        # Return the email for verification
        return {'email': email,"message":f"OTP sent to your email - {email}"}, 200

class Verify(Resource):
    def post(self):
        email = request.json.get('email')
        otp_user = request.json.get('otp')

        # Retrieve OTP from the dictionary
        stored_otp = signup_otp_map.get(email)

        if stored_otp and verify_otp(stored_otp, otp_user):
            # existing_user_email = User.query.filter_by(email=email).first()
            # existing_user_username = User.query.filter_by(username=username).first()

            # if existing_user_email:
            #     return {'error': '409 Conflict', 'message': 'Email already exists'}, 409
            # if existing_user_username:
            #     return {'error': '409 Conflict', 'message': 'Username already exists'}, 409
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

class DeleteAccount(Resource):
    @jwt_required()
    def delete(self):
        current_user_id = get_jwt_identity()
        user = User.query.filter_by(id=current_user_id).first()

        if not user:
            return {'error': '404 Not Found', 'message': 'User not found'}, 404

        db.session.delete(user)
        db.session.commit()

        return {'message': 'User account deleted successfully'}, 200
class ForgotPassword(Resource):
    def post(self):
        email = request.json.get('email')
        user = User.query.filter_by(email=email).first()

        if not user:
            return {'error': '404 Not Found', 'message': 'User not found'}, 404

        temporary_password = ''.join([str(random.randint(0, 9)) for _ in range(8)])
        reset_otp_map[email]=temporary_password
        # user.password_hash = temporary_password
        # db.session.commit()

        send_otp_email(email, temporary_password)

        return {'message': f'OTP sent to your email - {email}'}, 200
class ChangePassword(Resource):
    def post(self):
        email = request.json.get('email')
        otp_user = request.json.get('otp')
        new_password = request.json.get('new_password')

        stored_otp = reset_otp_map.get(email)

        if stored_otp and verify_otp(stored_otp, otp_user):
            user = User.query.filter_by(email=email).first()

            if not user:
                return {'error': '404 Not Found', 'message': 'User not found'}, 404

            user.password_hash = new_password
            db.session.commit()

            return {'message': 'Password changed successfully'}, 200
        else:
            return {'error': '401 Unauthorized', 'message': 'Invalid OTP'}, 401

    
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

class CustomerProducts(Resource):
    def get(self):
        products = Product.query.all()
        return jsonify([product.serialize() for product in products]), 200

class CustomerCart(Resource):
    @jwt_required()
    def get(self):
        current_user_id = get_jwt_identity()
        customer = User.query.get(current_user_id)
        cart_products = customer.cart_products
        return jsonify([product.serialize() for product in cart_products]), 200

    @jwt_required()
    def post(self):
        current_user_id = get_jwt_identity()
        customer = User.query.get(current_user_id)
        
        product_id = request.json.get('product_id')
        quantity = request.json.get('quantity')
        
        product = Product.query.get(product_id)
        if product:
            if quantity <= product.quantity_available:
                # Logic to add product to cart
                customer.cart_products.append(product)
                db.session.commit()
                return {'message': 'Product added to cart successfully'}, 200
            else:
                return {'error': '422 Unprocessable Entity', 'message': 'Quantity requested exceeds available stock'}, 422
        else:
            return {'error': '404 Not Found', 'message': 'Product not found'}, 404

class CustomerOrders(Resource):
    @jwt_required()
    def get(self):
        current_user_id = get_jwt_identity()
        orders = CustomerOrder.query.filter_by(customer_id=current_user_id).all()
        return jsonify([order.serialize() for order in orders]), 200

    @jwt_required()
    def delete(self, order_id):
        order = CustomerOrder.query.get(order_id)
        if order:
            db.session.delete(order)
            db.session.commit()
            return {'message': 'Order deleted successfully'}, 200
        else:
            return {'error': '404 Not Found', 'message': 'Order not found'}, 404

class CustomerPlaceOrder(Resource):
    @jwt_required()
    def post(self):
        current_user_id = get_jwt_identity()
        customer = User.query.get(current_user_id)
        
        # Logic to place an order
        order = CustomerOrder(customer_id=current_user_id, order_date=datetime.utcnow(), quantity_ordered=quantity, total_price=total_price, order_status="Placed")
        for product in customer.cart_products:
            order.products.append(product)
        db.session.add(order)
        db.session.commit()
        return {'message': 'Order placed successfully'}, 201

class FarmerAddProduct(Resource):
    @jwt_required()
    def post(self):
        current_user_id = get_jwt_identity()
        farmer = User.query.get(current_user_id)
        
        name = request.json.get('name')
        description = request.json.get('description')
        price = request.json.get('price')
        quantity_available = request.json.get('quantity_available')
        category = request.json.get('category')
        image = request.json.get('image')
        
        product = Product(name=name, description=description, price=price, quantity_available=quantity_available, category=category, image=image, farmer_id=current_user_id)
        db.session.add(product)
        db.session.commit()
        return {'message': 'Product added successfully'}, 201

class FarmerProducts(Resource):
    @jwt_required()
    def get(self):
        current_user_id = get_jwt_identity()
        products = Product.query.filter_by(farmer_id=current_user_id).all()
        return jsonify([product.serialize() for product in products]), 200

class FarmerOrders(Resource):
    @jwt_required()
    def get(self):
        current_user_id = get_jwt_identity()
        orders = Order.query.join(Product).filter(Product.farmer_id == current_user_id).all()
        return jsonify([order.serialize() for order in orders]), 200




api.add_resource(Signup, '/signup', endpoint='signup')
api.add_resource(Verify, '/verify')
api.add_resource(CheckSession,'/checksession')
api.add_resource(Login,'/login')
api.add_resource(FarmerDetails,'/farmerdetails')
api.add_resource(ChatMessages,'/chatmessages')
api.add_resource(ChatSenderMessages, "/chatsendermessages/<int:receiver>")
api.add_resource(delete_messages,'/deletemessage/<int:message_id>')

api.add_resource(DeleteAccount, '/delete-account')
api.add_resource(FarmerDetails, '/farmer-details')
api.add_resource(CustomerProducts, '/customer/products')
api.add_resource(CustomerCart, '/customer/cart')
api.add_resource(CustomerOrders, '/customer/orders', '/customer/orders/<int:order_id>')
api.add_resource(CustomerPlaceOrder, '/customer/place_order')
api.add_resource(FarmerAddProduct, '/farmer/add_product')
api.add_resource(FarmerProducts, '/farmer/products')
api.add_resource(FarmerOrders, '/farmer/orders')

if __name__ == "__main__":
    app.run(port=5555, debug=True)
