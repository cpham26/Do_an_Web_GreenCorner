import re
import secrets
from urllib.parse import urlparse
from flask import Flask, session, render_template, request, abort
from config import Config
from models import db, User, Product
from routes.main import main_bp
from routes.products import products_bp
from routes.cart import cart_bp, get_cart_items
from routes.checkout import checkout_bp
from routes.auth import auth_bp
from routes.orders import orders_bp
from routes.admin import admin_bp

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    app.config['TEMPLATES_AUTO_RELOAD'] = True

    # Initialize extensions
    db.init_app(app)

    # Register safe Python built-ins for Jinja templates
    app.jinja_env.globals['int'] = int

    def get_csrf_token():
        if '_csrf_token' not in session:
            session['_csrf_token'] = secrets.token_hex(24)
        return session['_csrf_token']

    app.jinja_env.globals['csrf_token'] = get_csrf_token

    # Custom Jinja Template Filters
    @app.template_filter('currency')
    def currency_filter(value):
        if value is None:
            return "0 ₫"
        try:
            return f"{int(value):,} ₫".replace(",", ".")
        except (ValueError, TypeError):
            return f"{value} ₫"

    @app.template_filter('datetime')
    def datetime_filter(value, format='%d/%m/%Y %H:%M'):
        if value is None:
            return ""
        try:
            return value.strftime(format)
        except Exception:
            return str(value)

    # Enforce separation & CSRF / Same-Origin protection
    @app.before_request
    def security_and_session_guard():
        # Skip static assets for high performance
        if request.endpoint == 'static':
            return

        # 1. CSRF & Same-Origin Verification on state-changing requests
        if request.method in ('POST', 'PUT', 'DELETE', 'PATCH'):
            origin = request.headers.get('Origin')
            referer = request.headers.get('Referer')
            host = request.host

            if origin:
                parsed_origin = urlparse(origin)
                if parsed_origin.netloc and parsed_origin.netloc != host:
                    abort(403)
            elif referer:
                parsed_ref = urlparse(referer)
                if parsed_ref.netloc and parsed_ref.netloc != host:
                    abort(403)

            submitted_token = request.form.get('csrf_token') or request.headers.get('X-CSRF-Token')
            session_token = session.get('_csrf_token')
            if session_token:
                if not submitted_token or not secrets.compare_digest(str(submitted_token), str(session_token)):
                    abort(403)

        # 2. Storefront session integrity check
        user_id = session.get('user_id')
        if user_id:
            user = db.session.get(User, user_id)
            if not user or user.role == 'Admin':
                session.pop('user_id', None)
                session.pop('user_name', None)
                session.pop('user_email', None)
                session.pop('user_role', None)

    # Security Headers & Automatic CSRF Form Injection
    @app.after_request
    def add_security_headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response.headers['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'

        if (
            response.content_type
            and response.content_type.startswith('text/html')
            and not response.direct_passthrough
        ):
            token = session.get('_csrf_token')
            if token:
                html = response.get_data(as_text=True)
                hidden_input = f'<input type="hidden" name="csrf_token" value="{token}" />'
                html = re.sub(
                    r'(<form\b[^>]*\bmethod=["\']post["\'][^>]*>)(?!\s*<input[^>]*name=["\']csrf_token["\'])',
                    rf'\1{hidden_input}',
                    html,
                    flags=re.IGNORECASE
                )
                response.set_data(html)

        return response

    # Global Context Processor for Templates
    @app.context_processor
    def inject_global_data():
        user_id = session.get('user_id')
        current_user = db.session.get(User, user_id) if user_id else None

        _, _, cart_count = get_cart_items()

        return {
            'current_user': current_user,
            'cart_count': cart_count,
            'user_role': session.get('user_role'),
            'user_name': session.get('user_name'),
            'csrf_token_val': get_csrf_token()
        }

    # Register Blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(products_bp)
    app.register_blueprint(cart_bp)
    app.register_blueprint(checkout_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(orders_bp)
    app.register_blueprint(admin_bp)

    @app.route('/favicon.ico')
    def favicon():
        return app.send_static_file('favicon.ico')

    @app.errorhandler(400)
    def bad_request(e):
        return render_template('error.html', code=400, message="Yêu cầu không hợp lệ. Vui lòng kiểm tra lại dữ liệu gửi lên."), 400

    @app.errorhandler(403)
    def forbidden(e):
        return render_template('error.html', code=403, message="Bạn không có quyền truy cập hoặc phiên làm việc đã hết hạn."), 403

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('error.html', code=404, message="Trang bạn tìm kiếm không tồn tại hoặc sản phẩm đã ngừng kinh doanh."), 404

    @app.errorhandler(405)
    def method_not_allowed(e):
        return render_template('error.html', code=405, message="Phương thức truy cập không được phép cho đường dẫn này."), 405

    @app.errorhandler(500)
    def internal_server_error(e):
        db.session.rollback()
        return render_template('error.html', code=500, message="Hệ thống đang gặp sự cố gián đoạn. Vui lòng thử lại sau."), 500

    return app
