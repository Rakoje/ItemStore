from flask import Flask
import json

from sqlalchemy import func, desc

from decorator import roleCheck
from configurationStore import Configuration
from modelsStore import database, Item, HasItem, Order, Category, HasCategory
from flask_jwt_extended import JWTManager, jwt_required

application = Flask(__name__)
application.config.from_object(Configuration)
jwt = JWTManager(application)


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


def response_error(msg):
    response = {
        "message": msg
    }
    return json.dumps(response), 400


def get_sold(category):
    return category.get("sold")

@application.route("/productStatistics", methods=["GET"])
@jwt_required()
@roleCheck(role = "admin")
def product_statistics():

    query = database.session.query(Item.name, func.sum(HasItem.quantity),
                                   func.sum(HasItem.quantity) - func.sum(HasItem.received))\
                                    .join(HasItem).join(Order).group_by(Item.id).all()
    statistics = []
    for row in query:
        statistics.append({"name": row[0], "sold": int(row[1]), "waiting": int(row[2])})

    return json.dumps({"statistics" : statistics}), 200


def f(e):
    return e['sold']


@application.route("/categoryStatistics", methods=["GET"])
@jwt_required()
@roleCheck(role = "admin")
def category_statistics():
    #query = database.session.query(Category.name, func.sum(HasItem.quantity)) \
    #                                .join(HasCategory).join(Item).join(HasItem).join(Order)\
    #    .group_by(Category.name).order_by(func.sum(HasItem.quantity), desc(Category.name)).all()
    query = database.session.query(Item.name, func.sum(HasItem.quantity)).join(HasCategory)\
        .join(Category).join(HasItem).join(Order).group_by(Item.name).all()

    products = []

    for row in query:
        products.append({"name": row[0], "sold": int(row[1])})

    query = database.session.query(Category.name, Item.name).join(HasCategory).join(Item).all()

    categories = []
    for row in query:
        categories.append({"name": row[0], "product": row[1]})

    for category in categories:
        for product in products:
            if category["product"] == product["name"]:
                category["product"] = product["sold"]
                break

    categories_sum = []

    for i in range(len(categories)):
        category_sum = categories[i]["product"]
        while categories[i + 1]["name"] == categories[i]["name"]:
            category_sum += categories[i + 1]["product"]
            i += 1
        categories_sum.append({"name": categories["name"], "sold": category_sum})

    categories_sum.sort(key=get_sold)
    statistics = []
    for category in category_sum:
        statistics.append(category)
    return json.dumps({"statistics" : statistics}), 200


if __name__ == "__main__":
    database.init_app(application)
    application.run(debug=True, host="0.0.0.0", port=5003)
