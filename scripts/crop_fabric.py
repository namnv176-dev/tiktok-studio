#!/usr/bin/env python3
"""Cắt ảnh cận chất liệu từ ảnh quần áo để gửi Gemini làm "ảnh tham chiếu chất liệu".

  python3 scripts/crop_fabric.py wedding-dress anh-04 --center 0.50,0.62
  python3 scripts/crop_fabric.py wedding-dress anh-09 --center 0.50,0.55 --scale 0.3

Ảnh nguồn: anh/<bộ>/<index>.*   ->   ảnh cắt: anh/<bộ>/crop/<index>.png

--scale  tỉ lệ mỗi cạnh so với ảnh gốc (mặc định 0.30 = 30% rộng x 30% cao, phóng to khoảng 3,3 lần).
--center tâm vùng cắt theo tỉ lệ 0..1 (x,y). Chọn vào chỗ thấy rõ vân vải và nếp rủ: thân váy, eo, chân váy.
         Tránh da, mặt, nền. Xem ảnh gốc bằng Read trước khi chọn.
--min-px cạnh ngắn của vùng cắt tối thiểu (pixel gốc, mặc định 240). Ảnh nguồn nhỏ (khoảng 450px) mà cắt 30% thì chỉ
         còn khoảng 135px, mờ không thấy vân, nên script tự nới scale lên cho đủ min-px rồi báo.
Ảnh cắt được phóng (LANCZOS) để cạnh ngắn đạt ít nhất 640px, giúp Gemini nhìn rõ hơn. Phóng không tạo thêm chi tiết.
"""
import argparse
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
IMG_EXT = {".png", ".jpg", ".jpeg", ".webp"}


def find_source(collection, index):
    src = ROOT / "anh" / collection
    for p in sorted(src.glob(index + ".*")):
        if p.suffix.lower() in IMG_EXT:
            return p
    sys.exit(f"Không thấy ảnh {src}/{index}.*")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("collection")
    ap.add_argument("index")
    ap.add_argument("--center", default="0.50,0.60", help="x,y trong 0..1 (mặc định 0.50,0.60)")
    ap.add_argument("--scale", type=float, default=0.30, help="tỉ lệ mỗi cạnh (mặc định 0.30)")
    ap.add_argument("--min-px", type=int, default=240, help="cạnh ngắn tối thiểu của vùng cắt, pixel gốc")
    ap.add_argument("--target-px", type=int, default=640, help="phóng để cạnh ngắn đạt ít nhất cỡ này")
    args = ap.parse_args()

    try:
        cx, cy = (float(v) for v in args.center.split(","))
    except ValueError:
        sys.exit("--center phải có dạng x,y (vd 0.5,0.6)")
    if not (0 < args.scale <= 1):
        sys.exit("--scale phải trong (0, 1]")

    path = find_source(args.collection, args.index)
    im = Image.open(path).convert("RGB")
    W, H = im.size

    scale = args.scale
    short = min(W, H)
    if short * scale < args.min_px:
        scale = min(0.9, args.min_px / short)
        print(f"Vùng cắt {args.scale:.0%} của ảnh {W}x{H} chỉ còn {round(short * args.scale)}px (< {args.min_px}px, sẽ mờ): "
              f"nới scale lên {scale:.2f}")

    w, h = max(1, int(W * scale)), max(1, int(H * scale))
    x = min(max(int(W * cx - w / 2), 0), W - w)
    y = min(max(int(H * cy - h / 2), 0), H - h)
    crop = im.crop((x, y, x + w, y + h))

    up = args.target_px / min(crop.size)
    if up > 1:
        crop = crop.resize((round(crop.width * up), round(crop.height * up)), Image.LANCZOS)

    out_dir = ROOT / "anh" / args.collection / "crop"
    out_dir.mkdir(exist_ok=True)
    out = out_dir / f"{args.index}.png"
    crop.save(out)
    print(f"{path.name} {W}x{H} -> vùng ({x},{y})-({x + w},{y + h}) -> {out.relative_to(ROOT)} {crop.width}x{crop.height}")


if __name__ == "__main__":
    main()
