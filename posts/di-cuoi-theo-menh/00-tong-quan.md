# Series: Đi Cưới Theo Mệnh

- Dạng bài: Photo Mode, mỗi tập 6 ảnh, 1 nhân vật AI cố định
- Kênh: @thichmacdodep555
- Mục tiêu chính: **kéo follow** (Bài 04 đạt hơn 1.000 view nhưng 0 follower). Mục tiêu phụ: đơn qua mã outfit và link ở bio.
- Thời điểm: đang mùa cưới ở Việt Nam, nên làm sớm
- Nguồn ý tưởng: `y-tuong-menh-mac-gi.md`. Chốt ngày 09/11/2026.

## Ý chính
Người xem sắp đi ăn cưới chỉ hỏi một câu: **"mặc gì để thu hút?"**. Series trả lời bằng outfit đẹp. **Mệnh chỉ là thú vui để giữ người xem**, không phải kiến thức để tin theo.

Mỗi mệnh vướng một luật ngầm khi đi cưới, nên mỗi tập tự có một vấn đề để giải. Series chưa chắc tự kéo được follow, nên ảnh cuối mỗi tập có CTA nhắc đúng thứ người xem còn thiếu: cách giải của mệnh tiếp theo.

## Danh sách tập
| Tập | Mệnh | Luật ngầm | Năm sinh trong tệp 22–31 tuổi | File | Trạng thái |
|---|---|---|---|---|---|
| 1 | Thủy | Hợp đen, nhưng mặc đen đi cưới bị chê xui | 1996, 1997, 2004 | [tap-01-thuy.md](tap-01-thuy.md) | Đã chốt bố cục, chưa làm ảnh |
| 2 | Kim | Hợp trắng, nhưng trắng lấn cô dâu | 2000, 2001 | [tap-02-kim.md](tap-02-kim.md) | Bản nháp |
| 3 | Thổ | Tông đất dễ trông già | 1998, 1999 | [tap-03-tho.md](tap-03-tho.md) | Bản nháp |
| 4 | Mộc | Sợ xanh lá trông quê | 2002, 2003 | [tap-04-moc.md](tap-04-moc.md) | Bản nháp |
| 5 | Hỏa | Đỏ trùng áo dài cô dâu | 1995 | [tap-05-hoa.md](tap-05-hoa.md) | Bản nháp |

**Vì sao theo thứ tự này:** làm mệnh có nhiều năm sinh trong tệp trước để series được phân phối rộng. Thủy có 3 năm; Kim, Thổ, Mộc mỗi mệnh 2 năm; Hỏa 1 năm. Đây là số năm sinh, không phải người xem thật của kênh. Kim xếp Tập 2 để giữ câu CTA người dùng đã viết.

**Năm sinh tính theo bảng nạp âm từ trí nhớ: phải đối chiếu lại trước khi đăng.** Người sinh đầu năm dương lịch, trước Tết, tính theo năm âm liền trước.

## Khung 6 ảnh (dùng cho mọi tập)
| Ảnh | Vai trò | Vị trí chữ |
|---|---|---|
| 1 | Hook nêu luật ngầm, kèm nhãn nhỏ "Tập N · Đi Cưới Theo Mệnh" | Giữa dọc, tối đa 2 dòng |
| 2 | Outfit 1, màu giải luật ngầm | Không chữ |
| 3 | Outfit 2 | Không chữ |
| 4 | Outfit 3 | Không chữ |
| 5 | Màu kỵ của mệnh: nhân vật mặc màu kỵ | Trên cùng, cách mép 150px |
| 6 | CTA, nhắc luật ngầm của mệnh tập sau, nhân vật mặc màu đó | Giữa dọc |

## Quy tắc chung
- **Ảnh outfit không để chữ**, vì ảnh chú thích giải thích thường bị chê quê. Chỉ ảnh hook và ảnh dạng phản đối, gợi ý, giải thích mới có chữ.
- Ảnh 1080x1920, kiểu chữ theo skill `tiktok-fashion-slides` (serif, khung xám mờ). Caption một dòng, không tràn mép; dài quá thì rút ngắn.
- **Ngoại lệ của series:** có CTA ở ảnh cuối, khác quy tắc "không CTA" của skill. Ảnh CTA được nhiều hơn 2 dòng.
- Không có ảnh bảng năm sinh hay infographic. Mệnh chỉ xuất hiện nhẹ trong chữ trên ảnh.
- Nhân vật giữ nguyên vóc dáng, hóa thân theo mệnh của từng tập, không có mệnh cố định.
- Mã outfit để trong caption, kèm "link ở bio". **Không để link Shopee, mã QR hay chữ "Shopee" trong ảnh, caption, bình luận.**
- Chưa ghi giá trên ảnh. Khi ghi thì phải là giá thật lúc làm bài.
- Caption ghi rõ xem mệnh cho vui, không hứa hẹn may mắn hay có người yêu.

## Quy trình làm một tập
1. Đối chiếu năm sinh của mệnh trong tập.
2. Chọn sản phẩm thật cho 3 outfit và ảnh màu kỵ, ảnh CTA. Bỏ ảnh quần áo vào `anh/di-cuoi-<mệnh>/`.
3. Gen ảnh thay đồ bằng `/agy-thay-do` hoặc `/gemini-thay-do`. Ảnh ra ở `generated/di-cuoi-<mệnh>/`.
4. Dựng 6 ảnh theo khung trên. Chốt mã outfit và caption.
5. Xác nhận nội dung với người dùng trước khi lưu nháp hoặc đăng trên TikTok.
6. Ghi kết quả vào mục "Kết quả" của tập.

## Đo sau mỗi tập
Ghi view, lưu, follower mới, bình luận hỏi mã hoặc link, và số đơn. So với Bài 04 (hơn 1.000 view, 0 follower). Đây là lần đầu kênh thử CTA, nên chưa có số để biết CTA có hiệu quả hay không.

## Còn mở
- Lịch đăng từng tập.
- CTA của Tập 5 (chưa có tập tiếp theo).
- Mùa 2 "mặc theo mệnh crush": chỉ làm nếu mùa 1 có đủ bình luận.
