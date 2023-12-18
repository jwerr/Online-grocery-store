from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api
from os import path
from flask_login import LoginManager
from flask_cors import CORS

db = SQLAlchemy()
DB_NAME = "database.db"
app = None
api = None

def create_app():
    
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'hjshjhdjah kjshkjdhjs'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    db.init_app(app)
    api = Api(app)

    # Enable CORS for all routes
    CORS(app)

    # Import and register your views and models here
    from .views import views
    from .auth import auth
    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    from .models import User, Category, Products, CartItem, PurchaseItem
    # Register your models with the SQLAlchemy
    with app.app_context():
        db.create_all()

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    # Register your API resource here
    from .api import CategoryAPI,ProductAPI, DisplayAPI
    api.add_resource(CategoryAPI, "/api/category","/api/user/category/<string:category_id>","/api/user/<int:user_id>/category/<string:category_id>")
    api.add_resource(ProductAPI, '/api/user/<int:user_id>/category/<string:category_id>/product',"/api/user/<int:user_id>/category/<string:category_id>/product/<string:product_name>")
    api.add_resource(DisplayAPI, '/api/categories','/api/products')

    return app, api

def create_database(app):
    if not path.exists('website/' + DB_NAME):
        db.create_all(app=app)
        print('Created Database!')
