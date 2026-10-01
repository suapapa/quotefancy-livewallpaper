#!/usr/bin/env bash
# QuoteFancy Live Wallpaper — launchd 등록 스크립트 (Phase 2)
# 정해진 시간마다 배경화면을 무작위로 변경하는 launchd 에이전트를 설치한다.
#
# 사용법:
#   ./install.sh              # 기본 주기 (config.yaml의 change_interval_seconds)
#   ./install.sh 600          # 600초(=10분) 주기로 재정의
set -euo pipefail

# 이 스크립트가 있는 디렉터리 = 프로젝트 루트
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LABEL="com.quotefancy.livewallpaper"
PLIST_PATH="$HOME/Library/LaunchAgents/${LABEL}.plist"

# macOS 확인
if [[ "$(uname -s)" != "Darwin" ]]; then
  echo "이 스크립트는 macOS에서만 실행해야 합니다." >&2
  exit 1
fi

# uv 경로 탐색
UV_BIN="$(command -v uv || true)"
if [[ -z "$UV_BIN" ]]; then
  echo "uv를 찾을 수 없습니다. 먼저 설치하세요 (예: brew install uv)." >&2
  exit 1
fi

# 변경 주기 결정
INTERVAL="${1:-}"
if [[ -z "$INTERVAL" ]]; then
  # config.yaml에서 change_interval_seconds 추출 (없으면 1800)
  INTERVAL=$("$UV_BIN" run --project "$SCRIPT_DIR" python -c 'import sys, yaml; print(yaml.safe_load(open(sys.argv[1])).get("change_interval_seconds", 1800))' "${SCRIPT_DIR}/config.yaml")
fi

mkdir -p "$HOME/Library/LaunchAgents"

cat > "$PLIST_PATH" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>${LABEL}</string>
    <key>ProgramArguments</key>
    <array>
        <string>${UV_BIN}</string>
        <string>run</string>
        <string>--project</string>
        <string>${SCRIPT_DIR}</string>
        <string>${SCRIPT_DIR}/change_wallpaper.py</string>
        <string>--config</string>
        <string>${SCRIPT_DIR}/config.yaml</string>
    </array>
    <key>WorkingDirectory</key>
    <string>${SCRIPT_DIR}</string>
    <key>StartInterval</key>
    <integer>${INTERVAL}</integer>
    <key>RunAtLoad</key>
    <true/>
    <key>StandardOutPath</key>
    <string>${SCRIPT_DIR}/logs/launchd.out.log</string>
    <key>StandardErrorPath</key>
    <string>${SCRIPT_DIR}/logs/launchd.err.log</string>
</dict>
</plist>
EOF

mkdir -p "${SCRIPT_DIR}/logs"

# 기존 에이전트가 있으면 내리고 다시 올림
launchctl unload "$PLIST_PATH" 2>/dev/null || true
launchctl load "$PLIST_PATH"

echo "✓ 등록 완료 (라벨: ${LABEL})"
echo "  변경 주기: ${INTERVAL}초"
echo "  plist: ${PLIST_PATH}"
echo "  로그: ${SCRIPT_DIR}/logs/launchd.{out,err}.log"
