from flask_restful import Resource,reqparse, fields, marshal_with
from .models import db
from .models import Category, Products
from flask import jsonify, request
from flask.views import MethodView
from .validation import NotFoundError,BusinessValidationError
category_fields = {
    "id": fields.Integer,
    "category_id": fields.String,
    "user_id": fields.Integer,
}
product_fields = {
    "id": fields.Integer,
    "name": fields.String,
    "description": fields.String,
    "unit": fields.String,
    "rate_unit": fields.Float,
    "quantity": fields.Float,
    "quantity_sold": fields.Float,
    # Add other product attributes here if needed
}
output_fields = {
    "id": fields.Integer,
    "category_id": fields.String,
    "user_id": fields.Integer,
    "products": fields.List(fields.Nested({
        "id": fields.Integer,
        "name": fields.String,
        "description": fields.String,
        "unit": fields.String,
        "rate_unit": fields.Integer,
        "quantity": fields.Integer,
        "quantity_sold": fields.Integer
    }))
}

create_user_parser = reqparse.RequestParser()
create_user_parser.add_argument('category_id')
create_user_parser.add_argument('user_id')

from flask_restful import reqparse

# Update the parser definition
update_category_parser = reqparse.RequestParser()
update_category_parser.add_argument("category_id", type=str, required=True, help="Category ID is required")

update_product_parser = reqparse.RequestParser()
update_product_parser.add_argument("name", type=str, required=True, help="Product name is required")
update_product_parser.add_argument("description", type=str, required=True, help="Product description is required")
update_product_parser.add_argument("unit", type=str, required=True, help="Product unit is required")
update_product_parser.add_argument("rate_unit", type=int, required=True, help="Product rate unit is required")
update_product_parser.add_argument("quantity", type=int, required=True, help="Product quantity is required")
update_product_parser.add_argument("quantity_sold", type=int, required=True, help="Product quantity sold is required")




class CategoryAPI(Resource):
    def put(self, user_id, category_id):
        args = update_category_parser.parse_args()
        new_category_id = args.get("category_id", None)
    
    # Check if the category with the given category_id exists for the provided user_id in the database
        category = Category.query.filter_by(user_id=user_id, category_id=category_id).first()

        if category:
        # Update the category name for all associated products
            products = Products.query.filter_by(user_id=user_id, category_id=category_id).all()
            for product in products:
                 product.category_id = new_category_id
        
        # Update the category with the new category_id
            category.category_id = new_category_id

        # Commit the changes to the database
            db.session.commit()

        # Return the updated category as the response
            return "", 200
        else:
        # If the category with the given category_id does not exist for the provided user_id,
        # return a response with an error message
            return {"message": "Category not found for the provided user_id"}, 404

    @marshal_with(output_fields)
    def get(self, category_id=None,user_id =None):
        if category_id:
        # Fetch a specific category by category_id from the database
            category = Category.query.filter_by(user_id=user_id, category_id=category_id).first()
            if category:
                return category
            else:
                raise NotFoundError(status_code=404)
        else:
        # Fetch all categories from the database
            categories = Category.query.all()
            category_list = []
            for category in categories:
                category_data = {
                    "id": category.id,
                    "category_id": category.category_id,
                    "user_id": category.user_id,
                    "products": [
                        {
                            "id": product.id,
                            "name": product.name,
                            "description": product.description,
                            "unit": product.unit,
                            "rate_unit": product.rate_unit,
                            "quantity": product.quantity,
                            "quantity_sold": product.quantity_sold
                        }
                        for product in category.products
                    ]
                }
                category_list.append(category_data)

            return category_list

    
    def post(self):
        args = create_user_parser.parse_args()
        category_id = args.get("category_id",None)
        user_id = args.get("user_id", None)
        
        if category_id is None:
            raise BusinessValidationError(status_code=400, error_code="BE1001", error_message="category name is required")
        
        if user_id is None:
            raise BusinessValidationError(status_code=400, error_code="BE1002", error_message="user id is required")
        
        category = Category(category_id=category_id, user_id=user_id)

        # Add the new category to the database
        db.session.add(category)
        db.session.commit()
        return "" ,201
        
        
        

    def delete(self, user_id, category_id):
    # Check if the category with the given category_id exists for the provided user_id in the database
        category = Category.query.filter_by(user_id=user_id, category_id=category_id).first()

        if category:
            try:
            # Fetch associated products and delete them
                products = Products.query.filter_by(category_id=category_id, user_id=user_id).all()
                for product in products:
                    db.session.delete(product)

            # Delete the category from the database
                db.session.delete(category)
                db.session.commit()

            # Return a response with a status code 204 (No Content) to indicate successful deletion
                return "", 204
            except Exception as e:
            # Handle any exceptions that occur during the deletion process
                db.session.rollback()
                return {"message": f"Error deleting category: {str(e)}"}, 500
        else:
        # If the category with the given category_id does not exist for the provided user_id,
        # return a response with an error message
            return {"message": "Category not found for the provided user_id"}, 404


class ProductAPI(Resource):
    def __init__(self):
        self.add_product_parser = reqparse.RequestParser()
        self.add_product_parser.add_argument('name', type=str, required=True, help='Name of the product is required')
        self.add_product_parser.add_argument('description', type=str, required=True, help='Description of the product is required')
        self.add_product_parser.add_argument('unit', type=str, required=True, help='Unit of the product is required')
        self.add_product_parser.add_argument('rate_unit', type=int, required=True, help='Rate unit of the product is required')
        self.add_product_parser.add_argument('quantity', type=int, required=True, help='Quantity of the product is required')

        super(ProductAPI, self).__init__()

    def post(self, user_id, category_id):
        # Parse the request data using the add_product_parser
        args = self.add_product_parser.parse_args()

        # Check if the provided user_id and category_id exist in the database
        category = Category.query.filter_by(user_id=user_id, category_id=category_id).first()
        if not category:
            return {"message": "Category not found for the provided user_id and category_id"}, 404

        # Create a new product with the provided data
        product = Products(
            name=args['name'],
            description=args['description'],
            unit=args['unit'],
            rate_unit=args['rate_unit'],
            quantity=args['quantity'],
            category_id=category_id,
            user_id=user_id
        )

        # Add the new product to the database
        db.session.add(product)
        db.session.commit()

        return {"message": "Product added successfully"}, 201
    
    def get(self, user_id, category_id):
    # Check if the provided user_id and category_id exist in the database
        category = Category.query.filter_by(user_id=user_id, category_id=category_id).first()
        if not category:
            return {"message": "Category not found for the provided user_id and category_id"}, 404

    # Get the product_name query parameter from the request
        product_name = request.args.get('product_name')

        if product_name:
        # Fetch products based on user_id, category_id, and product_name
            products = Products.query.filter_by(user_id=user_id, category_id=category_id, name=product_name).all()
        else:
        # Fetch all products for the given category_id and user_id
            products = Products.query.filter_by(user_id=user_id, category_id=category_id).all()

    # Convert the products to a list of dictionaries
        product_list = []
        for product in products:
            product_data = {
                "id": product.id,
                "name": product.name,
                "description": product.description,
                "unit": product.unit,
                "rate_unit": product.rate_unit,
                "quantity": product.quantity,
                "quantity_sold": product.quantity_sold
            }
            product_list.append(product_data)

        return product_list, 200

    
    
    def delete(self, user_id, category_id, product_name):
        # Check if the product with the given product_name exists for the provided user_id and category_id in the database
        product = Products.query.filter_by(user_id=user_id, category_id=category_id, name=product_name).first()

        if product:
            # Delete the product from the database
            db.session.delete(product)
            db.session.commit()

            # Return a response with a status code 204 (No Content) to indicate successful deletion
            return "", 204
        else:
            # If the product with the given product_name does not exist for the provided user_id and category_id,
            # return a response with an error message
            return {"message": "Product not found for the provided user_id and category_id"}, 404
        
    def put(self, user_id, category_id, product_name):
        args = update_product_parser.parse_args()
        new_name = args.get("name")
        new_description = args.get("description")
        new_unit = args.get("unit")
        new_rate_unit = args.get("rate_unit")
        new_quantity = args.get("quantity")
        new_quantity_sold = args.get("quantity_sold")

        # Check if the product with the given product_name exists for the provided user_id and category_id in the database
        product = Products.query.filter_by(user_id=user_id, category_id=category_id, name=product_name).first()

        if product:
            # Update the product with the new values
            product.name = new_name
            product.description = new_description
            product.unit = new_unit
            product.rate_unit = new_rate_unit
            product.quantity = new_quantity
            product.quantity_sold = new_quantity_sold

            # Commit the changes to the database
            db.session.commit()

            # Return the updated product as the response
            return "", 200
        else:
            # If the product with the given product_name does not exist for the provided user_id and category_id,
            # return a response with an error message
            return {"message": "Product not found for the provided user_id, category_id, and product_name"}, 404
class DisplayAPI(Resource):
    @marshal_with(category_fields)  # Use the marshal decorator with the output fields
    def get(self):
        # Fetch all categories for the provided user_id from the database
        categories = Category.query.all()

        # Return the list of categories as a response
        return categories, 200
    
    @marshal_with(product_fields)  # Use the marshal decorator with the output fields
    def get(self):
        # Fetch all products from the database
        products = Products.query.all()

        # Return the list of products as a response
        return products, 200