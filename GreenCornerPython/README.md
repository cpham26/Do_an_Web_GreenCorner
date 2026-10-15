# 🌿 GREEN CORNER - WEBSITE THƯƠNG MẠI ĐIỆN TỬ CÂY CẢNH (BẢN PYTHON)

Dự án website bán cây cảnh sinh thái cao cấp **Green Corner** được xây dựng theo kiến trúc hiện đại:
- **Backend:** **Python (Flask Framework)** + **SQLAlchemy ORM**.
- **Frontend / Giao diện:** **HTML5, CSS3, JavaScript** + Template Engine **Jinja2** (kế thừa toàn bộ 100% giao diện cao cấp phong cách OpenAI GPT-6 Astra, responsive mobile và hiệu ứng mượt mà).
- **Cơ sở dữ liệu (Database):** **SQL (SQLite)** tự khởi tạo và nạp dữ liệu tự động (`greencorner.db`), không cần cài đặt SQL Server phức tạp, chạy được ngay trên mọi máy tính.

---

## 🚀 HƯỚNG DẪN CHẠY DỰ ÁN

### Cách 1: Chạy bằng file `start.bat` (Nhanh nhất)
Nhấp đúp chuột vào file `start.bat` trong thư mục `GreenCornerPython`.

### Cách 2: Chạy bằng dòng lệnh Terminal / Command Prompt
```bash
cd GreenCornerPython
..\.venv\Scripts\python.exe run.py
```
*(Hoặc nếu máy đã cài Python: `python run.py`)*

Sau đó mở trình duyệt và truy cập: **http://localhost:5000**

---

## 🔑 TÀI KHOẢN ĐĂNG NHẬP SẴN

| Vai trò | Email | Mật khẩu |
| :--- | :--- | :--- |
| **Quản trị viên (Admin)** | `admin@greencorner.vn` | `admin123` |
| **Khách hàng mẫu (Customer)** | `customer@gmail.com` | `123456` |

---

## 🌟 CÁC TÍNH NĂNG NỔI BẬT

1. **Trang chủ (Homepage):**
   - Hero scene biểu tượng với cây cảnh sinh thái trung tâm và hiệu ứng hào quang ánh sáng.
   - Bảng giả lập không gian sống (Living Space Simulator) tương tác chuyển cảnh mượt mà.
   - 4 thẻ hệ sinh thái thực vật đặc trưng (Sen đá, Xương rồng, Cây để bàn, Cây phong thủy).
   - Danh sách sản phẩm tuyển chọn nổi bật.

2. **Cửa hàng & Danh mục:**
   - Bộ lọc theo danh mục, từ khóa tìm kiếm, sắp xếp theo giá hoặc độ mới.
   - Phân trang tự động.
   - Chi tiết sản phẩm với thông số ánh sáng, lượng nước, độ ẩm và kích thước chậu tương thích sinh thái học.

3. **Giỏ hàng & Thanh toán thông minh:**
   - Quản lý giỏ hàng lưu bằng Session (thêm, sửa số lượng, xóa, làm trống).
   - Tự động áp dụng chính sách **Miễn phí vận chuyển** cho đơn từ 300.000 ₫.
   - Hỗ trợ 2 hình thức vận chuyển: Tiêu chuẩn (2-3 ngày) hoặc Hỏa tốc 2H (+35.000 ₫) có tính toán tiền trực tiếp.
   - **Tích hợp mã VietQR Napas247 động:** Tự sinh mã QR ngân hàng MB Bank có sẵn số tiền và nội dung chuyển khoản theo mã đơn hàng.

4. **Trang Quản trị (Admin Dashboard):**
   - Truy cập tại: `/admin` (yêu cầu tài khoản Admin).
   - Thống kê doanh thu thực tế, số lượng đơn hàng, sản phẩm, thành viên.
   - Cảnh báo tồn kho thấp (< 10 cây).
   - Quản lý sản phẩm (Thêm, Sửa, Xóa, Cập nhật giá và số lượng).
   - Quản lý danh mục (Thêm, Sửa, Xóa danh mục).
   - Quản lý đơn hàng (Lọc trạng thái, xem chi tiết và duyệt trạng thái đơn hàng).
   - Quản lý người dùng (Danh sách tài khoản, chuyển đổi quyền Quản trị viên).
