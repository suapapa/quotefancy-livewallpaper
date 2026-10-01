# QuoteFancy 맥북 라이브 배경화면 프로젝트

> 무작위 명언 바탕화면을 정해진 시간마다 자동으로 바꿔주는 macOS용 프로그램

---

## 1. 목표 (Goal)

선택한 guru들의 명언 배경화면을 정해진 시간 간격으로 무작위 변경하는 맥북용 프로그램.

**대상 guru 예시:**
- bruce-lee-quotes
- jocko-willink-quotes
- (추후 확장 가능)

---

## 2. 사이트 구조 분석 결과 (QuoteFancy)

### 2.1 URL 패턴

| 항목 | 패턴 | 예시 |
|------|------|------|
| guru 목록 페이지 | `https://quotefancy.com/{slug}-quotes` | `.../bruce-lee-quotes` |
| 페이지네이션 | `{guru-url}/page/{N}` | `.../bruce-lee-quotes/page/3` |
| 썸네일 | `/media/wallpaper/thumb/{id}-{slug}.jpg` |  |
| 중간 해상도 800x450 | `/media/wallpaper/800x450/{id}-{slug}.jpg` |  |
| 중간 해상도 1600x900 | `/media/wallpaper/1600x900/{id}-{slug}.jpg` |  |
| **원본(4K)** | `/download/{id}/original/wallpaper.jpg` | `.../download/1697/original/wallpaper.jpg` |

### 2.2 이미지 해상도

- 원본(original) = **3840 × 2160 (4K)** ← 맥북 레티나/외장 4K에 최적
- 1600x900 = 표준 FHD 와이드
- 800x450 = 썸네일급

### 2.3 명언 데이터 포인트

- 각 명언은 고유 `id` 보유 (예: 1697, 2171, 17251)
- 이미지 파일명 = `{id}-{Author}-Quote-{슬러그화된명언}.jpg`
- 페이지당 이미지 표시 수: **약 52개**
- 확인된 규모:
  - **Bruce Lee**: 400개 명언 / 9페이지
  - **Jocko Willink**: 120개 명언 / 3페이지

### 2.4 HTML 파싱 포인트

- 명언 이미지 URL은 `<img>` 태그의 `src`(800x450) 및 `srcset`(1600x900)에서 추출
- 원본 이미지는 `href="/download/{id}/original/wallpaper.jpg"` 패턴으로 파생 가능
- 전체 명언 수는 `<title>`의 "Top {N} ... Quotes" 에서 파악 가능

---

## 3. 작업 계획 (Plan)

### Phase 0 — 스캐퍼 (quotefancy_scraper) ✅ 완료
`scrape.py` 스크립트로 모든 명언의 원본(4K) 이미지를 다운로드

- [x] guru slug 목록 입력 (config)
- [x] 각 guru의 전체 페이지네이션 순회
- [x] 모든 명언의 `{id}` 수집
- [x] 원본 4K 이미지 일괄 다운로드 → `wallpapers/{guru-slug}/{id}.jpg`
- [x] 이미 다운로드한 id는 건너뛰기 (재실행 대비 incremental)
- [x] 예의: 요청 간 지연(rate limiting), User-Agent 설정

### Phase 1 — 무작위 선택 + 배경화면 적용 ✅ 완료
`change_wallpaper.py`

- [x] `wallpapers/` 디렉터리에서 무작위 이미지 1장 선택
- [x] macOS 배경화면 변경:
  - `osascript -e 'tell application "System Events" to set picture of every desktop to POSIX file "<path>"'`
- [x] 멀티 모니터 대응: `every desktop` → 모든 디스플레이에 적용
- [x] 적용 이력 로그 (`logs/wallpaper.log`)

### Phase 2 — 스케줄링 (자동 주기 변경) ✅ 완료
- [x] `launchd` plist 생성 (`install.sh`)
  - `~/Library/LaunchAgents/com.quotefancy.livewallpaper.plist`
  - `StartInterval`로 변경 주기 지정 (config.json `change_interval_seconds`, 기본 1800초)
  - `RunAtLoad` = 최초 1회 즉시 실행
- [x] 해제 스크립트 (`uninstall.sh`)

### Phase 3 — 설정 파일 ✅ 완료
`config.json`
- [x] guru slug 리스트
- [x] 변경 주기 (`change_interval_seconds`)
- [x] 이미지 저장 경로 (`wallpaper_dir`)
- [x] 로그 경로 (`log_dir`)
- [x] 요청 지연 (`request_delay_seconds`)

### Phase 4 — 패키징 & 문서 ✅ 완료
- [x] README.md (설치/사용법)
- [x] launchd 등록/해제 스크립트 (`install.sh` / `uninstall.sh`)
- [x] 로그 남기기 (`logs/wallpaper.log`)

---

## 7. 구현 결과 요약 (검증 완료)

- **다운로드**: Bruce Lee 412장 + Jocko Willink 124장 = **총 536장** (전부 4K 3840×2160 확인)
- **incremental 재실행**: 이미 다운로드한 id는 전부 스킵 (재다운로드 0)
- **무작위 선택**: 전체 536장에서 무작위 선택 정상 동작
- **launchd**: plist 문법 검증 완료 (macOS에서 `install.sh` 실행 시 적용)
- **참고**: Bruce Lee 제목의 "Top 400"은 표기일 뿐 실제 수집 412장, Jocko 제목 "Top 120" → 실제 124장

## 8. macOS에서 실제 사용 방법

```bash
git clone https://github.com/suapapa/quotefancy-livewallpaper.git
cd quotefancy-livewallpaper
python3 scrape.py          # 명언 이미지 다운로드
./install.sh               # 30분마다 자동 변경 (주기 변경: ./install.sh 600)
```

배경화면을 즉시 바꿔보려면: `python3 change_wallpaper.py`

---

## 4. 디렉터리 구조 (제안)

```
ws/quotefancy-livewallpaper/
├── README.md
├── PLAN.md                 # 이 문서
├── config.json             # guru/주기 설정
├── scrape.py               # 명언 4K 이미지 다운로더
├── change_wallpaper.py     # 무작위 선택 + 배경화면 적용
├── install.sh              # launchd 등록
├── uninstall.sh            # launchd 해제
├── wallpapers/
│   ├── bruce-lee-quotes/
│   │   └── 1697.jpg
│   └── jocko-willink-quotes/
│       └── ...
└── logs/
    └── wallpaper.log
```

---

## 5. 주의사항 / 리스크

- ⚠️ **저작권**: QuoteFancy 이미지는 개인적 사용 목적으로만. 재배포 금지.
- ⚠️ **Rate limiting**: 400+ 이미지 일괄 다운로드 시 서버 부하 방지를 위해 지연 필수.
- ⚠️ 원본(original)은 4K라 파일 용량 큼 (평균 ~700KB/장). 400장 ≈ 280MB 수준.
- ⚠️ macOS 배경화면 변경은 `osascript` 권한(자동화 권한) 필요할 수 있음 — 최초 실행 시 허용 팝업.
- ⚠️ "jocko-willink-qoutes"는 오타로 추정 — 실제 slug는 `jocko-willink-quotes`.

---

## 6. 다음 단계

1. `scrape.py` 작성 및 Bruce Lee 400장 테스트 다운로드
2. `change_wallpaper.py` 작성
3. launchd 스케줄링 구성
4. 사용자 Mac에서 설치 테스트
