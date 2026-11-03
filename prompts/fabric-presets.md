# Chất liệu cho prompts/cloth-change.md (điền vào chỗ {FABRIC})

Mỗi mục "## <tên>" là một chất liệu, viết tiếng Anh vì gửi cho Gemini. Mỗi mục gồm: tên vải, bề mặt, độ bóng, cách rủ,
và câu cấm sai chất liệu thường gặp (Gemini hay đẩy vải bóng thành lì hoặc ngược lại).
Chọn bằng cách NHÌN ẢNH GỐC rồi chạy: python3 scripts/build_prompt.py --fabric <tên> --garment "<kiểu dáng>"
Thêm chất liệu mới (nhung, ren, len...): thêm một mục "## <tên>" ở cuối, build_prompt.py tự nhận.

## satin
It is a real silk satin: a smooth liquid surface, soft specular highlights that slide along every fold and gather, a lustrous pearlescent sheen, and a clear gradient from bright highlights to deep soft shadows in the folds. The window light must create this same sheen on the dress. Do NOT make it matte, dull, flat or crepe-like; do NOT turn it into cotton, linen, jersey, knit or polyester.

## matte
It is a MATTE woven fabric, like a fine crepe or twill: a smooth, dry, flat, non-reflective surface with a faint woven grain, a slightly thick body that holds the pleats and the volume of the skirt, soft natural wrinkles, NO satin sheen and NO glossy highlights. Do NOT make it shiny, silky, satin or glossy.

## organza
It is crisp, lightweight ORGANZA: semi-sheer and slightly translucent wherever it is single-layered (sleeves, ruffles), with a delicate faint sheen, a light stiffness that makes sleeves puff and ruffles float in soft layered waves, and visible fine pleats. Do NOT make it opaque, heavy cotton, thick satin or glossy silk.

## jersey
It is a MATTE stretch jersey knit: soft and slightly clingy, with a flat non-reflective surface, fine ruching and soft gathered folds, and NO sheen. Do NOT make it shiny, silky or satin.
