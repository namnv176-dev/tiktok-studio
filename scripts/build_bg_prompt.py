#!/usr/bin/env python3
"""Ghép prompt tạo ảnh nền trống cho `agy -p` (Banana Pro), không cần ảnh tham chiếu.

Lấy khối RULES + mô tả cảnh từ prompts/background-<set>.md (dòng "Dáng hợp" không gửi đi).
  --set checkin        điểm check-in nổi tiếng + góc phố, bố cục sát tường/cửa (mặc định)
  --set cafe-hien-dai  4 quán cà phê hiện đại, cùng bố cục

  python3 scripts/build_bg_prompt.py --set checkin --list
  python3 scripts/build_bg_prompt.py --set checkin --scene pho-tuong-da-be > <scratchpad>/bg.txt
  agy -p "$(cat <scratchpad>/bg.txt)" --dangerously-skip-permissions --output-format text
  # rồi cp ảnh trong output về ref/background_empty_<scene>.jpg
"""
import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

HEADER = """You must generate an image using your own image generation tool. Do not write code, do not call any external API, do not use run_command for this task, do not run any other command besides calling your image generation tool. No reference images are needed.

Use AspectRatio: "9:16" (vertical portrait).
ImageName: "{image_name}"

Prompt:
"{body}"

Execute the generation immediately and return the absolute saved image path."""


def load(src):
    text = src.read_text(encoding="utf-8")
    sections = {}
    for m in re.finditer(r"^##\s+(\S+)\s*\n(.*?)(?=^##\s|\Z)", text, re.S | re.M):
        body = re.sub(r"^Dáng hợp:.*$", "", m.group(2), flags=re.M)
        sections[m.group(1).strip()] = re.sub(r"\s*\n+\s*", " ", body).strip()
    rules = sections.pop("RULES", None)
    if not rules:
        sys.exit(f"{src} thiếu mục ## RULES")
    sections.pop("Tóm", None)  # "## Tóm tắt nghiên cứu" là ghi chú, không phải cảnh
    return rules, sections


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--set", default="checkin", help="checkin | cafe-hien-dai")
    ap.add_argument("--scene")
    ap.add_argument("--list", action="store_true")
    args = ap.parse_args()
    src = ROOT / "prompts" / f"background-{args.set}.md"
    if not src.exists():
        sys.exit(f"Không có {src}")
    rules, scenes = load(src)
    if args.list or not args.scene:
        print("\n".join(scenes))
        return
    if args.scene not in scenes:
        sys.exit(f"Không có cảnh '{args.scene}'. Có: {', '.join(scenes)}")
    body = (scenes[args.scene] + " " + rules).replace('"', "'")
    print(HEADER.format(image_name=f"background_empty_{args.scene}".replace("-", "_"), body=body))


if __name__ == "__main__":
    main()
