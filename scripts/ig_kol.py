#!/usr/bin/env python3
"""Tìm KOL thời trang Hàn trên Instagram qua hashtag (Apify: apify/instagram-scraper).

  python3 scripts/ig_kol.py discover --hashtags 출근룩 데일리룩 오오티디 --per-tag 50 [--dry-run]

Chỉ lấy dữ liệu công khai (bài, like, bình luận, chủ tài khoản) để nghiên cứu, không tải ảnh.
Dùng chung APIFY_TOKEN, ngân sách tháng và giới hạn mỗi lần chạy với scripts/trends.py.
Kết quả: data/instagram/kol-candidates-*.csv (gom theo tài khoản) và top-posts-*.csv.
"""
import argparse
import csv
import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from trends import (  # noqa: E402
    API, DATA_DIR, actor_prices, budget_status, env_float, env_str, load_env, log_ledger, monthly_usage,
)

OUT_DIR = DATA_DIR / "instagram"


def run_actor(actor, body, max_items, token, dry_run):
    max_run_usd = env_float("APIFY_MAX_USD_PER_RUN", 0.5)
    per_result, start, model = actor_prices(actor, token)
    estimate = max_items * per_result + start
    used, ceiling, remaining = budget_status(token)
    print(f"Actor: {actor} ({model}) — ~${per_result:.5f}/kết quả + ${start:.4f} khởi động")
    print(f"Lần chạy này: tối đa {max_items} kết quả ≈ ${estimate:.3f}")
    print(f"Tháng này: đã dùng ${used:.3f} / ngân sách ${ceiling:.2f} → còn ${remaining:.3f}")
    if estimate > max_run_usd:
        sys.exit(f"Dừng: ước tính ${estimate:.3f} > APIFY_MAX_USD_PER_RUN ${max_run_usd}.")
    if estimate > remaining:
        sys.exit(f"Dừng: không đủ ngân sách tháng (còn ${remaining:.3f}).")
    if dry_run:
        print("Chạy thử (--dry-run): chưa gọi actor.")
        return None

    charge_cap = round(min(max_run_usd, remaining), 4)
    req = urllib.request.Request(
        f"{API}/acts/{actor.replace('/', '~')}/run-sync-get-dataset-items"
        f"?timeout=600&maxItems={max_items}&maxTotalChargeUsd={charge_cap}",
        data=json.dumps(body).encode(),
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=630) as resp:
            items = json.load(resp)
    except (urllib.error.URLError, TimeoutError) as e:
        detail = e.read().decode(errors="replace")[:500] if isinstance(e, urllib.error.HTTPError) else str(e)
        log_ledger({"actor": actor, "input": body, "results": 0, "estimate_usd": round(estimate, 4), "error": detail})
        sys.exit(f"Apify lỗi: {detail}")
    try:
        used_after, _ = monthly_usage(token)
    except (urllib.error.URLError, KeyError):
        used_after = None
    spent = (used_after - used) if used_after is not None else None
    log_ledger({"actor": actor, "input": body, "results": len(items), "estimate_usd": round(estimate, 4),
                "spent_usd": spent, "month_used_usd": used_after})
    print(f"Nhận {len(items)} kết quả. Chi phí ghi nhận ≈ " + (f"${spent:.3f}" if spent is not None else "chưa cập nhật")
          + " (Apify có thể cập nhật trễ vài phút)")
    return items


def write_csv(path, rows, cols):
    with path.open("w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


def discover(a):
    token = env_str("APIFY_TOKEN")
    if not token:
        sys.exit("Thiếu APIFY_TOKEN trong .env.")
    actor = env_str("IG_ACTOR", "apify/instagram-scraper")
    tags = [t.lstrip("#") for t in a.hashtags]
    body = {
        "directUrls": [f"https://www.instagram.com/explore/tags/{urllib.parse.quote(t)}/" for t in tags],
        "resultsType": "posts",
        "resultsLimit": a.per_tag,
        "addParentData": True,
    }
    items = run_actor(actor, body, len(tags) * a.per_tag, token, a.dry_run)
    if items is None:
        return

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    stamp = time.strftime("%Y%m%d-%H%M")
    (OUT_DIR / f"raw-discover-{stamp}.json").write_text(json.dumps(items, ensure_ascii=False, indent=1))

    posts = []
    for it in items:
        if not isinstance(it, dict) or not it.get("ownerUsername") or it.get("error"):
            continue
        likes = it.get("likesCount")
        posts.append({
            "owner": it["ownerUsername"],
            "owner_name": it.get("ownerFullName") or "",
            "url": it.get("url"),
            "type": it.get("type"),
            "likes": likes if isinstance(likes, int) and likes >= 0 else None,  # -1 = KOL ẩn like
            "comments": it.get("commentsCount") or 0,
            "date": (it.get("timestamp") or "")[:10],
            "hashtags": " ".join("#" + h for h in (it.get("hashtags") or [])[:8]),
            "caption": (it.get("caption") or "").replace("\n", " ")[:200],
        })

    by_owner = defaultdict(list)
    for p in posts:
        by_owner[p["owner"]].append(p)
    kols = []
    for owner, ps in by_owner.items():
        liked = [p["likes"] for p in ps if p["likes"] is not None]
        best = max(ps, key=lambda p: p["likes"] or 0)
        kols.append({
            "owner": owner,
            "profile": f"https://www.instagram.com/{owner}/",
            "owner_name": ps[0]["owner_name"],
            "posts_found": len(ps),
            "avg_likes": round(sum(liked) / len(liked)) if liked else None,
            "max_likes": max(liked) if liked else None,
            "avg_comments": round(sum(p["comments"] for p in ps) / len(ps)),
            "best_post": best["url"],
            "sample_caption": best["caption"][:120],
        })
    kols.sort(key=lambda k: (k["avg_likes"] or 0, k["posts_found"]), reverse=True)
    posts.sort(key=lambda p: p["likes"] or 0, reverse=True)

    kpath = OUT_DIR / f"kol-candidates-{stamp}.csv"
    ppath = OUT_DIR / f"top-posts-{stamp}.csv"
    write_csv(kpath, kols, list(kols[0].keys()) if kols else ["owner"])
    write_csv(ppath, posts, ["likes", "comments", "owner", "url", "type", "date", "hashtags", "caption"])
    print(f"{len(posts)} bài từ {len(kols)} tài khoản (hashtag: {', '.join('#' + t for t in tags)})")
    print(f"KOL: {kpath}\nBài: {ppath}")
    for k in kols[:15]:
        print(f"- @{k['owner']:<24} bài={k['posts_found']} like TB={k['avg_likes']} max={k['max_likes']}")


def search_users(a):
    """Tìm tài khoản theo từ khóa (Instagram user search), trả về follower / bio / loại tài khoản."""
    token = env_str("APIFY_TOKEN")
    if not token:
        sys.exit("Thiếu APIFY_TOKEN trong .env.")
    actor = env_str("IG_ACTOR", "apify/instagram-scraper")
    body = {
        "search": ", ".join(a.queries),
        "searchType": "user",
        "searchLimit": a.limit,
        "resultsType": "details",
        "resultsLimit": 1,
    }
    items = run_actor(actor, body, len(a.queries) * a.limit, token, a.dry_run)
    if items is None:
        return

    save_profiles(items, "kol-search", f"từ khóa: {', '.join(a.queries)}")


def profile_rows(items):
    """Dòng KOL từ dữ liệu profile: follower, tương tác TB các bài gần nhất, ngày đăng gần nhất."""
    now = datetime.now(timezone.utc)
    rows, seen = [], set()
    for it in items:
        user = isinstance(it, dict) and it.get("username")
        if not user or user in seen or it.get("error"):
            continue
        seen.add(user)
        latest = [p for p in it.get("latestPosts") or [] if isinstance(p, dict)]
        liked = [p["likesCount"] for p in latest if isinstance(p.get("likesCount"), int) and p["likesCount"] >= 0]
        dates = sorted(p["timestamp"] for p in latest if p.get("timestamp"))
        last = datetime.fromisoformat(dates[-1].replace("Z", "+00:00")) if dates else None
        followers = it.get("followersCount") or 0
        avg = round(sum(liked) / len(liked)) if liked else None
        best = max(latest, key=lambda p: p.get("likesCount") or 0) if latest else {}
        rows.append({
            "username": user,
            "profile": f"https://www.instagram.com/{user}/",
            "full_name": it.get("fullName") or "",
            "followers": followers,
            "posts": it.get("postsCount"),
            "verified": it.get("verified"),
            "business": it.get("isBusinessAccount"),
            "category": it.get("businessCategoryName") or "",
            "avg_likes_latest": avg,
            "engagement_pct": round(100 * avg / followers, 2) if avg is not None and followers else None,
            "last_post": last.date().isoformat() if last else None,
            "days_since_post": (now - last).days if last else None,
            "best_recent_post": best.get("url"),
            "bio": (it.get("biography") or "").replace("\n", " ")[:160],
        })
    rows.sort(key=lambda r: r["followers"], reverse=True)
    return rows


def save_profiles(items, prefix, label):
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    stamp = time.strftime("%Y%m%d-%H%M")
    (OUT_DIR / f"raw-{prefix}-{stamp}.json").write_text(json.dumps(items, ensure_ascii=False, indent=1))
    rows = profile_rows(items)
    path = OUT_DIR / f"{prefix}-{stamp}.csv"
    write_csv(path, rows, list(rows[0].keys()) if rows else ["username"])
    print(f"{len(rows)} tài khoản ({label})\nFile: {path}")
    for r in rows:
        print(f"- @{r['username']:<18} fl={r['followers']:>9,} like TB={r['avg_likes_latest']} ER={r['engagement_pct']}% "
              f"đăng gần nhất={r['last_post']} {r['category']} | {r['bio'][:50]}")


def check_profiles(a):
    """Kiểm tra danh sách KOL đã biết tên (apify/instagram-profile-scraper)."""
    token = env_str("APIFY_TOKEN")
    if not token:
        sys.exit("Thiếu APIFY_TOKEN trong .env.")
    users = [u.lstrip("@") for u in a.usernames]
    actor = env_str("IG_PROFILE_ACTOR", "apify/instagram-profile-scraper")
    items = run_actor(actor, {"usernames": users, "includeAboutSection": False}, len(users), token, a.dry_run)
    if items is None:
        return
    save_profiles(items, "kol-profiles", f"{len(users)} tài khoản yêu cầu")
    missing = sorted(set(users) - {i.get("username") for i in items if isinstance(i, dict)})
    if missing:
        print(f"Không lấy được: {', '.join('@' + m for m in missing)}")


def main():
    load_env()
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("search", help="Tìm tài khoản theo từ khóa")
    s.add_argument("--queries", nargs="+", required=True, help="1–3 từ khóa")
    s.add_argument("--limit", type=int, default=8, help="Số tài khoản mỗi từ khóa")
    s.add_argument("--dry-run", action="store_true")
    pr = sub.add_parser("profiles", help="Kiểm tra KOL theo tên tài khoản")
    pr.add_argument("--usernames", nargs="+", required=True)
    pr.add_argument("--dry-run", action="store_true")
    d = sub.add_parser("discover", help="Tìm KOL qua hashtag")
    d.add_argument("--hashtags", nargs="+", required=True, help="1–3 hashtag (không cần dấu #)")
    d.add_argument("--per-tag", type=int, default=50, help="Số bài mỗi hashtag")
    d.add_argument("--dry-run", action="store_true")
    a = p.parse_args()
    if a.cmd == "profiles":
        if len(a.usernames) > 30:
            sys.exit("Tối đa 30 tài khoản mỗi lần chạy.")
        check_profiles(a)
    elif a.cmd == "search":
        if len(a.queries) > 3:
            sys.exit("Tối đa 3 từ khóa mỗi lần chạy.")
        search_users(a)
    elif a.cmd == "discover":
        if len(a.hashtags) > 3:
            sys.exit("Tối đa 3 hashtag mỗi lần chạy.")
        discover(a)


if __name__ == "__main__":
    main()
