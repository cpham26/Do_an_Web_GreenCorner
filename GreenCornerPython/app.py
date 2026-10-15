from flask import Flask, session, render_template, request
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
        return value.strftime(format)

    # Enforce separation: Admin accounts cannot be logged in on storefront
    @app.before_request
    def sanitize_storefront_session():
        # Skip static assets for high performance
        if request.endpoint == 'static':
            return

        user_id = session.get('user_id')
        if user_id:
            user = db.session.get(User, user_id)
            if user and user.role == 'Admin':
                session.pop('user_id', None)
                session.pop('user_name', None)
                session.pop('user_email', None)
                session.pop('user_role', None)

    # Security Headers for safe web operations
    @app.after_request
    def add_security_headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        return response

    # Global Context Processor for Templates
    @app.context_processor
    def inject_global_data():
        user_id = session.get('user_id')
        current_user = db.session.get(User, user_id) if user_id else None

        cart = session.get('cart', {})
        cart_count = sum(cart.values()) if cart else 0

        return {
            'current_user': current_user,
            'cart_count': cart_count,
            'user_role': session.get('user_role'),
            'user_name': session.get('user_name')
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

    @app.errorhandler(403)
    def forbidden(e):
        return render_template('error.html', code=403, message="Bạn không có quyền truy cập vào khu vực này."), 403

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('error.html', code=404, message="Trang bạn tìm kiếm không tồn tại hoặc đã được di dời."), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('error.html', code=500, message="Hệ thống đang gặp sự cố gián đoạn. Vui lòng thử lại sau."), 500

    return app
