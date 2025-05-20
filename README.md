# 📱 E-COMMERCE PHONE SHOP - AI RECOMMENDATION SYSTEM (FLASK + MONGODB + PHOBERT)

Dự án xây dựng một **website thương mại điện tử bán điện thoại thông minh**, tích hợp hệ thống **gợi ý sản phẩm thông minh sử dụng NLP và PhoBERT**. Người dùng có thể đăng ký, đăng nhập, xem sản phẩm, thêm vào giỏ hàng, thanh toán và nhận gợi ý điện thoại phù hợp nhu cầu.

---

## 🚀 TÍNH NĂNG CHÍNH

- ✅ Danh sách và chi tiết điện thoại (dữ liệu từ MongoDB)
- ✅ Tài khoản người dùng (Đăng ký / Đăng nhập / Đăng xuất)
- ✅ Thêm vào giỏ hàng, cập nhật số lượng, xóa từng sản phẩm
- ✅ Đặt hàng, tự động cập nhật tồn kho
- ✅ Gợi ý điện thoại dựa trên mô tả nhu cầu người dùng:
  - Nhập truy vấn tự nhiên (VD: “pin trâu, chơi game mượt, dưới 10 triệu”)
  - Hệ thống sử dụng PhoBERT để hiểu ngữ nghĩa và đề xuất sản phẩm

---

## 🧱 CÔNG NGHỆ SỬ DỤNG

| Thành phần     | Công nghệ                       |
|----------------|----------------------------------|
| Backend        | Python + Flask                  |
| Frontend       | HTML + CSS                      |
| Cơ sở dữ liệu  | MongoDB (Compass + pymongo)     |
| AI/NLP         | PhoBERT (vinai/phobert-base) + transformers |
| Thư viện khác  | torch, underthesea              |

---

## 📁 CẤU TRÚC DỰ ÁN

phone_shop/
│
├── app.py                  # Flask entrypoint
├── db.py                   # Kết nối MongoDB
├── requirements.txt
│
├── routes/                 # Flask Blueprints
│   ├── auth.py             # Đăng ký / đăng nhập
│   ├── shop.py             # Trang chủ, sản phẩm, giỏ hàng
│   └── recommend.py        # Gợi ý sản phẩm AI
│
├── ai/
│   ├── phobert_recommend.py  # NLP trích xuất đặc điểm từ truy vấn
│   └── data/                # Chứa phones_data.json (import vào MongoDB)
│
├── templates/             # Giao diện HTML
│   ├── index.html, login.html, cart.html, ...
│
└── static/
    └── css/styles.css     # CSS đơn giản
