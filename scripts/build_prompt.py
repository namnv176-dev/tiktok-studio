#!/usr/bin/env python3
"""Ghép prompt thay đồ thành MỘT dòng (Enter trong ô chat Gemini sẽ gửi sớm nên không được có xuống dòng).

  python3 scripts/build_prompt.py --list
  python3 scripts/build_prompt.py --fabric satin
  python3 scripts/build_prompt.py --fabric organza --garment "the asymmetric off-shoulder ruched bodice, long sheer balloon sleeves with bow cuffs, short tiered ruffled mini skirt"

Mẫu:       prompts/cloth-change.md   (có chỗ trống {GARMENT} và {FABRIC})
Chất liệu: prompts/fabric-presets.md (mỗi chất liệu là một mục "## <tên>")
--garment  tả kiểu dáng riêng của váy (tiếng Anh). Bỏ trống thì dùng câu chung. Nên tả khi váy có chi tiết đặc biệt
           (một vai, tay phồng, bèo tầng, đai...) hoặc độ dài lạ (mini, midi), vì Gemini hay tự đổi.
"""
import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_GARMENT = "cut, neckline, straps or sleeves, length, silhouette, color, pleats, ruching, ruffles and details"


def load_presets():
    text = (ROOT / "prompts" / "fabric-presets.md").read_text(encoding="utf-8")
    presets = {}
    for m in re.finditer(r"^##\s+(\S+)\s*\n(.*?)(?=^##\s|\Z)", text, re.S | re.M):
        presets[m.group(1).strip().lower()] = re.sub(r"\s*\n+\s*", " ", m.group(2)).strip()
    return presets


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--fabric", help="tên chất liệu trong prompts/fabric-presets.md")
    ap.add_argument("--garment", default=DEFAULT_GARMENT)
    ap.add_argument("--list", action="store_true", help="liệt kê chất liệu có sẵn")
    ap.add_argument("--template", default="cloth-change", help="tên mẫu trong prompts/ (mặc định cloth-change; lưới 4 ô: cloth-change-grid4)")
    ap.add_argument("--accessories", help="phụ kiện (tiếng Anh), điền vào {ACCESSORIES} nếu mẫu có")
    ap.add_argument("--panels", help="tên bộ 4 ô trong prompts/grid4-panels.md, điền vào {PANELS} nếu mẫu có")
    ap.add_argument("--pose", help="dáng + góc máy (tiếng Anh), điền vào {POSE} nếu mẫu có (vd mẫu cloth-change-hook)")
    args = ap.parse_args()

    presets = load_presets()
    if args.list:
        print("\n".join(presets))
        return
    if not args.fabric:
        sys.exit("Thiếu --fabric. Chạy --list để xem: " + ", ".join(presets))
    key = args.fabric.lower()
    if key not in presets:
        sys.exit(f"Không có chất liệu '{key}'. Có: {', '.join(presets)}")

    tpl = (ROOT / "prompts" / f"{args.template}.md").read_text(encoding="utf-8")
    one = re.sub(r"\s*\n+\s*", " ", tpl).strip()
    for ph in ("{GARMENT}", "{FABRIC}"):
        if ph not in one:
            sys.exit(f"Mẫu thiếu chỗ trống {ph}")
    one = one.replace("{GARMENT}", args.garment.strip()).replace("{FABRIC}", presets[key])
    if "{ACCESSORIES}" in one:
        if not args.accessories:
            sys.exit("Mẫu này cần --accessories")
        one = one.replace("{ACCESSORIES}", args.accessories.strip())
    if "{POSE}" in one:
        if not args.pose:
            sys.exit("Mẫu này cần --pose")
        one = one.replace("{POSE}", args.pose.strip())
    if "{PANELS}" in one:
        text = (ROOT / "prompts" / "grid4-panels.md").read_text(encoding="utf-8")
        sets = {m.group(1).strip().lower(): re.sub(r"\s*\n+\s*", " ", m.group(2)).strip()
                for m in re.finditer(r"^##\s+(\S+)\s*\n(.*?)(?=^##\s|\Z)", text, re.S | re.M)}
        if not args.panels or args.panels.lower() not in sets:
            sys.exit(f"Mẫu này cần --panels, có: {', '.join(sets)}")
        one = one.replace("{PANELS}", sets[args.panels.lower()])
    print(one)


if __name__ == "__main__":
    main()
