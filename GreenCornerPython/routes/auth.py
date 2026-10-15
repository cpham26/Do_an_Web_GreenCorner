import re
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models import db, User

auth_bp = Blueprint('auth', __name__)

def is_safe_redirect(target):
    if not target or not isinstance(target, str):
        return False
    target = target.strip()
    if target.startswith('//') or target.startswith('/\\'):
        return False
    if not target.startswith('/'):
        return False
    if target.startswith('/admin'):
        return False
    return True

@auth_bp.route('/account/login', methods=['GET', 'POST'])
def login():
    if session.get('user_id'):
        return redirect(url_for('main.index'))

    return_url = request.args.get('returnUrl') or request.form.get('return_url', '')

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        if not email or not password:
            flash('Vui lòng nhập đầy đủ Email và Mật khẩu!', 'error')
            return render_template('auth/login.html', email=email, return_url=return_url)

        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            if user.role == 'Admin':
                flash('Tài khoản Quản trị viên vui lòng đăng nhập tại Cổng Quản Trị (/admin/login)!', 'warning')
                return redirect(url_for('admin.login'))

            session['user_id'] = user.user_id
            session['user_name'] = user.full_name
            session['user_email'] = user.email
            session['user_role'] = user.role

            flash(f'Xin chào, {user.full_name}!', 'success')

            if is_safe_redirect(return_url):
                return redirect(return_url)

            return redirect(url_for('main.index'))
        else:
            flash('Email hoặc mật khẩu không chính xác. Vui lòng thử lại!', 'error')

    return render_template('auth/login.html', return_url=return_url)


@auth_bp.route('/account/register', methods=['GET', 'POST'])
def register():
    if session.get('user_id'):
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        phone = request.form.get('phone', '').strip()
        address = request.form.get('address', '').strip()

        if not full_name or not email or not password:
            flash('Vui lòng điền họ tên, email và mật khẩu!', 'error')
            return render_template('auth/register.html')

        if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
            flash('Định dạng email không hợp lệ!', 'error')
            return render_template('auth/register.html')

        if len(password) < 6:
            flash('Mật khẩu phải có tối thiểu 6 ký tự!', 'error')
            return render_template('auth/register.html')

        if password != confirm_password:
            flash('Mật khẩu xác nhận không khớp!', 'error')
            return render_template('auth/register.html')

        existing = User.query.filter_by(email=email).first()
        if existing:
            flash('Email này đã được sử dụng. Vui lòng đăng nhập hoặc chọn email khác!', 'error')
            return render_template('auth/register.html')

        new_user = User(
            full_name=full_name,
            email=email,
            phone=phone,
            address=address,
            role='Customer'
        )
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        # Auto login
        session['user_id'] = new_user.user_id
        session['user_name'] = new_user.full_name
        session['user_email'] = new_user.email
        session['user_role'] = new_user.role

        flash('Đăng ký tài khoản thành công! Chào mừng bạn đến với Green Corner.', 'success')
        return redirect(url_for('main.index'))

    return render_template('auth/register.html')


@auth_bp.route('/account/profile', methods=['GET', 'POST'])
def profile():
    user_id = session.get('user_id')
    if not user_id:
        flash('Vui lòng đăng nhập để xem hồ sơ cá nhân.', 'warning')
        return redirect(url_for('auth.login', returnUrl=url_for('auth.profile')))

    user = User.query.get_or_404(user_id)

    if request.method == 'POST':
        user.full_name = request.form.get('full_name', '').strip()
        user.phone = request.form.get('phone', '').strip()
        user.address = request.form.get('address', '').strip()
        db.session.commit()

        session['user_name'] = user.full_name
        flash('Đã cập nhật thông tin cá nhân thành công!', 'success')
        return redirect(url_for('auth.profile'))

    return render_template('auth/profile.html', user=user)


@auth_bp.route('/account/change-password', methods=['GET', 'POST'])
def change_password():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('auth.login'))

    user = User.query.get_or_404(user_id)

    if request.method == 'POST':
        current_password = request.form.get('current_password', '')
        new_password = request.form.get('new_password', '')
        confirm_password = request.form.get('confirm_password', '')

        if not user.check_password(current_password):
            flash('Mật khẩu hiện tại không đúng!', 'error')
            return render_template('auth/change_password.html')

        if len(new_password) < 6:
            flash('Mật khẩu mới phải có ít nhất 6 ký tự!', 'error')
            return render_template('auth/change_password.html')

        if new_password != confirm_password:
            flash('Mật khẩu xác nhận không khớp!', 'error')
            return render_template('auth/change_password.html')

        user.set_password(new_password)
        db.session.commit()
        flash('Đổi mật khẩu thành công!', 'success')
        return redirect(url_for('auth.profile'))

    return render_template('auth/change_password.html', user=user)


@auth_bp.route('/account/logout', methods=['GET', 'POST'])
def logout():
    session.clear()
    flash('Bạn đã đăng xuất tài khoản thành công.', 'success')
    return redirect(url_for('main.index'))
