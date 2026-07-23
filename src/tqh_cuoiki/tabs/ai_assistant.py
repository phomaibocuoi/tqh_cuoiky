import streamlit as st
import requests
import pandas as pd
import json
import plotly.io as pio
import io

import os

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

def get_schema_info(df: pd.DataFrame) -> str:
    schema = []
    for col in df.columns:
        dtype = df[col].dtype
        sample = df[col].dropna().head(3).tolist()
        schema.append(f"- Cột `{col}` (Kiểu: {dtype}): Mẫu dữ liệu {sample}")
    return "\n".join(schema)

def render(df: pd.DataFrame):
    st.markdown("""
        <style>
        .hero-title { font-size: 32px; font-weight: 800; color: var(--brand); letter-spacing: -0.8px; margin-bottom: 5px; }
        .hero-subtitle { font-size: 14px; color: var(--muted); margin-bottom: 25px; }
        .suggestion-card { border: 1px solid var(--line); border-radius: 8px; padding: 15px; margin-bottom: 10px; cursor: pointer; transition: all 0.2s; background: white;}
        .suggestion-card:hover { border-color: var(--brand); box-shadow: 0 4px 12px rgba(0,0,0,0.05); }
        .editor-container { border: 1px solid var(--line); border-radius: 8px; padding: 15px; background: #fafafa; margin-top:10px; }
        div[data-testid="stTextArea"] textarea { font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace !important; font-size: 14px !important; line-height: 1.5 !important; background-color: #f6f8fa !important; border: 1px solid #d0d7de !important;}
        div[data-testid="stChatInput"] { border: 2px solid #0B1849 !important; border-radius: 10px !important; box-shadow: 0 4px 14px rgba(11,24,73,0.15) !important; padding: 2px; }
        </style>
    """, unsafe_allow_html=True)
    
    st.markdown(
    """<div style="display:flex;align-items:center;justify-content:space-between;
    border-bottom:2px solid var(--line);padding-bottom:12px;margin-bottom:20px;width:100%;">
    <div style="font-size:30px;font-weight:800;color:var(--brand);letter-spacing:-0.8px;line-height:1.1;">
    Xin chào, tôi là 
    <span style="font-weight:800;">
    TRỢ LÝ AI
    </span>
    <div style="font-size:14px;color:var(--muted);margin-top:8px;font-weight:normal;">
    Nhập yêu cầu phân tích dữ liệu và AI sẽ tự động sinh mã nguồn để xử lý.
    </div>
    </div>
    <span style="background:var(--brand);color:#fff;font-size:10px;font-weight:800;
    padding:4px 10px;border-radius:999px;letter-spacing:.5px;text-transform:uppercase;">
    AI Assistant
    </span>
    </div>""",
    unsafe_allow_html=True,
    )
    
    with st.expander("Lịch sử sử dụng"):
        try:
            logs_res = requests.get(f"{API_BASE_URL}/api/logs")
            if logs_res.status_code == 200:
                logs = logs_res.json()
                if logs:
                    log_options = { f"{log['timestamp'][:16].replace('T', ' ')} | {str(log['user_prompt'])[:60]}...": log for log in logs }
                    selected_log_label = st.selectbox("Danh sách các câu hỏi: ", ["-- Chọn --"] + list(log_options.keys()))
                    
                    if selected_log_label != "-- Chọn --":
                        selected_log = log_options[selected_log_label]
                        st.markdown(f"**Yêu cầu:** {selected_log['user_prompt']}")
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            st.markdown("**Code AI sinh ra:**")
                            st.code(selected_log["ai_generated_code"], language="python")
                        with col2:
                            st.markdown("**Code thực thi cuối cùng:**")
                            st.code(selected_log["final_edited_code"], language="python")
                            
                        if st.button("Tái tạo biểu đồ từ mã nguồn này", type="primary"):
                            with st.spinner("Đang chạy lại mã nguồn..."):
                                exec_payload = {
                                    "code": selected_log["final_edited_code"],
                                    "user_prompt": selected_log["user_prompt"],
                                    "ai_code": selected_log["ai_generated_code"]
                                }
                                res = requests.post(f"{API_BASE_URL}/api/execute", json=exec_payload)
                                if res.status_code == 200:
                                    result_data = res.json()
                                    if result_data.get("status") != "error":
                                        if result_data.get("has_fig") and result_data.get("fig_json"):
                                            fig = pio.from_json(result_data.get("fig_json"))
                                            st.plotly_chart(fig, use_container_width=True)
                                        if result_data.get("has_df") and result_data.get("df_json"):
                                            res_df = pd.read_json(io.StringIO(result_data.get("df_json")), orient="records")
                                            st.dataframe(res_df)
                                    else:
                                        st.error("Lỗi khi chạy code:")
                                        st.code(result_data.get("traceback"))
                                else:
                                    st.error("Không thể kết nối đến API.")
                else:
                    st.info("Chưa có lịch sử hỏi đáp nào.")
        except Exception as e:
            st.error(f"Lỗi tải lịch sử: {e}")
        
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
        
    # Xử lý gợi ý
    if "pending_suggestion" not in st.session_state:
        st.session_state.pending_suggestion = None
    
    # Lấy prompt từ input hoặc từ suggestion
    input_prompt = st.chat_input("Nhập yêu cầu phân tích...")
    prompt = st.session_state.pending_suggestion or input_prompt
    
    if prompt:
        # Xóa pending suggestion sau khi đã dùng
        st.session_state.pending_suggestion = None
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        
        with st.spinner("Đang xử lý yêu cầu, vui lòng chờ trong chốc lát."):
            try:
                schema_info = get_schema_info(df)
                payload = {
                    "prompt": prompt,
                    "schema_info": schema_info
                }
                res = requests.post(f"{API_BASE_URL}/api/ai/generate", json=payload)
                if res.status_code == 200:
                    data = res.json()
                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "type": data.get("type", "code"),
                        "content": data.get("content", "")
                    })
                else:
                    st.error(f"Lỗi từ API: {res.text}")
            except Exception as e:
                st.error(f"Không thể kết nối đến AI API: {e}")
                st.info("Hãy đảm bảo bạn đang chạy server FastAPI (uvicorn api.main:app --reload) và đã set GEMINI_API_KEY.")
    
    # (Xóa phần empty state cũ ở đây để dời xuống dưới)
    # Render toàn bộ lịch sử chat
    for idx, msg in enumerate(st.session_state.chat_history):
        if msg["role"] == "user":
            st.markdown(f"""
            <div style="display: flex; justify-content: flex-end; margin-bottom: 20px; margin-top: 10px;">
                <div style="background-color: #0B1849; color: white; padding: 12px 20px; border-radius: 18px 18px 0px 18px; max-width: 75%; box-shadow: 0 4px 10px rgba(0,0,0,0.1); line-height: 1.5; font-size: 15px;">
                    {msg["content"]}
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            with st.chat_message("assistant"):
                if msg.get("type") == "chat":
                    st.write(msg["content"])
                elif msg.get("type") == "code":
                    st.code(msg["content"], language="python")
                elif msg.get("type") == "result":
                    result = msg["content"]
                    st.markdown("---")
                    if result.get("status") == "error":
                        st.error("Lỗi khi chạy code:")
                        st.code(result.get("traceback"))
                    else:
                        if result.get("logs"):
                            with st.expander("Logs thực thi (print)"):
                                st.text(result.get("logs"))
                        if result.get("has_fig") and result.get("fig_json"):
                            fig = pio.from_json(result.get("fig_json"))
                            st.plotly_chart(fig, use_container_width=True, key=f"chart_{idx}")
                        if result.get("has_df") and result.get("df_json"):
                            res_df = pd.read_json(io.StringIO(result.get("df_json")), orient="records")
                            st.dataframe(res_df, key=f"df_{idx}")
                        # Insight được đưa xuống cuối cùng
                        if result.get("insight"):
                            st.success(f"**Nhận xét tham khảo:** {result.get('insight')}")
            
    # Hiển thị khu vực chỉnh sửa code và nút thực thi cho đoạn code MỚI NHẤT
    if len(st.session_state.chat_history) > 0:
        last_msg = st.session_state.chat_history[-1]
        if last_msg["role"] == "assistant" and last_msg.get("type") == "code":
            st.markdown("<div class='editor-container'>", unsafe_allow_html=True)
            st.markdown("### Mã nguồn đề xuất")
            st.markdown("Bạn có thể **xem** và **chỉnh sửa** (nếu cần) đoạn mã bên dưới trước khi thực thi. Vui lòng nhớ rằng AI có thể mắc lỗi, hãy kiểm tra kỹ trước khi chấp nhận.")
            
            editor_key = f"code_editor_{len(st.session_state.chat_history)}"
            
            with st.form(key=f"code_form_{editor_key}"):
                edited_code = st.text_area("Mã Python", value=last_msg["content"], height=300, key=editor_key)
                submit_button = st.form_submit_button("Đồng ý", type="primary")
            
            if submit_button:
                with st.spinner("Đang thực thi mã nguồn..."):
                    try:
                        user_prompt = ""
                        if len(st.session_state.chat_history) >= 2:
                            user_prompt = st.session_state.chat_history[-2]["content"]
                            
                        exec_payload = {
                            "code": edited_code,
                            "user_prompt": user_prompt,
                            "ai_code": last_msg["content"]
                        }
                        res = requests.post(f"{API_BASE_URL}/api/execute", json=exec_payload)
                        if res.status_code == 200:
                            result_data = res.json()
                            
                            if result_data.get("status") != "error":
                                with st.spinner("AI đang đọc biểu đồ để rút ra nhận xét..."):
                                    try:
                                        data_context = ""
                                        if result_data.get("df_json"):
                                            data_context += "Dữ liệu mẫu: " + result_data["df_json"][:1500] + "\n\n"
                                            
                                        if result_data.get("fig_json"):
                                            try:
                                                fig_dict = json.loads(result_data["fig_json"])
                                                summary = []
                                                for trace in fig_dict.get("data", []):
                                                    name = trace.get("name", "Chuỗi dữ liệu")
                                                    y_vals = trace.get("y", [])
                                                    x_vals = trace.get("x", [])
                                                    
                                                    if isinstance(y_vals, list) and isinstance(x_vals, list) and len(y_vals) == len(x_vals):
                                                        valid_points = [(x, y) for x, y in zip(x_vals, y_vals) if y is not None and isinstance(y, (int, float))]
                                                        if valid_points:
                                                            valid_x = [p[0] for p in valid_points]
                                                            valid_y = [p[1] for p in valid_points]
                                                            max_y = max(valid_y)
                                                            min_y = min(valid_y)
                                                            max_x = valid_x[valid_y.index(max_y)]
                                                            min_x = valid_x[valid_y.index(min_y)]
                                                            summary.append(f"- {name}: Kéo dài từ {valid_x[0]} đến {valid_x[-1]}. Đỉnh cao nhất là {max_y} (tại {max_x}), đáy thấp nhất là {min_y} (tại {min_x}).")
                                                if summary:
                                                    data_context += "Thống kê từ Biểu đồ:\n" + "\n".join(summary)
                                            except:
                                                pass
                                                
                                        if not data_context.strip():
                                            data_context = result_data.get("logs", "Biểu đồ đã được vẽ.")
                                            
                                        if not result_data.get("insight"):
                                            insight_payload = {
                                                "prompt": user_prompt,
                                                "schema_info": data_context
                                            }
                                            insight_res = requests.post(f"{API_BASE_URL}/api/insight", json=insight_payload)
                                            if insight_res.status_code == 200:
                                                result_data["insight"] = insight_res.json().get("insight")
                                    except Exception as e:
                                        print("Lỗi khi lấy nhận xét:", e)
                            
                            # Cập nhật lại đoạn code trong lịch sử thành code đã chỉnh sửa
                            st.session_state.chat_history[-1]["content"] = edited_code
                            
                            st.session_state.chat_history.append({
                                "role": "assistant",
                                "type": "result",
                                "content": result_data
                            })
                            st.rerun()
                        else:
                            st.error(f"Lỗi thực thi: {res.text}")
                    except Exception as e:
                        st.error(f"Không thể kết nối đến Execution API: {e}")
            st.markdown("</div>", unsafe_allow_html=True)
            
    st.markdown("---")
    st.markdown("**Câu hỏi gợi ý nhanh:**")
    
    q1 = "Vẽ biểu đồ so sánh giá bán lẻ Xăng RON 95, E5 RON 92 và Dầu Diesel để phân tích tác động của sức ép toàn cầu."
    if st.button(f"1. (23120122) {q1}", use_container_width=True):
        st.session_state.pending_suggestion = q1
        st.rerun()

    q2 = "Vẽ biểu đồ kết hợp thể hiện giá bán lẻ và mức trích Quỹ BOG của dầu Mazut để đánh giá can thiệp điều tiết."
    if st.button(f"2. (23120151) {q2}", use_container_width=True):
        st.session_state.pending_suggestion = q2
        st.rerun()

    q3 = "Vẽ biểu đồ so sánh Giá bán lẻ và Giá cơ sở của xăng RON 95 để đánh giá cơ chế điều hành giá."
    if st.button(f"3. (23120152) {q3}", use_container_width=True):
        st.session_state.pending_suggestion = q3
        st.rerun()

    q4 = "So sánh giá Xăng RON 95 và Xăng E5 RON 92 để thấy rõ chính sách ưu đãi giá cho năng lượng xanh."
    if st.button(f"4. (23120172) {q4}", use_container_width=True):
        st.session_state.pending_suggestion = q4
        st.rerun()

    q5 = "So sánh diễn biến số dư Quỹ BOG của Petrolimex và PVOil để phân tích sự đồng pha trong trích lập và chi sử dụng quỹ."
    if st.button(f"5. (23120176) {q5}", use_container_width=True):
        st.session_state.pending_suggestion = q5
        st.rerun()
