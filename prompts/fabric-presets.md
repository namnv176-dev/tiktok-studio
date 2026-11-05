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

## chiffon
It is soft, airy silk CHIFFON: very lightweight, semi-sheer and see-through wherever it is single-layered (the cape, the hem), opaque only where it is lined, with a fine matte surface that has just a faint soft glow and no satin shine. It is limp and fluid, not stiff: it falls straight down in soft vertical folds, floats and ripples with any movement and moves in the air like a veil. Do NOT make it crisp organza, stiff tulle, glossy satin, opaque crepe or cotton.

## lace
It is an opaque corded GUIPURE LACE: a raised, three-dimensional floral or leaf pattern with clearly outlined motifs and small open holes between them, a matte cotton-like surface with no shine, a medium-weight body that holds the shape of the seams and the flare of the skirt, laid over a solid lining so the skin does not show through. Do NOT make it smooth plain fabric, shiny satin, sheer tulle or a printed pattern.

## lace-tulle
It is a fine EMBROIDERED LACE on soft tulle: delicate tone-on-tone floral and vine embroidery scattered over a semi-sheer net, with a very faint shimmer from the thread, layered over an opaque lining at the bodice and a lighter lining in the skirt so the skirt looks airy and slightly translucent at the hem. Soft and light, it drapes in gentle folds. Do NOT make it plain satin, heavy guipure, opaque crepe or a printed pattern.

## tulle
It is soft bridal TULLE: a fine, light, semi-sheer net in many layers, matte with no shine, airy and floaty; where there is only a short lining the legs show softly through the tulle, and the hem is soft and slightly uneven with gentle vertical folds. Do NOT make it opaque, stiff organza, glossy satin or chiffon with a print.
