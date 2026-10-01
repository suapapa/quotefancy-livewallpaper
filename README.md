# QuoteFancy Live Wallpaper

선택한 guru들의 명언 배경화면을 정해진 시간마다 무작위로 바꿔주는 **macOS용** 프로그램입니다.

명언 이미지는 [QuoteFancy](https://quotefancy.com)에서 4K(3840×2160) 원본으로 다운로드합니다.

## 동작 방식

```
scrape.py   →  wallpapers/<guru>/<id>.jpg  (4K 이미지 일괄 다운로드)
change_wallpaper.py →  무작위 1장 선택 → macOS 배경화면 변경
install.sh  →  launchd 에이전트 등록 → 정해진 시간마다 자동 변경
```

## 설치 & 사용법 (macOS)

### 1. 저장소 클론

```bash
git clone https://github.com/suapapa/quotefancy-livewallpaper.git
cd quotefancy-livewallpaper
```

### 2. 명언 이미지 다운로드

```bash
python3 scrape.py
```

기본 guru는 `config.json` 의 `gurus` 에 정의되어 있습니다. 원하는 guru를 추가/변경할 수 있습니다.

```bash
# 특정 guru만 다운로드
python3 scrape.py --guru bruce-lee-quotes

# 테스트용 (guru당 5장만)
python3 scrape.py --limit 5
```

### 3. 배경화면 수동 변경 테스트

```bash
python3 change_wallpaper.py                # 전체에서 무작위 선택
python3 change_wallpaper.py --guru jocko-willink-quotes
python3 change_wallpaper.py --list         # 이미지 수 확인
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
| `gurus` | 다운로드할 guru slug 목록 | `["bruce-lee-quotes", "jocko-willink-quotes"]` |
| `resolution` | 이미지 해상도 (`original` = 4K) | `original` |
| `wallpaper_dir` | 이미지 저장 디렉터리 | `wallpapers` |
| `log_dir` | 로그 디렉터리 | `logs` |
| `change_interval_seconds` | 배경화면 변경 주기 | `1800` (30분) |
| `request_delay_seconds` | 다운로드 간 지연 (서버 예의) | `1.5` |

## guru 추가 방법

QuoteFancy의 URL 슬러그를 `config.json` 의 `gurus` 에 추가하면 됩니다.

예) `https://quotefancy.com/jim-rohn-quotes` → `"jim-rohn-quotes"` 추가

## 저작권 주의

QuoteFancy 명언 이미지의 저작권은 원 저작자/사이트에 있습니다. **개인적 용도로만** 사용하고, 이미지를 재배포하거나 상업적으로 이용하지 마세요. 다운로드한 이미지는 `.gitignore` 로 git 저장소에서 제외됩니다.

## 디렉터리 구조

```
quotefancy-livewallpaper/
├── README.md
├── PLAN.md                 # 사이트 구조 분석 + 작업 계획
├── config.json             # guru/주기/경로 설정
├── scrape.py               # Phase 0: 4K 이미지 다운로더
├── change_wallpaper.py     # Phase 1: 무작위 선택 + 배경화면 적용
├── install.sh              # Phase 2: launchd 등록
├── uninstall.sh            # Phase 2: launchd 해제
├── wallpapers/             # 다운로드한 이미지 (git 제외)
└── logs/                   # 로그 (git 제외)
```
