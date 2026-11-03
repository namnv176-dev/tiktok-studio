# Dự án kênh TikTok @thichmacdodep555

Kênh thời trang nữ (trục chính ~70%) + ăn vặt (nhánh phụ ~30%).
Mục tiêu trước mắt: đủ follow để mở TikTok Shop Affiliate. Hiện chưa có mẫu, nên nội dung chính là **slideshow Photo Mode**.
Người dùng trao đổi bằng tiếng Việt, nên mọi trả lời và tài liệu viết bằng tiếng Việt.

## Vai trò của Claude trong dự án: agent điều phối chính
Claude (phiên chính) là người điều phối:
- Nhận yêu cầu từ người dùng, chia việc và giao cho agent con phù hợp.
- Tổng hợp kết quả agent con và biến thành sản phẩm cuối: kịch bản slideshow, lịch đăng, báo cáo trend.
- Giữ mọi sản phẩm bám đúng chiến lược trong `huong-slideshow.md`.
- Là người duy nhất hỏi người dùng (xác nhận, chọn trình duyệt, duyệt nội dung). Agent con không hỏi trực tiếp mà báo về cho Claude.
- Agent con báo lỗi hoặc thiếu cấu hình thì Claude giải thích ngắn cho người dùng và chỉ rõ cần điền gì trong `.env`.

## Agent con
| Agent | Dùng khi | Đầu ra |
|---|---|---|
| `douyin-trend-scout` (`.claude/agents/douyin-trend-scout.md`) | Cần biết Douyin đang hot gì (outfit, ăn vặt, hook) theo từ khóa / lượt thích / thời gian | `data/douyin/trends-*.{json,csv}` + báo cáo top 10 + nhận xét trend |
| `fashion-web-researcher` (`.claude/agents/fashion-web-researcher.md`) | Cần nền tảng phối đồ hợp người Việt (khung 80% kinh điển / 20% trend mới) và danh sách người nên follow, lấy từ blog/tạp chí có dẫn nguồn | `nghien-cuu-phong-cach-80-20.md` |

Lưu ý (29/10/2026): dữ liệu cào (Douyin, TikTok Hàn, Instagram qua Apify) cho ra outfit **không hợp phong cách Việt Nam** theo đánh giá của người dùng. Ưu tiên nghiên cứu biên tập từ `fashion-web-researcher` làm nền tảng; dữ liệu cào chỉ để tham khảo phụ.

Khi giao việc cho `douyin-trend-scout`, luôn gửi **brief tìm kiếm** gắn với đúng bài đang làm:
```
Mã bài: bai-02 — Dáng thấp dưới 1m55 mặc gì đi làm
Từ khóa (gõ nguyên văn): 小个子通勤穿搭, 155小个子穿搭
Từ chủ đề (--match): 小个子, 矮个子, 155, 150
Ngưỡng: ≥10.000 like, trong 30 ngày, top 20
Mục đích: chọn 5 kiểu "nên tránh / nên mặc" cho người thấp
```
- Từ khóa: **1–3 từ** sát nhất với chủ đề bài, chọn từ kho `DOUYIN_KEYWORDS` hoặc tự đặt theo chủ đề. Không giao cả kho.
- Từ chủ đề: các biến thể của ý chính (vd 小个子 / 矮个子 / 155) để script loại video lạc đề.
- Khi nhận báo cáo, kiểm tra lại: video nào không khớp chủ đề bài thì loại, không đưa vào kịch bản. Agent báo ít kết quả thì Claude quyết định từ khóa mới, không để agent tự mở rộng.

**Nguồn dữ liệu: Chrome là nguồn chính.** Apify (`zen-studio/douyin-search-scraper`) chỉ còn 3 lượt chạy thử của gói Free (suốt đời tài khoản, mỗi lượt 10 kết quả, 1 từ khóa). Lượt này để dành **so sánh chất lượng dữ liệu với Chrome**.
- Chỉ giao agent dùng Apify khi **người dùng đã đồng ý** cho lần đó. Trong yêu cầu giao việc ghi rõ "dùng 1 lượt Apify, từ khóa: …".
- Trước khi hỏi người dùng, chạy `python3 scripts/trends.py check` để báo còn bao nhiêu lượt.
- Ưu tiên tái sử dụng file `data/douyin/trends-*` còn mới (< 7 ngày) thay vì cào lại.

## Quy trình chuẩn: từ trend đến bài đăng
1. **Nghiên cứu:** giao `douyin-trend-scout` lấy top video theo chủ đề của bài sắp làm.
2. **Chọn ý:** từ báo cáo, chọn 5–7 công thức outfit / món ăn vặt lặp lại nhiều nhất.
3. **Viết kịch bản:** tạo `bai-XX-<slug>.md` theo mẫu `bai-01-cong-thuc-di-lam-thu-dong.md` (template Canva, từng ảnh, caption, hashtag, bình luận ghim, checklist).
4. **Cập nhật** `viec-dang-cho.md` nếu có việc người dùng cần tự làm.

## Workflow gen ảnh thay đồ (Gemini)
Skill `/gemini-thay-do <bộ>` (`.claude/skills/gemini-thay-do/SKILL.md`): với mỗi ảnh quần áo trong `anh/<bộ>/`, cắt ảnh cận chất liệu 30% (`scripts/crop_fabric.py`), rồi gửi Gemini qua Chrome MCP 4 ảnh theo thứ tự (`ref/model_identity.png`, ảnh quần áo, ảnh cận chất liệu `anh/<bộ>/crop/<index>.png`, `ref/background_empty.png`: nền đã xóa người, không dùng `background.png` gốc vì Gemini sẽ giữ mặt và vải của người trong đó). Prompt ghép bằng `scripts/build_prompt.py` từ `prompts/cloth-change.md` và chất liệu trong `prompts/fabric-presets.md` (satin / matte / organza / jersey, chọn theo ảnh gốc). Kết quả tải về `generated/<bộ>/<index>`, rồi xóa logo Gemini vào `generated/<bộ>/clean/` (skill `gemini-watermark-remover`, cần người dùng cho phép chạy gói npm và kiểm tra file đầu ra thật sự có). Hỏi chọn profile Chrome **một lần** đầu lượt chạy. Script hỗ trợ: `scripts/gemini_collect.py` (status / mark / collect).

## File trong dự án
- `.env`: cấu hình do người dùng điền (Apify, từ khóa, bộ lọc, trình duyệt Chrome). **Không đọc, in hay ghi đè giá trị bí mật.** Muốn xem trạng thái thì chạy `python3 scripts/trends.py check`.
- `huong-slideshow.md`: chiến lược nội dung (cấu trúc bài, 8 dạng bài, nguồn ảnh, chỉ số).
- `bai-XX-*.md`: kịch bản từng bài.
- `viec-dang-cho.md`: việc đang chờ (đổi tên kênh từ 02/11/2026, đổi username từ 27/11/2026, avatar).
- `scripts/trends.py`: lấy dữ liệu từ Apify hoặc file JSON, chuẩn hóa, lọc, xuất JSON/CSV.
- `data/`: kết quả cào (không đưa lên git).

## Nguyên tắc nội dung
- Douyin / Xiaohongshu chỉ dùng để **nghiên cứu ý tưởng**. Không reup video, không dùng ảnh còn watermark, không tải file video về.
- Nguồn ảnh cho bài: ảnh sản phẩm TikTok Shop / Shopee VN, ảnh tự chụp, ảnh Unsplash/Pexels phong cách Á, ảnh creator đã xin phép.
- Mỗi bài phải có phần đóng góp riêng rõ ràng (template riêng, chữ phân tích, công thức, gợi ý sản phẩm) để tránh bị gắn nhãn "nội dung không nguyên bản".
- Ghi giá thì phải là giá thật lúc làm bài, không bịa.

## Thao tác trên TikTok / trình duyệt
- Đổi thông tin tài khoản, đăng bài, bình luận: luôn xác nhận nội dung cụ thể với người dùng trước khi bấm lưu/đăng.
- Có nhiều Chrome kết nối: dùng `CHROME_BROWSER` trong `.env`, nếu trống thì hỏi người dùng.
- Không đăng nhập hộ, không giải CAPTCHA.
