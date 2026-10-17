import re
import time
from functools import wraps
from decimal import Decimal
from urllib.parse import urlparse
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models import db, User, Product, Category, Order, OrderDetail

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

_ADMIN_LOGIN_ATTEMPTS = {}
MAX_ADMIN_ATTEMPTS = 5
ADMIN_LOCKOUT_SECONDS = 60

def _check_admin_rate_limit(ip):
    now = time.time()
    record = _ADMIN_LOGIN_ATTEMPTS.get(ip)
    if not record:
        return True, 0
    count, start_ts = record
    if now - start_ts > ADMIN_LOCKOUT_SECONDS:
        _ADMIN_LOGIN_ATTEMPTS.pop(ip, None)
        return True, 0
    if count >= MAX_ADMIN_ATTEMPTS:
        remaining = int(ADMIN_LOCKOUT_SECONDS - (now - start_ts))
        return False, max(1, remaining)
    return True, 0

def _record_admin_failure(ip):
    now = time.time()
    record = _ADMIN_LOGIN_ATTEMPTS.get(ip)
    if not record or (now - record[1] > ADMIN_LOCKOUT_SECONDS):
        _ADMIN_LOGIN_ATTEMPTS[ip] = [1, now]
    else:
        record[0] += 1

def _reset_admin_attempts(ip):
    _ADMIN_LOGIN_ATTEMPTS.pop(ip, None)


def _normalize_image_url(raw_url):
    img = (raw_url or '').strip()[:255]
    if not img:
        return '/static/images/products/monstera.jpg'
    # Block dangerous schemes like javascript: or data:
    lower_img = img.lower()
    if lower_img.startswith(('javascript:', 'data:', 'vbscript:')):
        return '/static/images/products/monstera.jpg'
    if img.startswith(('/static/', 'http://', 'https://')):
        return img
    return f'/static/images/products/{img.lstrip("/")}'


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        admin_id = session.get('admin_id')
        if not admin_id or session.get('admin_role') != 'Admin':
            flash('Vui lòng đăng nhập với tài khoản Quản trị viên (Admin) để truy cập!', 'error')
            return redirect(url_for('admin.login', next=request.path))

        admin_user = db.session.get(User, admin_id)
        if not admin_user or admin_user.role != 'Admin':
            for k in ('admin_id', 'admin_name', 'admin_email', 'admin_role'):
                session.pop(k, None)
            flash('Phiên quản trị không còn hợp lệ. Vui lòng đăng nhập lại!', 'error')
            return redirect(url_for('admin.login'))

        return f(*args, **kwargs)
    return decorated_function


@admin_bp.context_processor
def inject_admin():
    admin_user = None
    if session.get('admin_id'):
        admin_user = db.session.get(User, session['admin_id'])
    return {'current_admin': admin_user}


# --- AUTHENTICATION FOR ADMIN ---
@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    if session.get('admin_id') and session.get('admin_role') == 'Admin':
        admin_user = db.session.get(User, session['admin_id'])
        if admin_user and admin_user.role == 'Admin':
            return redirect(url_for('admin.dashboard'))

    if request.method == 'POST':
        client_ip = request.remote_addr or 'unknown'
        allowed, wait_sec = _check_admin_rate_limit(client_ip)
        email = request.form.get('email', '').strip().lower()[:100]
        password = request.form.get('password', '')
        remember = bool(request.form.get('remember'))

        if not allowed:
            flash(f'Quá nhiều lần đăng nhập thất bại. Vui lòng thử lại sau {wait_sec} giây!', 'error')
            return render_template('admin/login.html', email=email)

        if not email or not password:
            flash('Vui lòng điền đầy đủ Email và Mật khẩu!', 'error')
            return render_template('admin/login.html', email=email)

        user = User.query.filter_by(email=email).first()
        if not user or not user.check_password(password):
            _record_admin_failure(client_ip)
            flash('Email hoặc mật khẩu không chính xác!', 'error')
            return render_template('admin/login.html', email=email)

        if user.role != 'Admin':
            _record_admin_failure(client_ip)
            flash('Tài khoản này không có quyền truy cập Cổng Quản trị!', 'error')
            return render_template('admin/login.html', email=email)

        _reset_admin_attempts(client_ip)
        session['admin_id'] = user.user_id
        session['admin_name'] = user.full_name
        session['admin_email'] = user.email
        session['admin_role'] = user.role
        session.permanent = remember

        flash(f'Chào mừng Quản trị viên {user.full_name}!', 'success')
        next_url = request.args.get('next') or request.form.get('next') or request.args.get('returnUrl') or request.form.get('returnUrl')
        if next_url and next_url.startswith('/admin') and not next_url.startswith('//') and not next_url.startswith('/\\') and next_url != '/admin/login':
            return redirect(next_url)
        return redirect(url_for('admin.dashboard'))

    return render_template('admin/login.html')


@admin_bp.route('/logout')
def logout():
    session.pop('admin_id', None)
    session.pop('admin_name', None)
    session.pop('admin_email', None)
    session.pop('admin_role', None)
    flash('Đã đăng xuất khỏi Cổng Quản trị thành công.', 'info')
    return redirect(url_for('admin.login'))


# --- DASHBOARD ---
@admin_bp.route('')
@admin_bp.route('/')
@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    total_products = Product.query.count()
    total_orders = Order.query.count()
    total_customers = User.query.filter_by(role='Customer').count()

    # Calculate total revenue from non-cancelled orders
    orders_query = Order.query.filter(Order.status != 'Đã hủy').all()
    total_revenue = sum(o.total_amount for o in orders_query) if orders_query else Decimal(0)

    recent_orders = Order.query.order_by(Order.created_at.desc(), Order.order_id.desc()).limit(8).all()
    low_stock_products = Product.query.filter(Product.quantity <= 10, Product.is_active == True).limit(6).all()

    return render_template(
        'admin/dashboard.html',
        total_products=total_products,
        total_orders=total_orders,
        total_customers=total_customers,
        total_revenue=total_revenue,
        recent_orders=recent_orders,
        low_stock_products=low_stock_products
    )


# --- PRODUCTS MANAGEMENT ---
@admin_bp.route('/products')
@admin_required
def products():
    search = request.args.get('q', '').strip()[:100]
    category_id = request.args.get('categoryId', type=int)
    page = max(1, request.args.get('page', 1, type=int) or 1)

    query = Product.query
    if search:
        query = query.filter(Product.product_name.ilike(f'%{search}%'))
    if category_id:
        query = query.filter_by(category_id=category_id)

    pagination = query.order_by(Product.product_id.desc()).paginate(page=page, per_page=15, error_out=False)
    categories = Category.query.all()

    return render_template(
        'admin/products/index.html',
        products=pagination.items,
        pagination=pagination,
        categories=categories,
        search=search,
        category_id=category_id
    )


@admin_bp.route('/products/create', methods=['GET', 'POST'])
@admin_required
def create_product():
    categories = Category.query.all()
    if request.method == 'POST':
        product_name = request.form.get('product_name', '').strip()[:150]
        category_id = request.form.get('category_id', type=int)
        price = request.form.get('price', type=float)
        quantity = request.form.get('quantity', type=int)
        image_url = request.form.get('image_url', '').strip()
        description = request.form.get('description', '').strip()[:2000]

        if not product_name or not category_id or price is None or quantity is None:
            flash('Vui lòng điền đầy đủ thông tin bắt buộc!', 'error')
            return render_template('admin/products/create.html', categories=categories)

        if not db.session.get(Category, category_id):
            flash('Danh mục đã chọn không hợp lệ!', 'error')
            return render_template('admin/products/create.html', categories=categories)

        if price < 0 or price > 999999999 or quantity < 0 or quantity > 100000:
            flash('Giá bán (0 - 999.999.999đ) và số lượng tồn kho (0 - 100.000) không hợp lệ!', 'error')
            return render_template('admin/products/create.html', categories=categories)

        product = Product(
            product_name=product_name,
            category_id=category_id,
            price=Decimal(str(round(price, 2))),
            quantity=quantity,
            image_url=_normalize_image_url(image_url),
            description=description,
            is_active=True
        )
        db.session.add(product)
        db.session.commit()
        flash(f'Đã thêm sản phẩm "{product.product_name}" thành công!', 'success')
        return redirect(url_for('admin.products'))

    return render_template('admin/products/create.html', categories=categories)


@admin_bp.route('/products/edit/<int:product_id>', methods=['GET', 'POST'])
@admin_required
def edit_product(product_id):
    product = db.get_or_404(Product, product_id)
    categories = Category.query.all()

    if request.method == 'POST':
        product_name = request.form.get('product_name', '').strip()[:150]
        cat_id = request.form.get('category_id', type=int)
        raw_price = request.form.get('price', type=float)
        raw_qty = request.form.get('quantity', type=int)

        if not product_name or not cat_id or raw_price is None or raw_qty is None:
            flash('Vui lòng điền đầy đủ thông tin bắt buộc!', 'error')
            return render_template('admin/products/edit.html', product=product, categories=categories)

        if not db.session.get(Category, cat_id):
            flash('Danh mục đã chọn không hợp lệ!', 'error')
            return render_template('admin/products/edit.html', product=product, categories=categories)

        if raw_price < 0 or raw_price > 999999999 or raw_qty < 0 or raw_qty > 100000:
            flash('Giá bán và số lượng tồn kho không hợp lệ!', 'error')
            return render_template('admin/products/edit.html', product=product, categories=categories)

        product.product_name = product_name
        product.category_id = cat_id
        product.price = Decimal(str(round(raw_price, 2)))
        product.quantity = raw_qty

        img = request.form.get('image_url', '').strip()
        if img:
            product.image_url = _normalize_image_url(img)

        product.description = request.form.get('description', '').strip()[:2000]
        product.is_active = request.form.get('is_active') == 'on'

        db.session.commit()
        flash(f'Đã cập nhật sản phẩm "{product.product_name}" thành công!', 'success')
        return redirect(url_for('admin.products'))

    return render_template('admin/products/edit.html', product=product, categories=categories)


@admin_bp.route('/products/delete/<int:product_id>', methods=['POST'])
@admin_required
def delete_product(product_id):
    product = db.get_or_404(Product, product_id)
    has_orders = OrderDetail.query.filter_by(product_id=product.product_id).first()
    if has_orders:
        product.is_active = False
        db.session.commit()
        flash(f'Sản phẩm "{product.product_name}" đã phát sinh đơn hàng nên được chuyển sang trạng thái Ngừng kinh doanh.', 'info')
    else:
        db.session.delete(product)
        db.session.commit()
        flash(f'Đã xóa hoàn toàn sản phẩm "{product.product_name}".', 'success')

    return redirect(url_for('admin.products'))


# --- CATEGORIES MANAGEMENT ---
@admin_bp.route('/categories')
@admin_required
def categories():
    cats = Category.query.order_by(Category.category_id.asc()).all()
    return render_template('admin/categories/index.html', categories=cats)


@admin_bp.route('/categories/create', methods=['POST'])
@admin_required
def create_category():
    name = request.form.get('category_name', '').strip()[:100]
    desc = request.form.get('description', '').strip()[:255]
    if not name:
        flash('Tên danh mục không được để trống!', 'error')
        return redirect(url_for('admin.categories'))

    existing = Category.query.filter(db.func.lower(Category.category_name) == name.lower()).first()
    if existing:
        flash(f'Tên danh mục "{name}" đã tồn tại!', 'error')
    else:
        cat = Category(category_name=name, description=desc)
        db.session.add(cat)
        db.session.commit()
        flash(f'Đã thêm danh mục "{name}" thành công!', 'success')
    return redirect(url_for('admin.categories'))


@admin_bp.route('/categories/edit/<int:category_id>', methods=['POST'])
@admin_required
def edit_category(category_id):
    cat = db.get_or_404(Category, category_id)
    name = request.form.get('category_name', '').strip()[:100]
    desc = request.form.get('description', '').strip()[:255]

    if not name:
        flash('Tên danh mục không được để trống!', 'error')
        return redirect(url_for('admin.categories'))

    duplicate = Category.query.filter(
        db.func.lower(Category.category_name) == name.lower(),
        Category.category_id != cat.category_id
    ).first()
    if duplicate:
        flash(f'Tên danh mục "{name}" đã tồn tại trên danh mục khác!', 'error')
        return redirect(url_for('admin.categories'))

    cat.category_name = name
    cat.description = desc
    db.session.commit()
    flash(f'Đã cập nhật danh mục "{name}" thành công!', 'success')
    return redirect(url_for('admin.categories'))


@admin_bp.route('/categories/delete/<int:category_id>', methods=['POST'])
@admin_required
def delete_category(category_id):
    cat = db.get_or_404(Category, category_id)
    if cat.products.count() > 0:
        flash(f'Không thể xóa danh mục "{cat.category_name}" vì còn chứa {cat.products.count()} sản phẩm!', 'error')
    else:
        db.session.delete(cat)
        db.session.commit()
        flash('Đã xóa danh mục thành công.', 'success')
    return redirect(url_for('admin.categories'))


# --- ORDERS MANAGEMENT ---
@admin_bp.route('/orders')
@admin_required
def orders():
    status = request.args.get('status', '').strip()
    page = max(1, request.args.get('page', 1, type=int) or 1)

    query = Order.query
    if status and status != 'Tất cả':
        query = query.filter_by(status=status)

    pagination = query.order_by(Order.created_at.desc(), Order.order_id.desc()).paginate(page=page, per_page=15, error_out=False)

    return render_template(
        'admin/orders/index.html',
        orders=pagination.items,
        pagination=pagination,
        status=status
    )


@admin_bp.route('/orders/<int:order_id>')
@admin_required
def order_detail(order_id):
    order = db.get_or_404(Order, order_id)
    return render_template('admin/orders/detail.html', order=order)


@admin_bp.route('/orders/<int:order_id>/status', methods=['POST'])
@admin_required
def update_order_status(order_id):
    order = db.get_or_404(Order, order_id)
    new_status = request.form.get('status', '').strip()
    valid_statuses = ['Chờ xác nhận', 'Đã xác nhận', 'Đang giao', 'Hoàn thành', 'Đã hủy']

    if new_status in valid_statuses:
        old_status = order.status
        if old_status == new_status:
            flash(f'Đơn hàng #{order.order_id} hiện đã ở trạng thái "{new_status}".', 'info')
            return redirect(url_for('admin.order_detail', order_id=order.order_id))

        # Check stock before restoring a cancelled order
        if old_status == 'Đã hủy' and new_status != 'Đã hủy':
            for detail in order.order_details:
                if detail.product and detail.product.quantity < detail.quantity:
                    flash(
                        f'Không thể khôi phục đơn hàng: "{detail.product.product_name}" chỉ còn {detail.product.quantity} cây trong kho (cần {detail.quantity} cây)!',
                        'error'
                    )
                    return redirect(url_for('admin.order_detail', order_id=order.order_id))

            for detail in order.order_details:
                if detail.product:
                    detail.product.quantity -= detail.quantity
            order.status = new_status
            flash(f'Đã khôi phục đơn hàng #{order.order_id} sang "{new_status}" và trừ tồn kho tương ứng.', 'info')

        elif new_status == 'Đã hủy' and old_status != 'Đã hủy':
            for detail in order.order_details:
                if detail.product:
                    detail.product.quantity += detail.quantity
            order.status = new_status
            flash(f'Đã hủy đơn hàng #{order.order_id} và hoàn lại {sum(d.quantity for d in order.order_details)} cây vào kho tồn.', 'info')

        else:
            order.status = new_status
            flash(f'Đã cập nhật trạng thái đơn hàng #{order.order_id} sang "{new_status}".', 'success')

        db.session.commit()
    else:
        flash('Trạng thái không hợp lệ!', 'error')

    return redirect(url_for('admin.order_detail', order_id=order.order_id))


# --- USERS MANAGEMENT ---
@admin_bp.route('/users')
@admin_required
def users():
    users_list = User.query.order_by(User.created_at.desc(), User.user_id.desc()).all()
    return render_template('admin/users/index.html', users=users_list)


@admin_bp.route('/users/create', methods=['POST'])
@admin_required
def create_user():
    full_name = request.form.get('full_name', '').strip()[:100]
    email = request.form.get('email', '').strip().lower()[:100]
    password = request.form.get('password', '')
    phone = re.sub(r'[\s\-\.]', '', request.form.get('phone', '').strip())[:20]
    address = request.form.get('address', '').strip()[:255]
    role = request.form.get('role', 'Customer').strip()

    if not full_name or not email or not password:
        flash('Họ tên, email và mật khẩu là bắt buộc!', 'error')
        return redirect(url_for('admin.users'))

    if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w{2,}$', email):
        flash('Định dạng email không hợp lệ!', 'error')
        return redirect(url_for('admin.users'))

    if len(password) < 6:
        flash('Mật khẩu phải có từ 6 ký tự trở lên!', 'error')
        return redirect(url_for('admin.users'))

    if User.query.filter_by(email=email).first():
        flash(f'Email "{email}" đã được sử dụng!', 'error')
        return redirect(url_for('admin.users'))

    if role not in ['Customer', 'Admin']:
        role = 'Customer'

    new_user = User(
        full_name=full_name,
        email=email,
        phone=phone or None,
        address=address or None,
        role=role
    )
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()

    flash(f'Đã thêm thành công tài khoản "{full_name}" ({role})!', 'success')
    return redirect(url_for('admin.users'))


@admin_bp.route('/users/<int:user_id>/edit', methods=['POST'])
@admin_required
def edit_user(user_id):
    user = db.get_or_404(User, user_id)
    full_name = request.form.get('full_name', '').strip()[:100]
    email = request.form.get('email', '').strip().lower()[:100]
    phone = re.sub(r'[\s\-\.]', '', request.form.get('phone', '').strip())[:20]
    address = request.form.get('address', '').strip()[:255]
    role = request.form.get('role', '').strip()
    new_password = request.form.get('new_password', '').strip()

    if not full_name or not email:
        flash('Họ tên và email không được để trống!', 'error')
        return redirect(url_for('admin.users'))

    if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w{2,}$', email):
        flash('Định dạng email không hợp lệ!', 'error')
        return redirect(url_for('admin.users'))

    existing = User.query.filter(User.email == email, User.user_id != user.user_id).first()
    if existing:
        flash(f'Email "{email}" đã tồn tại trên một tài khoản khác!', 'error')
        return redirect(url_for('admin.users'))

    # If updating logged in admin themselves
    if user.user_id == session.get('admin_id') and role and role != 'Admin':
        flash('Bạn không thể tự hạ quyền Admin của chính mình!', 'warning')
        role = 'Admin'

    user.full_name = full_name
    user.email = email
    user.phone = phone or None
    user.address = address or None
    if role in ['Customer', 'Admin']:
        user.role = role

    if new_password:
        if len(new_password) < 6:
            flash('Mật khẩu mới phải có từ 6 ký tự trở lên!', 'error')
            return redirect(url_for('admin.users'))
        user.set_password(new_password)
        flash('Đã cập nhật mật khẩu mới cho tài khoản!', 'info')

    if user.user_id == session.get('admin_id'):
        session['admin_name'] = user.full_name
        session['admin_email'] = user.email

    db.session.commit()
    flash(f'Đã cập nhật tài khoản "{user.full_name}" thành công!', 'success')
    return redirect(url_for('admin.users'))


@admin_bp.route('/users/<int:user_id>/delete', methods=['POST'])
@admin_required
def delete_user(user_id):
    user = db.get_or_404(User, user_id)
    if user.user_id == session.get('admin_id'):
        flash('Không thể xóa tài khoản Quản trị viên hiện đang đăng nhập!', 'error')
        return redirect(url_for('admin.users'))

    if user.role == 'Admin' and User.query.filter_by(role='Admin').count() <= 1:
        flash('Không thể xóa Quản trị viên duy nhất còn lại trong hệ thống!', 'error')
        return redirect(url_for('admin.users'))

    user_name = user.full_name

    # Preserve order history by disconnecting user foreign key
    Order.query.filter_by(user_id=user.user_id).update({'user_id': None})

    db.session.delete(user)
    db.session.commit()
    flash(f'Đã xóa tài khoản "{user_name}". Dữ liệu lịch sử đơn hàng đã được bảo lưu an toàn.', 'success')
    return redirect(url_for('admin.users'))


@admin_bp.route('/users/<int:user_id>/role', methods=['POST'])
@admin_required
def toggle_user_role(user_id):
    user = db.get_or_404(User, user_id)
    if user.user_id == session.get('admin_id'):
        flash('Bạn không thể tự hạ quyền quản trị của chính mình!', 'warning')
    elif user.role == 'Admin' and User.query.filter_by(role='Admin').count() <= 1:
        flash('Không thể hạ quyền Quản trị viên duy nhất còn lại trong hệ thống!', 'error')
    else:
        user.role = 'Admin' if user.role == 'Customer' else 'Customer'
        db.session.commit()
        flash(f'Đã chuyển quyền của {user.full_name} thành {user.role}.', 'success')

    return redirect(url_for('admin.users'))

