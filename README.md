# Control LED with Fingers using OpenCV, Python & ESP8266

Dự án điều khiển đèn LED / thiết bị ngoại vi thông qua nhận diện cử chỉ bàn tay theo thời gian thực (*Real-time Hand Gesture Control*). Hệ thống kết hợp Xử lý ảnh / Thị giác máy tính (OpenCV, MediaPipe), Máy chủ Web (Flask) và Vi điều khiển (ESP8266) kết nối qua giao tiếp Serial.

## 🚀 Tính năng nổi bật

- **Hand Tracking thời gian thực:** Sử dụng MediaPipe Hands để xác định 21 điểm khớp trên bàn tay với độ chính xác cao.
- **Xác định trạng thái 5 ngón tay:** Thuật toán tính toán vị trí tọa độ các ngón (Cái, Trỏ, Giữa, Áp út, Út) để phân loại trạng thái xòe/gập.
- **Giao diện Web Dashboard (Flask):** Livestream luồng video từ Webcam trực tiếp lên trình duyệt web kèm bảng hiển thị trạng thái ON/OFF của từng ngón tay theo thời gian thực.
- **Giao tiếp Serial tốc độ cao:** Truyền mảng trạng thái dữ liệu ngón tay xuống vi điều khiển ESP8266 qua cổng COM/UART để thực thi đóng/ngắt các chân GPIO (LED/Relay/Motor).
