# Bài 04: Cùng 1 chiếc váy, đi đám cưới vs đi tiệc

- Dạng bài: Đi đâu mặc gì (đám cưới vs tiệc), Photo Mode, 9 ảnh (dựng theo phong cách skill `tiktok-fashion-slides`)
- Mục tiêu: lượt lưu + follow
- Kênh: @thichmacdodep555
- Trạng thái: **đã lưu nháp** trong TikTok Studio (12:49, 05/11/2026), chưa chọn nhạc, chưa đăng. Nháp hết hạn sau 60 ngày (04/01/2027).

## Ý bài
- Hook: váy đẹp nhưng không nên mặc đi cưới, "trừ 1 trường hợp".
- So sánh: cùng một chiếc váy, chia đôi khung, nửa trái ✕ Đám Cưới, nửa phải ✓ Đi Tiệc.
- Slide chuyển tiếp: "Trường hợp ngoại lệ này mấy bà →".
- Xem thêm: 4 váy đẹp mà dùng được cả đi cưới lẫn đi tiệc (không chữ).

## Nguồn ảnh
- Ảnh quần áo gốc: `so-sanh/`, `xem-them/` (bản chép từ `anh/an-cuoi-sang-chanh/`, `anh/wedding-dress/`, `anh/wedding-vs-party/`).
- Ảnh gen mới: `generated/wedding-vs-party/`
  - `*-banana-pro.jpg`: gen bằng agy (Banana Pro), selfie gương trên `ref/background_empty.png`, mỗi ảnh xoay góc máy khác nhau.
  - Hook: `clean/ac-09-hook-gemini.png`, gen bằng Gemini web (3 ảnh tham chiếu: người mẫu, `anh/an-cuoi-sang-chanh/crop/09-noface.png`, `crop/09.png`), cảnh lối vào tiệc gala chụp flash, đã xóa logo.
- Dùng lại ảnh Bài 02: `generated/wedding-dress/clean/anh-04.png` (slide 3), `anh-08.png` (slide 9).

## Danh sách slide (1080x1920)
| Slide | Ảnh | Chữ |
|---|---|---|
| 1 | `wedding-vs-party/clean/ac-09-hook-gemini.png` | Đẹp Cỡ Này Cũng Đừng Mặc Đi Cưới / (Trừ 1 Trường Hợp), giữa dọc, 56px |
| 2 | `ac-08-banana-pro.jpg` chia đôi | ✕ Đám Cưới: Trắng Ren / Dễ Nhầm / Lấn Át · ✓ Đi Tiệc: Trắng Sang / Nổi Bật / Ren Thanh |
| 3 | `wedding-dress/clean/anh-04.png` chia đôi | ✕ Đám Cưới: Đỏ Rực / Quá Nổi / Hai Dây · ✓ Đi Tiệc: Sexy / Cuốn Hút / Tôn Eo |
| 4 | `ac-07-banana-pro.jpg` chia đôi | ✕ Đám Cưới: Trắng Kem / Dễ Nhầm · ✓ Đi Tiệc: Nữ Tính / Váy Xòe / Ăn Ảnh |
| 5 | `ref/background_empty.png` | Trường Hợp Ngoại Lệ / Này Mấy Bà → |
| 6 | `wd-03-banana-pro.jpg` | không chữ |
| 7 | `wd-02-banana-pro.jpg` | không chữ |
| 8 | `wd-07-banana-pro.jpg` | không chữ |
| 9 | `wedding-dress/clean/anh-08.png` | không chữ |

Bố cục slide so sánh: 2 nửa 538px cùng một ảnh, vạch trắng 4px ở giữa; khối chữ góc trên trái mỗi nửa (top 150px, left 32px), icon tròn SVG (đỏ ✕ / xanh ✓), tiêu đề 40px, các ý 34px, khung xám mờ.

File: `slides/slide-01..09.png` (bản `.jpg` dùng để tải lên TikTok). `slides/mau-so-sanh-wd-04.png` là bản mẫu bố cục đã duyệt.

## Đăng bài
**Caption (đã điền trong nháp):**
```
đẹp mấy cũng đừng mặc đi cưới nha mấy bà, trừ mấy mẫu cuối này 👀

#outfitideas #reviewquầnáonữ #myoutfit #thichmacdep #damancuoi #dicuoi #phoidodicuoi #phoidoxinh #vaydiitiec
```
**Nhạc:** người dùng tự chọn.

## Checklist
- [x] 9 ảnh 1080x1920, chữ serif đủ dấu, không tràn mép
- [x] Ảnh Gemini đã xóa logo ✦ (ảnh agy không có logo)
- [x] Thứ tự ảnh trong TikTok đúng (hook là ảnh bìa)
- [x] Caption + hashtag đã điền, đã lưu nháp
- [ ] Chọn nhạc (người dùng)
- [ ] Đăng / lên lịch (người dùng xác nhận trước khi bấm)

## Lưu ý
- Ảnh agy và ảnh Gemini gói thường chỉ 768x1376, phóng lên 1080x1920 nên hơi mềm.
- Slide 4 (ac-07): váy ra dài tới giữa ống chân, váy gốc dài tới mắt cá.
- wp-07 (váy đen tulle có hoa) đã thử nhiều lần nhưng không dùng; ảnh còn ở `generated/wedding-vs-party/anh-07-*`. `anh/wedding-vs-party/wd-07.webp` hiện là ảnh tham chiếu wp-07 màu be (người dùng thay), không còn là váy trắng mini.
