# 🚀 Hành trình tối ưu hóa Observathon (Lab 13)

**Kết quả cuối cùng:** Đạt **97.73 / 100** điểm (Public Phase)

Quá trình giải quyết thử thách này là một chuỗi các bước chẩn đoán và "vá" lỗi liên tục trên một hệ thống LLM Agent "hộp đen":

1. **Xây dựng Observability:** Đầu tiên, mình thiết lập bộ lọc PII và đưa vào `solution/wrapper.py` để đánh chặn các thông tin nhạy cảm (email, SĐT), đồng thời kích hoạt cache để tiết kiệm Token và đo đạc Latency.
2. **Khắc phục lỗi treo & Loop:** Agent ban đầu hay bị lặp vô tận khi dùng tool. Mình đã can thiệp vào `config.json` để khóa cứng `tool_budget=3`, bật `loop_guard` và thêm lệnh cấm *"1 call per tool"* vào Prompt.
3. **Ép cân System Prompt:** Để lấy tối đa điểm Prompt và tránh bị phạt Bloat, Prompt được "ép cân" xuống còn vỏn vẹn **453 ký tự**, nhưng sử dụng các quy tắc đanh thép để bắt Agent tính toán bằng công thức cố định thay vì tự đoán.
4. **Cân bằng Config & Latency:** Sau nhiều vòng lặp chạy giả lập, mình đã chốt hạ cấu hình dùng model `premium` kết hợp `self_consistency=3` để đảm bảo độ chính xác cao nhất (105/120 câu đúng), đổi lại tắt `planner` và giữ `context_size=8` để chống Quality Drift.
5. **Hoàn thiện Diagnosis F1:** Dựa trên các log thu thập được trong quá trình giả lập, mình đã khoanh vùng và "chỉ mặt đặt tên" chính xác 10 Fault Classes xảy ra trong tập Public (như `error_spike`, `tool_failure`, `cost_blowup`...), mang về điểm số chẩn đoán F1 1.0 hoàn hảo.
