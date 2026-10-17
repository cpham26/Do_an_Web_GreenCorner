from urllib.parse import urlparse
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models import db, Product

cart_bp = Blueprint('cart', __name__)

def safe_referrer(fallback_endpoint='products.index'):
    ref = request.referrer
    if ref:
        parsed = urlparse(ref)
        if not parsed.netloc or parsed.netloc == request.host:
            return ref
    return url_for(fallback_endpoint)


def get_cart_items():
    cart = session.get('cart', {})
    items = []
    subtotal = 0
    total_quantity = 0

    if not cart or not isinstance(cart, dict):
        return items, subtotal, total_quantity

    valid_pids = []
    for k in list(cart.keys()):
        try:
            valid_pids.append(int(k))
        except (ValueError, TypeError):
            del cart[k]
            session.modified = True

    if not valid_pids:
        return items, subtotal, total_quantity

    products = Product.query.filter(Product.product_id.in_(valid_pids)).all()
    product_dict = {p.product_id: p for p in products}

    for pid_str, raw_qty in list(cart.items()):
        try:
            pid = int(pid_str)
            qty = int(raw_qty)
        except (ValueError, TypeError):
            del cart[pid_str]
            session.modified = True
            continue

        product = product_dict.get(pid)
        if product and product.is_active and product.quantity > 0:
            clamped_qty = max(1, min(qty, product.quantity))
            if clamped_qty != qty:
                cart[pid_str] = clamped_qty
                session.modified = True
            line_total = product.price * clamped_qty
            items.append({
                'product': product,
                'quantity': clamped_qty,
                'unit_price': product.price,
                'line_total': line_total,
                'formatted_line_total': f"{int(line_total):,} ₫".replace(",", ".")
            })
            subtotal += line_total
            total_quantity += clamped_qty
        else:
            # Remove inactive, deleted, or out-of-stock product
            del cart[pid_str]
            session.modified = True

    return items, subtotal, total_quantity


@cart_bp.route('/cart')
def index():
    items, subtotal, total_quantity = get_cart_items()
    free_shipping = subtotal >= 300000
    shipping_estimate = 0 if (free_shipping or subtotal == 0) else 30000
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
    product = db.get_or_404(Product, product_id)
    if not product.is_active or product.quantity <= 0:
        flash(f'Sản phẩm "{product.product_name}" hiện đã hết hàng hoặc ngừng kinh doanh!', 'error')
        return redirect(safe_referrer('products.index'))

    qty = request.form.get('quantity', 1, type=int) if request.method == 'POST' else 1
    if not qty or qty < 1:
        qty = 1

    cart = session.get('cart', {})
    if not isinstance(cart, dict):
        cart = {}

    pid_str = str(product_id)
    current_qty = int(cart.get(pid_str, 0) or 0)

    if current_qty >= product.quantity:
        flash(f'Bạn đã thêm tối đa số lượng tồn kho ({product.quantity} cây) của "{product.product_name}" vào giỏ!', 'warning')
        if request.form.get('buy_now') == '1':
            return redirect(url_for('checkout.index'))
        return redirect(safe_referrer('cart.index'))

    new_qty = min(current_qty + qty, product.quantity)
    cart[pid_str] = new_qty
    session['cart'] = cart
    session.modified = True

    if request.form.get('buy_now') == '1':
        return redirect(url_for('checkout.index'))

    flash(f'Đã thêm "{product.product_name}" vào giỏ hàng thành công!', 'success')
    return redirect(safe_referrer('cart.index'))


@cart_bp.route('/cart/update', methods=['POST'])
def update():
    cart = session.get('cart', {})
    if not isinstance(cart, dict):
        cart = {}

    product_id = request.form.get('product_id', type=int)
    quantity = request.form.get('quantity', type=int)

    if product_id and quantity is not None:
        pid_str = str(product_id)
        if quantity <= 0:
            if pid_str in cart:
                del cart[pid_str]
                flash('Đã xóa sản phẩm khỏi giỏ hàng.', 'success')
        else:
            product = db.session.get(Product, product_id)
            if product and product.is_active and product.quantity > 0:
                if quantity > product.quantity:
                    cart[pid_str] = product.quantity
                    flash(f'Kho chỉ còn tối đa {product.quantity} chậu "{product.product_name}".', 'warning')
                else:
                    cart[pid_str] = quantity
                    flash('Đã cập nhật số lượng sản phẩm!', 'success')
            else:
                cart.pop(pid_str, None)
                flash('Sản phẩm này vừa hết hàng hoặc ngừng kinh doanh.', 'error')

        session['cart'] = cart
        session.modified = True

    return redirect(url_for('cart.index'))


@cart_bp.route('/cart/remove/<int:product_id>', methods=['POST', 'GET'])
def remove(product_id):
    cart = session.get('cart', {})
    pid_str = str(product_id)
    if isinstance(cart, dict) and pid_str in cart:
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
