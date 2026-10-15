from decimal import Decimal
from models import db, User, Category, Product, Order, OrderDetail

CATEGORIES_DATA = [
    {"name": "Sen đá", "desc": "Các loại sen đá mini tuyển chọn sinh thái"},
    {"name": "Xương rồng", "desc": "Các loại xương rồng để bàn phong cách hiện đại"},
    {"name": "Cây để bàn", "desc": "Cây cảnh nhỏ trang trí bàn làm việc và thanh lọc khí"},
    {"name": "Cây phong thủy", "desc": "Cây cảnh mang năng lượng tích cực, may mắn và thịnh vượng"},
    {"name": "Cây nội thất", "desc": "Cây dáng cao kiến tạo điểm nhấn cho phòng khách và studio"},
    {"name": "Cây hoa", "desc": "Cây hoa thanh lịch trang trí trong nhà"},
    {"name": "Chậu cây", "desc": "Các loại chậu gốm, sứ, đất nung tinh xảo"}
]

PRODUCTS_DATA = [
    # Sen đá
    ("Sen đá", "Sen đá kim cương", 79000, 20, "/static/images/products/echeveria.jpg", "Lá mọng xếp hoa thị trong trẻo; đặt nơi sáng thoáng và chỉ tưới khi giá thể đã khô."),
    ("Sen đá", "Sen đá nâu chocolate", 69000, 24, "/static/images/products/sen-da-nau-chocolate.jpg", "Lá nâu đỏ xếp hoa thị; cần sáng 4–6 giờ và chỉ tưới khi đất khô."),
    ("Sen đá", "Sen đá phật bà", 75000, 18, "/static/images/products/sen-da-phat-ba.jpg", "Tán lá nhiều lớp gọn đẹp; đón nắng sớm và tránh đọng nước giữa lá."),
    ("Sen đá", "Sen đá chuỗi ngọc", 89000, 16, "/static/images/products/sen-da-chuoi-ngoc.jpg", "Thân rủ với lá mọng như chuỗi ngọc; treo nơi sáng và tưới thưa."),
    ("Sen đá", "Sen đá đô la hồng", 85000, 15, "/static/images/products/sen-da-do-la-hong.jpg", "Lá tròn viền hồng khi đủ sáng; đặt nơi thoáng và tưới khi giá thể khô hẳn."),
    ("Sen đá", "Sen đá móng rồng", 79000, 22, "/static/images/products/sen-da-mong-rong.jpg", "Lá nhọn sọc trắng khỏe; hợp cửa sổ sáng và tưới khoảng 7–10 ngày một lần."),
    ("Sen đá", "Sen đá ngọc bích mini", 99000, 14, "/static/images/products/sen-da-ngoc-bich-mini.jpg", "Lá bầu xanh bóng, dáng bụi; ưa nắng nhẹ buổi sáng và không tưới quá tay."),
    ("Sen đá", "Sen đá sedum vàng", 65000, 25, "/static/images/products/sedum-vang.jpg", "Thảm lá nhỏ vàng xanh; cần nhiều ánh sáng và giá thể thoát nước tốt."),

    # Xương rồng
    ("Xương rồng", "Xương rồng tai thỏ", 69000, 15, "/static/images/products/bunny-ears-cactus.jpg", "Dáng tai thỏ đáng yêu; đặt nơi nhiều sáng, tưới ít và tránh chạm trực tiếp vào gai mịn."),
    ("Xương rồng", "Xương rồng bánh sinh nhật", 79000, 18, "/static/images/products/xuong-rong-banh-sinh-nhat.jpg", "Dáng cầu gai mịn dễ trưng bàn; cần nắng sáng và chỉ tưới khi đất khô."),
    ("Xương rồng", "Xương rồng cầu vồng", 95000, 12, "/static/images/products/xuong-rong-cau-vong.jpg", "Gai màu tạo vòng nổi bật; đặt nơi thật sáng và tưới ít vào gốc."),
    ("Xương rồng", "Xương rồng thanh sơn", 85000, 16, "/static/images/products/xuong-rong-thanh-son.jpg", "Thân cột mọc cụm như núi; chịu nắng tốt và cần tránh úng kéo dài."),
    ("Xương rồng", "Xương rồng bát tiên mini", 119000, 10, "/static/images/products/crown-of-thorns.jpg", "Hoa nhỏ bền màu; cần nắng nhẹ và nên để xa trẻ nhỏ, thú cưng vì cây có gai và nhựa mủ."),
    ("Xương rồng", "Xương rồng gymno ghép màu", 109000, 14, "/static/images/products/xuong-rong-gymno-ghep-mau.jpg", "Đầu ghép rực màu; dùng ánh sáng tán xạ mạnh và tránh nắng trưa gắt."),
    ("Xương rồng", "Xương rồng astro sao biển", 169000, 8, "/static/images/products/astrophytum.jpg", "Dáng sao cao cấp, ít gai; đặt nơi sáng thoáng và tưới rất tiết chế."),

    # Cây để bàn
    ("Cây để bàn", "Cây trầu bà để bàn", 99000, 12, "/static/images/products/golden-pothos.jpg", "Lá xanh pha vàng dễ chăm; hợp ánh sáng gián tiếp và tưới khi mặt đất se khô."),
    ("Cây để bàn", "Cây lưỡi hổ mini", 119000, 18, "/static/images/products/snake-plant.jpg", "Lá đứng gọn, chịu thiếu sáng; tưới khi đất khô sâu, khoảng 10–14 ngày."),
    ("Cây để bàn", "Cây lan ý mini", 139000, 12, "/static/images/products/peace-lily.jpg", "Lá xanh, hoa trắng thanh lịch; ưa sáng gián tiếp và đất ẩm nhẹ."),
    ("Cây để bàn", "Cây ngọc ngân", 129000, 14, "/static/images/products/aglaonema-silver.jpg", "Lá loang trắng xanh nổi bật; tránh nắng trực tiếp và tưới khi mặt đất se khô."),
    ("Cây để bàn", "Cây vạn niên thanh mini", 125000, 13, "/static/images/products/dieffenbachia.jpg", "Tán lá xanh mát, hợp phòng làm việc; cần sáng tán xạ và nên để xa thú cưng."),
    ("Cây để bàn", "Cây dương xỉ tổ chim mini", 149000, 10, "/static/images/products/birds-nest-fern.jpg", "Lá bản mềm tạo cảm giác nhiệt đới; thích ẩm, tránh nắng gắt và gió điều hòa."),
    ("Cây để bàn", "Cây cau tiểu trâm", 139000, 15, "/static/images/products/parlor-palm.jpg", "Tán lá thanh mảnh, hợp góc làm việc; cần sáng nhẹ, tưới vừa và giữ nơi thoáng."),
    ("Cây để bàn", "Cây peperomia đồng tiền", 109000, 17, "/static/images/products/peperomia.jpg", "Lá tròn bóng, dáng nhỏ xinh; để khô 2–3 cm mặt đất rồi mới tưới."),
    ("Cây để bàn", "Cây trầu bà lá xẻ mini", 179000, 9, "/static/images/products/monstera.jpg", "Lá xẻ trẻ trung cho bàn lớn; cần sáng tán xạ mạnh và độ ẩm vừa."),

    # Cây phong thủy
    ("Cây phong thủy", "Cây kim tiền mini", 149000, 10, "/static/images/products/zz-plant.jpg", "Lá xanh bóng, dáng khỏe; chịu sáng vừa và chỉ cần tưới khi đất gần khô."),
    ("Cây phong thủy", "Cây phát tài núi mini", 189000, 10, "/static/images/products/dracaena.jpg", "Dáng thân khỏe, biểu trưng phát triển; chịu sáng vừa và tưới khi đất gần khô."),
    ("Cây phong thủy", "Cây phú quý", 139000, 14, "/static/images/products/red-aglaonema.jpg", "Lá viền đỏ mang sắc may mắn; hợp sáng gián tiếp và độ ẩm vừa phải."),
    ("Cây phong thủy", "Cây bạch mã hoàng tử mini", 169000, 10, "/static/images/products/white-aglaonema.jpg", "Cuống trắng, tán lá sang; tránh nắng trực tiếp, lau lá và tưới khi mặt đất khô."),
    ("Cây phong thủy", "Cây trúc phú quý", 119000, 18, "/static/images/products/lucky-bamboo.jpg", "Thân xanh tượng trưng hanh thông; hợp sáng nhẹ, nếu trồng nước nên thay nước mỗi tuần."),
    ("Cây phong thủy", "Cây hạnh phúc mini", 199000, 8, "/static/images/products/china-doll.jpg", "Tán lá kép xanh bóng, ý nghĩa sum vầy; cần sáng tán xạ và đất ẩm vừa."),
    ("Cây phong thủy", "Cây may mắn chậu mini", 99000, 20, "/static/images/products/lucky-plant.jpg", "Bụi lá xanh nhỏ làm quà tặng; tránh nắng gắt và phun ẩm nhẹ khi hanh khô."),
    ("Cây phong thủy", "Cây kim ngân bím mini", 229000, 8, "/static/images/products/braided-money-tree.jpg", "Thân bím đẹp, biểu trưng tài lộc; đặt nơi sáng thoáng và tưới khi đất khô nửa chậu."),

    # Cây nội thất
    ("Cây nội thất", "Cây đa búp đỏ", 259000, 8, "/static/images/products/rubber-plant.jpg", "Lá lớn xanh sẫm và chồi non ánh đỏ; hợp phòng sáng, tránh đổi vị trí đột ngột và lau lá định kỳ."),
    ("Cây nội thất", "Cây bàng Singapore", 329000, 6, "/static/images/products/fiddle-leaf-fig.jpg", "Tán lá violin tạo điểm nhấn hiện đại; cần ánh sáng tán xạ mạnh và tưới khi mặt đất khô."),
    ("Cây nội thất", "Cây đuôi công Calathea", 239000, 7, "/static/images/products/calathea-orbifolia.jpg", "Lá sọc bạc xanh mềm mại; thích độ ẩm cao, ánh sáng dịu và nước ít khoáng."),

    # Cây hoa
    ("Cây hoa", "Cây hồng môn đỏ", 219000, 9, "/static/images/products/anthurium.jpg", "Hoa đỏ bóng nổi bật, lá xanh hình tim; cần sáng gián tiếp và giữ ẩm vừa, tránh úng.")
]

def init_db(app):
    with app.app_context():
        db.create_all()

        # 1. Seed Categories
        category_map = {}
        for cat_data in CATEGORIES_DATA:
            cat = Category.query.filter_by(category_name=cat_data["name"]).first()
            if not cat:
                cat = Category(category_name=cat_data["name"], description=cat_data["desc"])
                db.session.add(cat)
                db.session.flush()
            category_map[cat.category_name] = cat.category_id

        # 2. Seed Products
        for cat_name, prod_name, price, qty, img, desc in PRODUCTS_DATA:
            cat_id = category_map.get(cat_name)
            if not cat_id:
                continue

            existing = Product.query.filter_by(product_name=prod_name).first()
            if not existing:
                prod = Product(
                    category_id=cat_id,
                    product_name=prod_name,
                    price=Decimal(price),
                    quantity=qty,
                    image_url=img,
                    description=desc,
                    is_active=True
                )
                db.session.add(prod)
            else:
                # Update image_url to ensure it points to /static/images/products/
                existing.image_url = img

        # 3. Seed Admin Users
        admin_emails = ["admin@greencorner.vn", "admin@gmail.com"]
        for email in admin_emails:
            admin = User.query.filter_by(email=email).first()
            if not admin:
                admin = User(
                    full_name="Quản trị Green Corner",
                    email=email,
                    phone="0988668899",
                    address="68 Kim Mã, Ba Đình, Hà Nội",
                    role="Admin"
                )
                admin.set_password("admin123")
                db.session.add(admin)

        # 4. Seed Test Customer
        customer = User.query.filter_by(email="customer@gmail.com").first()
        if not customer:
            customer = User(
                full_name="Nguyễn Văn Khách",
                email="customer@gmail.com",
                phone="0912345678",
                address="120 Pasteur, Phường Bến Nghé, Quận 1, TP.HCM",
                role="Customer"
            )
            customer.set_password("123456")
            db.session.add(customer)

        db.session.commit()
        print(">> Database initialized and seeded successfully!")
