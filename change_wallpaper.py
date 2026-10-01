#!/usr/bin/env python3
"""
QuoteFancy 무작위 배경화면 적용기 (Phase 1)

wallpapers/ 디렉터리에서 무작위로 명언 이미지 1장을 골라
macOS의 모든 데스크톱(멀티 모니터 포함) 배경화면으로 설정한다.

사용법:
    python3 change_wallpaper.py                 # 모든 guru에서 무작위 선택
    python3 change_wallpaper.py --guru bruce-lee-quotes   # 특정 guru만
    python3 change_wallpaper.py --list          # 사용 가능한 이미지 수 확인
"""

import argparse
import glob
import json
import os
import random
import subprocess
import sys
import time

APP_NAME = "QuoteFancy Live Wallpaper"


def load_config(path="config.json"):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def collect_images(wallpaper_dir, guru=None):
    """wallpaper_dir 아래의 모든 .jpg 경로 목록을 반환."""
    if guru:
        pattern = os.path.join(wallpaper_dir, guru, "*.jpg")
    else:
        pattern = os.path.join(wallpaper_dir, "*", "*.jpg")
    return sorted(glob.glob(pattern))


def set_wallpaper(image_path):
    """
    macOS 배경화면 변경.

    osascript를 사용해 System Events에 지시한다.
    'picture of every desktop' 로 멀티 모니터 모두 적용.
    """
    abs_path = os.path.abspath(image_path)
    script = (
        'tell application "System Events" to set picture of every desktop '
        f'to POSIX file "{abs_path}"'
    )
    result = subprocess.run(
        ["osascript", "-e", script],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"배경화면 변경 실패 (exit {result.returncode}): {result.stderr.strip()}"
        )
    return abs_path


def log_history(log_dir, image_path):
    """어떤 명언이 언제 적용됐는지 로그를 남긴다."""
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, "wallpaper.log")
    guru = os.path.basename(os.path.dirname(image_path))
    fname = os.path.basename(image_path)
    line = f"{time.strftime('%Y-%m-%d %H:%M:%S')}  {guru}/{fname}\n"
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(line)


def main():
    parser = argparse.ArgumentParser(description="QuoteFancy 무작위 배경화면 적용기")
    parser.add_argument("--config", default="config.json")
    parser.add_argument("--guru", help="특정 guru slug만 사용")
    parser.add_argument("--list", action="store_true", help="이미지 수만 출력")
    args = parser.parse_args()

    cfg = load_config(args.config)
    wallpaper_dir = cfg.get("wallpaper_dir", "wallpapers")

    images = collect_images(wallpaper_dir, guru=args.guru)
    if not images:
        print(
            "배경화면 이미지가 없습니다. 먼저 `python3 scrape.py` 를 실행하세요.",
            file=sys.stderr,
        )
        sys.exit(1)

    if args.list:
        print(f"사용 가능한 이미지: {len(images)}장")
        return

    chosen = random.choice(images)

    if sys.platform == "darwin":
        abs_path = set_wallpaper(chosen)
        print(f"배경화면 변경 완료: {os.path.basename(abs_path)}")
    else:
        # 비-macOS (테스트/개발용): 실제 변경 없이 선택 결과만 출력
        print(f"[비-macOS] 선택된 이미지 (변경 미적용): {chosen}")

    log_dir = cfg.get("log_dir", "logs")
    log_history(log_dir, chosen)


if __name__ == "__main__":
    main()
