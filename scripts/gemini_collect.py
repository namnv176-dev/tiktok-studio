#!/usr/bin/env python3
"""Gom ảnh Gemini vừa tải về (thư mục Downloads của Chrome) vào đúng chỗ trong dự án, theo index của ảnh quần áo.

  - Xem việc còn lại:  python3 scripts/gemini_collect.py status wedding-dress
  - Đánh mốc trước khi bấm tải:  python3 scripts/gemini_collect.py mark
  - Lấy file mới về:   python3 scripts/gemini_collect.py collect wedding-dress anh-01 --since <mốc>
  - Lưu chỗ khác:      python3 scripts/gemini_collect.py collect - - --since <mốc> --to ref/background_empty

Ảnh nguồn: anh/<bộ>/<index>.*   ->   ảnh kết quả: generated/<bộ>/<index>.<đuôi gốc>
Thư mục Downloads: biến GEMINI_DOWNLOAD_DIR, mặc định ~/Downloads.
"""
import argparse
import os
import shutil
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
IMG_EXT = {".png", ".jpg", ".jpeg", ".webp"}
PARTIAL_EXT = {".crdownload", ".part", ".tmp"}


def download_dir():
    return Path(os.environ.get("GEMINI_DOWNLOAD_DIR", Path.home() / "Downloads")).expanduser()


def sources(collection):
    src = ROOT / "anh" / collection
    if not src.is_dir():
        sys.exit(f"Không có thư mục {src}")
    return sorted(p for p in src.iterdir() if p.suffix.lower() in IMG_EXT)


def done_indexes(collection):
    dst = ROOT / "generated" / collection
    if not dst.is_dir():
        return set()
    return {p.stem for p in dst.iterdir() if p.suffix.lower() in IMG_EXT}


def cmd_status(args):
    done = done_indexes(args.collection)
    todo = []
    for p in sources(args.collection):
        mark = "xong" if p.stem in done else "chưa"
        print(f"{p.stem}\t{mark}\t{p.relative_to(ROOT)}")
        if p.stem not in done:
            todo.append(p.stem)
    print(f"Còn lại: {len(todo)} ảnh" + (f" ({', '.join(todo)})" if todo else ""))


def cmd_mark(args):
    print(f"{time.time():.3f}")


def sniff_ext(path):
    """Đoán đuôi ảnh từ mấy byte đầu, không phải ảnh thì trả về None."""
    with open(path, "rb") as f:
        head = f.read(12)
    if head.startswith(b"\x89PNG"):
        return ".png"
    if head.startswith(b"\xff\xd8"):
        return ".jpg"
    if head[:4] == b"RIFF" and head[8:12] == b"WEBP":
        return ".webp"
    return None


def cmd_collect(args):
    dl = download_dir()
    deadline = time.time() + args.timeout
    sizes = {}  # file tạm của Chrome -> kích thước lần quét trước
    while True:
        files = [
            p for p in dl.iterdir()
            if p.is_file() and p.stat().st_mtime > args.since
        ] if dl.is_dir() else []
        partial = [p for p in files if p.suffix.lower() in PARTIAL_EXT]
        images = [p for p in files if p.suffix.lower() in IMG_EXT and not p.name.startswith(".")]
        if images and not partial:
            # Ưu tiên file tên Gemini_Generated_Image_*, sau đó lấy file mới nhất.
            images.sort(key=lambda p: (p.name.startswith("Gemini"), p.stat().st_mtime), reverse=True)
            src, ext, copy = images[0], images[0].suffix.lower(), False
            break
        # Chrome bật "hỏi vị trí lưu": dữ liệu nằm sẵn trong .com.google.Chrome.XXXX trong lúc hộp thoại
        # Save as còn mở. Khi file tạm đứng yên kích thước và là ảnh thì chép ra luôn.
        found = None
        for p in files:
            if not p.name.startswith(".com.google.Chrome."):
                continue
            size = p.stat().st_size
            if size > 0 and sizes.get(p) == size and sniff_ext(p):
                found = p
            sizes[p] = size
        if found:
            src, ext, copy = found, sniff_ext(found), True
            break
        if time.time() > deadline:
            sys.exit(f"Hết {args.timeout}s mà chưa thấy ảnh mới trong {dl}"
                     + (f" (còn {len(partial)} file đang tải dở)" if partial else ""))
        time.sleep(1.5)

    if args.to:
        stem = ROOT / args.to
        dst_dir, name = stem.parent, stem.name
    else:
        dst_dir, name = ROOT / "generated" / args.collection, args.index
    dst_dir.mkdir(parents=True, exist_ok=True)
    dst = dst_dir / f"{name}{ext}"
    if dst.exists() and not args.overwrite:
        sys.exit(f"{dst} đã có. Thêm --overwrite nếu muốn thay.")
    for old in dst_dir.glob(f"{name}.*"):
        old.unlink()
    shown = dst.relative_to(ROOT) if dst.is_relative_to(ROOT) else dst
    if copy:
        shutil.copyfile(src, dst)
        print(f"{src.name} (file tạm, hộp thoại Save as còn mở) -> {shown}")
    else:
        shutil.move(str(src), dst)
        print(f"{src.name} -> {shown}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("status", help="liệt kê ảnh nguồn và ảnh đã gen")
    p.add_argument("collection")
    p.set_defaults(func=cmd_status)

    p = sub.add_parser("mark", help="in mốc thời gian hiện tại")
    p.set_defaults(func=cmd_mark)

    p = sub.add_parser("collect", help="chuyển ảnh mới tải về vào generated/<bộ>/<index>")
    p.add_argument("collection")
    p.add_argument("index", help="vd anh-01 (trùng tên ảnh nguồn)")
    p.add_argument("--since", type=float, required=True, help="mốc từ lệnh mark")
    p.add_argument("--timeout", type=int, default=90)
    p.add_argument("--overwrite", action="store_true")
    p.add_argument("--to", help="lưu vào đường dẫn khác (không đuôi), vd ref/background_empty")
    p.set_defaults(func=cmd_collect)

    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
