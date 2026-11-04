# Nền chụp outfit: điểm check-in nổi tiếng và góc phố (prompt cho `agy` / Gemini)

Lệnh: `python3 scripts/build_bg_prompt.py --set checkin --scene <tên>`. Ảnh lưu `ref/background_empty_<tên>.jpg`. Bản copy sẵn ở `copy-nen-chup-anh.md`.

**Tiêu chí nền (người dùng chốt ngày 04/11/2026):**
- **Tiện để chụp**: người đứng sát một bức tường, cánh cửa hoặc mặt tiền, phía sau ít chi tiết. Nền chuẩn là `ref/background_empty_cafe-pho-co-door.jpg`. Không đứng trước không gian rộng hay sâu.
- **Thật**: trông như ảnh iPhone bạn bè chụp hộ. Với địa điểm nổi tiếng thì ghi đúng tên, tả cả nhà, cây và người qua đường ở mép ảnh.
- **Hợp đời sống hiện đại**: không lạm dụng nhà cổ. Không làm kiểu khách sạn 5 sao "sang chảnh" dựng bằng AI, vì người dùng chê là không thật.

## Tóm tắt nghiên cứu
**Điểm check-in được nhắc nhiều nhất, đã chọn những góc có tường / cửa / mặt tiền làm nền gần:**
- Hà Nội: **Nhà thờ Lớn** (mặt tiền Pháp cổ, tường cao, chụp trực diện), **Hoàng thành Thăng Long** ("bức tường vàng cung đình"), **phố bích họa Phùng Hưng** (vòm gạch cầu đường sắt, tranh tường Hà Nội xưa; đẹp lúc 8–10h). Ngoài ra còn ga Cát Linh, phố cổ Hàng Ngang (tường rêu, nhà mái ngói), phố sách 19/12, phố Phan Đình Phùng mùa thu, cầu Long Biên lúc 16–17h.
- Sài Gòn: **Bưu điện Trung tâm** (mặt tiền vàng đối xứng, kiến trúc Pháp), **Nhà thờ Tân Định** (màu hồng từ tháp chuông tới tường), **Bảo tàng Mỹ thuật** (kiến trúc cổ, kính màu), Lăng Ông Bà Chiểu (dãy tường vàng), Nhà hát Thành phố, chung cư 42 Nguyễn Huệ, Hồ Con Rùa.
- Hội An: tường vàng, cửa gỗ, hoa giấy, đèn lồng; ô cửa sổ ở cổng sau một quán cà phê trên Nguyễn Thái Học (đẹp lúc sáng sớm).
- Đà Lạt: **ga Đà Lạt**, các bức tường vàng của tiệm bánh.
- Huế: cung An Định (tường vàng rêu phong), Ngọ Môn.
- Đời sống hiện đại: tường trắng biệt thự có hoa giấy ở **Thảo Điền**.

**Nền học từ ảnh minh họa của các bài "tạo dáng chụp ảnh sang chảnh"** (toplist.vn, ngoisao.vn, fptshop.com.vn; ghi lại trong `pose-presets.md`): tường trơn trắng hoặc xám nhám ngay sau lưng, đứng trên vỉa hè lát đá; góc tường trắng giáp mảng tường đen có chậu cây; gờ tường thấp màu trắng để ngồi, có cành lá rủ; tường đá khối be; mặt tiền đá kem kiểu Âu có trụ và cửa gỗ tối; hành lang vòm trắng. Các cảnh `pho-*` bên dưới dựng theo những nền này.

Nguồn: vinwonders.com (check-in Hà Nội 2026; 40 địa điểm chụp hình Sài Gòn), mia.vn (địa điểm chụp hình đẹp ở Sài Gòn), vietnamairlines.com (địa điểm check-in Hà Nội), znews.vn (ô cửa sổ Hội An), toplist.vn, obiatravel.com.

## RULES
COMPOSITION, the most important rule, because this is a backdrop for an outfit photo: the camera faces the backdrop almost straight on from about 3 meters away. The backdrop (a wall, a door or a facade) stands close behind the spot where a woman will later be placed, only about 0.5 to 1 meter behind her, and it fills most of the frame like a portrait backdrop. There is very little depth behind the spot: no long corridor, no wide open square, no street vista directly behind it. Only the left and right edges of the frame, and a little at the top, show the surroundings. The ground in front of the backdrop is visible down to the bottom of the frame, with an empty spot in the center where she can stand head to toe with her feet fully visible. REAL PLACE: this is the real, named location; reproduce its actual architecture, colors and materials faithfully. Surroundings at the frame edges look like the real, living place: neighboring buildings, trees, parked motorbikes. A few ordinary passersby may appear only far away at the left or right edge, small and partly cut off, walking or sitting, not looking at the camera; nobody in the center and nobody near the spot. PHOTO: an ordinary, real, unedited iPhone snapshot taken by a friend, hand-held at chest height, vertical 9:16. Not a render, not CGI, not a postcard or stock photo. Casual framing with a barely noticeable tilt, natural phone exposure with slightly bright highlights in the sun, mild noise in the shadows, real weathering, dust and small stains where they would naturally be. No readable text, no logos, no brand names; any sign is out of frame or too far and blurry to read. One single photo, no collage, no border, no watermark.

## cafe-pho-co-door
The ground-floor entrance of a cafe in an old French-era tube house in the Hanoi Old Quarter. A close view of a pair of tall, old double wooden doors with louvered panels, painted dark green with the paint peeling, standing open, set in a faded mustard-yellow lime-washed wall with damp patches and cracks. Old patterned encaustic cement tiles on the floor, worn and slightly uneven, with a step at the threshold. A low wooden stool and a small wooden table at the edge of the frame, a potted plant by the door, a glimpse of the street with parked motorbikes through the doorway. Morning daylight from the street side. The spot is in front of the doors.
Dáng hợp: lean-wall, walk-toward, over-shoulder

## hn-nha-tho-lon
St. Joseph's Cathedral (Nhà thờ Lớn Hà Nội) on Nhà Chung street in the Hanoi Old Quarter. A close view of the base of its neo-Gothic facade: dark grey rendered stone walls streaked black by decades of rain and moss, one tall pointed-arch wooden door painted dark brown, closed, with iron hinges, and three worn stone steps in front. At the far left edge, part of the black iron fence and the trunk of a big old tree. At the right edge, a few low blue plastic stools of a lemon-tea street stall with two young people sitting far away, small and partly cut off, and motorbikes parked along the curb. Soft overcast autumn morning light typical of Hanoi. The spot is on the paved forecourt in front of the steps.
Dáng hợp: lean-wall, over-shoulder, hand-in-hair

## hn-hoang-thanh
Inside the Imperial Citadel of Thang Long (Hoàng thành Thăng Long), Hanoi. A close view of the wall of one of its old mustard-yellow French-era buildings: weathered yellow lime-washed wall with faded patches and a little moss near the base, two tall dark green louvered wooden shutters (closed) with white window frames, a strip of old grey stone pavement in front. Big old trees cast soft leafy shadows across the wall. At one edge, the corner of the next yellow building and one visitor walking far away on the path, small. Mid-morning sun. The spot is on the pavement between the two shutters.
Dáng hợp: lean-wall, hand-in-hair, over-shoulder

## hn-phung-hung
The Phùng Hưng mural street (phố bích họa Phùng Hưng) in Hanoi. A close view of one century-old red-brick arch of the railway viaduct; the arch is filled in with a wall painted with a nostalgic mural of old Hanoi life in soft muted colors (an old tram, old tube houses, a street vendor with a carrying pole), with no readable text. Worn red bricks frame the arch, the sidewalk in front is uneven grey tiles. At the edges: part of the next arch, a parked motorbike, a tree trunk, a vendor's bicycle loaded with flowers, one passerby far away. Slightly hazy morning light. The spot is on the sidewalk in front of the mural.
Dáng hợp: walk-toward, lean-wall, over-shoulder

## sg-buu-dien
Saigon Central Post Office (Bưu điện Trung tâm Sài Gòn), District 1. A close view of a section of its famous yellow French-colonial facade: warm yellow walls, white plaster pilasters and decorative moulding, one tall arched window with a dark green wooden frame. The ground is the light stone forecourt. At the edges: the trunk of a large old tree, a couple of tourists far away to the side, small and partly cut off, motorbikes passing on the street at the far edge. Bright tropical morning sun with soft shade from the trees. The spot is in front of the wall below the arched window.
Dáng hợp: lean-wall, hand-in-hair, walk-toward

## sg-tan-dinh
Tân Định Church (Nhà thờ Tân Định), the famous pink church on Hai Bà Trưng street, Saigon. A close view of its pink facade with white trim: a tall arched doorway with a dark wooden door, pink pillars and white decorative arches, a few grey stone steps. At the edges: part of the pink side wall, a palm tree, the iron gate, and motorbikes passing on the busy street at the far edge, with a street vendor far away. Bright morning sun. The spot is on the forecourt in front of the steps.
Dáng hợp: walk-toward, over-shoulder, lean-wall

## sg-bao-tang-my-thuat
Ho Chi Minh City Fine Arts Museum (Bảo tàng Mỹ thuật TP.HCM), 97A Phó Đức Chính, District 1. A close view of the old yellow colonial building's wall on its veranda: warm yellow walls with ornate white plaster details, one arched window of colorful stained glass, and the vintage patterned cement floor tiles of the veranda in front. At the edges: a large potted plant, an old wooden bench, and one visitor far away along the veranda, small and partly cut off. Soft daylight. The spot is on the tiles in front of the stained-glass window.
Dáng hợp: hand-in-hair, lean-wall, seated-chair

## hoi-an-tuong-vang
A quiet lane in Hoi An Ancient Town (phố cổ Hội An), near Nguyễn Thái Học street. A close view of a typical mustard-yellow old house wall, weathered with darker patches and moss near the ground, a dark brown traditional wooden double door (closed), a cascade of pink bougainvillea from above the door, two silk lanterns hanging from the eaves, the edge of an old terracotta tile roof at the top. At the edges: the neighboring house, a parked bicycle, and a couple of tourists walking far down the lane, small and partly cut off. Early morning soft light. The spot is on the lane in front of the door.
Dáng hợp: lean-wall, over-shoulder, hand-in-hair

## da-lat-ga
Dalat Railway Station (Ga Đà Lạt). A close view of a section of its yellow Art Deco facade: yellow walls with white lines and a tall window of colorful glass panes in a geometric pattern, with a strip of the paved platform in front. At the edges: the corner of an old vintage train carriage, pine trees, and a few tourists far away. Cool highland morning light, slightly overcast, a hint of mist. The spot is on the paving in front of the colored-glass window.
Dáng hợp: lean-wall, hand-in-hair, walk-toward

## sg-thao-dien-tuong-trang
A modern residential lane in Thảo Điền, Thủ Đức, Saigon. A close view of the clean white rendered wall of a modern villa with a tall matte black steel gate, and a cascade of magenta bougainvillea over the top of the wall; a grey concrete sidewalk with a small drain grate in front. At the edges: a parked motorbike, a tree in a sidewalk planter, a delivery rider passing far away, the next house with a black-framed window. Bright late-morning sun casting crisp shadows of the bougainvillea on the white wall. The spot is on the sidewalk in front of the white wall, beside the gate.
Dáng hợp: walk-toward, lean-wall, over-shoulder

## pho-goc-tuong-trang-den
A quiet corner outside a modern minimalist building in Thảo Điền, Saigon. A close view where a smooth off-white rendered wall meets a tall flat panel of matte black (a closed black steel door), forming a clean two-tone backdrop. A large dark ceramic pot with a dusty blue-grey shrub stands at the left edge. The ground is light grey stone paving with a low step. At the right edge, a sliver of the street with a parked motorbike and a tree trunk. Soft overcast daylight, gentle shadows. The spot is on the paving right in front of where the white wall meets the black panel.
Dáng hợp: look-up-profile, s-curve-bag, lean-back-wall

## pho-go-tuong-ngoi
A quiet modern residential street in Saigon. A close view of a smooth warm-white rendered wall with a low, wide white concrete ledge running along its base, about knee height, good for sitting. A branch of fresh green leaves from a tree hangs into the top of the frame and casts soft dappled shadows on the wall. Light grey sidewalk tiles in front. At the edge, the corner of the next house and a passerby far away. Soft late-morning light. The spot is on the ledge and the sidewalk right in front of it.
Dáng hợp: sit-ledge-look-down, lean-back-wall, hand-in-hair

## pho-tuong-trang-via-he
A sidewalk in a newer urban area of Saigon. A close view of a plain light grey-white textured rendered wall, slightly uneven with faint rain marks near the bottom, filling almost the whole frame; grey square sidewalk tiles with a thin metal curb strip in front. At the left edge, part of a young street tree in a planter; at the right edge, the edge of a shop's dark window frame and a parked motorbike. Bright but soft daylight, a faint soft shadow on the wall. The spot is on the sidewalk right in front of the wall.
Dáng hợp: lean-back-wall, s-curve-bag, arms-crossed-confident

## pho-tuong-da-be
The outside of a modern building in Phú Mỹ Hưng, District 7, Saigon. A close view of a wall clad in large rectangular blocks of warm beige natural stone with fine joints and subtle natural color variation, filling most of the frame. A narrow band of dark grey granite paving in front. At the edges: a slim black metal planter with a small olive tree, a glass door edge reflecting the street, a passerby far away. Warm late-afternoon side light raking across the stone texture. The spot is on the paving right in front of the stone wall.
Dáng hợp: hand-on-wall, s-curve-bag, look-up-profile

## pho-mat-tien-dong-khoi
A heritage French-colonial building on Đồng Khởi street, District 1, Saigon. A close view of its cream-colored stone facade at street level: two tall classical pilasters framing a tall, dark polished wooden double door (closed), a black metal wall lantern beside it, and a pair of large stone planters with clipped green shrubs. A clean light grey stone sidewalk in front. At the edges: the trunk of a big tamarind tree, part of the next shopfront without readable signs, motorbikes and a passerby far away. Soft morning light in the shade of the trees. The spot is on the sidewalk in front of the wooden door.
Dáng hợp: walk-toward, s-curve-bag, arms-crossed-confident

## pho-hanh-lang-vom
A white arched colonnade (arcade) along the ground floor of a modern French-style building in Hanoi. A close view: two or three white arches with simple columns directly behind the spot, the arches are shallow, and behind them is a plain white wall with a closed tall glass door, so there is little depth. Floor of large light cream stone tiles. At the edges: a large potted palm and a sliver of the street with a motorbike. Soft bright daylight from the street side. The spot is on the floor under the middle arch.
Dáng hợp: s-curve-bag, hand-in-hair, walk-toward
