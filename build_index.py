#!/usr/bin/env python3
"""
QuoteFancy 명언 인덱스 생성기 (이미지 다운로드 없음 — HTML만 수집)

각 guru의 페이지네이션을 순회해 명언 이미지 id 목록만 추출하여
quotes_index.json 에 저장한다. 배경화면 변경 시 필요한 1장만 다운로드하는
on-demand 방식의 기반이 된다. (bulk 다운로드 없이 수 초면 완료)

사용법:
    uv run build_index.py  # config.yaml 기준
    uv run build_index.py --guru bruce-lee-quotes
"""

import argparse
import json
import os
import re
import sys
import time
import urllib.request
import urllib.error
import yaml

BASE_URL = "https://quotefancy.com"
# 이미지 URL 패턴: /media/wallpaper/800x450/{id}-{Author}-Quote-{slug}.jpg
IMG_ID_RE = re.compile(r"/media/wallpaper/\d+x\d+/(\d+)-")


def load_config(path="config.yaml"):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


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


def scrape_ids(slug, cfg):
    """guru의 전체 페이지네이션을 순회해 명언 id 목록을 반환."""
    user_agent = cfg.get("user_agent", "Mozilla/5.0")
    delay = cfg.get("request_delay_seconds", 1.0)

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
        # 다음 페이지 링크가 없으면 종료
        if not re.search(r'href="[^"]*/page/{}"'.format(page + 1), html):
            break
        page += 1
        time.sleep(delay)

    return list(dict.fromkeys(all_ids))


def build_index(cfg, guru=None):
    """guru 목록의 id 인덱스를 생성해 quotes_index.json 에 저장하고 반환."""
    gurus = [guru] if guru else cfg.get("gurus", [])
    index = {}
    for slug in gurus:
        ids = scrape_ids(slug, cfg)
        index[slug] = ids
        print(f"  {slug}: {len(ids)}개 명언 id 수집")

    # 기존 인덱스가 있으면 병합 (다른 guru 보존)
    index_path = cfg.get("index_file", "quotes_index.json")
    if os.path.exists(index_path):
        with open(index_path, "r", encoding="utf-8") as f:
            existing = json.load(f)
        existing.update(index)
        index = existing

    with open(index_path, "w", encoding="utf-8") as f:
        json.dump(index, f, ensure_ascii=False, indent=2)
    return index


def main():
    parser = argparse.ArgumentParser(description="QuoteFancy 명언 인덱스 생성기")
    parser.add_argument("--config", default="config.yaml")
    parser.add_argument("--guru", help="특정 guru slug만 처리")
    args = parser.parse_args()

    cfg = load_config(args.config)
    if not args.guru and not cfg.get("gurus"):
        print("gurus가 비어 있습니다. config.yaml을 확인하세요.", file=sys.stderr)
        sys.exit(1)

    print("==> 명언 인덱스 생성 중 (이미지 다운로드 없음)...")
    index = build_index(cfg, guru=args.guru)
    total = sum(len(v) for v in index.values())
    print(f"==> 완료: 총 {total}개 명언 인덱스")


if __name__ == "__main__":
    main()
