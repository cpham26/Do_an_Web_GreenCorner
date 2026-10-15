from flask import Blueprint, render_template
from models import Product, Category

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    featured_products = Product.query.filter_by(is_active=True).order_by(Product.product_id.asc()).limit(12).all()
    categories = Category.query.all()
    return render_template('index.html', featured_products=featured_products, categories=categories)

@main_bp.route('/about')
def about():
    return render_template('about.html')

@main_bp.route('/privacy')
def privacy():
    return render_template('privacy.html')
