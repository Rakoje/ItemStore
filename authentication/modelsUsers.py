from flask_sqlalchemy import SQLAlchemy

database = SQLAlchemy()


class User(database.Model):
    __tablename__ = "users"

    id = database.Column(database.Integer, primary_key=True)
    forename = database.Column(database.String(256), nullable=False)
    surname = database.Column(database.String(256), nullable=False)
    email = database.Column(database.String(256), nullable=False, unique=True)
    password = database.Column(database.String(256), nullable=False)
    isCustomer = database.Column(database.Boolean(), nullable=False)
    role = database.Column(database.String(256), nullable=False)

    def __str__(self):
        return "({}, {}, {}, {}, {})".format(self.id, self.forename, self.surname, self.email, self.isCustomer)
