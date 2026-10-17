import re
from decimal import Decimal
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models import db, Product, Order, OrderDetail, User
from routes.cart import get_cart_items

checkout_bp = Blueprint('checkout', __name__)

PHONE_REGEX = re.compile(r'^\+?[0-9]{9,15}$')

@checkout_bp.route('/checkout', methods=['GET', 'POST'])
def index():
    items, subtotal, total_quantity = get_cart_items()
    if not items:
        flash('Giỏ hàng của bạn đang trống. Vui lòng chọn sản phẩm trước khi thanh toán!', 'warning')
        return redirect(url_for('products.index'))

    # Load current user info if logged in
    user_id = session.get('user_id')
    current_user = db.session.get(User, user_id) if user_id else None

    if request.method == 'POST':
        receiver_name = request.form.get('receiver_name', '').strip()[:100]
        raw_phone = request.form.get('phone', '').strip()
        clean_phone = re.sub(r'[\s\-\.]', '', raw_phone)[:20]
        address = request.form.get('address', '').strip()[:255]
        shipping_speed = request.form.get('shipping_speed', 'Tiêu chuẩn').strip()
        payment_method = request.form.get('payment_method', 'VietQR').strip()
        order_notes = request.form.get('order_notes', '').strip()[:500]

        if shipping_speed not in ('Tiêu chuẩn', 'Hỏa tốc'):
            shipping_speed = 'Tiêu chuẩn'
        if payment_method not in ('VietQR', 'COD'):
            payment_method = 'VietQR'

        if not receiver_name or not clean_phone or not address:
            flash('Vui lòng điền đầy đủ họ tên, số điện thoại và địa chỉ nhận hàng!', 'error')
            return redirect(url_for('checkout.index'))

        if not PHONE_REGEX.match(clean_phone):
            flash('Số điện thoại không hợp lệ (vui lòng nhập từ 9 đến 15 chữ số)!', 'error')
            return redirect(url_for('checkout.index'))

        try:
            # Re-verify stock & active status and calculate exact server-side subtotal
            verified_subtotal = Decimal(0)
            verified_items = []
            for item in items:
                product = db.session.get(Product, item['product'].product_id)
                if not product or not product.is_active:
                    flash('Một sản phẩm trong giỏ hàng hiện đã ngừng kinh doanh. Vui lòng kiểm tra lại giỏ hàng!', 'error')
                    return redirect(url_for('cart.index'))
                if product.quantity < item['quantity']:
                    flash(f'Sản phẩm "{product.product_name}" chỉ còn {product.quantity} chậu trong kho!', 'error')
                    return redirect(url_for('cart.index'))
                verified_subtotal += product.price * item['quantity']
                verified_items.append((product, item['quantity']))

            # Calculate shipping fee: Free for standard if >= 300k, otherwise 30k. Express is 35k.
            base_shipping = 0 if verified_subtotal >= 300000 else 30000
            shipping_fee = Decimal(35000 if shipping_speed == 'Hỏa tốc' else base_shipping)
            total_amount = verified_subtotal + shipping_fee

            # Create Order
            order = Order(
                user_id=current_user.user_id if current_user else None,
                receiver_name=receiver_name,
                phone=clean_phone,
                address=address,
                shipping_speed=shipping_speed,
                shipping_fee=shipping_fee,
                payment_method=payment_method,
                order_notes=order_notes,
                total_amount=total_amount,
                status='Chờ xác nhận'
            )
            db.session.add(order)
            db.session.flush()

            # Create OrderDetails and deduct inventory
            for product, qty in verified_items:
                detail = OrderDetail(
                    order_id=order.order_id,
                    product_id=product.product_id,
                    quantity=qty,
                    unit_price=product.price,
                    product_name_snapshot=product.product_name
                )
                db.session.add(detail)
                product.quantity -= qty

            db.session.commit()

            # Grant view permission to this session for guest checkout
            session[f'guest_order_{order.order_id}'] = True

            # Empty cart
            session.pop('cart', None)
            flash('Đặt hàng thành công! Cảm ơn bạn đã lựa chọn Green Corner.', 'success')
            return redirect(url_for('checkout.success', order_id=order.order_id))

        except Exception:
            db.session.rollback()
            flash('Đã xảy ra sự cố khi xử lý đơn hàng. Vui lòng thử lại!', 'error')
            return redirect(url_for('checkout.index'))

    # GET Request
    base_shipping = 0 if subtotal >= 300000 else 30000
    express_shipping = 35000

    # Initial default shipping option
    initial_shipping_fee = base_shipping
    initial_total = subtotal + initial_shipping_fee

    return render_template(
        'checkout/index.html',
        items=items,
        subtotal=subtotal,
        total_quantity=total_quantity,
        base_shipping=base_shipping,
        express_shipping=express_shipping,
        initial_shipping_fee=initial_shipping_fee,
        initial_total=initial_total,
        current_user=current_user
    )


@checkout_bp.route('/checkout/success/<int:order_id>')
def success(order_id):
    order = db.get_or_404(Order, order_id)
    user_id = session.get('user_id')
    is_admin = (session.get('admin_role') == 'Admin') or (session.get('user_role') == 'Admin')
    is_guest_allowed = session.get(f'guest_order_{order.order_id}') is True

    if not is_admin and not is_guest_allowed and (not user_id or order.user_id != user_id):
        flash('Bạn không có quyền xem thông tin đơn hàng này.', 'error')
        return redirect(url_for('main.index'))

    amount_int = int(order.total_amount)
    vietqr_url = f"https://img.vietqr.io/image/MB-888868689999-compact2.png?amount={amount_int}&addInfo=GC%20{order.order_id}&accountName=GREEN%20CORNER"

    return render_template(
        'checkout/success.html',
        order=order,
        vietqr_url=vietqr_url,
        amount_int=amount_int
    )
