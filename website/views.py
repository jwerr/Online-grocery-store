from flask import render_template, redirect, url_for, flash
from flask import Flask, render_template, request, jsonify, g, session, url_for, redirect, flash, Markup, Blueprint

from flask_login import login_required, current_user
from .models import  Category,  Products, CartItem, PurchaseItem
from flask_wtf import CSRFProtect

from . import db

views = Blueprint('views', __name__)

@views.route('/')
@login_required
def display_products_by_category():
    # Fetch all products from the database
    products = Products.query.all()

    # Create a dictionary to group products by their category names
    products_by_category = {}
    for product in products:
        if product.category:  # Check if the product has an associated category
            category_name = product.category.category_id
            if category_name not in products_by_category:
                products_by_category[category_name] = []
            products_by_category[category_name].append(product)

    print(products_by_category)

    return render_template('display_category_product.html', products_by_category=products_by_category, user=current_user)

@views.route('/add_category', methods=['POST', 'GET'])
@login_required
def index():
    return render_template('manager.html',user = current_user)

@views.route('/process_selection', methods=['POST', 'GET'])
@login_required
def home():
    if request.method == 'POST':
        note = request.form.get('selected_item')  # Gets the note from the HTML

        # providing the schema for the note
        new_note = Category(category_id=note, user_id=current_user.id)
        db.session.add(new_note)  # adding the note to the database
        db.session.commit()
        flash('Category added!', category='success')

    return redirect(url_for('views.display_categories'))


@views.route('/display_categories')
@login_required
def display_categories():
    # Fetch all categories from the database for the current user
    current_user_id = current_user.id
    categories = Category.query.filter_by(user_id=current_user_id).all()

    # Fetch all products for each category
    category_products = {}
    for category in categories:
        products = Products.query.filter_by(
            category_id=category.category_id, user_id=current_user.id).all()
        category_products[category.category_id] = products

    # Render the template to display the categories and their products
    return render_template('categories_display.html', categories=categories, user=current_user, category_products=category_products)


@views.route('/add_items/<category_id>', methods=['GET', 'POST'])
@login_required
def add_items(category_id):
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        unit = request.form['unit']
        rate_unit = int(request.form['rate_unit'])
        quantity = int(request.form['quantity'])

        # Create the product and set the user_id and category_id
        new_product = Products(
            name=name,
            description=description,
            unit=unit,
            rate_unit=rate_unit,
            quantity=quantity,
            category_id=category_id,
            user_id=current_user.id
        )

        db.session.add(new_product)
        db.session.commit()

        flash('Product added successfully', 'success')
        return redirect(url_for('views.display_categories'))

    return render_template('add_items.html', category_id=category_id, user=current_user)

# In your_app/views.py


@views.route('/action', methods=['POST'])
@login_required
def action():
    # Get the selected category_id from the form
    category_id = request.form.get('category_id')
    # Fetch the selected category from the database
    category = Category.query.get(category_id)
    # Fetch products associated with the category
    products = Products.query.filter_by(
        category_id=category_id, user_id=current_user.id).all()
    return render_template('home.html', category=category, products=products, user=current_user)


@views.route('/new_user')
@login_required
def new_user():
    return render_template('manager.html', user=current_user)


@views.route('/delete_category/<category_id>', methods=['POST'])
@login_required
def delete_category(category_id):
    category = Category.query.filter_by(
        category_id=category_id, user_id=current_user.id).first()
    if not category:
        flash('Category not found or you do not have permission to delete it', 'danger')
        return redirect(url_for('views.display_categories'))

    try:
        print(
            f'Deleting Category: {category.category_id}, User ID: {category.user_id}')

        # Fetch associated products for logging
        products = Products.query.filter_by(
            category_id=category.category_id, user_id=current_user.id).all()
        print(f'Associated Products: {[product.id for product in products]}')
        for product in products:
            db.session.delete(product)

        db.session.delete(category)
        db.session.commit()

        flash('Category and associated products deleted successfully', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error deleting category and products', 'danger')
        print(f'Error: {str(e)}')

    return redirect(url_for('views.display_categories'))


@views.route('/update_category/<category_id>', methods=['GET', 'POST'])
@login_required
def update_category(category_id):
    category = Category.query.filter_by(
        category_id=category_id, user_id=current_user.id).first()
    if not category:
        flash('Category not found or you do not have permission to update it', 'danger')
        return redirect(url_for('views.display_categories'))

    if request.method == 'POST':
        new_category_id = request.form['new_category_id']
        category.category_id = new_category_id

        # Update the category ID and name in associated products
        products = Products.query.filter_by(
            category_id=category_id, user_id=current_user.id).all()
        for product in products:
            product.category_id = new_category_id
            # product.category_name = category.category_id  # Or update the category name as needed
        db.session.commit()

        flash('Category updated successfully', 'success')
        return redirect(url_for('views.display_categories'))

    return render_template('update_category.html', category=category, user=current_user)


@views.route('/update_product/<int:product_id>', methods=['GET', 'POST'])
@login_required
def update_product(product_id):
    product = Products.query.get(product_id)

    if not product:
        flash('Product not found', 'danger')
        return redirect(url_for('views.display_categories'))

    if request.method == 'POST':
        # Get the updated product data from the form
        name = request.form['product_name']
        description = request.form['product_description']
        unit = request.form['unit']
        rate_unit = int(request.form['rate_unit'])
        quantity = int(request.form['quantity'])

        # Update the product details in the database
        product.name = name
        product.description = description
        product.unit = unit
        product.rate_unit = rate_unit
        product.quantity = quantity
        db.session.commit()

        flash('Product updated successfully', 'success')
        return redirect(url_for('views.display_categories'))

    return render_template('update_product.html', product=product, user=current_user)


@views.route('/delete_product/<int:product_id>', methods=['POST', 'GET'])
@login_required
def delete_product(product_id):
    product = Products.query.get(product_id)

    if not product:
        flash('Product not found', 'danger')
        return redirect(url_for('views.display_categories'))

    # Delete the product from the database
    db.session.delete(product)
    db.session.commit()

    flash('Product deleted successfully', 'success')
    return redirect(url_for('views.display_categories'))

@views.route('/add_to_cart/<int:product_id>', methods=['GET'])
@login_required
def add_to_cart(product_id):
    # Fetch the selected product details using the get_product_by_id() function
    selected_product = get_product_by_id(product_id)

    # Render the add_to_cart.html template and pass the selected product and quantity
    return render_template('add_to_cart.html', selected_product=selected_product, user = current_user)


def get_product_by_id(product_id):
    # Assuming you have a Products model defined with SQLAlchemy
    product = Products.query.get(product_id)
    return product



@views.route('/calculate_and_add_to_cart/<int:product_id>', methods=['POST'])
@login_required
def calculate_and_add_to_cart(product_id):
    selected_product = Products.query.get(product_id)
    if not selected_product:
        flash('Selected product not found.', category='error')
        return redirect(url_for('views.display_products_by_category'))

    quantity = int(request.form.get('quantity'))
    amount = selected_product.rate_unit * quantity
    print(amount)

    cart_item = CartItem.query.filter_by(user_id=current_user.id, product_id=product_id).first()
    selected_product.quantity -= quantity

    if cart_item:
        cart_item.quantity += quantity
    else:
        cart_item = CartItem(user_id=current_user.id, product_id=product_id, quantity=quantity)

    db.session.add(cart_item)
    db.session.commit()

    # Update the quantity_sold attribute for the selected_product
    selected_product.quantity_sold += quantity
    db.session.commit()

    flash('Product added to cart!', category='success')
    return redirect(url_for('views.display_products_by_category'))

from sqlalchemy import or_


@views.route('/search', methods=['GET'])
@login_required
def search():
    query = request.args.get('query')
    # Perform the search operation based on the query
    # Query the database to find results that match the category, product, or rate
    results = Products.query.filter(
        or_(
            Products.category_id.ilike(f'%{query}%'),
            Products.name.ilike(f'%{query}%'),
            Products.rate_unit.ilike(f'%{query}%')
        )
    ).all()

    return render_template('search_results.html', query=query, results=results , user = current_user)


@views.route('/cart')
@login_required
def cart():
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    total_amount = sum(item.price for item in cart_items)

    return render_template('cart.html', cart_items=cart_items, total_amount=total_amount, user = current_user)


@views.route('/buy_now', methods=['POST'])
@login_required
def buy_now():
    cart_items = CartItem.query.filter_by(user_id=current_user.id, purchased=False).all()

    # Perform any additional processing or calculations related to the purchase here

    # Create purchased items and store them in the PurchaseItem table
    for item in cart_items:
        purchased_item = PurchaseItem(
            user_id=item.user_id,
            product_id=item.product_id,
            quantity=item.quantity,
            price=item.price  # Set the price from the cart item's price
        )
        db.session.add(purchased_item)

    # Clear the cart by deleting cart items
    CartItem.query.filter_by(user_id=current_user.id, purchased=False).delete()

    db.session.commit()

    flash('Purchase successful!', category='success')
    return redirect(url_for('views.display_products_by_category'))



@views.route('/profile', methods=['GET'])
@login_required  
def profile():
    user = current_user
    purchase_history = PurchaseItem.query.filter_by(user_id=current_user.id).all()

    return render_template('profile.html', user=user, purchase_history=purchase_history)


from sqlalchemy import func

@views.route('/manager_dashboard')
@login_required
def manager_dashboard():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    if current_user.is_authenticated and 'manager' in [role.name for role in current_user.roles]:
        # Fetch the products associated with the manager
        manager_products = Products.query.filter_by(user_id=current_user.id).all()

        # Calculate the quantity sold and total amount for each product
        product_details = []
        for product in manager_products:
            quantity_sold = db.session.query(func.sum(PurchaseItem.quantity)).filter_by(product_id=product.id).scalar() or 0
            total_amount = db.session.query(func.sum(PurchaseItem.price)).filter_by(product_id=product.id).scalar() or 0
            product_details.append({
                'product': product,
                'quantity_sold': quantity_sold,
                'total_amount': total_amount
            })

        return render_template('manager_d.html', product_details=product_details, user = current_user)

    flash('You are not authorized to access this page.', category='error')
    return redirect(url_for('views.display_products_by_category'))



@views.route('/remove_product/<int:product_id>', methods=['POST'])
def remove_product(product_id):
    # Get the current user
    user = current_user

    # Find the cart item associated with the product_id and user_id
    cart_item = CartItem.query.filter_by(user_id=user.id, product_id=product_id).first()

    # Remove the cart item if it exists
    if cart_item:
        db.session.delete(cart_item)
        db.session.commit()

    # Redirect back to the cart page
    return redirect(url_for('views.cart'))

