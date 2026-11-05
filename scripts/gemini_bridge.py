#!/usr/bin/env python3
"""Local Bridge Server kết nối giữa thư mục dự án và UserScript Tampermonkey trên gemini.google.com.
Chạy server này để cung cấp ảnh và prompt trực tiếp cho trình duyệt mà không cần API key.

Cách dùng:
  python3 scripts/gemini_bridge.py wedding-dress
  python3 scripts/gemini_bridge.py wedding-dress --port 8765
"""
import argparse
import json
import mimetypes
import os
import re
import sys
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from build_prompt import load_presets, DEFAULT_GARMENT
from gemini_collect import done_indexes, sources, download_dir, sniff_ext, PARTIAL_EXT, IMG_EXT

DEFAULT_PORT = 8765


class BridgeHandler(BaseHTTPRequestHandler):
    collection = "wedding-dress"

    def _set_cors(self, content_type="application/json"):
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_OPTIONS(self):
        self._set_cors()

    def do_GET(self):
        path = self.path.split("?")[0]

        if path == "/api/status":
            self._handle_status()
        elif path == "/api/next-task":
            self._handle_next_task()
        elif path.startswith("/file/"):
            self._handle_file_serve(path[6:])
        else:
            self.send_error(404, "Not Found")

    def do_POST(self):
        path = self.path.split("?")[0]
        if path == "/api/collect":
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length)
            data = json.loads(body.decode("utf-8")) if body else {}
            self._handle_collect(data)
        else:
            self.send_error(404, "Not Found")

    def _handle_status(self):
        done = done_indexes(self.collection)
        all_items = [p.stem for p in sources(self.collection)]
        pending = [s for s in all_items if s not in done]
        
        self._set_cors()
        self.wfile.write(json.dumps({
            "collection": self.collection,
            "total": len(all_items),
            "done": sorted(list(done)),
            "pending": pending
        }).encode("utf-8"))

    def _handle_next_task(self):
        done = done_indexes(self.collection)
        pending = [p for p in sources(self.collection) if p.stem not in done]

        if not pending:
            self._set_cors()
            self.wfile.write(json.dumps({"has_task": False}).encode("utf-8"))
            return

        target = pending[0]
        index = target.stem

        # Xác định chất liệu & kiểu dáng (có thể cấu hình thêm hoặc dùng mặc định)
        presets = load_presets()
        fabric_type = "matte"  # mặc định cho crepe/twill như bộ wedding-dress
        
        # Đọc prompt mẫu
        tpl = (ROOT / "prompts" / "cloth-change.md").read_text(encoding="utf-8")
        one_line_prompt = re.sub(r"\s*\n+\s*", " ", tpl).strip()
        one_line_prompt = one_line_prompt.replace("{GARMENT}", DEFAULT_GARMENT)
        one_line_prompt = one_line_prompt.replace("{FABRIC}", presets.get(fabric_type, presets.get("matte", "")))

        # 4 ảnh đầu vào theo đúng quy chuẩn dự án
        crop_path = ROOT / "anh" / self.collection / "crop" / f"{index}.png"
        if not crop_path.is_file():
            # Nếu chưa có crop thì dùng chính ảnh gốc làm fallback
            crop_path = target

        images = [
            f"http://127.0.0.1:{self.server.server_port}/file/ref/model_identity.png",
            f"http://127.0.0.1:{self.server.server_port}/file/anh/{self.collection}/{target.name}",
            f"http://127.0.0.1:{self.server.server_port}/file/anh/{self.collection}/crop/{crop_path.name}",
            f"http://127.0.0.1:{self.server.server_port}/file/ref/background_empty.png"
        ]

        self._set_cors()
        self.wfile.write(json.dumps({
            "has_task": True,
            "collection": self.collection,
            "index": index,
            "prompt": one_line_prompt,
            "images": images
        }).encode("utf-8"))

    def _handle_file_serve(self, rel_path):
        # Đảm bảo an toàn không thoát khỏi workspace
        clean_rel = os.path.normpath(rel_path).lstrip("/")
        file_path = ROOT / clean_rel

        if not file_path.is_file():
            self.send_error(404, f"File not found: {clean_rel}")
            return

        mime, _ = mimetypes.guess_type(str(file_path))
        self._set_cors(mime or "application/octet-stream")
        with open(file_path, "rb") as f:
            self.wfile.write(f.read())

    def _handle_collect(self, data):
        index = data.get("index")
        since = float(data.get("since", time.time() - 120))
        
        dl = download_dir()
        dst_dir = ROOT / "generated" / self.collection
        dst_dir.mkdir(parents=True, exist_ok=True)
        
        # Quét thư mục Downloads tìm ảnh mới
        deadline = time.time() + 60
        found_file = None
        
        while time.time() < deadline:
            files = [p for p in dl.iterdir() if p.is_file() and p.stat().st_mtime > since] if dl.is_dir() else []
            images = [p for p in files if p.suffix.lower() in IMG_EXT and not p.name.startswith(".")]
            if images:
                images.sort(key=lambda p: (p.name.startswith("Gemini"), p.stat().st_mtime), reverse=True)
                found_file = images[0]
                break
            time.sleep(1)

        if found_file:
            target_path = dst_dir / f"{index}.png"
            import shutil
            shutil.copy2(found_file, target_path)
            self._set_cors()
            self.wfile.write(json.dumps({"success": True, "saved_to": str(target_path)}).encode("utf-8"))
        else:
            self._set_cors()
            self.wfile.write(json.dumps({"success": False, "error": "Chưa thấy ảnh mới trong Downloads"}).encode("utf-8"))

    def log_message(self, format, *args):
        # Rút gọn log console
        print(f"[Bridge] {args[0]} -> {args[1]}")


def run(collection, port=DEFAULT_PORT):
    BridgeHandler.collection = collection
    server = HTTPServer(("127.0.0.1", port), BridgeHandler)
    print(f"\n========================================================")
    print(f"🚀 Gemini Local Bridge Server đang chạy tại: http://127.0.0.1:{port}")
    print(f"📁 Bộ ảnh đang xử lý: {collection}")
    print(f"👉 Mở gemini.google.com và bấm nút '▶ Chạy Auto (2K)'")
    print(f"========================================================\n")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nĐã dừng server.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Gemini Local Bridge Server cho UserScript")
    parser.add_argument("collection", nargs="?", default="wedding-dress", help="Tên bộ ảnh (vd: wedding-dress)")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help="Port cho server (mặc định: 8765)")
    args = parser.parse_args()
    run(args.collection, args.port)
