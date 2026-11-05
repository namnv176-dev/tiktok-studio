#!/usr/bin/env python3
"""Ghép prompt cho skill `agy-thay-do` (xem .claude/skills/agy-thay-do/SKILL.md).

Khác với scripts/build_prompt.py (gửi Gemini qua Chrome, cần 1 dòng, ảnh đính kèm thật qua UI),
prompt này được truyền làm đối số/stdin cho lệnh `agy -p`, nên giữ nguyên nhiều dòng và liệt kê
đường dẫn ảnh (ImagePaths) để agent của agy tự gọi tool generate_image. Dùng đúng 4 ảnh tham
chiếu như gemini-thay-do (người mẫu, quần áo, cận chất liệu, phòng trống) và cùng một mẫu prompt
prompts/cloth-change.md, vì không có giới hạn nào cho số ảnh đầu vào được xác nhận — chỉ bị giới
hạn bởi token input của model như mọi request multimodal khác.

  python3 scripts/build_agy_prompt.py --list
  python3 scripts/build_agy_prompt.py --bo wedding-dress --index anh-01 --fabric matte \
      --garment "an elegant ivory asymmetric off-the-shoulder draped midi dress"
"""
import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
IMG_EXT = {".png", ".jpg", ".jpeg", ".webp"}
DEFAULT_GARMENT = "cut, neckline, straps or sleeves, length, silhouette, color, pleats, ruching, ruffles and details"

HEADER = """You must generate an image using your own image generation tool with reference images. Do not write code, do not call any external API, do not use run_command for this task, do not run any other command besides calling your image generation tool.

Use AspectRatio: "9:16" (vertical portrait).
ImageName: "{image_name}"

Reference image paths, in this exact order (pass all 4 to your tool's ImagePaths):
- Image 1 (Identity): {identity_path}
- Image 2 (Outfit): {garment_path}
- Image 3 (Fabric close-up): {crop_path}
- Image 4 (Background): {background_path}

Prompt:
"{body}"

Execute the generation immediately and return the absolute saved image path."""


def load_presets():
    text = (ROOT / "prompts" / "fabric-presets.md").read_text(encoding="utf-8")
    presets = {}
    for m in re.finditer(r"^##\s+(\S+)\s*\n(.*?)(?=^##\s|\Z)", text, re.S | re.M):
        presets[m.group(1).strip().lower()] = re.sub(r"\s*\n+\s*", " ", m.group(2)).strip()
    return presets


def build_body(garment, fabric):
    tpl = (ROOT / "prompts" / "cloth-change.md").read_text(encoding="utf-8")
    one = re.sub(r"\s*\n+\s*", " ", tpl).strip()
    for ph in ("{GARMENT}", "{FABRIC}"):
        if ph not in one:
            sys.exit(f"Mẫu prompts/cloth-change.md thiếu chỗ trống {ph}")
    return one.replace("{GARMENT}", garment.strip()).replace("{FABRIC}", fabric)


def find_garment(bo, index):
    src = ROOT / "anh" / bo
    for p in sorted(src.glob(index + ".*")):
        if p.suffix.lower() in IMG_EXT:
            return p
    sys.exit(f"Không thấy ảnh quần áo khớp anh/{bo}/{index}.*")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--bo", help="tên bộ ảnh, vd wedding-dress")
    ap.add_argument("--index", help="tên ảnh quần áo không kèm đuôi, vd anh-01")
    ap.add_argument("--fabric", help="tên chất liệu trong prompts/fabric-presets.md")
    ap.add_argument("--garment", default=DEFAULT_GARMENT)
    ap.add_argument("--image-name", help="ImageName truyền cho agy, mặc định <bo>_<index>")
    ap.add_argument("--list", action="store_true", help="liệt kê chất liệu có sẵn")
    args = ap.parse_args()

    presets = load_presets()
    if args.list:
        print("\n".join(presets))
        return
    if not (args.bo and args.index and args.fabric):
        sys.exit("Cần --bo, --index và --fabric. Chạy --list để xem chất liệu.")

    key = args.fabric.lower()
    if key not in presets:
        sys.exit(f"Không có chất liệu '{key}'. Có: {', '.join(presets)}")

    garment_path = find_garment(args.bo, args.index)
    identity_path = ROOT / "ref" / "model_identity.png"
    crop_path = ROOT / "anh" / args.bo / "crop" / f"{args.index}.png"
    background_path = ROOT / "ref" / "background_empty.png"
    for p in (identity_path, crop_path, background_path):
        if not p.exists():
            sys.exit(f"Thiếu {p}" + (" (chạy scripts/crop_fabric.py trước)" if p == crop_path else ""))

    image_name = args.image_name or f"{args.bo}_{args.index}".replace("/", "_")
    body = build_body(args.garment, presets[key])

    print(HEADER.format(
        image_name=image_name,
        identity_path=identity_path,
        garment_path=garment_path,
        crop_path=crop_path,
        background_path=background_path,
        body=body,
    ))


if __name__ == "__main__":
    main()
