#!/usr/bin/env python3
"""
QuoteFancy 무작위 배경화면 적용기 — on-demand 다운로드 방식 (Phase 1 개선)

동작 흐름:
  1. quotes_index.json 에서 무작위로 명언 1개 선택
  2. 해당 이미지가 캐시에 없으면 → 그 1장만 다운로드 (bulk 다운로드 없음)
  3. macOS의 모든 데스크톱 배경화면으로 설정
  4. 캐시가 max_cache_per_guru 를 초과하면 오래된 것부터 정리

사용법:
    uv run change_wallpaper.py                # 무작위 1장 적용
    uv run change_wallpaper.py --list         # 인덱스에 있는 명언 수 확인
    uv run change_wallpaper.py --build-index  # 인덱스만 갱신
"""

import argparse
import glob
import json
import os
import random
import subprocess
import sys
import time
import urllib.request
import urllib.error
from build_index import load_config

BASE_URL = "https://quotefancy.com"


def load_index(cfg):
    index_path = cfg.get("index_file", "quotes_index.json")
    if not os.path.exists(index_path):
        return None
    with open(index_path, "r", encoding="utf-8") as f:
        return json.load(f)


def ensure_index(cfg):
    """인덱스가 없으면 생성 (bulk 다운로드 없이 HTML만)."""
    index = load_index(cfg)
    if index:
        return index
    print("인덱스가 없습니다. 생성합니다...", file=sys.stderr)
    import build_index
    return build_index.build_index(cfg)


def download_image(qid, out_path, user_agent):
    """원본 4K 이미지 1장만 다운로드."""
    url = f"{BASE_URL}/download/{qid}/original/wallpaper.jpg"
    req = urllib.request.Request(url, headers={"User-Agent": user_agent})
    with urllib.request.urlopen(req, timeout=60) as resp:
        data = resp.read()
    with open(out_path, "wb") as f:
        f.write(data)
    return out_path


def evict_cache(wallpaper_dir, max_per_guru):
    """guru별 캐시 개수를 max_per_guru 로 제한 (오래된 것부터 삭제)."""
    if not max_per_guru or max_per_guru <= 0:
        return
    for guru_dir in glob.glob(os.path.join(wallpaper_dir, "*")):
        if not os.path.isdir(guru_dir):
            continue
        files = sorted(
            glob.glob(os.path.join(guru_dir, "*.jpg")),
            key=os.path.getmtime,
            reverse=True,
        )
        for f in files[max_per_guru:]:
            os.remove(f)


def set_wallpaper(image_path):
    """macOS 모든 데스크톱의 배경화면을 변경."""
    abs_path = os.path.abspath(image_path)
    script = (
        'tell application "System Events" to set picture of every desktop '
        f'to POSIX file "{abs_path}"'
    )
    result = subprocess.run(
        ["osascript", "-e", script], capture_output=True, text=True
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"배경화면 변경 실패 (exit {result.returncode}): {result.stderr.strip()}"
        )
    return abs_path


def log_history(log_dir, image_path):
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, "wallpaper.log")
    guru = os.path.basename(os.path.dirname(image_path))
    fname = os.path.basename(image_path)
    line = f"{time.strftime('%Y-%m-%d %H:%M:%S')}  {guru}/{fname}\n"
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(line)


def main():
    parser = argparse.ArgumentParser(description="QuoteFancy 무작위 배경화면 적용기")
    parser.add_argument("--config", default="config.yaml")
    parser.add_argument("--guru", help="특정 guru만 사용")
    parser.add_argument("--list", action="store_true", help="명언 수만 출력")
    parser.add_argument("--build-index", action="store_true", help="인덱스만 갱신")
    args = parser.parse_args()

    cfg = load_config(args.config)
    wallpaper_dir = cfg.get("wallpaper_dir", "wallpapers")
    log_dir = cfg.get("log_dir", "logs")
    max_cache = cfg.get("max_cache_per_guru", 0)
    user_agent = cfg.get("user_agent", "Mozilla/5.0")

    if args.build_index:
        import build_index
        build_index.build_index(cfg, guru=args.guru)
        return

    index = ensure_index(cfg)
    if not index:
        print("명언 인덱스가 비어 있습니다. build_index.py 를 실행하세요.", file=sys.stderr)
        sys.exit(1)

    # guru 필터 적용
    if args.guru:
        if args.guru not in index:
            print(f"인덱스에 '{args.guru}' 가 없습니다.", file=sys.stderr)
            sys.exit(1)
        index = {args.guru: index[args.guru]}

    # (guru, id) 쌍의 평평한 목록
    entries = [
        (slug, qid) for slug, ids in index.items() for qid in ids
    ]
    if not entries:
        print("명언 인덱스가 비어 있습니다.", file=sys.stderr)
        sys.exit(1)

    if args.list:
        print(f"인덱스에 있는 명언: {len(entries)}개")
        return

    # 무작위 선택
    slug, qid = random.choice(entries)
    out_dir = os.path.join(wallpaper_dir, slug)
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, f"{qid}.jpg")

    # 캐시에 없으면 1장만 다운로드
    if not (os.path.exists(out_path) and os.path.getsize(out_path) > 0):
        print(f"다운로드: {slug}/{qid}.jpg (on-demand)")
        download_image(qid, out_path, user_agent)
    else:
        print(f"캐시 사용: {slug}/{qid}.jpg")

    # 캐시 정리
    evict_cache(wallpaper_dir, max_cache)

    # 배경화면 적용
    if sys.platform == "darwin":
        abs_path = set_wallpaper(out_path)
        print(f"배경화면 변경 완료: {os.path.basename(abs_path)}")
    else:
        print(f"[비-macOS] 선택된 이미지 (변경 미적용): {out_path}")

    log_history(log_dir, out_path)


if __name__ == "__main__":
    main()
