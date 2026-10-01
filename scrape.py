#!/usr/bin/env python3
"""
QuoteFancy 명언 4K 배경화면 다운로더 (Phase 0)

config.json 의 gurus 목록을 순회하며, 각 guru의 모든 명언 페이지에서
이미지 id를 추출하고 원본(4K, 3840x2160) 배경화면을 wallpapers/<slug>/<id>.jpg 로 저장한다.

이미 다운로드한 id는 건너뛴다 (incremental 재실행 가능).

사용법:
    python3 scrape.py            # config.json 기준 전체 다운로드
    python3 scrape.py --guru bruce-lee-quotes   # 특정 guru만
    python3 scrape.py --limit 5  # guru당 최대 5장만 (테스트용)
"""

import argparse
import json
import os
import re
import sys
import time
import urllib.request
import urllib.error

BASE_URL = "https://quotefancy.com"
# 이미지 URL 패턴: /media/wallpaper/800x450/{id}-{Author}-Quote-{slug}.jpg
IMG_ID_RE = re.compile(r"/media/wallpaper/\d+x\d+/(\d+)-")
# 원본 다운로드 URL 패턴: /download/{id}/original/wallpaper.jpg
DOWNLOAD_RE = re.compile(r'href="(/download/\d+/original/wallpaper\.jpg)"')


def load_config(path="config.json"):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def fetch(url, user_agent, timeout=30):
    req = urllib.request.Request(url, headers={"User-Agent": user_agent})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read()


def fetch_page(slug, page_num, user_agent):
    """페이지 HTML을 반환. 1페이지는 /slug, 2페이지부터 /slug/page/N"""
    if page_num == 1:
        url = f"{BASE_URL}/{slug}"
    else:
        url = f"{BASE_URL}/{slug}/page/{page_num}"
    return fetch(url, user_agent).decode("utf-8", errors="replace")


def extract_ids(html):
    """페이지에서 명언 이미지 id 목록을 추출 (중복 제거, 순서 유지)."""
    ids = []
    seen = set()
    for m in IMG_ID_RE.finditer(html):
        qid = m.group(1)
        if qid not in seen:
            seen.add(qid)
            ids.append(qid)
    return ids


def download_image(qid, out_dir, user_agent, delay):
    """원본 4K 이미지를 다운로드. 이미 있으면 스킵."""
    out_path = os.path.join(out_dir, f"{qid}.jpg")
    if os.path.exists(out_path) and os.path.getsize(out_path) > 0:
        return "skip", out_path

    url = f"{BASE_URL}/download/{qid}/original/wallpaper.jpg"
    data = fetch(url, user_agent)
    with open(out_path, "wb") as f:
        f.write(data)
    time.sleep(delay)
    return "download", out_path


def scrape_guru(slug, cfg, limit=None):
    user_agent = cfg.get("user_agent", "Mozilla/5.0")
    delay = cfg.get("request_delay_seconds", 1.5)
    base_dir = os.path.join(cfg.get("wallpaper_dir", "wallpapers"), slug)
    os.makedirs(base_dir, exist_ok=True)

    all_ids = []
    page = 1
    while True:
        try:
            html = fetch_page(slug, page, user_agent)
        except urllib.error.HTTPError as e:
            if e.code == 404 and page > 1:
                break  # 마지막 페이지 초과
            raise
        ids = extract_ids(html)
        if not ids:
            break
        all_ids.extend(ids)
        # 페이지에 다음 페이지 링크가 있는지 확인 (없으면 종료)
        if not re.search(r'href="[^"]*/page/{}"'.format(page + 1), html):
            break
        page += 1
        time.sleep(delay)

    # 중복 제거
    unique_ids = list(dict.fromkeys(all_ids))
    if limit is not None:
        unique_ids = unique_ids[:limit]

    downloaded = skipped = 0
    for qid in unique_ids:
        status, _ = download_image(qid, base_dir, user_agent, delay)
        if status == "download":
            downloaded += 1
        else:
            skipped += 1

    return {
        "slug": slug,
        "total_ids": len(unique_ids),
        "downloaded": downloaded,
        "skipped": skipped,
    }


def main():
    parser = argparse.ArgumentParser(description="QuoteFancy 4K 배경화면 다운로더")
    parser.add_argument("--config", default="config.json")
    parser.add_argument("--guru", help="특정 guru slug만 처리")
    parser.add_argument("--limit", type=int, help="guru당 최대 다운로드 수 (테스트용)")
    args = parser.parse_args()

    cfg = load_config(args.config)
    gurus = [args.guru] if args.guru else cfg.get("gurus", [])

    if not gurus:
        print("gurus가 비어 있습니다. config.json 을 확인하세요.")
        sys.exit(1)

    for slug in gurus:
        print(f"==> {slug} 처리 중...")
        result = scrape_guru(slug, cfg, limit=args.limit)
        print(
            f"    완료: 총 {result['total_ids']}개, "
            f"새로 다운로드 {result['downloaded']}개, 스킵 {result['skipped']}개"
        )


if __name__ == "__main__":
    main()
