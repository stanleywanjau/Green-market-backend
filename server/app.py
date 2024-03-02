from flask import  jsonify, request, make_response,session
from flask_restful import  Resource

from config import db,api,app
from models import User 





if __name__ == "__main__":
    app.run(port=5555,debug=True)