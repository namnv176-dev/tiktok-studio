#!/usr/bin/env python3
"""Lấy danh sách video Douyin / TikTok (link + số liệu) để nghiên cứu trend, lọc theo lượt xem / lượt thích / chủ đề.

Nguồn dữ liệu:
  - Kiểm tra cấu hình: python3 scripts/trends.py check
  - Douyin (Apify):    python3 scripts/trends.py apify  --post bai-01 --keywords ... --match ...
  - TikTok (Apify):    python3 scripts/trends.py tiktok --post bai-01 --keywords ... --match ...
  - File JSON:         python3 scripts/trends.py file data/douyin/raw-chrome-xxx.json --post ... --keywords ... --match ...

Chỉ lưu metadata và link, không tải video.
Cấu hình đọc từ file .env ở gốc dự án (biến môi trường đã export sẽ được ưu tiên).
"""
import argparse
import csv
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ENV_FILE = ROOT / ".env"
DATA_DIR = ROOT / "data"


def load_env():
    """Đọc .env vào os.environ, không ghi đè biến đã export."""
    if not ENV_FILE.exists():
        return
    for line in ENV_FILE.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, val = line.split("=", 1)
        os.environ.setdefault(key.strip(), val.strip().strip('"').strip("'"))


def env_str(key, default=""):
    return os.environ.get(key, "").strip() or default


def env_int(key, default=None):
    val = env_str(key)
    if not val:
        return default
    try:
        return int(val)
    except ValueError:
        sys.exit(f"{key} trong .env phải là số, đang là: {val!r}")


def env_list(key):
    return [v.strip() for v in env_str(key).split(",") if v.strip()]

# Các actor Douyin trên Apify đặt tên field khác nhau, nên thử lần lượt từng đường dẫn.
FIELD_PATHS = {
    "id": ["aweme_id", "awemeId", "id", "videoId"],
    # Không dùng "videoUrl": ở một số actor đó là link MP4 tạm thời, không phải link bài.
    "url": ["url", "webVideoUrl", "shareUrl", "share_url"],
    "desc": ["desc", "description", "text", "title", "caption"],
    "author": ["author.nickname", "authorMeta.name", "author.name", "nickname", "author"],
    "views": ["statistics.play_count", "stats.playCount", "playCount", "play_count", "views", "viewCount"],
    "likes": ["statistics.diggCount", "statistics.digg_count", "stats.diggCount", "diggCount", "digg_count", "likes", "likeCount"],
    "comments": ["statistics.commentCount", "statistics.comment_count", "stats.commentCount", "commentCount", "comment_count", "comments"],
    "shares": ["statistics.shareCount", "statistics.share_count", "stats.shareCount", "shareCount", "share_count", "shares"],
    "collects": ["statistics.collectCount", "statistics.collect_count", "stats.collectCount", "collectCount", "collect_count", "collects"],
    "create_time": ["create_time", "createTime", "createTimeISO", "created_at", "publishTime"],
    "cover": ["videoMeta.cover", "video.cover.url_list.0", "cover", "coverUrl", "videoMeta.coverUrl", "thumbnail"],
    "hashtags": ["text_extra", "hashtags", "challenges", "tags"],
}


def dig(obj, path):
    for key in path.split("."):
        if isinstance(obj, list) and key.isdigit() and int(key) < len(obj):
            obj = obj[int(key)]
        elif isinstance(obj, dict) and key in obj:
            obj = obj[key]
        else:
            return None
    return obj


def first(item, field):
    for path in FIELD_PATHS[field]:
        val = dig(item, path)
        if val not in (None, "", []):
            return val
    return None


def parse_count(val):
    """Đổi '1.2万', '3亿', '12,345', 5000 -> int."""
    if val is None:
        return 0
    if isinstance(val, (int, float)):
        return int(val)
    s = str(val).strip().replace(",", "").lower()
    mult = 1
    for suffix, m in (("万", 10_000), ("w", 10_000), ("亿", 100_000_000), ("k", 1_000), ("m", 1_000_000)):
        if s.endswith(suffix):
            s, mult = s[: -len(suffix)], m
            break
    try:
        return int(float(s) * mult)
    except ValueError:
        return 0


def parse_time(val):
    if val in (None, ""):
        return None
    if isinstance(val, (int, float)) or str(val).isdigit():
        ts = int(val)
        if ts > 10**12:  # mili giây
            ts //= 1000
        return datetime.fromtimestamp(ts, tz=timezone.utc)
    try:
        dt = datetime.fromisoformat(str(val).replace("Z", "+00:00"))
        return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
    except ValueError:
        return None


def parse_hashtags(raw, desc):
    tags = set()
    if isinstance(raw, list):
        for t in raw:
            if isinstance(t, str):
                tags.add(t.lstrip("#"))
            elif isinstance(t, dict):
                name = t.get("hashtag_name") or t.get("name") or t.get("title") or t.get("cha_name")
                if name:
                    tags.add(str(name).lstrip("#"))
    tags.update(re.findall(r"#([^\s#@]+)", desc or ""))
    return sorted(tags)


def normalize(item):
    desc = first(item, "desc") or ""
    vid = first(item, "id")
    url = first(item, "url") or (f"https://www.douyin.com/video/{vid}" if vid else None)
    if not vid and url:
        m = re.search(r"/video/(\d+)", url)
        vid = m.group(1) if m else None
    created = parse_time(first(item, "create_time"))
    author = first(item, "author")
    return {
        "id": str(vid) if vid else None,
        "url": url,
        "author": author if isinstance(author, str) else None,
        "desc": desc.strip(),
        "hashtags": parse_hashtags(first(item, "hashtags"), desc),
        "video_tags": [t.get("name") for t in item.get("videoTags") or [] if isinstance(t, dict) and t.get("name")],
        "views": parse_count(first(item, "views")),
        "likes": parse_count(first(item, "likes")),
        "comments": parse_count(first(item, "comments")),
        "shares": parse_count(first(item, "shares")),
        "collects": parse_count(first(item, "collects")),
        "created": created.isoformat() if created else None,
        "cover": first(item, "cover"),
        "keyword": item.get("_keyword") or item.get("searchQuery") or item.get("searchTerm") or item.get("keyword"),
    }


def apply_filter(rows, flt):
    """Lọc và trả về (danh sách giữ lại, thống kê số video bị loại theo từng lý do)."""
    now = datetime.now(timezone.utc)
    tags_any = [t.lower().lstrip("#") for t in flt.get("tags_any") or []]
    match = [t.lower().lstrip("#") for t in flt.get("match") or []]
    keywords = set(flt.get("keywords") or [])
    out, seen = [], set()
    dropped = {"trùng/thiếu link": 0, "sai từ khóa": 0, "không liên quan chủ đề": 0, "dưới ngưỡng": 0, "quá cũ": 0}
    for r in rows:
        if not r["url"] or r["id"] in seen:
            dropped["trùng/thiếu link"] += 1
            continue
        # Kết quả cào từ một từ khóa khác (vd agent lỡ tìm thêm) thì bỏ.
        if keywords and r["keyword"] and r["keyword"] not in keywords:
            dropped["sai từ khóa"] += 1
            continue
        hay = " ".join(r["hashtags"] + r["video_tags"] + [r["desc"]]).lower()
        if match and not any(t in hay for t in match):
            dropped["không liên quan chủ đề"] += 1
            continue
        if tags_any and not any(t in hay for t in tags_any):
            dropped["không liên quan chủ đề"] += 1
            continue
        if r["views"] < flt.get("min_views", 0) or r["likes"] < flt.get("min_likes", 0):
            dropped["dưới ngưỡng"] += 1
            continue
        max_age = flt.get("max_age_days")
        if max_age and r["created"]:
            if (now - datetime.fromisoformat(r["created"])).days > max_age:
                dropped["quá cũ"] += 1
                continue
        seen.add(r["id"])
        out.append(r)
    # Douyin thường ẩn lượt xem, nên khi views = 0 thì xếp theo lượt thích.
    out.sort(key=lambda r: (r["views"], r["likes"]), reverse=True)
    return out[: flt.get("top") or len(out)], dropped


API = "https://api.apify.com/v2"
LEDGER = ROOT / "data" / "apify-ledger.jsonl"


def env_float(key, default=None):
    val = env_str(key)
    if not val:
        return default
    try:
        return float(val)
    except ValueError:
        sys.exit(f"{key} trong .env phải là số, đang là: {val!r}")


def apify_get(path, token):
    req = urllib.request.Request(f"{API}{path}", headers={"Authorization": f"Bearer {token}"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.load(resp)["data"]


def actor_prices(actor, token, addons=()):
    """Giá mỗi kết quả và phí khởi động (USD) của actor pay-per-event, theo gói Free.

    Chỉ cộng: sự kiện chính + phí mỗi dòng dataset + các add-on trong `addons` (những add-on thực sự bật).
    """
    info = apify_get(f"/acts/{actor.replace('/', '~')}", token)
    pricing = (info.get("pricingInfos") or [{}])[-1]
    events = (pricing.get("pricingPerEvent") or {}).get("actorChargeEvents") or {}
    per_result = start = 0.0
    for name, ev in events.items():
        price = ev.get("eventPriceUsd")
        if price is None:  # giá theo bậc: lấy bậc FREE (đắt nhất) cho an toàn
            price = ((ev.get("eventTieredPricingUsd") or {}).get("FREE") or {}).get("tieredEventPriceUsd", 0)
        if ev.get("isOneTimeEvent") or "start" in name:
            start += price
        elif ev.get("isPrimaryEvent") or name == "apify-default-dataset-item" or name in addons:
            per_result += price
    missing = [a for a in addons if a not in events]
    if missing:
        sys.exit(f"Actor {actor} không có add-on {missing}: giá có thể đã đổi, kiểm tra lại trước khi chạy.")
    return per_result, start, pricing.get("pricingModel")


def monthly_usage(token):
    """(đã dùng tháng này, hạn mức tháng của tài khoản) theo USD."""
    lim = apify_get("/users/me/limits", token)
    used = (lim.get("current") or {}).get("monthlyUsageUsd")
    cap = (lim.get("limits") or {}).get("maxMonthlyUsageUsd")
    return used, cap


def budget_status(token):
    budget = env_float("APIFY_MONTHLY_BUDGET_USD", 5.0)
    used, cap = monthly_usage(token)
    if used is None:
        sys.exit("Không đọc được mức đã dùng trên Apify, dừng để tránh vượt ngân sách.")
    ceiling = min(budget, cap) if cap else budget
    return used, ceiling, ceiling - used


def ledger_runs(actor):
    """Số lần đã gọi actor (kể cả lần lỗi), theo data/apify-ledger.jsonl."""
    if not LEDGER.exists():
        return 0
    runs = 0
    for line in LEDGER.read_text(encoding="utf-8").splitlines():
        try:
            runs += json.loads(line).get("actor") == actor
        except json.JSONDecodeError:
            continue
    return runs


def log_ledger(entry):
    LEDGER.parent.mkdir(parents=True, exist_ok=True)
    with LEDGER.open("a", encoding="utf-8") as f:
        f.write(json.dumps({"time": datetime.now().isoformat(timespec="seconds"), **entry}, ensure_ascii=False) + "\n")


def douyin_job(keywords):
    """(actor, input, add-on bật, số kết quả/từ khóa, số từ khóa tối đa, giới hạn lượt suốt đời)."""
    extra = env_str("APIFY_EXTRA_INPUT")
    try:
        body = json.loads(extra) if extra else {}
    except json.JSONDecodeError as e:
        sys.exit(f"APIFY_EXTRA_INPUT trong .env không phải JSON hợp lệ: {e}")
    per_kw = env_int("APIFY_RESULTS_PER_KEYWORD", 10)
    body[env_str("APIFY_KEYWORDS_FIELD", "keywords")] = keywords
    body[env_str("APIFY_LIMIT_FIELD", "maxResultsPerQuery")] = per_kw
    for key in ("shouldDownloadVideos", "shouldDownloadCovers", "shouldDownloadSlideshowImages"):
        body[key] = False  # không tải media: vừa tốn tiền vừa ngoài phạm vi nghiên cứu
    return (env_str("APIFY_DOUYIN_ACTOR"), body, (), per_kw,
            env_int("APIFY_MAX_KEYWORDS_PER_RUN", 1), env_int("APIFY_MAX_LIFETIME_RUNS"))


def tiktok_job(keywords):
    per_kw = env_int("TIKTOK_RESULTS_PER_KEYWORD", 20)
    sort = env_str("TIKTOK_SORT", "MOST_RELEVANT")
    date = env_str("TIKTOK_DATE_FILTER", "ALL_TIME")
    body = {
        "searchQueries": keywords,
        "searchSection": "/video",
        "resultsPerPage": per_kw,
        "videoSearchSorting": sort,
        "videoSearchDateFilter": date,
        # Tắt hết phần lấy thêm / tải media (mặc định hashtags=['fyp'] sẽ cào thêm #fyp nếu không ghi đè).
        "hashtags": [], "profiles": [], "postURLs": [],
        "scrapeRelatedVideos": False, "scrapeRelatedSearchWords": False, "scrapeAdditionalAuthorMeta": False,
        "shouldDownloadVideos": False, "shouldDownloadCovers": False, "shouldDownloadSlideshowImages": False,
        "shouldDownloadAvatars": False, "shouldDownloadMusicCovers": False,
        "downloadSubtitlesOptions": "NEVER_DOWNLOAD_SUBTITLES",
        "aiVideoDescription": False, "aiVideoSummary": False,
        "commentsPerPost": 0, "topLevelCommentsPerPost": 0, "maxRepliesPerComment": 0,
        "maxFollowersPerProfile": 0, "maxFollowingPerProfile": 0,
        "proxyCountryCode": "None",
    }
    addons = []
    if sort != "MOST_RELEVANT":
        addons.append("mobile-filter-sorting-applied")
    if date != "ALL_TIME":
        addons.append("filter-applied")
    return (env_str("TIKTOK_ACTOR", "clockworks/tiktok-scraper"), body, tuple(addons), per_kw,
            env_int("TIKTOK_MAX_KEYWORDS_PER_RUN", 3), None)


def run_apify(platform, keywords, dry_run=False):
    token = env_str("APIFY_TOKEN")
    if not token:
        sys.exit("Thiếu APIFY_TOKEN trong .env.")
    build = douyin_job if platform == "douyin" else tiktok_job
    _, _, _, per_kw, max_kw, max_runs = build(keywords)
    if per_kw <= 0:
        sys.exit("Số kết quả mỗi từ khóa phải > 0 (0 = lấy hết, rất tốn tiền).")
    if len(keywords) > max_kw:
        print(f"Chỉ dùng {max_kw} từ khóa đầu: {', '.join(keywords[:max_kw])}")
        keywords = keywords[:max_kw]
    actor, body, addons, per_kw, _, _ = build(keywords)
    if not actor:
        sys.exit(f"Thiếu actor {platform} trong .env.")

    runs = ledger_runs(actor)
    if max_runs is not None:
        if runs >= max_runs:
            sys.exit(f"Dừng: đã dùng hết {runs}/{max_runs} lượt chạy Apify cho {actor}. Dùng nguồn Chrome.")
        print(f"Lượt chạy Apify: đã dùng {runs}/{max_runs}" + (" (chạy thật sẽ dùng thêm 1 lượt)" if not dry_run else ""))
    max_run_usd = env_float("APIFY_MAX_USD_PER_RUN", 0.5)

    max_items = len(keywords) * per_kw
    per_result, start, model = actor_prices(actor, token, addons)
    estimate = max_items * per_result + start
    used, ceiling, remaining = budget_status(token)
    charge_cap = round(min(max_run_usd, remaining), 4)
    print(f"Actor: {actor} ({model}) — ~${per_result:.5f}/kết quả + ${start:.4f} khởi động"
          + (f" (add-on: {', '.join(addons)})" if addons else ""))
    print(f"Lần chạy này: {len(keywords)} từ khóa x {per_kw} = tối đa {max_items} kết quả ≈ ${estimate:.3f}")
    print(f"Tháng này: đã dùng ${used:.3f} / ngân sách ${ceiling:.2f} → còn ${remaining:.3f}")

    if estimate > max_run_usd:
        sys.exit(f"Dừng: ước tính ${estimate:.3f} > APIFY_MAX_USD_PER_RUN ${max_run_usd}. Giảm số từ khóa hoặc số kết quả mỗi từ khóa.")
    if estimate > remaining:
        sys.exit(f"Dừng: không đủ ngân sách tháng (còn ${remaining:.3f}).")
    if dry_run:
        print("Chạy thử (--dry-run): chưa gọi actor.")
        return None

    # maxTotalChargeUsd / maxItems: Apify tự dừng actor khi chạm trần, kể cả khi ước tính sai.
    qs = f"timeout=600&maxItems={max_items}&maxTotalChargeUsd={charge_cap}"
    req = urllib.request.Request(
        f"{API}/acts/{actor.replace('/', '~')}/run-sync-get-dataset-items?{qs}",
        data=json.dumps(body).encode(),
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=630) as resp:
            items = json.load(resp)
    except (urllib.error.URLError, TimeoutError) as e:
        # Lần lỗi vẫn có thể đã tính lượt / tính tiền bên Apify, nên vẫn ghi sổ.
        detail = e.read().decode(errors="replace")[:500] if isinstance(e, urllib.error.HTTPError) else str(e)
        log_ledger({"actor": actor, "keywords": keywords, "results": 0, "estimate_usd": round(estimate, 4), "error": detail})
        sys.exit(f"Apify lỗi: {detail}")

    try:
        used_after, _ = monthly_usage(token)
    except (urllib.error.URLError, KeyError):
        used_after = None
    spent = (used_after - used) if used_after is not None else None
    log_ledger({
        "actor": actor, "keywords": keywords, "results": len(items), "estimate_usd": round(estimate, 4),
        "spent_usd": spent, "month_used_usd": used_after,
    })
    print(f"Nhận {len(items)} kết quả. Chi phí lần này ≈ " + (f"${spent:.3f}" if spent is not None else "chưa cập nhật (Apify ghi nhận trễ)"))
    if max_runs is not None:
        print(f"Còn {max_runs - runs - 1}/{max_runs} lượt chạy Apify.")
    return items


def save(rows, raw, source, post=None, platform="douyin"):
    out_dir = DATA_DIR / platform
    out_dir.mkdir(parents=True, exist_ok=True)
    stamp = time.strftime("%Y%m%d-%H%M")
    if post:
        source = f"{re.sub(r'[^A-Za-z0-9_-]+', '-', post)}-{source}"
    if raw is not None:
        (out_dir / f"raw-{source}-{stamp}.json").write_text(json.dumps(raw, ensure_ascii=False, indent=1))
    jpath = out_dir / f"trends-{source}-{stamp}.json"
    cpath = out_dir / f"trends-{source}-{stamp}.csv"
    jpath.write_text(json.dumps(rows, ensure_ascii=False, indent=1))
    cols = ["url", "views", "likes", "collects", "shares", "comments", "created", "author", "hashtags", "desc", "keyword"]
    with cpath.open("w", newline="", encoding="utf-8-sig") as f:  # utf-8-sig để Excel đọc đúng tiếng Trung/Việt
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow({**r, "hashtags": " ".join("#" + t for t in r["hashtags"])})
    return jpath, cpath


def check():
    """In trạng thái cấu hình (không in giá trị token)."""
    token, actor = env_str("APIFY_TOKEN"), env_str("APIFY_DOUYIN_ACTOR")
    print(f".env: {'có' if ENV_FILE.exists() else 'KHÔNG có'} ({ENV_FILE})")
    print(f"APIFY_TOKEN: {'đã điền' if token else 'trống'}")
    print(f"APIFY_DOUYIN_ACTOR: {actor or 'trống'}")
    source = env_str("DOUYIN_SOURCE", "chrome").lower()
    if source == "apify" and not (token and actor):
        source = "chrome (DOUYIN_SOURCE=apify nhưng thiếu token/actor)"
    print(f"Nguồn sẽ dùng: {source}")
    if actor:
        max_runs = env_int("APIFY_MAX_LIFETIME_RUNS")
        print(f"Lượt chạy Apify đã dùng: {ledger_runs(actor)}" + (f"/{max_runs}" if max_runs is not None else ""))
    print(f"CHROME_BROWSER: {env_str('CHROME_BROWSER') or 'trống (hỏi khi cần)'}")
    print(f"DOUYIN_KEYWORDS: {', '.join(env_list('DOUYIN_KEYWORDS')) or 'trống'}")
    print(f"Bộ lọc Douyin: {filter_from_env('douyin')}")
    print(f"Douyin Apify: {env_int('APIFY_MAX_KEYWORDS_PER_RUN', 1)} từ khóa x {env_int('APIFY_RESULTS_PER_KEYWORD', 10)} kết quả/lần")
    print(f"TIKTOK_ACTOR: {env_str('TIKTOK_ACTOR', 'clockworks/tiktok-scraper')} — "
          f"{env_int('TIKTOK_MAX_KEYWORDS_PER_RUN', 3)} từ khóa x {env_int('TIKTOK_RESULTS_PER_KEYWORD', 20)} kết quả/lần, "
          f"sort {env_str('TIKTOK_SORT', 'MOST_RELEVANT')}, ngày {env_str('TIKTOK_DATE_FILTER', 'ALL_TIME')}")
    print(f"TIKTOK_KEYWORDS: {', '.join(env_list('TIKTOK_KEYWORDS')) or 'trống'}")
    print(f"Bộ lọc TikTok: {filter_from_env('tiktok')}")
    print(f"Ngân sách Apify (dùng chung): ${env_float('APIFY_MONTHLY_BUDGET_USD', 5.0)}/tháng, "
          f"tối đa ${env_float('APIFY_MAX_USD_PER_RUN', 0.5)}/lần")
    if token:
        try:
            used, ceiling, remaining = budget_status(token)
            print(f"Apify tháng này: đã dùng ${used:.3f} / ${ceiling:.2f} → còn ${remaining:.3f}")
        except (urllib.error.URLError, KeyError) as e:
            print(f"Không đọc được mức dùng Apify: {e}")


def filter_from_env(platform="douyin"):
    """Ngưỡng lọc; TikTok dùng TIKTOK_MIN_VIEWS / TIKTOK_MIN_LIKES / TIKTOK_MAX_AGE_DAYS nếu có, không thì dùng ngưỡng chung."""
    pre = "TIKTOK_" if platform == "tiktok" else ""
    return {
        "min_views": env_int(pre + "MIN_VIEWS", env_int("MIN_VIEWS", 0)),
        "min_likes": env_int(pre + "MIN_LIKES", env_int("MIN_LIKES", 0)),
        "tags_any": env_list("TAGS_ANY"),
        "max_age_days": env_int(pre + "MAX_AGE_DAYS", env_int("MAX_AGE_DAYS")),
        "top": env_int("TOP", 50),
    }


def main():
    load_env()
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("source", choices=["check", "apify", "tiktok", "file"])
    p.add_argument("--platform", choices=["douyin", "tiktok"], help="Với source=file: dữ liệu của nền tảng nào (mặc định douyin)")
    p.add_argument("path", nargs="?", help="File JSON (khi source=file)")
    p.add_argument("--keywords", nargs="+", help="BẮT BUỘC: từ khóa đúng của bài đang làm (1–3 từ)")
    p.add_argument("--match", nargs="+", help="BẮT BUỘC: từ phải xuất hiện trong mô tả/hashtag để coi là đúng chủ đề")
    p.add_argument("--post", help="Mã bài (vd bai-02) để đặt tên file kết quả")
    p.add_argument("--min-views", type=int)
    p.add_argument("--min-likes", type=int)
    p.add_argument("--tags", nargs="+", help="Giữ video có ít nhất 1 tag/từ này")
    p.add_argument("--days", type=int, help="Chỉ lấy video đăng trong N ngày")
    p.add_argument("--top", type=int)
    p.add_argument("--dry-run", action="store_true", help="Apify: chỉ ước tính chi phí, không chạy actor")
    a = p.parse_args()

    if a.source == "check":
        check()
        return

    platform = "tiktok" if a.source == "tiktok" else (a.platform or "douyin")
    flt = filter_from_env(platform)
    for arg, key in (("min_views", "min_views"), ("min_likes", "min_likes"), ("tags", "tags_any"), ("days", "max_age_days"), ("top", "top")):
        if getattr(a, arg) is not None:
            flt[key] = getattr(a, arg)
    # Không tự lấy cả danh sách DOUYIN_KEYWORDS: mỗi lần chạy phải gắn với đúng một bài.
    if not a.keywords:
        sys.exit("Thiếu --keywords: ghi đúng 1–3 từ khóa của bài đang làm (DOUYIN_KEYWORDS / TIKTOK_KEYWORDS trong .env chỉ là kho gợi ý).")
    if len(a.keywords) > 3:
        sys.exit(f"Quá nhiều từ khóa ({len(a.keywords)}). Tối đa 3 từ khóa sát nhất với bài đang làm.")
    if not a.match:
        sys.exit("Thiếu --match: ghi các từ chủ đề (vd 小个子 矮个子 155) để loại video lạc đề.")
    keywords = a.keywords
    flt["keywords"], flt["match"] = keywords, a.match

    if a.source in ("apify", "tiktok"):
        raw = run_apify(platform, keywords, a.dry_run)
        if raw is None:
            return
    else:
        if not a.path:
            sys.exit("Cần đường dẫn file JSON.")
        raw = json.loads(Path(a.path).read_text())
        raw = raw.get("items", raw) if isinstance(raw, dict) else raw

    rows, dropped = apply_filter([normalize(i) for i in raw if isinstance(i, dict)], flt)
    jpath, cpath = save(rows, raw if a.source != "file" else None, "apify" if a.source != "file" else "file", a.post, platform)
    print(f"Từ khóa: {', '.join(keywords)} | Từ chủ đề: {', '.join(a.match)}")
    print(f"{len(raw)} video thô -> {len(rows)} video sau lọc")
    print("Bị loại: " + ", ".join(f"{k} {v}" for k, v in dropped.items() if v) if any(dropped.values()) else "Bị loại: 0")
    print(f"JSON: {jpath}\nCSV:  {cpath}")
    for r in rows[:10]:
        print(f"- views={r['views']:>9} likes={r['likes']:>8} {r['url']}  {' '.join('#' + t for t in r['hashtags'][:4])}")


if __name__ == "__main__":
    main()
