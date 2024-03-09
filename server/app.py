from sqlite3 import IntegrityError
from flask import  jsonify, request, make_response
from flask_restful import Resource
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from _datetime import datetime
import random
from datetime import datetime
import smtplib
from models import ChatMessage, User
import logging


# app = Flask(__name__)

from config import db, api, app
from models import User,Farmer,Order,Product,Reviews

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

class CustomerOrders(Resource):
    @jwt_required()
    def get(self):
        # Get current user ID
        user_id = get_jwt_identity()

        # Query orders associated with the current user (customer)
        orders = Order.query.filter_by(customer_id=user_id).all()

        # Serialize orders data and return
        return make_response({'orders': [order.serialize() for order in orders]}, 200)

    @jwt_required()
    def post(self):
        # Get current user ID
        user_id = get_jwt_identity()

        # Parse request data
        data = request.json
        product_id = data.get('product_id')
        quantity = data.get('quantity')

        # Check if product_id and quantity are provided
        if not product_id or not quantity:
            return make_response({'error': 'Missing fields', 'message': 'Both product_id and quantity are required'}, 400)

        # Validate quantity
        try:
            quantity = int(quantity)
            if quantity <= 0:
                raise ValueError('Quantity must be a positive integer')
        except ValueError:
            return make_response({'error': 'Invalid quantity', 'message': 'Quantity must be a positive integer'}, 400)

        # Check if the product exists and handle quantity available
        product = Product.query.get(product_id)
        if not product:
            return make_response({'error': 'Product not found', 'message': 'The specified product does not exist'}, 404)
        if product.quantity_available < quantity:
            return make_response({'error': 'Insufficient quantity available', 'message': 'The requested quantity exceeds available stock'}, 400)

        # Create new order
        try:
            new_order = Order(customer_id=user_id, product_id=product_id, quantity_ordered=quantity, order_date=datetime.utcnow())
            db.session.add(new_order)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return make_response({'error': 'Database error', 'message': 'Failed to create order'}, 500)

        # Decrement product quantity
        product.quantity_available -= quantity
        db.session.commit()

        return make_response({'message': 'Order placed successfully'}, 201)


class FarmerOrders(Resource):
    @jwt_required()
    def get(self):
        # Get current farmer's user ID
        farmer_id = get_jwt_identity()

        # Query orders associated with products of the current farmer
        orders = Order.query.join(Product).join(Farmer).filter(Farmer.id == farmer_id).all()

        # Serialize orders data and return
        return make_response({'orders': [order.serialize() for order in orders]}, 200)

    @jwt_required()
    def put(self, order_id):
        # Get current farmer's user ID
        farmer_id = get_jwt_identity()

        # Check if the order belongs to the current farmer
        order = Order.query.join(Product).join(Farmer).filter(Farmer.id == farmer_id, Order.id == order_id).first()
        if not order:
            return {'error': '404 Not Found', 'message': 'Order not found or does not belong to the farmer'}, 404

        # Update order status (example: mark as completed)
        data = request.get_json()
        new_status = data.get('order_status')
        order.order_status = new_status
        db.session.commit()

        return make_response({'message': 'Order status updated successfully'}, 200)

    @jwt_required()
    def delete(self, order_id):
        # Get current farmer's user ID
        farmer_id = get_jwt_identity()

        # Check if the order belongs to the current farmer
        order = Order.query.join(Product).join(Farmer).filter(Farmer.id == farmer_id, Order.id == order_id).first()
        if not order:
            return {'error': '404 Not Found', 'message': 'Order not found or does not belong to the farmer'}, 404

        # Delete the order
        db.session.delete(order)
        db.session.commit()

        return make_response({'message': 'Order deleted successfully'}, 200)
#products routes
class ProductList(Resource):
    def get(self):
       
        products =[ {"id":product.id,"name":product.name,"price":product.price,"image":product.image }for product in Product.query.all()]

        
        # serialized_products = [product.serialize() for product in products]
        return make_response(jsonify(products))


class FarmerProductList(Resource):
    @jwt_required()
    def get(self):
        farmer_id = get_jwt_identity()

        # Query products associated with the current farmer
        products = Product.query.filter_by(farmer_id=farmer_id).all()

        # Serialize products data and return
        serialized_products = [product.serialize() for product in products]
        return jsonify({'products': serialized_products})


class productbyid(Resource):
    def get(self,productid):
        product= Product.query.filter_by(id=productid).first()
        product_data={
            "id":product.id,
            "name":product.name,
        }
        return make_response(jsonify(product_data))


class ReviewsResource(Resource):
    @jwt_required()
    def post(self):
        identity = get_jwt_identity()
        user = User.query.filter_by(id=identity).first()

        if user.role != 'customer':
            return make_response(jsonify(message="Only customers can submit reviews"), 403)

        rating = request.json.get("rating")
        comments = request.json.get("comment")
        product_id = request.json.get("product_id")
        
        try:
            rating = int(rating)
            if rating < 1 or rating > 5:
                raise ValueError("Rating must be between 1 and 5")
        except (TypeError, ValueError):
            return make_response(jsonify(message="Invalid rating. Rating must be an integer between 1 and 5"), 400)

        # Check if the user has completed an order for the product they want to review
        order = Order.query.filter_by(customer_id=identity, product_id=product_id, order_status='completed').first()
        if not order:
            return make_response(jsonify(message="You can only review products you have ordered and received"), 403)

        # Create a new Reviews object with the provided data
        review = Reviews(rating=rating, comments=comments, product_id=product_id, customer_id=identity)

        
        
        db.session.add(review)
        db.session.commit()
        return make_response(jsonify(message="Review successfully posted"))
        

        
class Reviewperproduct(Resource):
    def get(self, productid):        
        reviews = Reviews.query.filter_by(product_id=productid).all()
        if not reviews:
            return {"error":"not found","message":"product not found"}
        review_data=[]
        for review in reviews:
            review_data.append({
                "id":review.id,
                "name":review.rating,
                "comments":review.comments
            })
        return make_response(jsonify(review_data))
class ProductReview(Resource):
    @jwt_required()
    def delete(self, review_id):
        identity = get_jwt_identity()
        user = User.query.filter_by(id=identity).first()

        # Check if the user exists
        if not user:
            return make_response(jsonify(error="User not found"), 404)

        # Check if the review exists
        review = db.session.get(Reviews, review_id)

        if not review:
            return make_response(jsonify(error="Review not found"), 404)

        # Check if the user is authorized to delete the review
        if review.customer_id != identity:
            return make_response(jsonify(error="You are not authorized to delete this review"), 403)

        # Delete the review
        db.session.delete(review)
        db.session.commit()

        return make_response(jsonify(message="Review deleted successfully"), 200)
    
    
    
    
    
    
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


api.add_resource(ForgotPassword, '/forgot-password')
api.add_resource(ChangePassword, '/change-password')


api.add_resource(CustomerOrders, '/customer/orders')
api.add_resource(FarmerOrders, '/farmer/orders')
# api.add_resource(ProductList, '/products/farmers', endpoint='farmer_products')
api.add_resource(ProductList, '/products')
api.add_resource(productbyid,"/product/<int:productid>")
api.add_resource(ReviewsResource,'/reviews')
api.add_resource(Reviewperproduct, '/review/<int:productid>')
api.add_resource(ProductReview,'/deleteReview/<int:review_id>')



if __name__ == "__main__":
    app.run(port=5555, debug=True)
