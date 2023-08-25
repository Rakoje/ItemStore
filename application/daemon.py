import json

from redis import Redis
from configurationStore import Configuration
from modelsStore import Item, Category, HasCategory, Order, HasItem, database
from warehouse import application

if (__name__ == "__main__"):
    with Redis(host=Configuration.REDIS_HOST) as redis:
        while True:
            with application.app_context():
                database.init_app(application)
                data = json.loads(redis.brpop(Configuration.REDIS_ITEMS_LIST, 0)[1])
                if data:
                    print(data)
                    categories = Category.query.all()
                    category_names = []
                    if len(categories) != 0:
                        for category in categories:
                            category_names.append(category.name)
                    for item in data["items"]:
                        items = Item.query.filter(Item.name == item["name"]).all()
                        if len(items) == 0:
                            new_item = Item(name=item["name"], price=item["price"], quantity=item["quantity"])
                            database.session.add(new_item)
                            database.session.commit()
                            new_categories = item["categories"]
                            categories = Category.query.all()
                            for new_category in new_categories:
                                flag = True
                                category_id = 0
                                for category in categories:
                                    if category.name == new_category:
                                        category_id = category.id
                                        flag = False
                                        break
                                if flag is True:
                                    category = Category(name=new_category)
                                    database.session.add(category)
                                    database.session.commit()
                                    category_id = category.id
                                has_category = HasCategory(item_id=new_item.id, category_id=category_id)
                                database.session.add(has_category)
                                database.session.commit()
                        else:
                            new_categories = []
                            category_names = []
                            new_categories = item["categories"]
                            categories = Category.query.join(HasCategory).join(Item).filter(
                                Item.name == item["name"]).all()
                            for category in categories:
                                category_names.append(category.name)
                            category_names.sort()
                            new_categories.sort()
                            print(category_names)
                            print(new_categories)
                            if len(new_categories) == len(category_names):
                                count = 0
                                flag = True
                                while count < len(new_categories):
                                    if new_categories[count] != category_names[count]:
                                        flag = False
                                        break
                                    count += 1
                                if flag is True:
                                    product = Item.query.filter(Item.name == item["name"]).first()
                                    print(product)
                                    quantity = product.quantity
                                    price = product.price
                                    new_quantity = quantity + item["quantity"]
                                    store_orders = Order.query.join(HasItem).join(Item).filter(
                                        Item.id == product.id).order_by(Order.id).all()
                                    for store_order in store_orders:
                                        if store_order.status == "PENDING":
                                            print("Radi")
                                            has_item = HasItem.query.filter(HasItem.item_id == product.id).filter(
                                                HasItem.order_id == store_order.id).first()
                                            received = has_item.received
                                            requested = has_item.quantity
                                            need_more = requested - received
                                            left_quantity = new_quantity - need_more
                                            if left_quantity >= 0:
                                                new_quantity = left_quantity
                                                database.session.query(HasItem).filter(
                                                    HasItem.item_id == product.id).filter(
                                                    HasItem.order_id == store_order.id).update(
                                                    {'received': has_item.quantity})
                                                database.session.commit()
                                                has_items = HasItem.query.filter(
                                                    HasItem.order_id == store_order.id).all()
                                                status_flag = True
                                                for order_item in has_items:
                                                    if order_item.received != order_item.quantity:
                                                        status_flag = False
                                                        break
                                                if status_flag is True:
                                                    database.session.query(Order).filter(
                                                        Order.id == store_order.id).update({"status": "COMPLETE"})
                                                    database.session.commit()
                                            else:
                                                new_received = received + new_quantity
                                                new_quantity = 0
                                                database.session.query(HasItem).filter(
                                                    HasItem.item_id == product.id).filter(
                                                    HasItem.order_id == store_order.id).update(
                                                    {'received': new_received})
                                                database.session.commit()
                                    new_price = (quantity * price + item["quantity"] * item["price"]) / \
                                                (quantity + item["quantity"])
                                    database.session.query(Item). \
                                        filter(Item.id == product.id). \
                                        update({'quantity': new_quantity})
                                    database.session.commit()
                                    database.session.query(Item). \
                                        filter(Item.id == product.id). \
                                        update({'price': new_price})
                                    database.session.commit()
