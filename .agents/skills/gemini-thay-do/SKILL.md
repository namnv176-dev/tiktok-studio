---
name: gemini-thay-do
description: Thay đồ cho người mẫu bằng Gemini qua Chrome MCP. Với từng ảnh quần áo trong anh/<bộ>/, cắt ảnh cận chất liệu 30%, gửi Gemini 4 ảnh (người mẫu, quần áo, ảnh cận chất liệu, phòng trống) cùng prompt ghép từ prompts/cloth-change.md và prompts/fabric-presets.md, rồi tải kết quả về generated/<bộ>/<index>, sau đó xóa logo Gemini. Dùng khi người dùng gõ /gemini-thay-do <bộ> hoặc nhờ gen, gen lại ảnh mặc thử đồ cho bài đăng, kể cả khi chỉ nói "làm ảnh 7 8 9 10" hay "gen lại cho đúng chất liệu".
---

# Workflow: thay đồ cho mẫu bằng Gemini

Tham số: tên bộ ảnh (vd `wedding-dress`). Không có thì hỏi hoặc liệt kê `anh/`. Có thể kèm danh sách index (vd `anh-02 anh-05`) để chỉ làm lại vài ảnh.

**Vì sao có ảnh cận chất liệu:** chỉ gửi ảnh váy nguyên bộ thì Gemini hay đoán sai vải (lụa bóng ra lì, vải lì ra bóng, organza ra đặc). Ảnh cắt cận 30% làm vân vải, độ bóng và nếp rủ chiếm cả khung hình, nên Gemini có thứ để sao chép. Ảnh váy nguyên bộ chỉ còn lo kiểu dáng.

## Đầu vào (4 ảnh, luôn đính kèm đúng thứ tự này)
1. Người mẫu: `/home/namnv/workspace/tiktok/ref/model_identity.png`. Không gửi cả bảng 14 ô, mặt quá nhỏ nên Gemini không giữ được nhận diện.
2. Quần áo: `/home/namnv/workspace/tiktok/anh/<bộ>/<index>.*`
3. Ảnh cận chất liệu: `/home/namnv/workspace/tiktok/anh/<bộ>/crop/<index>.png` (tạo ở Bước 1).
4. Phòng trống: `/home/namnv/workspace/tiktok/ref/background_empty.png`. **Không gửi `background.png` gốc**, vì có sẵn một cô gái mặc váy trắng nên Gemini giữ lại mặt và vải của cô ấy.
- Tổng dung lượng 4 ảnh phải dưới 10 MB (thường khoảng 8 MB, trong đó phòng trống chiếm 6,6 MB).
- Đầu ra: `generated/<bộ>/<index>.png`, index trùng tên ảnh quần áo.

## Bước 0: chuẩn bị (một lần cho cả lượt)
1. `python3 scripts/gemini_collect.py status <bộ>` lấy index **chưa** làm. Làm lại thì chép bản cũ sang `generated/<bộ>/v1/` trước, rồi `collect` thêm `--overwrite`.
2. Nạp tool Chrome trong **một** lần ToolSearch:
   `select:mcp__claude-in-chrome__list_connected_browsers,mcp__claude-in-chrome__select_browser,mcp__claude-in-chrome__switch_browser,mcp__claude-in-chrome__tabs_context_mcp,mcp__claude-in-chrome__tabs_create_mcp,mcp__claude-in-chrome__navigate,mcp__claude-in-chrome__computer,mcp__claude-in-chrome__find,mcp__claude-in-chrome__read_page,mcp__claude-in-chrome__file_upload,mcp__claude-in-chrome__javascript_tool`
3. **Chọn Chrome, chỉ hỏi một lần:** `list_connected_browsers`, rồi hỏi người dùng bằng AskUserQuestion (tên + deviceId, máy này xếp trước). Không tự chọn thay họ. Chrome phải chạy **trên máy này**, vì ảnh tải về phải vào `~/Downloads` thì script mới gom được. Người dùng muốn tự bấm thì dùng `switch_browser` (họ bấm Connect trong Chrome).
4. `tabs_context_mcp` (kèm `createIfEmpty`) rồi mở Gemini: `https://gemini.google.com/app`. Người dùng có thể dùng tài khoản khác ở `/u/1/app`. Chụp màn hình kiểm tra:
   - Chưa đăng nhập: dừng, nhờ người dùng tự đăng nhập.
   - Có popup điều khoản hoặc cookie: báo người dùng, không tự bấm đồng ý.
   - Trên ô chat có dòng **"Your limit resets at …"**: hết lượt. Dừng cả vòng, báo người dùng đổi tài khoản hoặc chờ. Không tự nâng cấp hay đổi tài khoản.
   - Tài khoản Pro cho ảnh nét hơn (khoảng 1536×2752) so với gói thường.
5. **Nền trống** (chỉ khi chưa có `ref/background_empty.png`): làm theo `prompts/background-empty.md`, `collect - - --since <mốc> --to ref/background_empty`, mở ảnh kiểm tra còn dấu người hoặc điện thoại trong gương thì gen lại một lần.

## Bước 1: chuẩn bị từng ảnh (làm hết trước khi mở Chrome)
Với mỗi `<index>` cần làm, dùng Read mở ảnh quần áo gốc rồi:
1. **Phân loại chất liệu** theo ảnh gốc, chọn một mục trong `prompts/fabric-presets.md` (`python3 scripts/build_prompt.py --list`): `satin` (bóng, có điểm sáng chạy theo nếp), `matte` (lì, vân dệt mịn), `organza` (mỏng, xuyên sáng), `jersey` (thun co giãn, lì). Đừng đoán theo màu hay theo tên sản phẩm: váy kem có thể là lụa hoặc crepe lì. Không có mục hợp thì thêm một mục mới vào file presets.
2. **Cắt ảnh cận 30%:** `python3 scripts/crop_fabric.py <bộ> <index> --center x,y` (mặc định `--scale 0.30`, tức mỗi cạnh còn 30%). Chọn tâm vào thân váy, eo hoặc chân váy, nơi thấy rõ vân và nếp rủ; tránh da, mặt, nền. Mở `anh/<bộ>/crop/<index>.png` bằng Read kiểm tra có thấy rõ chất liệu. Ảnh nguồn nhỏ (khoảng 450px) thì script tự nới tỉ lệ vì 30% chỉ còn vài chục pixel, khi đó dời tâm xuống đúng phần váy để khỏi lẫn da và nền.
3. **Tả kiểu dáng** ngắn bằng tiếng Anh cho `--garment`: cổ, tay, eo, độ dài, chi tiết đặc biệt (một vai, tay phồng, bèo tầng, đai). Váy mini hoặc midi phải ghi rõ độ dài, vì Gemini hay tự đổi. Ảnh gốc có chữ in trên ảnh (vd "D2985") thì không cần lo, prompt đã dặn bỏ qua chữ.
4. **Ghép prompt thành một dòng:**
   `python3 scripts/build_prompt.py --fabric <tên> --garment "<kiểu dáng>"`
   Prompt phải một dòng vì Enter trong ô chat sẽ gửi sớm. Prompt ghi thứ tự ảnh 1 đến 4, nên không đổi thứ tự đính kèm.

## Bước 2: gen từng ảnh (tuần tự, mỗi ảnh một chat mới)
1. **Chat mới:** `navigate` tới `https://gemini.google.com/app` (hoặc `/u/1/app`).
2. **Mở menu đính kèm:** `find` "Upload & tools (+) button in the chat input" rồi click theo **ref**. Không click theo tọa độ: viewport hay đổi cao, từng có lần click trượt vào mục "Create image" và Gemini chuyển sang trang `/images`. Sau đó chờ khoảng 1 giây.
3. **Đính kèm 4 ảnh:** ô `input[type=file]` chỉ xuất hiện sau khi mở menu. **Không bấm "Upload files"** vì nó mở hộp chọn file hệ thống. Dùng `javascript_tool` gắn nhãn:
   `document.querySelectorAll('[aria-label=IMAGE_UPLOAD_INPUT]').forEach(e=>e.removeAttribute('aria-label')); const el=[...document.querySelectorAll('input[type=file]')].find(i=>i.accept.startsWith('image/')); el ? (el.setAttribute('aria-label','IMAGE_UPLOAD_INPUT'),'ok') : 'NO_INPUT'`
   `NO_INPUT` thì chờ 1 đến 2 giây chạy lại. Rồi `find` "file input with aria-label IMAGE_UPLOAD_INPUT" và gọi `file_upload` **một lần** với 4 đường dẫn theo thứ tự trên.
4. **`file_upload` hay báo lỗi dù ảnh đã lên** ("did not respond in time", "never delivered", "Couldn't determine which page"). **Không tải lại**, vì sẽ bị đính kèm trùng. Làm theo thứ tự:
   `tabs_context_mcp` → chờ khoảng 6 giây → chụp màn hình. Thường đã thấy đủ 4 thumbnail.
   - Nếu `tabs_context_mcp` báo "extension disconnected" hoặc "tab group no longer exists": extension ngắt kết nối. Gọi `switch_browser` (người dùng bấm Connect) rồi `tabs_context_mcp` lại, tab cũ thường vẫn còn. Danh sách trình duyệt chỉ còn máy khác (Windows): dừng, nhờ người dùng mở lại Chrome và bật extension, không dùng máy khác. Trường hợp này thường xảy ra đúng lúc tải 4 ảnh nặng; nếu lặp lại nhiều, đề xuất nén `background_empty.png` (cần người dùng đồng ý).
   - Xác nhận **4 thumbnail đúng thứ tự**. **Không click vào thumbnail** (mở trình vẽ). Lỡ mở thì bấm mũi tên ← góc trên trái, không bấm Save.
5. **Nhập prompt:** click vào ô "Ask Gemini", `type` chuỗi một dòng từ Bước 1, `find` "Send message button", click theo ref.
6. **Chờ gen:** 30 đến 60 giây. Chụp màn hình mỗi khoảng 10 giây, tối đa khoảng 3 phút.
   - Chỉ trả lời chữ, không có ảnh: gửi "Please generate the image now." một lần.
   - Từ chối hoặc lỗi: ghi lại index và lý do, chuyển ảnh tiếp. Hết lượt thì dừng cả vòng.
7. **Tải về:**
   - `python3 scripts/gemini_collect.py mark`, giữ mốc thời gian.
   - `find` "Download full size image button", click theo ref.
   - `python3 scripts/gemini_collect.py collect <bộ> <index> --since <mốc>` (thêm `--overwrite` khi làm lại). Ảnh độ phân giải cao tải chậm (Gemini hiện "Downloading full size…"), mà collect chờ tối đa 90 giây mỗi lần. Hết giờ thì **chạy lại đúng lệnh đó một lần** (`lệnh || lệnh`) trước khi nghi ngờ.
   - Chrome của người dùng hỏi vị trí lưu từng tệp nên mở hộp thoại Save as của hệ điều hành mà agent không bấm được. Không sao: `collect` chép từ file tạm `~/Downloads/.com.google.Chrome.XXXX`. Cuối lượt nhắc người dùng đóng các hộp thoại đó (Cancel).
8. **Kiểm tra:** Read ảnh đã lưu. So với ảnh mẫu (mặt), ảnh váy (dáng, độ dài, chi tiết) và **ảnh cận (chất liệu: bóng hay lì, mềm hay cứng, xuyên sáng hay đặc)**, và căn phòng. Lệch rõ thì ghi "cần gen lại", không tự gen lại quá một lần mỗi ảnh. Lỗi hay gặp: tự thêm đường xẻ, đổi vị trí tay hoặc vai (ảnh selfie gương có thể lật trái phải, chấp nhận được), vải sai bóng/lì. Sửa bằng cách tả kỹ hơn trong `--garment`, không sửa file mẫu.

## Biến thể: 1 ảnh 9:16 lưới 4 ô (4 dáng, 4 góc máy)
- Mẫu `prompts/cloth-change-grid4.md`; bộ 4 ô theo từng nền trong `prompts/grid4-panels.md` (mỗi nền một mục `## <tên>`, dáng bám vào cửa/cột/chậu của nền đó). Ghép:
  `python3 scripts/build_prompt.py --template cloth-change-grid4 --panels <nền> --fabric <vải> --garment "..." --accessories "..."`
- Mỗi mẫu đồ mới cần nền riêng hợp hoàn cảnh: tạo nền trống trước (`build_bg_prompt.py`, lấy phần mô tả cảnh trong `Prompt: "..."` để gửi Gemini web), lưu `ref/background_empty_<nền>.jpg`.
- **Cắt bỏ đầu người mẫu khỏi ảnh quần áo** (`anh/<bộ>/crop/<index>-noface.png`) rồi gửi bản đó làm ảnh 2. Lần đầu gửi ảnh còn mặt: 2/4 ô lấy luôn mặt và tóc đuôi ngựa của người mẫu shop, túi cũng bị chép dáng.
- Phụ kiện tự chọn thì ghi rõ "NOT the bag from Image 2", vì Gemini hay chép túi trong ảnh quần áo.
- Lưu `generated/<bộ>/<index>-grid4[-vN].png` bằng `collect - - --since <mốc> --to ...`, để không tính là đã làm ảnh đơn.
- Kế hoạch từng ảnh (nền, vải, kiểu dáng, phụ kiện) ghi trong `generated/<bộ>/grid4-plan.json`; nền dùng chung cho 2 váy để tiết kiệm lượt Gemini.
- **Nền tải về cũng có thể dính logo ✦** (thường là file PNG) hoặc bàn chân người chụp ở mép dưới: soi góc dưới phải trước khi dùng, có thì cắt bớt đáy, giữ tỉ lệ 9:16, lưu bản gốc ở `ref/raw/`.
- Gemini vẫn hay chép **dáng túi hàng hiệu** trong ảnh quần áo (vd túi có mặt chữ treo) hoặc tự thêm logo lên túi chần bông. Muốn tránh thì tả túi thật khác dáng gốc.

## Làm hook / upscale một ảnh có sẵn
Người dùng chọn một ảnh hoặc một ô của ảnh lưới để làm hook, hay nhờ "scale lên": **không gen lại cảnh**. Cắt đúng ô đó (theo vạch trắng giữa các ô) ra `anh/<bộ>/crop/<index>-hook-ref.png`, mở chat Gemini mới, đính kèm **chỉ ảnh đó**, gửi prompt `prompts/upscale-keep.md` (một dòng). Tải về `generated/<bộ>/<index>-hook.png`, xóa logo vào `clean/`. Không tự sửa chi tiết trong ảnh.

## Bước 3: xóa logo Gemini
Gemini đóng dấu logo ✦ ở góc dưới phải. AGENTS.md cấm dùng ảnh còn watermark, nên xóa trước khi làm slide. Dùng skill `gemini-watermark-remover`, đầu ra `generated/<bộ>/clean/<index>.png` (giữ nguyên ảnh gốc).
- Script của skill chạy `pnpm dlx @pilio/gemini-watermark-remover`, tức tải và chạy gói npm bên thứ ba. **Cần người dùng đồng ý** (hệ thống chặn nếu chưa cho phép).
- **Đừng tin mã thoát 0.** Wrapper của skill nuốt lỗi: gói thiếu thư viện `sharp` thì thoát mã 0, không tạo file, không in gì. Lệnh chạy được:
  `pnpm dlx --package=@pilio/gemini-watermark-remover --package=sharp gwr remove generated/<bộ>/<index>.png --output generated/<bộ>/clean/<index>.png`
- Có thể chạy mỗi ảnh một job nền. Xong thì kiểm tra file **có tồn tại**, cùng kích thước ảnh gốc, rồi cắt vùng góc dưới phải của bản gốc và bản sạch ghép cạnh nhau để nhìn. Từng có ảnh còn vết mờ (nền là tường phẳng); gặp thì báo, vá bằng PIL hoặc gen lại.

## Bước 4: báo cáo
- `status <bộ>` lại.
- Bảng: index | kết quả (lưu ở đâu / lỗi gì) | nhận xét chất lượng (mặt, dáng váy, chất vải, phòng).
- Nhắc: đóng hộp thoại Save as còn mở; ảnh đã xóa logo nằm ở `clean/`.

## Không làm
- Không đăng nhập, không giải CAPTCHA, không bấm đồng ý điều khoản, không nâng cấp hay đổi tài khoản Gemini thay người dùng.
- Không tự chọn Chrome thay người dùng, không dùng máy khác khi Chrome của máy này mất kết nối.
- Không chạy song song nhiều tab Gemini, vì dễ lẫn ảnh tải về giữa các index.
- Không sửa `prompts/cloth-change.md` giữa chừng. Đổi vải thì đổi `--fabric`, đổi kiểu dáng thì đổi `--garment`.
