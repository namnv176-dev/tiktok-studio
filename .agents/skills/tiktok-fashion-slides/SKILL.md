---
name: "tiktok-fashion-slides"
description: "Dựng bộ slide ảnh TikTok 1080x1920 cho bài phối đồ: 1 hook, số ảnh sau không giới hạn, caption serif trong khung xám mờ ở trên cùng cách mép 150px (ảnh lưới 4 ô thì caption ở chính giữa ảnh, nhỏ hơn 20%), không infographic, không CTA."
---

# Dựng slide TikTok kiểu phối đồ

Trả lời bằng tiếng Việt. Kết quả là các file PNG 1080x1920 gửi bằng SendUserFile.

## Cấu trúc bộ slide
- Slide 1 là DUY NHẤT một slide hook.
- Sau hook là các ảnh nội dung, số lượng KHÔNG giới hạn (theo số set đồ hoặc số ảnh người dùng đưa). Không ép về 3 slide. TikTok Photo Mode nhận 4 đến 35 ảnh, nhắc người dùng nếu bộ ảnh ít hơn 4.

## Quy tắc thiết kế (người dùng đã chọn)
- Mỗi slide là MỘT ảnh full màn hình. Không tự ghép lưới (ảnh layout 4 do Gemini/agy gen sẵn thành một ảnh thì vẫn dùng bình thường), không bảng giá, không infographic, không thẻ thông tin.
- Chữ chồng trực tiếp lên ảnh: serif mảnh kiểu Garamond (EB Garamond 600), màu trắng, Title Case tiếng Việt, cỡ khoảng 66px.
- Chữ nằm trong khung xám mờ (rgba(70,70,70,.58)), padding 18px 40px, bo góc nhỏ khoảng 10px, căn giữa theo chiều ngang.
- Vị trí chữ:
  - Slide hook: khung chữ ở giữa chiều dọc (ngang phần thân người, top 960px), tối đa 2 dòng.
  - Các ảnh sau hook: caption đặt TRÊN CÙNG, căn chính giữa, mép trên khung cách mép ảnh 150px (top:150px; left:50%; transform:translateX(-50%)). Một dòng, ví dụ "Set 1: Sơ Mi + Quần Ống Rộng".
  - Ảnh layout 4 (một ảnh 9:16 lưới 4 ô, 4 dáng/4 góc máy): caption đặt CHÍNH GIỮA ảnh cả chiều ngang lẫn chiều dọc (giao điểm của lưới, top 960px; left:50%; transform:translate(-50%,-50%)), một dòng. Khung và chữ thu nhỏ 20% so với caption thường: cỡ chữ 53px (thay 66px), padding 14px 32px (thay 18px 40px), bo góc 8px.
- Không CTA trên ảnh, không nhãn đỏ. Đường dẫn bán hàng để ở bio hoặc mục nổi bật.
- Tránh phông sans đậm đen trắng (giống bài đưa tin) và chữ thư pháp.
- Hook theo kiểu kênh mẫu: nêu vấn đề ("Outfit Cùng Quần Dài Cho Nàng Ngại Mặc Váy"), theo dịp ("Đi Đám Cưới Mặc Gì"), theo dáng người, hoặc "Đơn Giản Nhưng Xinh". Không bịa số liệu hay giá.

## Ảnh nền
Không tạo được ảnh người thật. Dùng ảnh người dùng gửi làm nền (cover, 1080x1920, cắt giữ chủ thể). Nếu chưa có ảnh, dựng khung với nền màu và ghi chú vị trí ảnh, nói rõ đó là chỗ trống. Cho người dùng biết họ có thể tự đặt chữ bằng công cụ chữ của TikTok.

## Kỹ thuật dựng (Playwright có sẵn)
1. Cài phông qua npm: `npm i @fontsource/eb-garamond` trong thư mục riêng. Khai báo @font-face ba lần cho weight 600 với các file latin, vietnamese, latin-ext trong node_modules/@fontsource/eb-garamond/files, mỗi file kèm unicode-range đúng, dùng đường dẫn file://. Phải có cả latin và vietnamese, nếu không dấu tiếng Việt bị lỗi.
2. Viết mỗi slide thành một HTML, body 1080x1920, nền là ảnh (background-size: cover) hoặc màu thay thế. Khung chữ là div position:absolute; text-align:center; white-space:nowrap. Lớp hook: top:960px; left:50%; transform:translate(-50%,-50%). Lớp caption phía trên: top:150px; left:50%; transform:translateX(-50%). Lớp caption ảnh layout 4: top:960px; left:50%; transform:translate(-50%,-50%); font-size:53px; padding:14px 32px; border-radius:8px.
3. Script Python chạy playwright chromium, viewport 1080x1920, lặp qua đúng số slide cần dựng (không cố định) và chụp từng slide ra PNG. Chạy bằng `python3 -I`.
4. Mở từng PNG bằng Read để kiểm tra: không bị cắt chữ, không xuống dòng lẻ (một từ đứng một mình), dấu tiếng Việt đủ, caption một dòng không tràn mép (chừa tối thiểu 60px mỗi bên; nếu dài thì rút ngắn nhãn hoặc giảm cỡ chữ). Hook không đè nút của TikTok (tránh sát mép phải và 400px dưới cùng).
5. Gửi tất cả bằng SendUserFile.

## Caption bài đăng gợi ý
Một câu hội thoại ngắn, ví dụ "Tìm ra được set đi làm ưng ý luôn ý 😘", kèm hashtag: #phoidoxinh #tipphoido #outfitideas #reviewquầnáonữ #myoutfit.

## Khi người dùng chê
Hỏi đúng chỗ chê là chữ, màu hay vị trí rồi sửa riêng chỗ đó. Phản hồi "giống bài đưa tin" nghĩa là phông sans đậm quá nặng: chuyển sang serif mảnh và khung mờ.