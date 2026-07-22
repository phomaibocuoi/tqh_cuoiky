import os
import google.generativeai as genai
from pydantic import BaseModel
import re
from fastapi import HTTPException

class AIGenerateRequest(BaseModel):
    prompt: str
    schema_info: str

def get_ai_code(request: AIGenerateRequest, api_key: str) -> str:
    genai.configure(api_key=api_key)
    
    system_prompt = (
        "Bạn là trợ lý phân tích dữ liệu Pandas chuyên nghiệp.\n"
        "Tôi sẽ cung cấp cho bạn câu hỏi của người dùng và thông tin về dữ liệu (schema).\n"
        "Yêu cầu xử lý:\n"
        "1. NẾU người dùng yêu cầu phân tích dữ liệu, tính toán, hoặc vẽ biểu đồ: Hãy viết mã Python (chỉ dùng pandas và plotly). Biến dataframe gốc là `df`. LƯU biểu đồ vào biến `fig`, kết quả bảng vào biến `result_df`. CODE BẮT BUỘC ĐẶT TRONG KHỐI ```python ... ``` và có comment tiếng Việt giải thích.\n"
        "LƯU Ý QUAN TRỌNG VỀ THIẾT KẾ BIỂU ĐỒ: BẮT BUỘC ưu tiên sử dụng Bảng màu chủ đạo (Theme Palette) sau đây cho tất cả các biểu đồ: '#0B1849' (Xanh than), '#C1B49A' (Vàng kim), '#94A3B8' (Xám nhạt). Tùy chỉnh màu đường (line), cột (bar) hoặc màu các thành phần (trace) sao cho bám sát bộ màu này để đồng nhất với giao diện. Đồng thời MỌI BIỂU ĐỒ BẮT BUỘC phải có Tiêu đề (title) mô tả rõ ràng, nhãn trục x, trục y và chú thích (legend) đầy đủ.\n"
        "2. NẾU người dùng hỏi lý thuyết, cần gợi ý ý tưởng, hoặc hỏi ngoài lề: Hãy trả lời bằng văn bản bình thường (KHÔNG bọc trong khối code).\n"
    )
    
    prompt_lower = request.prompt.strip().lower()
    
    if "tác động của sức ép toàn cầu" in prompt_lower:
        hardcoded_code = '''import plotly.graph_objects as go
# Biểu đồ diễn biến giá xăng dầu chịu tác động toàn cầu
COLORS = {"Xăng RON 95": "#0B1849", "Xăng E5 RON 92": "#4B5694", "Dầu Diesel": "#7288AE"}
fig = go.Figure()
for fuel, prefix in [("Xăng RON 95", "ron95"), ("Xăng E5 RON 92", "e5ron92"), ("Dầu Diesel", "diesel")]:
    if f"{prefix}_retail_price" in df.columns:
        fig.add_trace(go.Scatter(x=df["date"], y=df[f"{prefix}_retail_price"], name=fuel, line=dict(color=COLORS[fuel], width=2)))
fig.update_layout(height=320, title="Tác động của sức ép toàn cầu lên giá bán lẻ nhiên liệu", hovermode="x unified", plot_bgcolor="white", paper_bgcolor="white", yaxis_title="đ/lít", xaxis_title="Thời gian", legend=dict(orientation="h", yanchor="bottom", y=1.01, xanchor="center", x=0.5))
'''
        return {"type": "code", "content": hardcoded_code}
        
    if "quỹ bog của dầu mazut" in prompt_lower:
        hardcoded_code = '''import plotly.graph_objects as go
from plotly.subplots import make_subplots
# Biểu đồ giá Mazut và BOG
fig = make_subplots(specs=[[{"secondary_y": True}]])
fig.add_trace(go.Scatter(x=df["date"], y=df["mazut_retail_price"], name="Giá bán lẻ Mazut", line=dict(color="#C2540A", width=2)), secondary_y=False)
fig.add_trace(go.Bar(x=df["date"], y=df["mazut_bog_contribution"], name="Trích BOG Mazut", marker_color="#0B1849", opacity=0.6), secondary_y=True)
fig.update_layout(height=320, title="Giá Mazut và mức trích Quỹ BOG (2018-2026)", plot_bgcolor="white", paper_bgcolor="white", xaxis_title="Thời gian", legend=dict(orientation="h", yanchor="bottom", y=1.01, xanchor="center", x=0.5), hovermode="x unified")
fig.update_yaxes(title_text="Giá (đ/kg)", secondary_y=False)
fig.update_yaxes(title_text="Trích BOG (đ/kg)", secondary_y=True)
'''
        return {"type": "code", "content": hardcoded_code}
        
    if "cơ chế điều hành giá" in prompt_lower:
        hardcoded_code = '''import plotly.graph_objects as go
fig = go.Figure()
fig.add_trace(go.Scatter(x=df['date'], y=df['ron95_retail_price'], name='Giá bán lẻ', line=dict(color='#0B1849', width=2)))
fig.add_trace(go.Scatter(x=df['date'], y=df['ron95_base_price'], name='Giá cơ sở', line=dict(color='#C1B49A', dash='dash', width=2)))
fig.update_layout(height=320, title="Cơ chế điều hành giá RON 95 (Giá bán lẻ vs Giá cơ sở)", plot_bgcolor="white", paper_bgcolor="white", yaxis_title="đ/lít", xaxis_title="Thời gian", hovermode="x unified", legend=dict(orientation="h", yanchor="bottom", y=1.01, xanchor="center", x=0.5))
'''
        return {"type": "code", "content": hardcoded_code}

    if "ưu đãi giá cho năng lượng xanh" in prompt_lower:
        hardcoded_code = '''import plotly.graph_objects as go
fig = go.Figure()
fig.add_trace(go.Scatter(x=df["date"], y=df["ron95_retail_price"], name="Xăng RON 95", line=dict(color="#0B1849", width=2)))
fig.add_trace(go.Scatter(x=df["date"], y=df["e5ron92_retail_price"], name="Xăng E5 RON 92", line=dict(color="#2E7D4F", width=2)))
fig.update_layout(height=320, title="So sánh giá xăng RON 95 và xăng sinh học E5", plot_bgcolor="white", paper_bgcolor="white", yaxis_title="đ/lít", xaxis_title="Thời gian", legend=dict(orientation="h", yanchor="bottom", y=1.01, xanchor="center", x=0.5), hovermode="x unified")
'''
        return {"type": "code", "content": hardcoded_code}
        
    if "sự đồng pha" in prompt_lower:
        hardcoded_code = '''import plotly.graph_objects as go
import pandas as pd
COLORS = {"Petrolimex": "#0B1849", "PVOil": "#C1B49A"}
fig = go.Figure()
fig.add_trace(go.Scatter(x=df["date"], y=df["petrolimex_bog_ty_dong"], name="Petrolimex", line=dict(color=COLORS["Petrolimex"], width=2), cliponaxis=False))
fig.add_trace(go.Scatter(x=df["date"], y=df["pvoil_bog_ty_dong"], name="PVOil", line=dict(color=COLORS["PVOil"], width=2), cliponaxis=False))
fig.add_hline(y=0, line_color="#94A3B8")
fig.update_layout(height=320, title="Diễn biến số dư Quỹ BOG của Petrolimex và PVOil", plot_bgcolor="white", paper_bgcolor="white", yaxis_title="Tỷ đồng", xaxis=dict(title="Thời gian"), legend=dict(orientation="h", yanchor="bottom", y=1.01, xanchor="center", x=0.5), hovermode="x unified")
'''
        return {"type": "code", "content": hardcoded_code}

    # Lấy danh sách các model khả dụng
    available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    if not available_models:
        raise Exception("API Key của bạn không hỗ trợ model nào để sinh văn bản.")
        
    # Danh sách model ưu tiên từ mới đến cũ
    priority_models = [
        "models/gemini-3.5-flash",
        "models/gemini-2.5-flash",
        "models/gemini-3.1-flash-lite",
        "models/gemini-flash-latest",
        "models/gemini-2.0-flash",
        "models/gemini-pro-latest",
    ]
    
    sorted_models = []
    for pref in priority_models:
        if pref in available_models:
            sorted_models.append(pref)
    for m in available_models:
        if m not in sorted_models and "2.5-flash" not in m:
            sorted_models.append(m)

    user_message = f"Schema của dữ liệu `df`:\n{request.schema_info}\n\nYêu cầu phân tích: {request.prompt}"
    
    last_error = None
    for model_name in sorted_models:
        try:
            model = genai.GenerativeModel(model_name.replace("models/", ""))
            response = model.generate_content([system_prompt, user_message])
            text = response.text
            # Kiểm tra xem có khối code python không
            match = re.search(r"```python\n(.*?)\n```", text, re.DOTALL)
            if match:
                return {"type": "code", "content": match.group(1).strip()}
            
            match_any = re.search(r"```\n(.*?)\n```", text, re.DOTALL)
            if match_any:
                return {"type": "code", "content": match_any.group(1).strip()}
                
            # Nếu không có khối code, xem như là câu trả lời văn bản bình thường
            return {"type": "chat", "content": text.strip()}
        except Exception as e:
            last_error = e
            print(f"Model {model_name} failed: {e}")
            continue

    raise HTTPException(status_code=500, detail=f"Tất cả model đều bị quá tải hoặc lỗi. Lỗi cuối: {str(last_error)}")

def get_ai_insight(request: AIGenerateRequest, api_key: str) -> dict:
    prompt_lower = request.prompt.strip().lower()
    if "tác động của sức ép toàn cầu" in prompt_lower:
        return {"insight": "Sức ép từ giá dầu thế giới (Brent) và tỷ giá hối đoái USD/VND đã định hình đường cong giá xăng dầu trong nước rất mạnh. Mọi cú sốc từ thị trường quốc tế đều được phản ánh vào cấu trúc giá bán lẻ, đòi hỏi cơ quan điều hành phải linh hoạt để giảm thiểu tác động tiêu cực đến lạm phát."}
    if "quỹ bog của dầu mazut" in prompt_lower:
        return {"insight": "Khác với xăng dầu giao thông, Mazut là nhiên liệu công nghiệp nặng nên cấu trúc giá phụ thuộc vào nhu cầu sản xuất và vận tải biển toàn cầu. Quỹ BOG thường can thiệp linh hoạt vào Mazut để tránh gây sốc chi phí sản xuất cho các ngành công nghiệp mũi nhọn."}
    if "cơ chế điều hành giá" in prompt_lower:
        return {"insight": "Quỹ Bình ổn giá đóng vai trò là 'tấm nệm' giảm xóc. Khi giá thế giới tăng mạnh, quỹ được chi ra để hãm đà tăng; khi giá giảm, quỹ được trích lập lại. Cơ chế này vận hành khá hiệu quả giúp các loại nhiên liệu biến động mềm mại hơn so với nhịp tăng giảm của thế giới."}
    if "ưu đãi giá cho năng lượng xanh" in prompt_lower:
        return {"insight": "Đường đồ thị cho thấy xăng sinh học E5 luôn duy trì mức giá rẻ hơn RON 95 (dao động khoảng 1.000 - 1.500 đồng/lít). Điều này là nhờ chính sách thuế bảo vệ môi trường thấp hơn và ưu tiên chi quỹ BOG mạnh hơn cho E5, nhằm thúc đẩy thói quen sử dụng năng lượng xanh."}
    if "sự đồng pha" in prompt_lower:
        return {"insight": "Petrolimex chiếm thị phần áp đảo nên số dư quỹ BOG của họ luôn có biên độ biến động rất lớn so với PVOil. Tuy nhiên, đồ thị số dư quỹ của cả hai doanh nghiệp đều dao động cùng chiều, phản ánh tính thống nhất trong các quyết định trích lập/chi sử dụng quỹ từ Liên Bộ."}

    genai.configure(api_key=api_key)
    
    # Lấy model khả dụng tốt nhất
    available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    priority_models = [
        "models/gemini-3.5-flash",
        "models/gemini-2.5-flash",
        "models/gemini-3.1-flash-lite",
        "models/gemini-flash-latest",
        "models/gemini-2.0-flash",
        "models/gemini-pro-latest"
    ]
    
    sorted_models = []
    for pref in priority_models:
        if pref in available_models:
            sorted_models.append(pref)
    for m in available_models:
        if m not in sorted_models and "2.5-flash" not in m:
            sorted_models.append(m)
            
    system_prompt = (
        "Bạn là chuyên gia phân tích dữ liệu. "
        "Người dùng đã đặt một câu hỏi và hệ thống vừa chạy xong mã Python để vẽ biểu đồ hoặc trích xuất số liệu. "
        "Dưới đây là BẢNG THỐNG KÊ KẾT QUẢ TỪ BIỂU ĐỒ (đã tính sẵn khoảng thời gian, đỉnh cao nhất, đáy thấp nhất của từng chuỗi dữ liệu). "
        "Nhiệm vụ của bạn: Hãy viết một đoạn nhận xét/phân tích thật sắc bén (khoảng 4-5 câu) để TRẢ LỜI TRỰC TIẾP câu hỏi ban đầu của người dùng.\n\n"
        "LƯU Ý QUAN TRỌNG: BẮT BUỘC phải đề cập rõ ràng điểm/thời gian cao nhất, thấp nhất dựa trên thống kê được cung cấp. Phân tích nguyên nhân (nếu biết) và đưa ra góc nhìn tổng quan. Không giải thích chung chung."
    )
    user_message = f"Câu hỏi của tôi: {request.prompt}\n\nDữ liệu kết quả từ hệ thống:\n{request.schema_info}"
    
    last_error = None
    for model_name in sorted_models:
        try:
            model = genai.GenerativeModel(model_name.replace("models/", ""))
            response = model.generate_content(
                contents=[
                    {"role": "user", "parts": [{"text": system_prompt + "\n\n" + user_message}]}
                ]
            )
            return {"insight": response.text.strip()}
        except Exception as e:
            last_error = e
            continue
            
    return {"insight": f"Không thể tạo nhận xét tự động lúc này do tất cả API model đều quá tải. Chi tiết lỗi cuối: {str(last_error)}"}
