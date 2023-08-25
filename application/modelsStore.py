from flask_sqlalchemy import SQLAlchemy

database = SQLAlchemy()


class HasCategory(database.Model):
    __tablename__ = "has_category"
    id = database.Column(database.Integer, primary_key=True)
    item_id = database.Column(database.Integer, database.ForeignKey("items.id"), nullable=False)
    category_id = database.Column(database.Integer, database.ForeignKey("categories.id"), nullable=False)


class HasItem(database.Model):
    __tablename__ = "has_item"
    id = database.Column(database.Integer, primary_key=True)
    item_id = database.Column(database.Integer, database.ForeignKey("items.id"), nullable=False)
    order_id = database.Column(database.Integer, database.ForeignKey("orders.id"), nullable=False)
    item_price = database.Column(database.Float, nullable=False)
    quantity = database.Column(database.Integer, nullable=False)
    received = database.Column(database.Integer, nullable=False)

    def __repr__(self):
        return "({}, {}, {}, {}, {}, {})".format(
            self.id, str(self.item_id), str(self.order_id), str(self.item_price), str(self.quantity),
            str(self.received))


class Item(database.Model):
    __tablename__ = "items"
    id = database.Column(database.Integer, primary_key=True)
    name = database.Column(database.String(256), nullable=False)
    price = database.Column(database.Float, nullable=False)
    categories = database.relationship("Category", secondary=HasCategory.__table__, back_populates="items")
    quantity = database.Column(database.Integer, nullable=False)
    orders = database.relationship("Order", secondary=HasItem.__table__, back_populates="items")

    def __repr__(self):
        return "({}, {}, {}, {}, {})".format(
            self.id, self.name, str(self.price), str(self.categories), str(self.quantity))


class Category(database.Model):
    __tablename__ = "categories"
    id = database.Column(database.Integer, primary_key=True)
    name = database.Column(database.String(256), nullable=False)
    items = database.relationship("Item", secondary=HasCategory.__table__, back_populates="categories")

    def __repr__(self):
        return "({}, {})".format(self.id, self.name)


class Order(database.Model):
    __tablename__ = "orders"
    id = database.Column(database.Integer, primary_key=True)
    items = database.relationship("Item", secondary=HasItem.__table__, back_populates="orders")
    price = database.Column(database.Float, nullable=False)
    status = database.Column(database.String(256), nullable=False)
    date = database.Column(database.DateTime, nullable=False)
    customer = database.Column(database.String(256), nullable=False)

    def __repr__(self):
        return "({}, {}, {}, {}, {})".format(
            self.id, str(self.items), str(self.price), self.status, str(self.date))
