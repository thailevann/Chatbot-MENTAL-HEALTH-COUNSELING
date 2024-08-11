# Chatbot-MENTAL-HEALTH

Dự án Chatbot-MENTAL-HEALTH nhằm mục đích cung cấp một công cụ hỗ trợ tâm lý qua chatbot, với dữ liệu được thu thập từ nhiều nguồn khác nhau để tăng cường chất lượng và độ chính xác của các phản hồi. Dưới đây là chi tiết về cách thu thập và xử lý dữ liệu, cũng như các kết quả so sánh mô hình và triển khai.

## Thu thập dữ liệu

1. **Crawl dữ liệu từ các comment hỏi đáp giữa người gặp vấn đề tâm lý với các chuyên gia tâm lý:**
   - [BookingCare.vn](https://bookingcare.vn/cam-nang/hoi-dap)
   - [Ivie.vn](https://ivie.vn/cong-dong/Chuyen-khoa-Tu-van-Tam-ly-486)

2. **Gen data từ Gemini:**
   - **Câu prompt dùng để gen:**
     ```text
     Tạo 1 câu hỏi với vai trò là người cần tham vấn tâm lý và câu trả lời dưới góc nhìn của một chuyên gia tư vấn tâm lý bằng tiếng Việt, đa dạng các chủ đề về tâm lý và lưu theo format sau:
       Người cần tham vấn tâm lý: "đưa ra câu hỏi"
       Chuyên gia tư vấn tâm lý: "đưa ra câu trả lời"
       Ví dụ:
       Người cần tham vấn tâm lý: Em đang là học sinh lớp 12, sắp tới em sẽ có 1 kỳ thi quan trọng nhưng em lại không học được bài. Điều đó khiến em stress kinh khủng. Có hôm em đã khóc 3-4 tiếng liên tục. Gần đây thì ngày nào em cũng khóc (dù cho đó là những điều nhỏ nhặt nhất). Bây giờ em không biết phải làm sao ạ? Em không thể kiềm chế được cảm xúc của mình. Trước đây em đã đi khám và được chuẩn đoán là bị bệnh rối loạn thần kinh thực vật.
       Chuyên gia tư vấn tâm lý: Chào bạn, cảm ơn những chia sẻ của bạn. Theo những gì bạn mô tả, tôi liên tưởng đến một cốc nước đã tràn đầy không thể đổ thêm vào được nữa. Tôi nghe được những trăn trở của bạn, đặc biệt là trước một kỳ thi có tính chất quan trọng. Việc bạn khóc ba bốn tiếng liên tục có thể khi ấy bạn chỉ cảm nhận sự bế tắc, bất lực. Nhưng ở một góc nhìn khác, đó là sự lên tiếng của một đứa trẻ đang bị dồn ép quá lâu, những cảm xúc tuôn trào không thể tiếp tục kiềm chế nữa. Bạn sẽ dành tình thương, thấu cảm cho nó hay bạn sẽ tiếp tục ép nó? Những giọt nước mắt cũng tương tự như những giọt nước tràn ra khỏi chiếc cốc. Vậy phải làm sao cho cốc nước vơi đi để có thể rót thêm vào?
       Gần đây tôi có tiếp nhận một bạn 12 tuổi, do áp lực học tập mà sinh ra loạn thần, hoang tưởng giải cứu thế giới, phải kết hợp dùng thuốc bệnh viện. May mắn là giờ bạn lạc quan, chấp nhận nghỉ và học chậm 1 năm, thông qua gián đoạn mà bạn tìm thấy đam mê và định hướng rõ ràng cho nghề nghiệp tương lai để không phải chọn nhầm ngành rồi phải bắt đầu lại, như vậy việc chậm này có khả năng lại nhanh hơn so với nhiều người khác.
       Điều tôi cảm thấy vui nhất không phải là mình làm được gì, mà là chứng kiến được sức mạnh của tâm trí con người khi gỡ bỏ áp lực tự kỳ vọng, tâm trí họ linh hoạt và sáng tạo để tự nghĩ ra những giải pháp và góc nhìn mới.
       Chúc bạn sớm vượt qua giai đoạn hiện tại.
     ```

3. **Dịch data từ tiếng Anh sang tiếng Việt:**
   - Dữ liệu được lấy từ [Amod/mental_health_counseling_conversations](https://huggingface.co/datasets/Amod/mental_health_counseling_conversations)
Tổng hợp toàn bộ dữ liệu được lưu trên Hugging Face Hub: [thailevann/mental_health_vi_1](https://huggingface.co/datasets/thailevann/mental_health_vi_1)

## So sánh Mô Hình

Dựa vào bảng xếp hạng VLMU, chọn hai mô hình đứng thứ 14 và 15 để so sánh:
- `ura-llama-7b`
- `vinallama-7b-chat`
Sau khi fine-tuning, lưu 2 model lên Hugging Face Hub

- `ura-llama-7b` : https://huggingface.co/thailevann/ura-llama-7b-mental-health_1
  
- `vinallama-7b-chat` : https://huggingface.co/thailevann/vinallama-mental-health_1
  
Kết quả so sánh cho thấy `vinallama-7b-chat` hoạt động tốt hơn.

## Triển khai

Ttriển khai chatbot sử dụng Streamlit và vinallama-7b-chat sau khi fine-tuning. Xem demo tại liên kết sau:

https://www.loom.com/share/83057b5b7d664be1adaa1c9ad9f28426?sid=d520605d-85b5-495b-8ee1-7fafe49d9d72 

Hình ảnh demo:
![image](https://github.com/user-attachments/assets/15cf9035-1429-40da-afa2-760e3baef708)

![image](https://github.com/user-attachments/assets/c12e8106-16b8-48b4-9c79-4c865cda301a)

