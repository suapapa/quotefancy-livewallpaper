#!/usr/bin/env bash
# QuoteFancy Live Wallpaper — launchd 해제 스크립트 (Phase 2)
set -euo pipefail

LABEL="com.quotefancy.livewallpaper"
PLIST_PATH="$HOME/Library/LaunchAgents/${LABEL}.plist"

if [[ "$(uname -s)" != "Darwin" ]]; then
  echo "이 스크립트는 macOS에서만 실행해야 합니다." >&2
  exit 1
fi

launchctl unload "$PLIST_PATH" 2>/dev/null || true
rm -f "$PLIST_PATH"

echo "✓ 해제 완료 (라벨: ${LABEL})"
