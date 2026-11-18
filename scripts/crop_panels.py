#!/usr/bin/env python3
"""Cắt scene sheet (n khung cạnh nhau) thành từng khung 9:16. Dùng: crop_panels.py sheet.png outdir [n=3]"""
import sys
from pathlib import Path
from PIL import Image
src, out = Path(sys.argv[1]), Path(sys.argv[2]); n = int(sys.argv[3]) if len(sys.argv) > 3 else 3
im = Image.open(src).convert("RGB"); w, h = im.size; out.mkdir(parents=True, exist_ok=True)
m = 6  # chừa vạch ngăn giữa các khung
for i in range(n):
    x0, x1 = round(i*w/n)+m, round((i+1)*w/n)-m
    im.crop((x0, 0, x1, h)).save(out/f"panel-{i+1}.png"); print(out/f"panel-{i+1}.png", (x1-x0, h))
