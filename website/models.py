from . import db
from flask_login import UserMixin
from flask_security import RoleMixin


roles_users = db.Table('roles_users',
                       db.Column('user_id', db.Integer(),
                                 db.ForeignKey('user.id')),
                       db.Column('role_id', db.Integer(), db.ForeignKey('role.id')))


class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    # name = db.Column(db.String, unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    category = db.relationship('Category')
    roles = db.relationship('Role', secondary=roles_users, backref='roled')
    # categories = db.relationship('Category', secondary=user_category, backref='users')


class Role(db.Model, RoleMixin):
    __tablename__ = 'role'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)

    def __repr__(self):
        return self.name


class Category(db.Model):
    __tablename__ = 'category'
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    category_id = db.Column(db.String, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    products = db.relationship('Products', backref='category', lazy=True, cascade='all, delete-orphan', passive_deletes=True)


class Products(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.String(100), nullable=False)
    unit = db.Column(db.String, nullable=False)
    rate_unit = db.Column(db.Integer, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    # Add this field to track quantity sold
    quantity_sold = db.Column(db.Integer, default=0)
    category_id = db.Column(db.String, db.ForeignKey('category.category_id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


class CartItem(db.Model):
    __tablename__ = 'cart_item'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey(
        'products.id'), nullable=False)
    quantity = db.Column(db.Integer)
    # Add a new field to track purchased items
    purchased = db.Column(db.Boolean, default=False)

    user = db.relationship('User', backref='cart_items')
    product = db.relationship('Products')

    @property
    def price(self):
        return self.quantity * self.product.rate_unit


class PurchaseItem(db.Model):
    __tablename__ = 'purchase_item'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey(
        'products.id'), nullable=False)
    quantity = db.Column(db.Integer)
    price = db.Column(db.Float)

    user = db.relationship('User', backref='purchase_items')
    product = db.relationship('Products')
