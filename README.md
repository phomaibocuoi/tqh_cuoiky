# Dashboard Giá Xăng Dầu Việt Nam

Dashboard Streamlit phân tích dữ liệu giá xăng dầu Việt Nam theo thời gian, gồm 4 màn hình chính:

- Tổng quan thị trường
- Cơ chế điều hành và điều tiết giá
- Sức ép thị trường toàn cầu
- Nhiên liệu công nghiệp Mazut

## Cấu trúc dự án

```text
.
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

1. Tạo môi trường Python mới nếu cần.
2. Cài thư viện:

```bash
pip install -r requirements.txt
```

3. Chạy app:

```bash
streamlit run app.py
```

## Dữ liệu

- File dữ liệu chính: `data/vn_fuel_price_2018_present.csv`
- Notebook tiền xử lý: `notebooks/preprocess.ipynb`

## Ghi chú

- `app.py` ở thư mục gốc chỉ làm nhiệm vụ khởi chạy.
- Logic hiển thị được gom vào `src/tqh_cuoiki/` để dễ mở rộng và bảo trì.
