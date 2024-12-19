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
    customer_cart = Cart.query.filter_by(customer_link=current_user.id)
    if customer_cart.count() > 0:  # Change this to check if there are any cart items
        try:
            total = 0
            for item in customer_cart:
                total += item.product.current_price * item.quantity

            service = APIService(token=API_TOKEN, publishable_key=API_PUBLISHABLE_KEY, test=True)
            create_order_response = service.collect.mpesa_stk_push(
                phone_number='8810223022', email=current_user.email,
                amount=total + 200, narrative='Purchase of goods'
            )

            print(create_order_response)  # Print the response for debugging

            for item in customer_cart:
                new_order = Order()
                new_order.quantity = item.quantity
                new_order.price = item.product.current_price
                new_order.status = create_order_response['invoice']['state'].capitalize()
                new_order.payment_id = create_order_response['id']

                new_order.product_link = item.product_link
                new_order.customer_link = item.customer_link

                db.session.add(new_order)

                product = Product.query.get(item.product_link)
                product.in_stock -= item.quantity
                db.session.delete(item)

            db.session.commit()  # Commit everything together after the loop

            flash('Order Placed Successfully', 'success')
            return redirect('/orders')

        except Exception as e:
            print("Error placing order:", e)
            flash(f'Order not placed. Error: {str(e)}', 'danger')
            return redirect('/')

    else:
        flash('Your cart is Empty', 'warning')
        return redirect('/')


@views.route('/orders')
@login_required
def order():
    orders = Order.query.filter_by(customer_link=current_user.id).all()  # Corrected to use 'Order'
    return render_template('orders.html', orders=orders)
