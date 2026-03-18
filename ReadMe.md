# Dữ liệu Chèo và Nghệ thuật Sân khấu Truyền thống

Repository này chứa dữ liệu về Chèo và một số loại hình nghệ thuật sân khấu truyền thống khác của Việt Nam. Dữ liệu được thu thập và xử lý phục vụ cho các mục đích nghiên cứu, phân tích xu hướng tiếp cận của đại chúng trong việc bảo tồn và phát triển văn hóa dân tộc.

Dữ liệu hiện tại được chia làm 2 bộ chính:

---

## 1. Bộ dữ liệu Văn bản (Text Dataset)

Bộ dữ liệu này bao gồm nội dung thu thập từ các video về lĩnh vực Chèo trên nền tảng YouTube. Các trường thông tin được lưu trữ bao gồm:

### Thông tin cơ bản từ YouTube:
* **Video Title**: Tiêu đề video.
* **Channel**: Kênh đăng tải.
* **Duration (s)**: Thời lượng video tính bằng giây.
* **Upload Date**: Ngày đăng tải video.
* **View Count**: Tổng số lượt xem.
* **Like Count**: Tổng số lượt thích.
* **Description**: Nội dung mô tả gốc của video.

### Thông tin trích xuất về vở diễn:
Các thông tin sau được trích xuất từ phần mô tả video (Description) sử dụng **API Gemini 3**:
* **Tác giả vở diễn**: Người viết kịch bản.
* **Đoàn diễn**: Tên nhà hát hoặc đoàn nghệ thuật thực hiện.
* **Soạn giả**: Người soạn lời/làn điệu.
* **Tên vở diễn**: Tên đầy đủ của tác phẩm hoặc trích đoạn.
* **Ngày biểu diễn**: Thời gian thực hiện buổi diễn.
* **Người hát**: Danh sách các nghệ sĩ tham gia.
* **Làn điệu**: Các làn điệu cụ thể được sử dụng trong video (ví dụ: Đào liễu, Cách cú, Luyện năm cung...).

> **Note**: Do giới hạn về thời lượng sử dụng API, tính đến thời điểm hiện tại, khoảng **50%** dữ liệu văn bản đã được hoàn thành trích xuất các thông tin chi tiết về vở diễn.

Location: Statistic/Dataset.xlsx

---

## 2. Bộ dữ liệu Âm thanh (Audio Dataset)

Dữ liệu audio được tải về từ YouTube và lưu trữ dưới định dạng chất lượng cao `.wav`.

### Phạm vi và quy mô:
Bộ dữ liệu bao phủ **137 vở diễn** thuộc **6 loại hình nghệ thuật** khác nhau bao gồm:
1. **Chèo**
2. **Cải Lương**
3. **Ca Trù**
4. **Chầu Văn**
5. **Hát Xẩm**
6. **Quan Họ**

### Phân đoạn (Segmentation):
Dữ liệu audio được xử lý cắt nhỏ để tối ưu cho việc huấn luyện mô hình và phân tích đặc trưng:
* **Độ dài chung**: Các file audio gốc thường được cắt thành các segment có độ dài cố định là **45 giây**.
* **Trường hợp đặc biệt**: Đối với các vở **Chèo có ID từ 13 đến 22**, các file audio được cắt thủ công theo các đoạn thoại có nội dung và ý nghĩa độc lập. Phương pháp này giúp giữ nguyên ngữ cảnh, sắc thái biểu cảm và giá trị nghệ thuật đặc thù của từng phân cảnh.

Location: Audio Dataset

---