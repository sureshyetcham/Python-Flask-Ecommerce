from flask import Blueprint, render_template, flash, redirect, request, jsonify
from .models import Product, Cart, Order
from flask_login import login_required, current_user
from . import db
from .payment import client, RAZORPAY_KEY_ID
views = Blueprint('views', __name__)


@views.route('/')
def home():
    items = Product.query.filter_by(flash_sale=True)

    return render_template('home.html', items=items, cart=Cart.query.filter_by(customer_link=current_user.id).all()
                           if current_user.is_authenticated else [])




@views.route('/add_to_cart/<int:item_id>')
@login_required
def add_to_cart(item_id):
    item_to_add = Product.query.get(item_id)
    item_exists = Cart.query.filter_by(product_link=item_id, customer_link=current_user.id).first()
    if item_exists:
        try:
            item_exists.quantity = item_exists.quantity + 1
            db.session.commit()
            flash(f' Quantity of { item_exists.product.product_name } has been updated')
            return redirect(request.referrer)
        except Exception as e:
            print('Quantity not Updated', e)
            flash(f'Quantity of { item_exists.product.product_name } not updated')
            return redirect(request.referrer)

    new_cart_item = Cart()
    new_cart_item.quantity = 1
    new_cart_item.product_link = item_to_add.id
    new_cart_item.customer_link = current_user.id

    try:
        db.session.add(new_cart_item)
        db.session.commit()
        flash(f'{new_cart_item.product.product_name} added to cart')
    except Exception as e:
        print('Item not added to cart', e)
        flash(f'{new_cart_item.product.product_name} has not been added to cart')

    return redirect(request.referrer)

@views.route('/cart')
@login_required
def show_cart():
    cart = Cart.query.filter_by(customer_link=current_user.id).all()
    amount = 0
    for item in cart:
        amount += item.product.current_price * item.quantity

    return render_template('cart.html', cart=cart, amount=amount, total=amount+200)

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






@views.route('/removecart')
@login_required
def remove_cart():

    cart_id = request.args.get('cart_id')
    cart_item = Cart.query.get(cart_id)

    if cart_item:
        db.session.delete(cart_item)
        db.session.commit()

    cart = Cart.query.filter_by(customer_link=current_user.id).all()

    amount = sum(item.product.current_price * item.quantity for item in cart)

    return jsonify({
        'amount': amount,
        'total': amount + 200 if amount > 0 else 0,
        'cart_count': len(cart)
    })



@views.route('/place-order')
@login_required
def place_order():

    cart = Cart.query.filter_by(
        customer_link=current_user.id
    ).all()

    amount = 0

    for item in cart:
        amount += item.product.current_price * item.quantity

    total = amount + 200

    razorpay_order = client.order.create({
        "amount": int(total * 100),
        "currency": "INR",
        "payment_capture": 1
    })

    return render_template(
        'place_order.html',
        total=total,
        razorpay_order_id=razorpay_order['id'],
        razorpay_key=RAZORPAY_KEY_ID
    )


@views.route('/payment-success')
@login_required
def payment_success():

    payment_id = request.args.get('payment_id')

    cart_items = Cart.query.filter_by(
        customer_link=current_user.id
    ).all()

    for item in cart_items:

        order = Order(
            quantity=item.quantity,
            price=item.product.current_price * item.quantity,
            status='Paid',
            payment_id=payment_id,
            customer_link=current_user.id,
            product_link=item.product.id
        )

        db.session.add(order)

    for item in cart_items:
        db.session.delete(item)

    db.session.commit()

    flash('Order placed successfully!', 'success')

    return redirect('/orders')


@views.route('/orders')
@login_required
def order():
    orders = Order.query.filter_by(customer_link=current_user.id).all()
    return render_template('orders.html', orders=orders)


@views.route('/search')
def search():

    search_query = request.args.get('search', '')

    items = []

    if search_query:
        items = Product.query.filter(
            Product.product_name.ilike(f'%{search_query}%')
        ).all()

    return render_template(
        'search.html',
        items=items,
        cart=Cart.query.filter_by(customer_link=current_user.id).all()
        if current_user.is_authenticated else []
    )