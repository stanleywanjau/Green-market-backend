from flask import jsonify, request
from flask_restful import Resource
from flask_jwt_extended import create_access_token
import random
import smtplib

from config import db, api, app
from models import User

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
    # You need to replace placeholders with your SMTP server details
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

api.add_resource(Signup, '/signup', endpoint='signup')
api.add_resource(Verify, '/verify')

if __name__ == "__main__":
    app.run(port=5555, debug=True)
