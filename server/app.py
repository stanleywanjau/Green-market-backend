from flask import  jsonify, request, make_response
from flask_restful import Resource
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
import random
from datetime import datetime
import smtplib
import logging
from config import db, api, app
from models import User,Farmer,Reviews,Order,Product,ChatMessage


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

        if not (username and email  and role):
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


    


class ForgotPassword(Resource):
    def post(self):
        email = request.json.get('email')
        user = User.query.filter_by(email=email).first()

        if not user:
            return {'error': '404 Not Found', 'message': 'User not found'}, 404

        temporary_password = ''.join([str(random.randint(0, 9)) for _ in range(8)])
        reset_otp_map[email]=temporary_password
        
        send_otp_email(email, temporary_password)

        return {'message': f'OTP sent to your email - {email}'}, 200
class ChangePassword(Resource):
    def post(self):
        email = request.json.get('email')
        otp_user = request.json.get('otp')
        new_password = request.json.get('new_password')

        stored_otp = reset_otp_map.get(email)

        if stored_otp and verify_otp_reset(stored_otp, otp_user):
            user = User.query.filter_by(email=email).first()

            if not user:
                return {'error': '404 Not Found', 'message': 'User not found'}, 404

            user.password_hash = new_password
            db.session.commit()

            return {'message': 'Password changed successfully'}, 200
        else:
            return {'error': '401 Unauthorized', 'message': 'Invalid OTP'}, 401

def verify_otp_reset(stored_otp, otp_user):
    # Compare the stored OTP with the OTP provided by the user
    return stored_otp == otp_user   

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
                "comments":review.comments,
                "review_date":review.review_date
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
    
class FarmerProducts(Resource):
    @jwt_required()
    def get(self):
        # Get current farmer's identity
        current_farmer_id = get_jwt_identity()

        # Check if the current user is a farmer
        current_user = User.query.filter_by(id=current_farmer_id).first()
        if not current_user or current_user.role != 'farmer':
            return {'message': 'Unauthorized'}, 401

        # Retrieve all products belonging to the current farmer
        products = Product.query.filter_by(farmer_id=current_farmer_id).all()

        # Prepare response data
        products_data = []
        for product in products:
            products_data.append({
                'id': product.id,
                'name': product.name,
                'description': product.description,
                'image': product.image,
                'price': product.price,
                'quantity_available': product.quantity_available,
                'category': product.category
            })

        return make_response(jsonify(products_data))
class AddProduct(Resource):        
    @jwt_required()
    def post(self):
        # Get current farmer's identity
        current_farmer_id = get_jwt_identity()

        # Check if the current user is a farmer
        current_user = User.query.filter_by(id=current_farmer_id).first()
        if not current_user or current_user.role != 'farmer':
            return {'message': 'Unauthorized'}, 401

        # Parse product data from request
        data = request.json
        name = data.get('name')
        description = data.get('description')
        image = data.get('image')
        price = data.get('price')
        quantity_available = data.get('quantity_available')
        category = data.get('category')

        # Validate product data
        if not all([name, description, image, price, quantity_available, category]):
            return {'message': 'Missing product information'}, 400

        # Convert quantity_available to integer
        try:
            quantity_available = int(quantity_available)
        except ValueError:
            return {'message': 'Invalid quantity_available, must be an integer'}, 400

        # Validate quantity_available
        if quantity_available <= 0:
            return make_response({'message': 'Quantity available must be greater than 0'}, 400)

        # Create a new product
        new_product = Product(
            name=name,
            description=description,
            image=image,
            price=price,
            quantity_available=quantity_available,
            category=category,
            farmer_id=current_farmer_id
        )

        # Add the product to the database
        db.session.add(new_product)
        db.session.commit()

        return make_response({'message': 'Product added successfully'}, 201)
class UpdateProduct(Resource):    
    @jwt_required()
    def put(self, product_id):
        # Get current farmer's identity
        current_farmer_id = get_jwt_identity()

        # Check if the current user is a farmer
        current_user = User.query.filter_by(id=current_farmer_id).first()
        if not current_user or current_user.role != 'farmer':
            return make_response({'message': 'Unauthorized'}, 401)

        # Retrieve the product to update
        product = Product.query.filter_by(id=product_id, farmer_id=current_farmer_id).first()
        if not product:
            return make_response({'message': 'Product not found'}, 404)

        # Parse updated product data from request
        data = request.json
        # Update fields if they exist in the request data
        if 'name' in data:
            product.name = data['name']
        if 'description' in data:
            product.description = data['description']
        if 'image' in data:
            product.image = data['image']
        if 'price' in data:
            product.price = data['price']
        if 'quantity_available' in data:
            product.quantity_available = data['quantity_available']
        if 'category' in data:
            product.category = data['category']

        # Commit changes to the database
        db.session.commit()

        return make_response({'message': 'Product updated successfully'})
class DeleteProduct(Resource):
    @jwt_required()    
    def delete(self, product_id):
        # Get current farmer's identity
        current_farmer_id = get_jwt_identity()

        # Check if the current user is a farmer
        current_user = User.query.filter_by(id=current_farmer_id).first()
        if not current_user or current_user.role != 'farmer':
            return {'message': 'Unauthorized'}, 401

        # Retrieve the product to delete
        product = Product.query.filter_by(id=product_id, farmer_id=current_farmer_id).first()
        if not product:
            return {'message': 'Product not found'}, 404

        # Delete the product
        db.session.delete(product)
        db.session.commit()

        return make_response({'message': 'Product deleted successfully'})
    
class FarmerOrders(Resource):
    @jwt_required()
    def get(self):
        # Get current farmer's identity
        current_farmer_id = get_jwt_identity()

        # Check if the current user is a farmer
        current_user = User.query.filter_by(id=current_farmer_id).first()
        if not current_user or current_user.role != 'farmer':
            return {'message': 'Unauthorized'}, 401

        # Retrieve orders made by customers for the current farmer's products
        orders = Order.query.join(Product).filter(Product.farmer_id == current_farmer_id).all()

        order_data = []
        for order in orders:
            order_data.append({
                'customer_id': order.customer_id,
                # 'customer_username': order.role,
                'order_date': order.order_date.strftime("%Y-%m-%d"),
                'product_id': order.product_id,
                'quantity_ordered': order.quantity_ordered,
                'total_price': order.total_price,
                'order_status': order.order_status
            })

        return jsonify(order_data)
    

    @jwt_required()
    def put(self, order_id):
        # Get current farmer's identity
        current_farmer_id = get_jwt_identity()

        # Retrieve the order
        order = Order.query.get(order_id)
        if not order:
            return {'message': 'Order not found'}, 404

        # Check if the order belongs to the current farmer
        product = Product.query.filter_by(id=order.product_id, farmer_id=current_farmer_id).first()
        if not product:
            return {'message': 'Unauthorized'}, 401

        # Parse action from the request
        data = request.json
        action = data.get('action')

        # Validate action
        if action not in ['cancel', 'complete']:
            return {'message': 'Invalid action'}, 400

        # Update order status based on the action
        if action == 'cancel':
            order.order_status = 'cancelled'
        elif action == 'complete':
            order.order_status = 'completed'

        # Commit changes to the database
        db.session.commit()

        return make_response({'message': f'Order {action} successfully'}, 200)
class Products(Resource):
    def get(self):
        products = Product.query.all()

        product_data = []
        for product in products:
            product_data.append({
                    'id': product.id,
                    'name': product.name,
                    'price': product.price,
                    'image': product.image,
                    'category': product.category,
                    'farmer_id': product.farmer_id,
                
                })

        return jsonify(product_data)
class CustomerProducts(Resource):

    def get(self, product_id):
    
       

        # Retrieve all products posted by farmers
        product = Product.query.filter_by(id=product_id).first()

        # product_data = []
        # for product in products:
        product_data = {
                'id': product.id,
                'name': product.name,
                'price': product.price,
                'image': product.image,
                'category': product.category,
                'farmer_id': product.farmer_id,
                'description': product.description,
                'quantity_available':product.quantity_available
            }

        return jsonify(product_data)
class CustomerOrders(Resource):
    @jwt_required()
    def get(self):
        # Get current customer's identity
        current_customer_id = get_jwt_identity()

        # Retrieve orders made by the current customer
        orders = Order.query.filter_by(customer_id=current_customer_id).all()

        order_data = []
        for order in orders:
            order_data.append({
                'order_id': order.id,
                'order_date': order.order_date.strftime("%Y-%m-%d"),
                # 'products': [product.serialize() for product in order.products],  # Include associated products
                'total_price': order.total_price,
                'order_status': order.order_status
            })

        return jsonify(order_data)

    @jwt_required()
    def post(self):
        # Get current customer's identity
        current_customer_id = get_jwt_identity()

        # Parse order data from request
        data = request.json
        product_id = data.get('product_id')
        quantity_ordered = data.get('quantity_ordered')

        # Validate order data
        if not (product_id and quantity_ordered):
            return {'message': 'Missing order information'}, 400

        # Check if the product exists
        product = Product.query.filter_by(id=product_id).first()
        if not product:
            return {'message': 'Product not found'}, 404

        # Convert quantity_ordered to integer
        try:
            quantity_ordered = int(quantity_ordered)
        except ValueError:
            return {'message': 'Invalid quantity_ordered, must be an integer'}, 400

        # Validate quantity_ordered
        if quantity_ordered <= 0:
            return {'message': 'Quantity ordered must be greater than 0'}, 400

        # Calculate total price
        total_price = product.price * quantity_ordered

        # Get current timestamp
        current_time = datetime.now()

        # Create a new order with the current timestamp
        new_order = Order(
            customer_id=current_customer_id,
            product_id=product_id,
            quantity_ordered=quantity_ordered,
            total_price=total_price,
            order_status='pending',
            order_date=current_time  # Set order date to current timestamp
        )

        try:
            # Add the order to the database
            db.session.add(new_order)
            db.session.commit()
            return {'message': 'Order placed successfully'}, 201
        except Exception as e:
            # Rollback transaction in case of error
            db.session.rollback()
            return {'message': 'Failed to place order: ' + str(e)}, 500

class DeleteOrder(Resource):
    @jwt_required()
    def delete(self, order_id):
        # Get current customer's identity
        current_customer_id = get_jwt_identity()

        # Retrieve the order
        order = Order.query.filter_by(id=order_id, customer_id=current_customer_id).first()

        if not order:
            return {'message': 'Order not found'}, 404

        # Delete the order
        db.session.delete(order)
        db.session.commit()

        return make_response({'message': 'Order deleted successfully'}, 200)
    
    
    
class ChatMessages(Resource):
    @jwt_required()
    def get(self):
        current_user_id = get_jwt_identity()
        user = User.query.filter_by(id=current_user_id).first()

        if not user:
            return {'error': 'Not Found', 'message': 'User not found'}, 404

       
        # 
        # messages = ChatMessage.query.filter(
        #     ((ChatMessage.sender_id == current_user_id) & (ChatMessage.receiver_id == receiver_user.id)) |
        #     ((ChatMessage.sender_id == receiver_user.id) & (ChatMessage.receiver_id == current_user_id))
        # ).order_by(ChatMessage.timestamp.asc()).all()
        messages=ChatMessage.query.filter_by(receiver_id=current_user_id).all()
        # for message  in messages:
        messages_data = [{
            'id': message.id,
            'sender_id': message.sender_id,
            'receiver_id': message.receiver_id,
            'message_text': message.message_text,
            'timestamp': message.timestamp
        } for message in messages]

        return make_response(jsonify(messages_data), 200)
    

class ChatSenderMessages(Resource):
    @jwt_required()
    def post(self, receiver):
        try:
            current_user_id = get_jwt_identity()
        except Exception as e:
            logging.error(f"Error getting JWT identity: {str(e)}")
            return {'error': 'Unauthorized', 'message': 'Failed to get JWT identity'}, 401

        user = User.query.filter_by(id=current_user_id).first()

        if not user:
            return {'error': 'Not Found', 'message': 'User not found'}, 404

        receiver_user = User.query.filter_by(id=receiver).first()

        if not receiver_user:
            return {'error': 'Not Found', 'message': 'Receiver not found or not a farmer'}, 404

        message_text = request.json.get('message_text')

        if not message_text:
            return {'error': 'Unprocessable Entity', 'message': 'Content is required for the chat message'}, 422

        new_message = ChatMessage(sender_id=current_user_id, receiver_id=receiver_user.id, message_text=message_text)
        db.session.add(new_message)
        db.session.commit()

        return {'message': 'Chat message sent successfully'}, 201
        


    @jwt_required()
    def get(self, receiver):
        current_user_id = get_jwt_identity()
        user = db.session.query(User).get(current_user_id)

        if not user:
            response_data = {'error': 'Not Found', 'message': 'User not found'}
            return make_response(jsonify(response_data), 404)

        receiver_user = db.session.query(User).get(receiver)

        if not receiver_user or receiver_user.role != 'customer':
            response_data = {'error': 'Not Found', 'message': 'Receiver not found or not a customer'}
            return make_response(jsonify(response_data), 404)

        messages = db.session.query(ChatMessage).filter(
            ((ChatMessage.sender_id == current_user_id) & (ChatMessage.receiver_id == receiver_user.id)) |
            ((ChatMessage.sender_id == receiver_user.id) & (ChatMessage.receiver_id == current_user_id))
        ).order_by(ChatMessage.timestamp.asc()).all()

        messages_data = [
            {
                'id': message.id,
                'sender_id': message.sender_id,
                'receiver_id': message.receiver_id,
                'message_text': message.message_text,
                'timestamp': message.timestamp
            } for message in messages
        ]

        return make_response(jsonify(messages_data), 200)


 

class delete_messages(Resource):
    @jwt_required()
    def delete(self, message_id):
        current_user_id = get_jwt_identity()
        user = User.query.filter_by(id=current_user_id).first()

        if not user:
            return {'error': 'Not Found', 'message': 'User not found'}, 404

       # message = ChatMessage.query.get(message_id)
        message=db.session.get(ChatMessage, message_id)
    
        if not message:
            return {'error': 'Not Found', 'message': 'Message not found'}, 404

        # Check if the current user is the sender of the message
        if not (user.id == message.sender_id):
            return {'error': 'Forbidden', 'message': 'User is not authorized to delete this message'}, 403

        db.session.delete(message)
        db.session.commit()

        return {'message': 'Chat message deleted successfully'}, 200


#authetification
api.add_resource(Signup, '/signup', endpoint='signup')
api.add_resource(Verify, '/verify')
api.add_resource(CheckSession,'/checksession')
api.add_resource(Login,'/login')
api.add_resource(DeleteAccount, '/delete-account')
api.add_resource(ForgotPassword, '/forgot-password')
api.add_resource(ChangePassword, '/change-password')
#review
api.add_resource(ReviewsResource,'/reviews')
api.add_resource(Reviewperproduct, '/review/<int:productid>')
api.add_resource(ProductReview,'/deleteReview/<int:review_id>')
#farmer
api.add_resource(FarmerProducts, '/farmerproducts')#get all products 
api.add_resource(AddProduct, '/addproduct')#add product
api.add_resource(DeleteProduct, '/deleteproduct/<int:product_id>')
api.add_resource(UpdateProduct, '/updateproduct/<int:product_id>')
# api.add_resource(FarmerOrders, '/farmerorders')
api.add_resource(FarmerOrders, '/farmerorders', '/farmerorders/<int:order_id>')
#cutomer
api.add_resource(CustomerProducts, '/customerproducts/<int:product_id>')
api.add_resource(CustomerOrders, '/customerorders')
api.add_resource(DeleteOrder, '/deleteorder/<int:order_id>')
api.add_resource(Products, '/productslist')
#farmer
api.add_resource(FarmerDetails, '/farmer-details')
#chatmessage
api.add_resource(ChatMessages,'/chatmessages')
api.add_resource(ChatSenderMessages, "/chatsendermessages/<int:receiver>")
api.add_resource(delete_messages,'/deletemessage/<int:message_id>')

if __name__ == "__main__":
    app.run(port=5555, debug=True)
