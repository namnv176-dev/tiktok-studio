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
Skill `/gemini-thay-do <bộ>` (`.claude/skills/gemini-thay-do/SKILL.md`): với mỗi ảnh quần áo trong `anh/<bộ>/`, cắt ảnh cận chất liệu 30% (`scripts/crop_fabric.py`), rồi gửi Gemini qua Chrome MCP 4 ảnh theo thứ tự (`ref/model_identity.png`, ảnh quần áo, ảnh cận chất liệu `anh/<bộ>/crop/<index>.png`, `ref/background_empty.png`: nền đã xóa người, không dùng `background.png` gốc vì Gemini sẽ giữ mặt và vải của người trong đó). Prompt ghép bằng `scripts/build_prompt.py` từ `prompts/cloth-change.md` và chất liệu trong `prompts/fabric-presets.md` (satin / matte / organza / jersey, chọn theo ảnh gốc). Kết quả tải về `generated/<bộ>/<index>`, rồi xóa logo Gemini vào `generated/<bộ>/clean/` (skill `gemini-watermark-remover`, cần người dùng cho phép chạy gói npm và kiểm tra file đầu ra thật sự có). Hỏi chọn profile Chrome **một lần** đầu lượt chạy. Script hỗ trợ: `scripts/gemini_collect.py` (status / mark / collect). Biến thể **1 ảnh 9:16 lưới 4 ô** (4 dáng + 4 góc máy, phụ kiện tự phối): mẫu `prompts/cloth-change-grid4.md` + `prompts/grid4-panels.md`, xem mục "Biến thể" trong SKILL.md; mẫu đồ mới thì tạo nền riêng trước.

## Workflow gen ảnh thay đồ (Antigravity CLI `agy`, Banana Pro)
Skill `/agy-thay-do <bộ>` (`.claude/skills/agy-thay-do/SKILL.md`): đường đi song song không cần Chrome, gọi thẳng `agy -p ... --dangerously-skip-permissions` để agent của Antigravity tự `invoke_subagent` model "pro" (Banana Pro / "Nano Banana Pro"). Tool `generate_image` nội bộ của nó nhận **4 ảnh tham chiếu** như `gemini-thay-do` (người mẫu, quần áo, cận chất liệu, phòng trống) — đã test trực tiếp, không có giới hạn số ảnh nào được xác nhận. Prompt ghép bằng `scripts/build_agy_prompt.py` (dùng chung `prompts/cloth-change.md` + `prompts/fabric-presets.md`). Ảnh ra chỉ ~1K, không upscale được, không có logo ✦ nên không cần bước xóa watermark. Kết quả lưu `generated/<bộ>/<index>-banana-pro.jpg`. Chỉ chạy lệnh `--dangerously-skip-permissions` trong phiên chính (Claude), không đóng gói thành agent con riêng tự bật cờ này — đã thử và bị hệ thống chặn vì coi là tạo agent không an toàn.

## Phân công model theo việc (chốt 09/11/2026)
Mục tiêu: giữ quota tạo ảnh của `agy`. Việc ngoài tạo ảnh chỉ giao cho `agy` khi người dùng yêu cầu lần đó.

| Việc | Giao cho | Trạng thái |
|---|---|---|
| Tạo ảnh thay đồ | `agy` subagent `pro` (`image-generator`); agent điều phối `--model gemini-3.8-flash-high` (người dùng chọn model lớn để mô tả ảnh sát yêu cầu) | Đã thử: tạo được lưới 4 ô từ 1 ảnh tham chiếu; chưa thử với ảnh quần áo thật |
| Tìm web, đọc ảnh sản phẩm có sẵn trên máy | `agy --model claude-sonnet-5-5-low --mode plan`, chạy trong thư mục trống | Đã thử: đọc ảnh và `search_web` đều chạy |
| Xác minh giá, lượt bán, ảnh trên Shopee/TikTok | Claude phiên chính + Chrome MCP | Quy trình hiện có, không tốn quota `agy` |
| Duyệt web bằng `agy` (khi người dùng đã nối Chrome) | `agy --model claude-sonnet-5-5-low` | Chưa chạy được: chưa nối Chrome |
| Ý kiến thứ hai về kịch bản (cần góc nhìn khác Claude) | `agy --model gemini-4-argon-medium` | Chưa thử; tốn quota tuần riêng của Argon, dùng ít |
| Soát ảnh, tổng hợp, viết kịch bản | Claude phiên chính | Không tốn quota `agy` |

Lưu ý khi gọi `agy`:
- Luôn ghi rõ `--model`. Quota tạo ảnh chưa có dòng riêng trong `agy -p /usage`, nên chưa biết trừ vào nhóm nào.
- Từ Git Bash, lệnh bắt đầu bằng `/` (vd `/browser`) phải đặt `MSYS_NO_PATHCONV=1`, nếu không sẽ bị đổi thành đường dẫn.
- Link từ `search_web` là link chuyển hướng và số liệu chỉ từ đoạn trích, phải xác minh trước khi đưa vào bài.

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
