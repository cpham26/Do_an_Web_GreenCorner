from flask import Blueprint, render_template, request, abort
from models import db, Product, Category

products_bp = Blueprint('products', __name__)

@products_bp.route('/products')
def index():
    query = request.args.get('q', '').strip()[:100]
    category_id = request.args.get('categoryId', type=int)
    sort_option = request.args.get('sort', 'newest')
    in_stock_only = request.args.get('inStockOnly') == 'true'
    page = max(1, request.args.get('page', 1, type=int) or 1)
    per_page = 12

    products_query = Product.query.filter_by(is_active=True)

    if query:
        like_pattern = f'%{query}%'
        products_query = products_query.filter(
            db.or_(
                Product.product_name.ilike(like_pattern),
                Product.description.ilike(like_pattern)
            )
        )

    if category_id:
        products_query = products_query.filter_by(category_id=category_id)

    if in_stock_only:
        products_query = products_query.filter(Product.quantity > 0)

    if sort_option == 'price-asc':
        products_query = products_query.order_by(Product.price.asc())
    elif sort_option == 'price-desc':
        products_query = products_query.order_by(Product.price.desc())
    else:  # newest
        sort_option = 'newest'
        products_query = products_query.order_by(Product.created_at.desc(), Product.product_id.desc())

    pagination = products_query.paginate(page=page, per_page=per_page, error_out=False)
    categories = Category.query.all()
    selected_category = db.session.get(Category, category_id) if category_id else None

    return render_template(
        'products/index.html',
        products=pagination.items,
        pagination=pagination,
        categories=categories,
        selected_category=selected_category,
        query=query,
        category_id=category_id,
        sort_option=sort_option,
        in_stock_only=in_stock_only
    )


@products_bp.route('/products/<int:product_id>')
def detail(product_id):
    product = db.get_or_404(Product, product_id)
    if not product.is_active:
        abort(404)

    related_products = Product.query.filter(
        Product.category_id == product.category_id,
        Product.product_id != product.product_id,
        Product.is_active == True
    ).limit(4).all()

    # Determine botanical specs based on category
    cat_name = product.category.category_name if product.category else ""
    if "Sen đá" in cat_name or "Xương rồng" in cat_name:
        spec_light = "Nắng trực tiếp 4-6h/ngày"
        spec_water = "Tưới thưa 1 lần/tuần khi đất thật khô"
        spec_humidity = "30% - 50% (khô thoáng)"
        spec_size = "Mini để bàn (8 - 12 cm)"
    elif "nội thất" in cat_name.lower():
        spec_light = "Sáng tán xạ, tránh nắng gắt"
        spec_water = "Tưới 2 lần/tuần, giữ ẩm đều"
        spec_humidity = "60% - 75% (ẩm mát)"
        spec_size = "Dáng cao trang trí (60 - 120 cm)"
    else:
        spec_light = "Ánh sáng gián tiếp bàn làm việc"
        spec_water = "Tưới 2-3 ngày/lần khi mặt đất khô"
        spec_humidity = "50% - 65% (tiêu chuẩn)"
        spec_size = "Để bàn tiêu chuẩn (15 - 25 cm)"

    return render_template(
        'products/detail.html',
        product=product,
        related_products=related_products,
        spec_light=spec_light,
        spec_water=spec_water,
        spec_humidity=spec_humidity,
        spec_size=spec_size
    )
