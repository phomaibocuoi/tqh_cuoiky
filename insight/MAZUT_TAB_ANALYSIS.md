# Thuyết minh tab Nhiên Liệu Công Nghiệp Mazut

## Mục tiêu phân tích

Tab này trả lời câu hỏi chính: giá Mazut được hình thành và điều chỉnh như thế nào, Quỹ BOG can thiệp ra sao, và Mazut khác gì so với mặt bằng nhiên liệu giao thông?

Dữ liệu sử dụng là file `data/vn_fuel_price_2018_present.csv`, giai đoạn 2018-2026. Mazut được phân tích bằng đơn vị `đ/kg`; nhóm nhiên liệu giao thông gồm RON95, E5 RON92 và Diesel.

## KPI tổng quan

Các KPI đầu trang được dùng để tạo bối cảnh nhanh trước khi đọc biểu đồ.

| KPI | Câu hỏi trả lời | Ý nghĩa |
| --- | --- | --- |
| Giá Mazut kỳ cuối | Giá hiện tại của Mazut đang ở mức nào? | Cho biết điểm kết thúc của chuỗi dữ liệu, cập nhật ngày 31/05/2026 là 21.142 đ/kg. |
| Giá cơ sở kỳ cuối | Giá cơ sở ghi nhận đang thấp/cao hơn giá bán lẻ thế nào? | Ngày 31/05/2026, giá cơ sở là 20.442 đ/kg, thấp hơn giá bán lẻ 700 đ/kg. |
| Kỳ có can thiệp BOG | BOG có xuất hiện thường xuyên trong các kỳ điều chỉnh Mazut không? | Có 122/246 kỳ điều chỉnh có BOG, tương đương 49,6%. |
| Biến động TB/kỳ | Mỗi lần điều chỉnh, Mazut thường thay đổi mạnh đến đâu? | Biến động tuyệt đối trung bình là khoảng 445 đ/kg/kỳ. |

## 1. Giá cơ sở, giá bán lẻ và BOG Mazut

**Câu hỏi phân tích:** Giá bán lẻ Mazut đi theo giá cơ sở như thế nào, và BOG xuất hiện ở những giai đoạn nào?

**Biểu đồ lựa chọn:** Biểu đồ kết hợp line chart và bar chart hai trục.

**Lý do chọn:** Giá cơ sở và giá bán lẻ là chuỗi liên tục theo thời gian nên phù hợp với line chart. Trích lập và chi sử dụng BOG là các mức can thiệp tại từng kỳ nên phù hợp với bar chart. Việc đặt chung trong một biểu đồ giúp nhìn được mối quan hệ giữa diễn biến giá và công cụ điều tiết.

**Phân tích:** Giá Mazut giảm sâu trong giai đoạn 2020, sau đó phục hồi mạnh và đạt vùng cao trong năm 2022. Từ 2023 đến 2025, giá dao động trong vùng trung bình hơn, trước khi tăng mạnh trở lại đầu năm 2026. Các cột BOG xuất hiện không đều, tập trung rõ hơn ở một số giai đoạn như 2019-2023 và thưa hơn trong 2024-2025.

**Insight:** Giá bán lẻ Mazut không chỉ phản ánh giá cơ sở mà còn chịu tác động từ cơ chế BOG. Có những giai đoạn BOG xuất hiện dày đặc khi thị trường biến động, nhưng cũng có giai đoạn giá được điều chỉnh gần như không cần can thiệp BOG.

## 2. Cơ cấu can thiệp BOG theo năm

**Câu hỏi phân tích:** Trong từng năm, BOG với Mazut chủ yếu là không can thiệp, trích lập, chi sử dụng hay vừa trích vừa chi?

**Biểu đồ lựa chọn:** Stacked bar chart theo năm.

**Lý do chọn:** Mỗi năm gồm nhiều loại kỳ can thiệp khác nhau. Stacked bar giúp vừa thấy tổng số kỳ, vừa thấy cơ cấu từng loại BOG trong cùng một năm.

**Phân tích:** Giai đoạn 2018-2022 có nhiều kỳ trích lập hoặc chi sử dụng BOG. Năm 2022 nổi bật với số kỳ trích lập cao. Sang 2024-2025, phần “không can thiệp” chiếm tỷ trọng lớn hơn, đặc biệt 2025 ghi nhận 49 kỳ điều chỉnh nhưng đều thuộc nhóm không can thiệp BOG.

**Insight:** Cơ chế BOG với Mazut thay đổi theo thời gian. Giai đoạn đầu dữ liệu cho thấy BOG đóng vai trò điều tiết rõ hơn; các năm gần đây, đặc biệt 2024-2025, Mazut được điều chỉnh nhiều hơn theo cơ chế không can thiệp trực tiếp.

## 3. Nhịp điều chỉnh Mazut theo năm

**Câu hỏi phân tích:** Mazut được điều chỉnh dày hay thưa qua từng năm, và mức biến động trung bình mỗi kỳ có thay đổi không?

**Biểu đồ lựa chọn:** Combo chart gồm bar chart cho số kỳ điều chỉnh và line chart cho biến động trung bình.

**Lý do chọn:** Hai chỉ số có bản chất khác nhau: số kỳ là tần suất, biến động trung bình là cường độ. Bar chart thể hiện tốt số lượng, line chart giúp đọc xu hướng cường độ qua năm.

**Phân tích:** Số kỳ điều chỉnh tăng rõ từ 2018 đến 2025. Năm 2024 có 48 kỳ, năm 2025 có 49 kỳ, cao nhất trong giai đoạn. Tuy nhiên, biến động trung bình không tăng tương ứng; 2024-2025 có nhiều kỳ điều chỉnh nhưng biên độ trung bình thấp hơn 2019-2020 và 2022. Năm 2026 dù mới có 19 kỳ trong dữ liệu đến 31/05/2026, biến động trung bình lại rất cao, khoảng 1.059 đ/kg/kỳ.

**Insight:** Tần suất điều chỉnh cao không đồng nghĩa với biến động mạnh. Giai đoạn 2024-2025 cho thấy Mazut được điều chỉnh thường xuyên nhưng tương đối “nhỏ nhịp”. Ngược lại, đầu 2026 ít kỳ hơn nhưng cường độ biến động lớn hơn nhiều.

## 4. 10 kỳ điều chỉnh Mazut mạnh nhất

**Câu hỏi phân tích:** Những cú điều chỉnh Mazut lớn nhất xảy ra vào ngày nào, tăng hay giảm, và có đi kèm BOG không?

**Biểu đồ lựa chọn:** Horizontal bar chart.

**Lý do chọn:** Biểu đồ thanh ngang phù hợp để xếp hạng các kỳ điều chỉnh theo biên độ, đồng thời dễ đọc nhãn ngày. Trục âm/dương giúp phân biệt kỳ giảm và kỳ tăng.

**Phân tích:** Các kỳ tăng mạnh nhất tập trung nhiều ở năm 2026, gồm 07/03/2026 tăng 3.831 đ/kg và 08/04/2026 tăng 2.944 đ/kg. Một số kỳ giảm mạnh nằm ở 2019 và 2022, ví dụ 11/07/2022 giảm 1.860 đ/kg và 16/08/2019 giảm 1.855 đ/kg. Không phải tất cả cú sốc đều đi kèm BOG; các kỳ tăng rất mạnh đầu 2026 thuộc nhóm không can thiệp.

**Insight:** Các cú điều chỉnh lớn nhất không phân bổ đều qua thời gian. Đầu năm 2026 là giai đoạn có nhiều cú tăng mạnh, trong khi các cú giảm lớn hơn xuất hiện ở các năm trước. Điều này giúp tách “năm nhiều kỳ điều chỉnh” khỏi “năm có cú sốc mạnh”.

## 5. Mazut so với trung bình nhóm nhiên liệu giao thông

**Câu hỏi phân tích:** Sau khi hiểu nội tại Mazut, giá Mazut đang nằm ở vị thế nào so với mặt bằng RON95, E5 và Diesel?

**Biểu đồ lựa chọn:** Line chart so sánh giá Mazut với trung bình nhóm giao thông, kết hợp vùng chênh lệch trên trục phụ.

**Lý do chọn:** Hai đường giá giúp so sánh xu hướng tương đối. Vùng chênh lệch giúp người xem đọc nhanh khoảng cách giữa Mazut và nhóm giao thông mà không phải tự ước lượng bằng mắt.

**Phân tích:** Mazut thường thấp hơn trung bình nhóm nhiên liệu giao thông trong toàn giai đoạn. Chênh lệch trung bình khoảng -4.802 đ/kg hoặc đ/lít theo giá ghi nhận. Khoảng cách sâu nhất vào 01/07/2022, khoảng -10.601; khoảng cách hẹp nhất vào 13/03/2025, khoảng -1.948.

**Insight:** Mazut có mặt bằng giá thấp hơn nhóm nhiên liệu giao thông, nhưng khoảng cách này không ổn định. Có giai đoạn Mazut bị kéo ra rất xa khỏi nhóm giao thông, nhất là quanh 2022; có giai đoạn khoảng cách thu hẹp đáng kể, như 2025. Biểu đồ này đóng vai trò bối cảnh, không thay thế các biểu đồ phân tích nội tại Mazut.

## Kết luận chính

Tab Mazut nên được đọc theo luồng sau:

1. Nhìn KPI để biết trạng thái mới nhất và mức độ can thiệp tổng quan.
2. Đọc biểu đồ giá cơ sở, giá bán lẻ và BOG để hiểu diễn biến chính.
3. Đọc cơ cấu can thiệp BOG để hiểu BOG được dùng theo kiểu nào qua từng năm.
4. Đọc nhịp điều chỉnh và top 10 kỳ mạnh nhất để phân biệt tần suất với cường độ biến động.
5. Cuối cùng, đặt Mazut vào bối cảnh rộng hơn bằng biểu đồ so sánh với nhóm nhiên liệu giao thông.

Insight tổng quát là Mazut không chỉ biến động theo xu hướng giá cơ sở; cách can thiệp BOG và nhịp điều chỉnh thay đổi rõ qua từng giai đoạn. Những năm gần đây cho thấy tần suất điều chỉnh cao hơn, nhưng không phải lúc nào biên độ cũng lớn. Đầu 2026 là giai đoạn cần chú ý vì có nhiều cú điều chỉnh mạnh dù dữ liệu mới đến cuối tháng 5.
