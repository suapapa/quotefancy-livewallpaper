# QuoteFancy Live Wallpaper

선택한 guru들의 명언 배경화면을 정해진 시간마다 무작위로 바꿔주는 **macOS용** 프로그램입니다.

명언 이미지는 [QuoteFancy](https://quotefancy.com)에서 4K(3840×2160) 원본으로 제공됩니다.

## 동작 방식 (on-demand)

- **인덱스 생성** — 명언 id 목록만 가볍게 수집 (이미지 다운로드 없음, ~13초)
- **배경화면 변경 시 1장만 다운로드** — 필요한 그 이미지만 받아서 로컬 캐시에 저장
- **캐시 재사용** — 이미 받은 이미지는 다시 다운로드하지 않음
- **캐시 정리** — guru당 일정 개수 초과 시 오래된 것부터 삭제

이렇게 하면 처음에 수백 장을 한꺼번에 받을 필요가 없어 시간도 절약되고,
서버에 과도한 요청(abusing)으로 차단당할 위험도 없습니다.

```
build_index.py      →  quotes_index.json  (명언 id 목록, 수 초)
change_wallpaper.py →  무작위 1장 선택 → 없으면 1장만 다운로드 → macOS 배경화면 변경
install.sh          →  launchd 에이전트 등록 → 정해진 시간마다 자동 변경
```

## 설치 & 사용법 (macOS)

### 1. 저장소 클론

```bash
git clone https://github.com/suapapa/quotefancy-livewallpaper.git
cd quotefancy-livewallpaper
```

### 2. 명언 인덱스 생성 (이미지 없음)

```bash
python3 build_index.py
```

기본 guru는 `config.json` 의 `gurus` 에 정의되어 있습니다. 원하는 guru를 추가/변경할 수 있습니다.

```bash
# 특정 guru만 인덱스 생성
python3 build_index.py --guru bruce-lee-quotes
```

### 3. 배경화면 변경 테스트 (필요한 1장만 다운로드)

```bash
python3 change_wallpaper.py            # 무작위 1장 (인덱스 없으면 자동 생성)
python3 change_wallpaper.py --guru jocko-willink-quotes
python3 change_wallpaper.py --list     # 인덱스에 있는 명언 수 확인
python3 change_wallpaper.py --build-index   # 인덱스만 갱신
```

> ⚠️ 최초 실행 시 macOS가 "자동화 권한"을 요청할 수 있습니다. 허용해 주세요.

### 4. 자동 변경 스케줄 등록 (launchd)

```bash
./install.sh              # config.json 의 change_interval_seconds 기준 (기본 1800초 = 30분)
./install.sh 600          # 600초(=10분) 주기로 재정의
```

해제:

```bash
./uninstall.sh
```

로그: `logs/wallpaper.log` (어떤 명언이 언제 적용됐는지), `logs/launchd.{out,err}.log` (실행 로그)

## 설정 (config.json)

| 키 | 의미 | 기본값 |
|----|------|--------|
| `gurus` | 사용할 guru slug 목록 | `["bruce-lee-quotes", "jocko-willink-quotes"]` |
| `wallpaper_dir` | 이미지 캐시 디렉터리 | `wallpapers` |
| `index_file` | 명언 id 인덱스 파일 | `quotes_index.json` |
| `log_dir` | 로그 디렉터리 | `logs` |
| `change_interval_seconds` | 배경화면 변경 주기 | `1800` (30분) |
| `max_cache_per_guru` | guru당 캐시 최대 개수 (초과 시 오래된 것 삭제, 0=무제한) | `40` |
| `request_delay_seconds` | 인덱스 수집 페이지 간 지연 (서버 예의) | `1.0` |

## guru 추가 방법

QuoteFancy의 URL 슬러그를 `config.json` 의 `gurus` 에 추가하면 됩니다.

예) `https://quotefancy.com/jim-rohn-quotes` → `"jim-rohn-quotes"` 추가

## 저작권 주의

QuoteFancy 명언 이미지의 저작권은 원 저작자/사이트에 있습니다. **개인적 용도로만** 사용하고, 이미지를 재배포하거나 상업적으로 이용하지 마세요. 다운로드한 이미지와 인덱스는 `.gitignore` 로 git 저장소에서 제외됩니다.

## 디렉터리 구조

```
quotefancy-livewallpaper/
├── README.md
├── PLAN.md                 # 사이트 구조 분석 + 작업 계획
├── config.json             # guru/주기/경로 설정
├── build_index.py          # 명언 id 인덱스 생성 (이미지 없음)
├── change_wallpaper.py     # 무작위 선택 + on-demand 다운로드 + 배경화면 적용
├── install.sh              # launchd 등록
├── uninstall.sh            # launchd 해제
├── quotes_index.json       # 명언 id 인덱스 (git 제외, 재생성 가능)
├── wallpapers/             # 다운로드한 이미지 캐시 (git 제외)
└── logs/                   # 로그 (git 제외)
```
