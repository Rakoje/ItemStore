import datetime

from flask import Flask, request
import json

from decorator import roleCheck
from configurationStore import Configuration
from modelsStore import Item, HasCategory, Category, Order, HasItem, database
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity

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


@application.route("/search", methods=["GET"])
@roleCheck(role="customer")
def search():
    try:
        product_name = request.args["name"]
    except KeyError:
        product_name = ""
    try:
        category = request.args["category"]
    except KeyError:
        category = ""
    cats = []
    products = []
    if product_name == "":
        if category == "":
            items = Item.query.all()
            database.session.commit()
            categories = Category.query.all()
            database.session.commit()
        else:
            items = Item.query.join(HasCategory).join(Category).filter(Category.name.like(f"%{category}")).all()
            database.session.commit()
            categories = Category.query.join(HasCategory).join(Item).filter(Category.name.like(f"%{category}")).all()
            database.session.commit()
    if category == "" and product_name != "":
        items = Item.query.join(HasCategory).join(Category).filter(Item.name.like(f"%{product_name}")).all()
        database.session.commit()
        categories = Category.query.join(HasCategory).join(Item).filter(Item.name.like(f"%{product_name}")).all()
        database.session.commit()
    elif category != "" and product_name != "":
        items = Item.query.join(HasCategory).join(Category).filter(Item.name.like(f"%{product_name}")).filter(
            Category.name.like(f"%{category}")).all()
        database.session.commit()
        categories = Category.query.join(HasCategory).join(Item).filter(Item.name.like(f"%{product_name}")).filter(
            Category.name.like(f"%{category}")).all()
        database.session.commit()
    for cat in categories:
        cats.append(cat.name)
    for item in items:
        item_cats = []
        for cat in item.categories:
            item_cats.append(cat.name)
        item_data = {
            "categories": item_cats,
            "id": item.id,
            "name": item.name,
            "price": item.price,
            "quantity": item.quantity
        }
        products.append(item_data)
    response = {
        "categories": cats,
        "products": products
    }
    database.session.close()
    return json.dumps(response), 200


@application.route("/order", methods=["POST"])
@jwt_required()
@roleCheck(role="customer")
def order():
    email = get_jwt_identity()
    data = request.get_json(force=True)
    if "requests" not in data or len(data["requests"]) == 0:
        return response_error("Field requests is missing.")
    count = 0
    price = 0.0
    for req in data["requests"]:
        if "id" not in req:
            return response_error("Product id is missing for request number " + str(count) + ".")
        if "quantity" not in req:
            return response_error("Product quantity is missing for request number " + str(count) + ".")
        if not if_integer(req["id"]):
            return response_error("Invalid product id for request number " + str(count) + ".")
        if int(req["id"]) < 0:
            return response_error("Invalid product id for request number " + str(count) + ".")
        if not if_float(req["quantity"]):
            return response_error("Invalid product quantity for request number " + str(count) + ".")
        if float(req["quantity"]) < 0:
            return response_error("Invalid product quantity for request number " + str(count) + ".")
        items = Item.query.filter(Item.id == req["id"]).all()
        if len(items) == 0:
            database.session.close()
            return response_error("Invalid product for request number " + str(count) + ".")
        count += 1
    store_order = Order(price=0.0, status="PENDING", date=datetime.datetime.now(), customer=email)
    database.session.add(store_order)
    database.session.commit()
    can_send = 0
    for req in data["requests"]:
        item = Item.query.filter(Item.id == req["id"]).first()
        has_item = HasItem(item_id=item.id, order_id=store_order.id, item_price=item.price, quantity=req["quantity"],
                           received=0)
        database.session.add(has_item)
        database.session.commit()
        has_item_id = has_item.id
        price += item.price * req["quantity"]
        new_quantity = item.quantity - req["quantity"]
        if new_quantity >= 0:
            has_item.received = has_item.quantity
            database.session.commit()
            new_item_after = database.session.query(Item).get(req["id"])
            new_item_after.quantity = new_quantity
            database.session.commit()
            database.session.query(Item).filter(Item.id == req["id"]).update({"quantity": new_quantity})
            database.session.commit()
            new_item_after = database.session.query(Item).get(req["id"])
            print("Posle: " + str(new_item_after))
            can_send += 1
        else:
            has_item.received = item.quantity
            database.session.commit()
            item = database.session.query(Item).get(req["id"])
            item.quantity = 0
            database.session.commit()
            database.session.query(Item).filter(Item.id == req["id"]).update({"quantity": 0})
            database.session.commit()
            item = database.session.query(Item).get(req["id"])
            print("Posle: " + str(item))
    if can_send == len(data["requests"]):
        database.session.query(Order).filter(Order.id == store_order.id).update({"status": "COMPLETE"})
        database.session.commit()
    database.session.query(Order).filter(Order.id == store_order.id).update({"price": price})
    database.session.commit()
    return json.dumps({"id": store_order.id}), 200


@application.route("/status", methods=["GET"])
@jwt_required()
@roleCheck(role="customer")
def status():
    email = get_jwt_identity()
    orders = Order.query.filter(Order.customer == email).all()
    orders_list = []
    timestamp = ""
    for curr_order in orders:
        products = []
        for item in curr_order.items:
            print(item)
            categories = Category.query.join(HasCategory).join(Item).filter(Item.id == item.id).all()
            cats = []
            for category in categories:
                cats.append(category.name)
            has_item = HasItem.query.filter(HasItem.item_id == item.id).filter(
                HasItem.order_id == curr_order.id).first()
            requested = has_item.quantity
            received = has_item.received
            price = has_item.item_price
            item_data = {
                "categories": cats,
                "name": item.name,
                "price": price,
                "received": received,
                "requested": requested
            }
            products.append(item_data)
            timestamp = curr_order.date.strftime("%Y-%m-%dT%H:%M:%Sz")
            print(timestamp)
        order_data = {
            "products": products,
            "price": curr_order.price,
            "status": curr_order.status,
            "timestamp": timestamp
        }
        orders_list.append(order_data)
        print(orders_list)
    return json.dumps({"orders": orders_list}), 200


if __name__ == "__main__":
    database.init_app(application)
    application.run(debug=True, host="0.0.0.0", port=5001)
