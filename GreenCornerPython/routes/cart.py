from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from models import db, Product

cart_bp = Blueprint('cart', __name__)

def get_cart_items():
    cart = session.get('cart', {})
    items = []
    subtotal = 0
    total_quantity = 0

    if not cart:
        return items, subtotal, total_quantity

    product_ids = [int(pid) for pid in cart.keys()]
    products = Product.query.filter(Product.product_id.in_(product_ids)).all()
    product_dict = {p.product_id: p for p in products}

    for pid_str, qty in list(cart.items()):
        pid = int(pid_str)
        product = product_dict.get(pid)
        if product and product.is_active:
            # Validate max stock
            qty = max(1, min(qty, product.quantity))
            line_total = product.price * qty
            items.append({
                'product': product,
                'quantity': qty,
                'unit_price': product.price,
                'line_total': line_total,
                'formatted_line_total': f"{int(line_total):,} ₫".replace(",", ".")
            })
            subtotal += line_total
            total_quantity += qty
        else:
            # Remove inactive or deleted product
            del cart[pid_str]
            session.modified = True

    return items, subtotal, total_quantity


@cart_bp.route('/cart')
def index():
    items, subtotal, total_quantity = get_cart_items()
    # Check free shipping rule (> 300,000đ)
    free_shipping = subtotal >= 300000
    shipping_estimate = 0 if free_shipping else 30000
    total = subtotal + shipping_estimate

    return render_template(
        'cart/index.html',
        items=items,
        subtotal=subtotal,
        total_quantity=total_quantity,
        free_shipping=free_shipping,
        shipping_estimate=shipping_estimate,
        total=total
    )


@cart_bp.route('/cart/add/<int:product_id>', methods=['GET', 'POST'])
def add(product_id):
    product = Product.query.get_or_404(product_id)
    if product.quantity <= 0:
        flash(f'Sản phẩm "{product.product_name}" hiện đã hết hàng!', 'error')
        return redirect(request.referrer or url_for('products.index'))

    qty = request.form.get('quantity', 1, type=int) if request.method == 'POST' else 1
    if qty < 1:
        qty = 1

    cart = session.get('cart', {})
    pid_str = str(product_id)
    current_qty = cart.get(pid_str, 0)
    new_qty = min(current_qty + qty, product.quantity)

    cart[pid_str] = new_qty
    session['cart'] = cart
    session.modified = True

    if request.form.get('buy_now') == '1':
        return redirect(url_for('checkout.index'))

    flash(f'Đã thêm "{product.product_name}" vào giỏ hàng thành công!', 'success')
    return redirect(request.referrer or url_for('cart.index'))


@cart_bp.route('/cart/update', methods=['POST'])
def update():
    cart = session.get('cart', {})
    product_id = request.form.get('product_id', type=int)
    quantity = request.form.get('quantity', type=int)

    if product_id and quantity is not None:
        pid_str = str(product_id)
        if quantity <= 0:
            if pid_str in cart:
                del cart[pid_str]
        else:
            product = db.session.get(Product, product_id)
            if product:
                cart[pid_str] = min(quantity, product.quantity)

        session['cart'] = cart
        session.modified = True
        flash('Đã cập nhật giỏ hàng!', 'success')

    return redirect(url_for('cart.index'))


@cart_bp.route('/cart/remove/<int:product_id>', methods=['POST', 'GET'])
def remove(product_id):
    cart = session.get('cart', {})
    pid_str = str(product_id)
    if pid_str in cart:
        del cart[pid_str]
        session['cart'] = cart
        session.modified = True
        flash('Đã xóa sản phẩm khỏi giỏ hàng.', 'success')

    return redirect(url_for('cart.index'))


@cart_bp.route('/cart/clear', methods=['POST'])
def clear():
    session.pop('cart', None)
    flash('Đã làm trống giỏ hàng.', 'success')
    return redirect(url_for('cart.index'))
