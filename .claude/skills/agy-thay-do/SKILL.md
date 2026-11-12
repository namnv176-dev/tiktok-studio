---
name: agy-thay-do
description: Thay đồ cho người mẫu bằng Antigravity CLI (lệnh `agy`), model Banana Pro (Nano Banana Pro) — tạo ảnh từ 4 tham chiếu (người mẫu, trang phục, cận chất liệu, phòng trống), không cần mở Chrome/đăng nhập Gemini web. Dùng khi người dùng gõ /agy-thay-do <bộ>, nói "dùng agy", "dùng banana pro", "dùng nano banana" để gen ảnh, hoặc muốn một cách gen ảnh thử đồ khác không qua trình duyệt.
---

# Workflow: thay đồ cho mẫu bằng Antigravity CLI (`agy`)

Tham số: tên bộ ảnh (vd `wedding-dress`). Không có thì hỏi hoặc liệt kê `anh/`. Có thể kèm danh sách index (vd `anh-02 anh-05`) để chỉ làm lại vài ảnh.

Đây là đường đi **song song** với skill `gemini-thay-do` (Chrome + gemini.google.com), dùng chung `ref/`, `anh/<bộ>/`, `prompts/cloth-change.md`, `prompts/fabric-presets.md` và thư mục `generated/<bộ>/`, nhưng gọi thẳng model qua CLI nên nhanh hơn, không cần chọn Chrome hay đăng nhập tay. Đổi lại ảnh ra hiện tại chỉ khoảng ~1K (không nét bằng tài khoản Gemini Pro trên web) — xem phần "Giới hạn đã biết" dưới đây.

## Giới hạn đã biết của `agy` (đã kiểm chứng, không cần dò lại)
- `agy` là CLI dạng agent (giống Claude Code) của Antigravity/Google. Nó **không** có model ảnh để chọn qua `--model` (`agy models` chỉ liệt text model: gemini-3.8-flash-*, claude-*, gpt-oss-*). Muốn tạo ảnh phải để agent chính của `agy` tự gọi tool nội bộ `invoke_subagent` với `Model: "pro"`, `TypeName: "image-generator"` — subagent này mới có tool `generate_image` (tham số `AspectRatio`, `ImageName`, `Prompt`, `ImagePaths`).
- `ImagePaths` nhận **4 ảnh bình thường** (đã test trực tiếp, không có lỗi hay cắt bớt). Không có giới hạn số ảnh nào được xác nhận — chỉ bị giới hạn chung bởi token input của model như mọi request multimodal khác, nên cứ dùng đủ 4 ảnh như `gemini-thay-do`, đừng tự rút bớt.
- Ảnh ra chỉ khoảng ~1K (quan sát thực tế 768×1376 cho khung 9:16), **không có tham số chọn 2K/4K và không upscale được** bằng chính model này. Cần ảnh nét hơn để đăng thì dùng `gemini-thay-do` (tài khoản Pro cho ảnh ~1536×2752) hoặc hỏi người dùng có muốn upscale bằng công cụ khác.
- Ảnh ra **không có logo ✦** hiển thị như khi dùng web Gemini, nên **không cần** bước xóa watermark của skill `gemini-thay-do`. (Ảnh vẫn có thể mang watermark số ẩn SynthID của Google — không ảnh hưởng việc dùng, không cần xử lý.)
- Chạy không tương tác (`agy -p ...`) thì không có người bấm "approve" từng tool call, nên lệnh **phải** thêm `--dangerously-skip-permissions`, nếu không sẽ treo chờ xác nhận. Vì cờ này bỏ qua toàn bộ xác nhận tool-call của `agy` (kể cả lệnh shell tùy ý mà agent của nó có thể chạy), **chỉ chạy lệnh này trong phiên của bạn (không đóng gói thành một subagent luôn tự bật cờ này)**, và giữ nguyên câu chặn trong prompt ("không viết code, không gọi API ngoài, không chạy lệnh khác ngoài tool tạo ảnh") để giảm rủi ro nó làm việc ngoài ý muốn.
- Mỗi lần gọi `agy -p` (không kèm `--continue`/`--conversation`) là một hội thoại mới sạch, tương đương "mỗi ảnh một chat mới" của `gemini-thay-do`. Sinh ảnh thường mất 1–3 phút; lệnh dài hơn 120s thì tự chuyển sang chạy nền, chờ thông báo thay vì poll.

## Đầu vào (4 ảnh, đúng thứ tự)
1. Người mẫu: `ref/model_identity.png`
2. Trang phục: `anh/<bộ>/<index>.*`
3. Ảnh cận chất liệu: `anh/<bộ>/crop/<index>.png` (tạo ở Bước 1)
4. Phòng trống: `ref/background_empty.png` (bắt buộc đã có; nếu chưa có thì làm theo `prompts/background-empty.md` trong skill `gemini-thay-do` trước, đây không tự tạo)
- Đầu ra: `generated/<bộ>/<index>-banana-pro.jpg`

## Bước 0: kiểm tra `agy`
```bash
which agy && agy models
```
Lỗi "command not found", lỗi xác thực, hoặc danh sách model rỗng thì dừng, báo người dùng — không tự cài, không tự đăng nhập.

## Bước 1: chuẩn bị từng ảnh (giống `gemini-thay-do` bước 1)
Với mỗi `<index>` cần làm:
1. Read ảnh quần áo gốc `anh/<bộ>/<index>.*`.
2. Cắt cận 30%: `python3 scripts/crop_fabric.py <bộ> <index> --center x,y` (tâm vào thân/eo/chân váy, tránh da và nền). Read `anh/<bộ>/crop/<index>.png` kiểm tra thấy rõ vân vải.
3. Chọn chất liệu trong `prompts/fabric-presets.md`: `python3 scripts/build_agy_prompt.py --list` (satin / matte / organza / jersey). Không có mục hợp thì thêm mục mới vào file presets trước (cùng file dùng chung với `gemini-thay-do`).
4. Tả kiểu dáng ngắn bằng tiếng Anh cho `--garment`: cổ, tay, eo, độ dài, chi tiết đặc biệt. Váy mini/midi phải ghi rõ độ dài.

## Bước 2: build prompt và gọi `agy`
```bash
python3 scripts/build_agy_prompt.py --bo <bộ> --index <index> --fabric <tên> --garment "<tả>" > <scratchpad>/agy-prompt-<index>.txt
agy -p "$(cat <scratchpad>/agy-prompt-<index>.txt)" --model gemini-3.8-flash-high --dangerously-skip-permissions --output-format text
```
(dùng đúng thư mục scratchpad của phiên hiện tại). Mặc định prompt có bước phân tích: model điều phối dùng `read_file` xem ảnh quần áo và ảnh cận chất liệu, tự ghi chi tiết (cổ, tay, độ dài, chất vải...) rồi nối vào prompt gửi Banana Pro; bước này tốn thêm quota. Thêm `--no-analyze` khi cần tạo ảnh đối chứng. Chạy ở thư mục gốc dự án (để `agy` nhận đúng workspace). Timeout hoặc lỗi thì chạy lại đúng lệnh đó **một lần** trước khi báo lỗi.

## Bước 3: lấy ảnh ra và lưu vào dự án
Output của `agy` có dòng dạng "Absolute Path: `/home/.../antigravity-cli/brain/<convId>/<ImageName>_<timestamp>.jpg`". Lấy đường dẫn đó:
```bash
mkdir -p generated/<bộ>
cp "<đường dẫn ảnh từ output agy>" "generated/<bộ>/<index>-banana-pro.jpg"
```
Không thấy đường dẫn ảnh trong output (model chỉ trả lời chữ, từ chối, hoặc báo lỗi tool) thì ghi lại index và lý do, chạy lại **một lần**, không quá.

## Bước 4: kiểm tra chất lượng
Read `generated/<bộ>/<index>-banana-pro.jpg`, so với:
- `ref/model_identity.png` — mặt, tóc, vóc dáng có đúng là người này không.
- `anh/<bộ>/<index>.*` và `anh/<bộ>/crop/<index>.png` — dáng váy, độ dài, chi tiết, chất liệu (bóng/lì/xuyên sáng).
- `ref/background_empty.png` — phòng, góc máy, ánh sáng.
Lệch rõ thì ghi "cần gen lại", sửa `--garment` cho rõ hơn rồi làm lại Bước 2–3 **một lần** cho index đó, không lặp nhiều lần.

## Bước 5: báo cáo
Bảng: index | lưu ở `generated/<bộ>/<index>-banana-pro.jpg` hay lỗi gì | nhận xét (mặt, dáng, chất vải, phòng) | có cần ảnh nét hơn qua `gemini-thay-do` không.

## Không làm
- Không chạy `agy` cho việc gì khác ngoài tạo ảnh thử đồ của bài đang làm.
- Không sửa cấu hình `~/.gemini/antigravity-cli/` hay thông tin đăng nhập `agy`.
- Không dùng `--continue`/`--conversation` để nối các ảnh vào cùng một hội thoại `agy` — mỗi ảnh một lệnh `agy -p` mới.
- Không tìm cách gọi trực tiếp API/backend của Gemini để né quota hay giới hạn độ phân giải (đã thử ở phiên trước: không khả thi nếu không có API key riêng của người dùng, và không tự đăng ký hộ).
