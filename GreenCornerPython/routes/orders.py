from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from models import db, Order

orders_bp = Blueprint('orders', __name__)

@orders_bp.route('/orders')
def index():
    user_id = session.get('user_id')
    if not user_id:
        flash('Vui lòng đăng nhập để xem lịch sử đơn hàng.', 'warning')
        return redirect(url_for('auth.login', returnUrl=url_for('orders.index')))

    orders = Order.query.filter_by(user_id=user_id).order_by(Order.created_at.desc(), Order.order_id.desc()).all()
    return render_template('orders/index.html', orders=orders)


@orders_bp.route('/orders/<int:order_id>')
def detail(order_id):
    order = db.get_or_404(Order, order_id)
    user_id = session.get('user_id')
    user_role = session.get('user_role')

    # Security check: User can only view their own order unless Admin or placed in current session
    is_admin = (session.get('admin_role') == 'Admin') or (user_role == 'Admin')
    is_guest_allowed = session.get(f'guest_order_{order.order_id}') is True
    if not is_admin and not is_guest_allowed and (not user_id or order.user_id != user_id):
        flash('Vui lòng đăng nhập để xem thông tin đơn hàng này.', 'warning')
        return redirect(url_for('auth.login', returnUrl=request.path))

    # Prepare VietQR URL if order is pending
    amount_int = int(order.total_amount)
    vietqr_url = f"https://img.vietqr.io/image/MB-888868689999-compact2.png?amount={amount_int}&addInfo=GC%20{order.order_id}&accountName=GREEN%20CORNER"

    # Status index for stepper
    status_steps = ['Chờ xác nhận', 'Đã xác nhận', 'Đang giao', 'Hoàn thành']
    try:
        current_step_index = status_steps.index(order.status)
    except ValueError:
        current_step_index = -1

    return render_template(
        'orders/detail.html',
        order=order,
        vietqr_url=vietqr_url,
        status_steps=status_steps,
        current_step_index=current_step_index
    )


@orders_bp.route('/orders/<int:order_id>/cancel', methods=['POST'])
def cancel(order_id):
    order = db.get_or_404(Order, order_id)
    user_id = session.get('user_id')
    is_admin = (session.get('admin_role') == 'Admin') or (session.get('user_role') == 'Admin')
    is_guest_allowed = session.get(f'guest_order_{order.order_id}') is True

    if not is_admin and not is_guest_allowed and (not user_id or order.user_id != user_id):
        flash('Bạn không có quyền thao tác trên đơn hàng này.', 'error')
        return redirect(url_for('orders.index'))

    if order.status != 'Chờ xác nhận':
        flash('Chỉ có thể hủy đơn hàng khi đang ở trạng thái "Chờ xác nhận"!', 'warning')
        return redirect(url_for('orders.detail', order_id=order.order_id))

    order.status = 'Đã hủy'
    for detail_item in order.order_details:
        if detail_item.product:
            detail_item.product.quantity += detail_item.quantity

    db.session.commit()
    flash(f'Đã hủy đơn hàng #GC-{order.order_id} thành công.', 'success')
    return redirect(url_for('orders.detail', order_id=order.order_id))
