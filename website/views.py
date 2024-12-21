from flask import Blueprint, render_template, flash, redirect, request, jsonify
from .models import Product, Cart, Order
from flask_login import login_required, current_user
from . import db


views = Blueprint('views', __name__)


@views.route('/')
def home():

    items = Product.query.filter_by(flash_sale=True).all()  

    return render_template('home.html', items=items, cart=Cart.query.filter_by(customer_link=current_user.id).all()
                           if current_user.is_authenticated else [])


@views.route('/add-to-cart/<int:item_id>')
@login_required
def add_to_cart(item_id):
    item_to_add = Product.query.get(item_id)
    if not item_to_add:
        flash("The product does not exist.")
        return redirect(request.referrer or '/')

    item_exists = Cart.query.filter_by(product_link=item_id, customer_link=current_user.id).first()

    if item_exists:
        try:
            item_exists.quantity += 1
            db.session.commit()
            flash(f'Quantity of {item_exists.product.product_name} updated in the cart.')
        except Exception as e:
            print(f"Error updating item quantity: {e}")
            flash(f"Failed to update the quantity of {item_exists.product.product_name}.")
    else:
        try:
            new_cart_item = Cart(
                quantity=1,
                product_link=item_to_add.id,
                customer_link=current_user.id
            )
            db.session.add(new_cart_item)
            db.session.commit()
            flash(f"{item_to_add.product_name} added to the cart.")
        except Exception as e:
            print(f"Error adding item to cart: {e}")
            flash(f"Failed to add {item_to_add.product_name} to the cart.")
    
    return redirect(request.referrer or '/')

    

@views.route('/cart')
@login_required
def show_cart():
    cart = Cart.query.filter_by(customer_link=current_user.id).all()
    amount = 0
    for item in cart:
        amount += item.product.current_price * item.quantity

    return render_template('cart.html', cart=cart, amount=amount, total=amount+200) #200 is the shipping fees


@views.route('/pluscart')
@login_required
def plus_cart():
    if request.method == 'GET':
        cart_id = request.args.get('cart_id')
        cart_item = Cart.query.get(cart_id)
        cart_item.quantity = cart_item.quantity + 1
        db.session.commit()

        cart = Cart.query.filter_by(customer_link=current_user.id).all()

        amount = 0

        for item in cart:
            amount += item.product.current_price * item.quantity

        data = {
            'quantity': cart_item.quantity,
            'amount': amount,
            'total': amount + 200
        }

        return jsonify(data)


@views.route('/minuscart')
@login_required
def minus_cart():
    if request.method == 'GET':
        cart_id = request.args.get('cart_id')
        cart_item = Cart.query.get(cart_id)
        cart_item.quantity = cart_item.quantity - 1
        db.session.commit()

        cart = Cart.query.filter_by(customer_link=current_user.id).all()

        amount = 0

        for item in cart:
            amount += item.product.current_price * item.quantity

        data = {
            'quantity': cart_item.quantity,
            'amount': amount,
            'total': amount + 200
        }

        return jsonify(data)


@views.route('removecart')
@login_required
def remove_cart():
    if request.method == 'GET':
        cart_id = request.args.get('cart_id')
        cart_item = Cart.query.get(cart_id)
        db.session.delete(cart_item)
        db.session.commit()

        cart = Cart.query.filter_by(customer_link=current_user.id).all()

        amount = 0

        for item in cart:
            amount += item.product.current_price * item.quantity

        data = {
            'quantity': cart_item.quantity,
            'amount': amount,
            'total': amount + 200
        }

        return jsonify(data)


@views.route('/place-order')
@login_required
def place_order():
    customer_cart = Cart.query.filter_by(customer_link=current_user.id).all()
    if customer_cart:  # Check if the cart is not empty
        try:
            total = 0
            for item in customer_cart:
                total += item.product.current_price * item.quantity

            # Process the order without the API service
            for item in customer_cart:
                new_order = Order()
                new_order.quantity = item.quantity
                new_order.price = item.product.current_price
                new_order.status = 'Pending'  # Order status
                new_order.payment_id = 'N/A'  # No payment integration, so set a placeholder value

                new_order.product_link = item.product_link
                new_order.customer_link = item.customer_link

                db.session.add(new_order)

                product = Product.query.get(item.product_link)
                product.in_stock -= item.quantity
                db.session.delete(item)  # Remove the item from the cart

            db.session.commit()  # Commit all changes

            flash('Order Placed Successfully', 'success')
            return redirect('/orders')

        except Exception as e:
            print("Error placing order:", e)
            flash(f'Order not placed. Error: {str(e)}', 'danger')
            return redirect('/')

    else:
        flash('Your cart is empty', 'warning')
        return redirect('/')



@views.route('/orders')
@login_required
def order():
    if current_user.is_admin:
        # If the user is admin, show pending orders (orders that are not approved yet)
        orders = Order.query.filter_by(is_approved=False).all()
        return render_template('pending_orders.html', orders=orders)

    # If the user is not an admin, show their own orders
    orders = Order.query.filter_by(customer_link=current_user.id).all()
    return render_template('orders.html', orders=orders)



@views.route('/admin/orders')
@login_required
def admin_orders():
    if not current_user.is_admin:
        flash('Access denied', 'danger')
        return redirect('/')

    # Get orders that are pending approval
    orders = Order.query.filter_by(is_approved=False).all()
    return render_template('admin_orders.html', orders=orders)



@views.route('/admin/approve-order/<int:order_id>', methods=['GET', 'POST'])
@login_required
def approve_order(order_id):
    if not current_user.is_admin:
        flash('Access denied', 'danger')
        return redirect('/')

    order = Order.query.get(order_id)
    if not order:
        flash('Order not found', 'danger')
        return redirect('/orders')

    if request.method == 'POST':
        try:
            order.is_approved = True
            order.status = 'Approved'
            db.session.commit()

            flash('Order has been approved!', 'success')
            return redirect('/admin/orders')
        except Exception as e:
            print(f"Error approving order: {e}")
            flash('Error approving order.', 'danger')

    # Render confirmation page for GET request
    return render_template('approve_order_confirmation.html', order=order)




@views.route('/pending-orders')
@login_required
def pending_orders():
    if not current_user.is_admin:
        flash('Access denied', 'danger')
        return redirect('/')

    orders = Order.query.filter_by(is_approved=False).all()  # Get all pending orders
    return render_template('pending_orders.html', orders=orders)
