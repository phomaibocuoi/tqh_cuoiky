# Thuyết minh tab Quỹ Bình Ổn Giá BOG Petrolimex vs PVOil

## Mục tiêu phân tích

Tab này trả lời câu hỏi chính: số dư quỹ BOG của Petrolimex và PVOil biến động ra sao theo thời gian, mức độ xuất hiện giá trị âm được ghi nhận như thế nào và chênh lệch số dư giữa hai doanh nghiệp đang ở mức nào trong phạm vi bộ lọc.

Dữ liệu sử dụng là file data/vn_fuel_price_2018_present.csv, giai đoạn 08/05/2018 đến 31/05/2026 với 2.946 ngày quan sát và độ phủ 100,0 phần trăm theo ngày lịch. Số dư quỹ được ghi nhận theo đơn vị tỷ đồng. Phần phân tích chu kỳ sử dụng cờ is_adjustment_day và tổng mức chi BOG theo ngày của bốn nhóm nhiên liệu RON95, E5 RON92, Diesel và Mazut.

## 1. Diễn biến số dư quỹ theo thời gian

**Câu hỏi phân tích:** Số dư quỹ của Petrolimex và PVOil biến động như thế nào theo thời gian và những giai đoạn nào xuất hiện giá trị âm.

**Biểu đồ lựa chọn:** Line chart hai chuỗi theo thời gian, kèm đường mốc 0.

**Lý do chọn:** Số dư quỹ là chuỗi liên tục theo ngày nên line chart phù hợp để theo dõi xu hướng. Đường mốc 0 hỗ trợ nhận diện trực quan các đoạn thời gian có số dư âm.

**Phân tích:** Kỳ cuối 31/05/2026, Petrolimex ghi nhận 1,074 tỷ đồng và PVOil ghi nhận -1,611.45 tỷ đồng, tương ứng chênh lệch 2,685.45 tỷ đồng. Trong toàn giai đoạn, Petrolimex âm quỹ 15,3 phần trăm số ngày, trong khi PVOil âm quỹ 79,1 phần trăm số ngày. Chênh lệch giữa hai chuỗi quan sát theo thời gian có biên độ từ 279.1 tỷ đồng vào 17/05/2019 đến 8,457.4 tỷ đồng vào 21/11/2022. Các đoạn đường nằm dưới mốc 0 thể hiện các giai đoạn âm quỹ liên tục, có thể đối chiếu với thống kê độ dài giai đoạn âm ở mục 3.

**Insight:** Số dư quỹ của Petrolimex và PVOil vận động theo hai mặt bằng khác nhau. Petrolimex chủ yếu duy trì trạng thái dương, trong khi PVOil phần lớn nằm dưới mốc 0. Vì vậy, chênh lệch giữa hai doanh nghiệp phản ánh khác biệt trạng thái quỹ kéo dài qua nhiều giai đoạn, không chỉ là biến động ngắn hạn ở một vài thời điểm.

## 2. Phân phối số dư quỹ

**Câu hỏi phân tích:** Trong toàn bộ kỳ lọc, số dư quỹ của mỗi doanh nghiệp phân bố ở mức nào, độ phân tán ra sao và vị trí tương đối so với mốc 0 như thế nào.

**Biểu đồ lựa chọn:** Box plot cho Petrolimex và PVOil, kèm đường mốc 0.

**Lý do chọn:** Box plot phù hợp để tóm tắt phân phối của chuỗi số dư trong cả kỳ lọc, thể hiện trung vị, khoảng tứ phân vị và mức độ phân tán mà không cần đọc từng ngày.

**Phân tích:** Với Petrolimex, trung vị là 2,125.5 tỷ đồng, tứ phân vị 25 phần trăm là 629 tỷ đồng và tứ phân vị 75 phần trăm là 3,082 tỷ đồng. Giá trị nhỏ nhất quan sát được là -470 tỷ đồng và giá trị lớn nhất là 4,410 tỷ đồng. Với PVOil, trung vị là -138.42 tỷ đồng, tứ phân vị 25 phần trăm là -525.09 tỷ đồng và tứ phân vị 75 phần trăm là -62.42 tỷ đồng. Giá trị nhỏ nhất quan sát được là -7,113.4 tỷ đồng và giá trị lớn nhất là 593.61 tỷ đồng. Các thống kê này cho thấy phân phối của PVOil nằm dưới mốc 0 trong phần lớn giai đoạn quan sát, trong khi Petrolimex chủ yếu nằm phía dương.

**Insight:** Phân phối số dư xác nhận đây là khác biệt có tính cấu trúc. Với Petrolimex, vùng giá trị điển hình nằm phía dương; với PVOil, vùng giá trị điển hình lại nằm phía âm. Điều đó cho thấy trạng thái âm của PVOil là đặc điểm lặp lại trong toàn bộ giai đoạn, không phải do một vài điểm cực trị kéo lệch kết quả.

## 3. Độ dài các giai đoạn âm quỹ

**Câu hỏi phân tích:** Khi số dư chuyển sang âm, các giai đoạn âm thường kéo dài bao lâu và giai đoạn dài nhất là bao nhiêu ngày.

**Biểu đồ lựa chọn:** Grouped bar chart gồm độ dài trung bình mỗi đợt âm và độ dài đợt âm dài nhất, so sánh giữa Petrolimex và PVOil.

**Lý do chọn:** Hai chỉ số có mục tiêu khác nhau. Độ dài trung bình mô tả mức độ kéo dài điển hình, còn độ dài lớn nhất mô tả trường hợp kéo dài tối đa. Bar chart theo nhóm giúp đọc nhanh chênh lệch giữa hai doanh nghiệp.

**Phân tích:** Trong giai đoạn quan sát, Petrolimex có 2 giai đoạn âm quỹ, độ dài trung bình 225 ngày và giai đoạn dài nhất 374 ngày. PVOil có 3 giai đoạn âm quỹ, độ dài trung bình 777 ngày và giai đoạn dài nhất 1.892 ngày. Các chỉ tiêu này bổ sung cho tỷ lệ ngày âm và mô tả mức độ liên tục của các giai đoạn âm trong chuỗi thời gian.

**Insight:** Khác biệt lớn nhất nằm ở tính kéo dài của các đợt âm quỹ. PVOil không chỉ âm nhiều hơn mà còn âm theo các đợt dài hơn rõ rệt, cho thấy áp lực âm quỹ mang tính liên tục. Trong khi đó, Petrolimex vẫn có giai đoạn âm, nhưng chủ yếu ngắn hơn và ít lặp lại hơn.

## 4. Chi quỹ BOG và độ dài chu kỳ giữ giá

**Câu hỏi phân tích:** Ở góc nhìn theo chu kỳ điều chỉnh giá, chi sử dụng BOG bình quân theo ngày có liên hệ như thế nào với độ dài chu kỳ giữa hai lần điều chỉnh giá liên tiếp.

**Biểu đồ lựa chọn:** Scatter plot, mỗi điểm là một chu kỳ, kèm đường xu hướng tuyến tính khi đủ số lượng chu kỳ.

**Lý do chọn:** Scatter plot phù hợp để quan sát mối quan hệ giữa hai biến liên tục. Đường xu hướng tuyến tính hỗ trợ mô tả hướng quan hệ tổng quát trong phạm vi dữ liệu lọc.

**Phân tích:** Trong toàn giai đoạn, có 246 chu kỳ giữa các lần điều chỉnh giá. Độ dài chu kỳ trung bình là 12,0 ngày và trung vị là 9 ngày. Hệ số tương quan giữa chi BOG bình quân theo ngày và độ dài chu kỳ là r = 0.44 trên tập chu kỳ quan sát. Chu kỳ dài nhất là 116 ngày từ 06/11/2018 đến 02/03/2019 với chi bình quân 2,201 theo ngày. Chu kỳ có chi bình quân cao nhất là 5,354 theo ngày trong giai đoạn 02/03/2019 đến 17/04/2019 với độ dài 46 ngày. Hai giai đoạn 25/02/2021 đến 12/03/2021 và 12/03/2021 đến 27/03/2021 có độ dài 15 ngày với chi bình quân lần lượt 4,800 và 4,300 theo ngày.

**Insight:** Chi BOG bình quân và độ dài chu kỳ điều chỉnh có xu hướng đi cùng chiều. Điều này gợi ý rằng trong những giai đoạn chi quỹ lớn hơn, thời gian giữa hai lần điều chỉnh thường dài hơn. Tuy vậy, mức liên hệ mới ở ngưỡng trung bình, nên nên hiểu đây là xu hướng quan sát trong dữ liệu hơn là quy luật cố định.

## Kết luận chính

Tab Quỹ BOG nên được đọc theo luồng sau:

1. Nhìn KPI để xác định độ phủ dữ liệu và trạng thái kỳ cuối của Petrolimex, PVOil, cùng mức chênh lệch tại kỳ cuối.
2. Đọc biểu đồ diễn biến theo thời gian để nhận diện xu hướng, mức chênh lệch theo giai đoạn và các đoạn nằm dưới mốc 0.
3. Đọc box plot để tổng hợp trung vị và độ phân tán trong toàn kỳ lọc, phục vụ so sánh tổng quan.
4. Đọc biểu đồ độ dài giai đoạn âm để mô tả tính liên tục của các đợt âm theo số ngày.
5. Cuối cùng, đọc scatter theo chu kỳ để bổ sung góc nhìn tham khảo về quan hệ giữa chi BOG bình quân và độ dài chu kỳ điều chỉnh.

Insight tổng quát là quỹ BOG của Petrolimex và PVOil không chỉ khác nhau về mức số dư, mà khác nhau cả về trạng thái vận hành. Petrolimex nhìn chung duy trì được mặt bằng dương, còn PVOil thường xuyên rơi vào trạng thái âm và các đợt âm cũng kéo dài hơn đáng kể. Vì vậy, chênh lệch giữa hai doanh nghiệp là đặc điểm kéo dài của toàn giai đoạn dữ liệu, không phải hiện tượng nhất thời. Ở góc nhìn điều hành, dữ liệu cũng cho thấy chi BOG lớn hơn thường đi cùng chu kỳ giữ giá dài hơn, dù mối liên hệ này mới dừng ở mức xu hướng quan sát.
