# 🌿 Green Corner - Website Thương Mại Điện Tử Cây Cảnh Sinh Thái

Website bán cây cảnh sinh thái cao cấp **Green Corner** được xây dựng với mục tiêu mang đến trải nghiệm mua sắm cây cảnh để bàn, sen đá, xương rồng và cây phong thủy tiện lợi, trực quan và hiện đại.

---

## 🛠️ Công Nghệ Sử Dụng

* **Backend:** Python (Flask Framework 3.x), Flask-SQLAlchemy (ORM), Werkzeug (băm mật khẩu bảo mật).
* **Frontend:** HTML5, CSS3 hiện đại, Vanilla JavaScript, Jinja2 Template Engine.
* **Cơ sở dữ liệu:** 
  * Mặc định: **SQLite** (`greencorner.db`) tự động khởi tạo và nạp dữ liệu mẫu ban đầu.
  * Tùy chọn: **Microsoft SQL Server** (kèm file script `SQLWeb.sql`).
* **Thanh toán:** Tích hợp sinh mã **VietQR Napas247** động chuyển khoản ngân hàng theo từng đơn hàng.

---

## 📂 Cấu Trúc Thư Mục Dự Án

```text
Do_an_Web/
├── .gitignore                          # Cấu hình bỏ qua file rác khi đẩy lên Git
├── Chay_Website_Python.bat             # File khởi động nhanh website
├── requirements.txt                    # Danh sách thư viện phụ thuộc
├── SQLWeb.sql                          # Kịch bản tạo CSDL trên MS SQL Server
├── Bao_Cao_Do_An_Website_GreenCorner.docx # Báo cáo phân tích thiết kế đồ án
└── GreenCornerPython/                  # Thư mục mã nguồn chính của website
    ├── app.py                          # Khởi tạo ứng dụng Flask, bộ lọc Jinja, bảo mật
    ├── config.py                       # Cấu hình ứng dụng và kết nối CSDL
    ├── db_init.py                      # Tự động nạp dữ liệu danh mục, cây cảnh mẫu
    ├── greencorner.db                  # File CSDL SQLite
    ├── models.py                       # Định nghĩa các bảng dữ liệu (ORM)
    ├── run.py                          # File thực thi khởi chạy máy chủ
    ├── routes/                         # Các module điều hướng nghiệp vụ
    │   ├── main.py                     # Trang chủ, giới thiệu, chính sách
    │   ├── products.py                 # Danh sách cây, bộ lọc, chi tiết cây
    │   ├── cart.py                     # Quản lý giỏ hàng
    │   ├── checkout.py                 # Đặt hàng, tính phí ship, VietQR
    │   ├── orders.py                   # Lịch sử và trạng thái đơn hàng
    │   ├── auth.py                     # Đăng ký, đăng nhập tài khoản khách
    │   └── admin.py                    # Cổng quản trị viên (Dashboard, CRUD)
    ├── static/                         # Tài nguyên tĩnh (CSS, JS, hình ảnh cây)
    └── templates/                      # Các trang giao diện HTML (Jinja2)
```

---

## 🚀 Hướng Dẫn Cài Đặt & Khởi Chạy

### 1. Yêu cầu môi trường
* Đã cài đặt **Python 3.10** trở lên trên máy tính.

### 2. Cài đặt thư viện
Mở Terminal / Command Prompt tại thư mục dự án và chạy:
```bash
pip install -r requirements.txt
```

### 3. Khởi chạy website
* **Cách 1 (Nhanh nhất trên Windows):** Nhấp đúp chuột vào file `Chay_Website_Python.bat`.
* **Cách 2 (Dòng lệnh):**
```bash
cd GreenCornerPython
python run.py
```

Truy cập website trên trình duyệt: **http://localhost:5000**

---

## 🔑 Tài Khoản Thử Nghiệm

| Phân hệ | Tài khoản (Email) | Mật khẩu |
| :--- | :--- | :--- |
| **Quản trị viên (Admin)** | `admin@greencorner.vn` | `admin123` |
| **Khách hàng mẫu** | `customer@gmail.com` | `123456` |

* Cổng đăng nhập Quản trị viên: **http://localhost:5000/admin/login**
* Cổng đăng nhập Khách hàng: **http://localhost:5000/account/login**

---

## ✨ Tính Năng Nổi Bật

1. **Khách hàng:**
   - Xem góc không gian sống mẫu (*Living Space Simulator*).
   - Tìm kiếm, lọc theo danh mục (Sen đá, Xương rồng, Cây để bàn, Cây phong thủy), sắp xếp theo giá cả.
   - Xem chi tiết cây kèm 4 thông số chăm sóc chuẩn sinh học (lượng nước tưới, ánh sáng cần thiết, độ ẩm).
   - Giỏ hàng thông minh, tự động áp dụng **Miễn phí vận chuyển** cho đơn từ 300.000 ₫.
   - Tự động sinh mã VietQR Napas247 có sẵn số tiền và nội dung chuyển khoản theo mã đơn.
   - Theo dõi trạng thái đơn hàng qua 4 bước (Chờ xác nhận -> Đã xác nhận -> Đang giao -> Hoàn thành).

2. **Quản trị viên:**
   - Dashboard thống kê tổng doanh thu, số đơn, số sản phẩm, số khách hàng.
   - Bảng cảnh báo sản phẩm sắp hết hàng trong kho (dưới 10 cây).
   - Quản lý sản phẩm (Thêm, Sửa, Xóa mềm bảo toàn đơn hàng).
   - Quản lý danh mục loại cây cảnh.
   - Quản lý đơn hàng và **tự động hoàn trả tồn kho nếu đơn bị hủy**.
   - Quản lý tài khoản và phân quyền người dùng.
