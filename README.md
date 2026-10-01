# QuoteFancy Live Wallpaper

선택한 guru의 명언으로 **macOS 배경화면**을 일정 시간마다 바꿉니다.

명언 이미지는 [QuoteFancy](https://quotefancy.com)에서 4K(3840×2160) 원본으로 제공됩니다.

## 동작 방식

- 명언 ID 목록만 수집합니다. 이미지는 이때 받지 않습니다(약 13초).
- 배경화면을 바꿀 때 필요한 이미지 한 장만 받아 캐시에 저장합니다.
- 받은 이미지는 다시 다운로드하지 않고, guru별 캐시가 설정한 개수를 넘으면 오래된 이미지부터 지웁니다.

처음부터 수백 장을 받지 않아도 되므로 시간이 덜 걸리고, 과도한 요청으로 차단당할 위험도 없습니다.

```
build_index.py      →  quotes_index.json  (명언 id 목록, 수 초)
change_wallpaper.py →  무작위 1장 선택 → 없으면 1장만 다운로드 → macOS 배경화면 변경
install.sh          →  launchd 에이전트 등록 → 정해진 시간마다 자동 변경
```

## 설치 및 사용법 (macOS)

### 1. 설치

```bash
git clone https://github.com/suapapa/quotefancy-livewallpaper.git
cd quotefancy-livewallpaper
brew install uv
```

### 2. 명언 인덱스 생성

```bash
uv run build_index.py
```

기본 guru는 `config.yaml`의 `gurus`에 적혀 있습니다. 원하는 guru로 바꿔 쓰면 됩니다.

```bash
# 특정 guru만 인덱스 생성
uv run build_index.py --guru bruce-lee-quotes
```

### 3. 배경화면 바꿔보기

```bash
uv run change_wallpaper.py                # 무작위 1장 (인덱스 없으면 자동 생성)
uv run change_wallpaper.py --guru jocko-willink-quotes
uv run change_wallpaper.py --list         # 인덱스에 있는 명언 수 확인
uv run change_wallpaper.py --build-index  # 인덱스만 갱신
```

> 처음 실행할 때 macOS가 "자동화 권한"을 요청할 수 있습니다. 배경화면을 바꾸려면 허용해 주세요.

### 4. 자동 변경 등록 (launchd)

```bash
./install.sh              # config.yaml의 change_interval_seconds 기준 (기본 1800초 = 30분)
./install.sh 600          # 600초(10분) 주기로 변경
```

자동 변경을 끄려면:

```bash
./uninstall.sh
```

적용 내역은 `logs/wallpaper.log`, 실행 로그는 `logs/launchd.{out,err}.log`에서 볼 수 있습니다.

## 설정 (config.yaml)

| 키 | 의미 | 기본값 |
|----|------|--------|
| `gurus` | 사용할 guru 슬러그 목록 | `bruce-lee-quotes`, `jocko-willink-quotes` |
| `wallpaper_dir` | 이미지 캐시 디렉터리 | `wallpapers` |
| `index_file` | 명언 ID 인덱스 파일 | `quotes_index.json` |
| `log_dir` | 로그 디렉터리 | `logs` |
| `change_interval_seconds` | 배경화면 변경 주기 | `1800` (30분) |
| `max_cache_per_guru` | guru당 캐시 최대 개수 (초과 시 오래된 것 삭제, 0=무제한) | `40` |
| `request_delay_seconds` | 인덱스 수집 요청 간 대기 시간 | `1.0`초 |
| `user_agent` | QuoteFancy 요청에 사용할 User-Agent | `config.yaml` 참조 |

## guru 추가 방법

QuoteFancy URL의 슬러그를 `config.yaml`의 `gurus`에 추가하세요.

예) `https://quotefancy.com/jim-rohn-quotes` → `- jim-rohn-quotes` 추가

## 저작권 주의

QuoteFancy 명언 이미지의 저작권은 원 저작자/사이트에 있습니다. **개인적 용도로만** 사용하고 이미지를 재배포하거나 상업적으로 이용하지 마세요. 다운로드한 이미지와 인덱스는 `.gitignore`에 따라 Git에 올라가지 않습니다.

## 디렉터리 구조

```
quotefancy-livewallpaper/
├── README.md
├── PLAN.md                 # 사이트 구조 분석 + 작업 계획
├── config.yaml             # guru/주기/경로 설정
├── pyproject.toml          # Python 의존성
├── uv.lock                 # 잠긴 의존성 버전
├── build_index.py          # 명언 ID 인덱스 생성 (이미지 없음)
├── change_wallpaper.py     # 무작위 선택 + on-demand 다운로드 + 배경화면 적용
├── install.sh              # launchd 등록
├── uninstall.sh            # launchd 해제
├── quotes_index.json       # 명언 ID 인덱스 (Git 제외, 재생성 가능)
├── wallpapers/             # 다운로드한 이미지 캐시 (git 제외)
└── logs/                   # 로그 (git 제외)
```
