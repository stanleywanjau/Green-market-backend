from tkinter import messagebox
from flask import  jsonify, request, make_response
from flask_restful import Resource
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from _datetime import datetime
import random
import smtplib
from models import ChatMessage, User
import logging


# app = Flask(__name__)

from config import db, api, app
from models import ChatMessage, User,Farmer

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
        return {'email': email,"message":f"check otp in the {email}"}, 200

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

if __name__ == "__main__":
    app.run(port=5555, debug=True)
