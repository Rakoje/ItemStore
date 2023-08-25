import csv
import io

from flask import Flask, request
import json

from redis import Redis

from decorator import roleCheck
from configurationStore import Configuration
from flask_jwt_extended import JWTManager, jwt_required

from modelsStore import database

application = Flask(__name__)
application.config.from_object(Configuration)
jwt = JWTManager(application)


def response_error(msg):
    response = {
        "message": msg
    }
    return json.dumps(response), 400


def if_integer(string):
    try:
        int(string)
        return True
    except ValueError:
        return False


def if_float(string):
    try:
        float(string)
        return True
    except ValueError:
        return False


@application.route("/update", methods=["POST"])
@jwt_required()
@roleCheck(role="manager")
def update():
    try:
        file = request.files["file"]
    except KeyError:
        return response_error("Field file is missing.")
    content = request.files["file"].stream.read().decode("utf-8")
    stream = io.StringIO(content)
    reader = csv.reader(stream)

    items = []
    count = 0
    for row in reader:
        if len(row) != 4:
            return response_error("Incorrect number of values on line " + str(count) + ".")
        if not if_integer(row[2]):
            return response_error("Incorrect quantity on line " + str(count) + ".")
        if int(row[2]) < 0:
            return response_error("Incorrect quantity on line " + str(count) + ".")
        if not if_float(row[3]):
            return response_error("Incorrect price on line " + str(count) + ".")
        if float(row[3]) < 0:
            return response_error("Incorrect price on line " + str(count) + ".")
        categories = row[0].split("|")
        name = row[1]
        quantity = int(row[2])
        price = float(row[3])
        item = {
            "categories": categories,
            "name": name,
            "quantity": quantity,
            "price": price
        }
        items.append(item)
        count += 1

    response = {
        "items": items
    }
    with Redis(host=Configuration.REDIS_HOST) as redis:
        redis.rpush(Configuration.REDIS_ITEMS_LIST, json.dumps(response))

    return "", 200


if ( __name__ == "__main__" ):
    database.init_app ( application );
    application.run ( debug = True, host="0.0.0.0", port=5002);