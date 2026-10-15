from decimal import Decimal
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models import db, Product, Order, OrderDetail, User
from routes.cart import get_cart_items

checkout_bp = Blueprint('checkout', __name__)

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
        receiver_name = request.form.get('receiver_name', '').strip()
        phone = request.form.get('phone', '').strip()
        address = request.form.get('address', '').strip()
        shipping_speed = request.form.get('shipping_speed', 'Tiêu chuẩn')
        payment_method = request.form.get('payment_method', 'VietQR')
        order_notes = request.form.get('order_notes', '').strip()

        if not receiver_name or not phone or not address:
            flash('Vui lòng điền đầy đủ họ tên, số điện thoại và địa chỉ nhận hàng!', 'error')
            return redirect(url_for('checkout.index'))

        # Calculate shipping fee: Free for standard if >= 300k, otherwise 30k. Express is +35k.
        base_shipping = 0 if subtotal >= 300000 else 30000
        shipping_fee = Decimal(35000 if shipping_speed == 'Hỏa tốc' else base_shipping)
        total_amount = subtotal + shipping_fee

        # Validate stock availability
        for item in items:
            product = db.session.get(Product, item['product'].product_id)
            if product.quantity < item['quantity']:
                flash(f'Sản phẩm "{product.product_name}" chỉ còn {product.quantity} sản phẩm trong kho!', 'error')
                return redirect(url_for('cart.index'))

        try:
            # Create Order
            order = Order(
                user_id=current_user.user_id if current_user else None,
                receiver_name=receiver_name,
                phone=phone,
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
            for item in items:
                product = db.session.get(Product, item['product'].product_id)
                detail = OrderDetail(
                    order_id=order.order_id,
                    product_id=product.product_id,
                    quantity=item['quantity'],
                    unit_price=product.price,
                    product_name_snapshot=product.product_name
                )
                db.session.add(detail)
                product.quantity -= item['quantity']

            db.session.commit()

            # Grant view permission to this session for guest checkout
            session[f'guest_order_{order.order_id}'] = True

            # Empty cart
            session.pop('cart', None)
            flash('Đặt hàng thành công! Cảm ơn bạn đã lựa chọn Green Corner.', 'success')
            return redirect(url_for('checkout.success', order_id=order.order_id))

        except Exception as e:
            db.session.rollback()
            flash(f'Đã xảy ra lỗi khi tạo đơn hàng: {str(e)}', 'error')
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
    order = Order.query.get_or_404(order_id)
    amount_int = int(order.total_amount)
    
    # VietQR Napas247 URL
    vietqr_url = f"https://img.vietqr.io/image/MB-888868689999-compact2.png?amount={amount_int}&addInfo=GC%20{order.order_id}&accountName=GREEN%20CORNER"

    return render_template(
        'checkout/success.html',
        order=order,
        vietqr_url=vietqr_url,
        amount_int=amount_int
    )
