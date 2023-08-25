from flask import Flask, request
import json
import re

from decorator import roleCheck
from configurationUsers import Configuration
from modelsUsers import User, database
from flask_jwt_extended import JWTManager, create_access_token, create_refresh_token, jwt_required, get_jwt, \
    get_jwt_identity

application = Flask(__name__)
application.config.from_object(Configuration)
jwt = JWTManager(application)


def response_error(msg: str):
    response = {
        "message": msg
    }
    return json.dumps(response), 400


def response_refresh_token(access_token: str):
    response = {
        "accessToken": access_token
    }
    return json.dumps(response), 200


regex_forename = r'^\w{1,256}$'
regex_surname = r'^\w{1,256}$'
regex_password_digit = r'\d'
regex_password_lower = r'[a-z]'
regex_password_upper = r'[A-Z]'
regex_password_8_or_more = r'^.{8,}$'
regex_email = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'


@application.route("/register", methods=["POST"])
def register():
    data = request.get_json(force=True)

    if "forename" not in data or len(data["forename"]) == 0:
        return response_error("Field forename is missing.")
    if "surname" not in data or len(data["surname"]) == 0:
        return response_error("Field surname is missing.")
    if "email" not in data or len(data["email"]) == 0:
        return response_error("Field email is missing.")
    if "password" not in data or len(data["password"]) == 0:
        return response_error("Field password is missing.")
    if "isCustomer" not in data or data["isCustomer"] is None:
        return response_error("Field isCustomer is missing.")

    forename = data['forename']
    surname = data['surname']
    email = data['email']
    password = data['password']
    isCustomer = data['isCustomer']

    if not re.match(regex_forename, forename):
        return response_error("Invalid forename.")
    if not re.match(regex_surname, surname):
        return response_error("Invalid surname.")
    if not re.match(regex_email, email) or len(email) > 256:
        return response_error("Invalid email.")

    if (re.search(regex_password_digit, password) is None or
            re.search(regex_password_lower, password) is None or
            re.search(regex_password_upper, password) is None or
            re.search(regex_password_8_or_more, password) is None or
            len(password) > 256 or len(password) < 8):
        return response_error("Invalid password.")

    if len(User.query.filter(User.email == email).all()) != 0:
        return response_error("Email already exists.")

    if isCustomer is True:
        role = "customer"
    else:
        role = "manager"

    user = User(forename=forename, surname=surname, email=email, password=password, isCustomer=isCustomer, role=role)
    database.session.add(user)
    database.session.commit()
    return "", 200


@application.route("/login", methods=["POST"])
def login():
    data = request.get_json(force=True)

    if "email" not in data or len(data["email"]) == 0:
        return response_error("Field email is missing.")
    if "password" not in data or len(data["password"]) == 0:
        return response_error("Field password is missing.")

    email = data['email']
    password = data['password']

    if not re.match(regex_email, email) or len(email) > 256:
        return response_error("Invalid email.")

    users = User.query.filter(User.email == email).all()

    if len(users) == 0:
        return response_error("Invalid credentials.")

    user = users[0]
    if user.password != password:
        return response_error("Invalid credentials.")

    additional_claims = {
        "forename": user.forename,
        "surname": user.surname,
        "isCustomer": user.isCustomer,
        "role": user.role
    }

    access_token = create_access_token(identity=user.email, additional_claims=additional_claims)
    ref_token = create_refresh_token(identity=user.email, additional_claims=additional_claims)

    response = {
        "accessToken": access_token,
        "refreshToken": ref_token
    }
    return json.dumps(response), 200


@application.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh_token():
    identity = get_jwt_identity()
    token_claims = get_jwt()
    additional_claims = {
        "forename": token_claims["forename"],
        "surname": token_claims["surname"],
        "isCustomer": token_claims["isCustomer"],
        "role": token_claims["role"]
    }

    access_token = create_access_token(identity=identity, additional_claims=additional_claims)
    response = {
        "accessToken": access_token
    }
    return json.dumps(response), 200


@application.route("/delete", methods=["POST"])
@roleCheck(role="admin")
def delete_user():
    data = request.get_json(force=True)

    if "email" not in data or len(data["email"]) == 0:
        return response_error("Field email is missing.")

    email = data['email']

    if not re.match(regex_email, email) or len(email) > 256:
        return response_error("Invalid email.")
    user = User.query.filter(User.email == email).first()

    if not user:
        return response_error("Unknown user.")

    database.session.delete(user)
    database.session.commit()
    return "", 200


@application.route("/", methods=["GET"])
def index():
    return "Hello world!"

if __name__ == "__main__":
    database.init_app(application)
    application.run(debug=True, host="0.0.0.0", port=5000)
