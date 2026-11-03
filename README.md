# tiktok-studio

Tài liệu, skill, workflow và mẫu prompt cho kênh TikTok @thichmacdodep555 (thời trang nữ + ăn vặt).

## Nội dung

- `CLAUDE.md` — hướng dẫn điều phối dự án (vai trò, agent con, quy trình).
- `huong-slideshow.md` — chiến lược nội dung slideshow.
- `bai-01-*.md`, `bai-02-*.md` — kịch bản từng bài đăng.
- `nghien-cuu-phong-cach-80-20.md`, `nghien-cuu-doi-thu-mee-studio25.md`, `kol-han-instagram.md` — báo cáo nghiên cứu.
- `viec-dang-cho.md` — việc đang chờ xử lý.
- `.claude/agents/` — định nghĩa agent con (douyin-trend-scout, fashion-web-researcher).
- `.claude/skills/` — skill tự viết cho dự án (gemini-thay-do, tiktok-fashion-slides).
- `scripts/` — script workflow (thu thập trend, build prompt, crop ảnh, thu ảnh gen...).
- `prompts/` — mẫu prompt dùng với Gemini (đổi đồ, tạo nền trống, đặt nhân vật, preset chất liệu).
- `ref/` — ảnh tham chiếu dùng cho workflow gen ảnh (identity người mẫu, nền trống).

## Không bao gồm

Dữ liệu cào (`data/`), ảnh quần áo gốc (`anh/`), ảnh đã gen (`generated/`), và `.env` (cấu hình bí mật) được loại khỏi repo này theo chủ đích.

Skill `gemini-watermark-remover` (xóa watermark Gemini) là skill bên thứ ba, cài qua `pnpm dlx skills add GargantuaX/gemini-watermark-remover` — không copy lại ở đây, xem tại https://github.com/GargantuaX/gemini-watermark-remover.
