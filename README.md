# Dashboard Giá Xăng Dầu Việt Nam

Dashboard Streamlit phân tích dữ liệu giá xăng dầu Việt Nam theo thời gian, gồm 4 màn hình chính:

- Tổng quan thị trường
- Cơ chế điều hành và điều tiết giá
- Sức ép thị trường toàn cầu
- Nhiên liệu công nghiệp Mazut

Bên cạnh đó, ứng dụng tích hợp **Trợ lý AI** giúp người dùng truy vấn dữ liệu và tạo biểu đồ bằng ngôn ngữ tự nhiên.

## Cấu trúc dự án

```text
.
├── api/
│   ├── main.py
│   ├── log_service.py
│   ├── ai_service.py
│   └── execution_service.py
├── app.py
├── data/
│   └── vn_fuel_price_2018_present.csv
├── notebooks/
│   └── preprocess.ipynb
├── requirements.txt
├── src/
│   └── tqh_cuoiki/
│       ├── app.py
│       ├── dashboard_utils.py
│       └── tabs/
│           ├── overview.py
│           ├── price_management.py
│           ├── global_pressure.py
│           └── industrial_fuel.py
└── .streamlit/
    └── config.toml
```

## Chạy ứng dụng

Ứng dụng bao gồm 2 phần: **Backend API (FastAPI)** cho Trợ lý AI và **Frontend (Streamlit)** cho Dashboard.

### 1. Cài đặt môi trường

Tạo môi trường ảo Python mới và cài đặt các thư viện:

```bash
pip install -r requirements.txt
pip install fastapi uvicorn google-generativeai pydantic
```

### 2. Thiết lập biến môi trường (AI Assistant)

Để sử dụng chức năng AI, bạn cần thiết lập biến môi trường `GEMINI_API_KEY`:

- **Windows (PowerShell):**
  ```powershell
  $env:GEMINI_API_KEY="your_api_key_here"
  ```
- **Linux/Mac:**
  ```bash
  export GEMINI_API_KEY="your_api_key_here"
  ```
*(Lưu ý: Nếu không thiết lập, hệ thống sẽ sử dụng key mặc định dùng cho mục đích phát triển).*

### 3. Khởi chạy Backend API (FastAPI)

Mở một terminal mới và chạy lệnh sau để khởi động API:

```bash
python -m uvicorn api.main:app --reload --port 8000
```

### 4. Khởi chạy Frontend Dashboard (Streamlit)

Mở một terminal thứ hai và chạy lệnh sau để khởi động giao diện Streamlit:

```bash
python -m streamlit run app.py
```

## Dữ liệu

- File dữ liệu chính: `data/vn_fuel_price_2018_present.csv`
- Notebook tiền xử lý: `notebooks/preprocess.ipynb`

## Ghi chú

- `app.py` ở thư mục gốc chỉ làm nhiệm vụ khởi chạy Dashboard.
- Cấu trúc API được đặt trong thư mục `api/` xử lý kết nối model AI, lưu vết log, và thực thi mã an toàn.
- Logic hiển thị của Dashboard được gom vào `src/tqh_cuoiki/` để dễ mở rộng và bảo trì.
