# 알림 사운드 재생 기능 설계

날짜: 2026-07-19 (v1.1 반영 개정)

## 목표

타이머 알림(토스트)이 발생할 때 사운드를 함께 재생한다. 환경설정의
드롭다운에서 알림 사운드를 선택한다: 사용 안 함 / 사용자 지정(WAV·MP3) /
내장 차임 / 시스템 사운드 목록.

## 설정 값 (src/config.py DEFAULTS)

| 키 | 기본값 | 설명 |
|----|--------|------|
| `sound` | `"builtin"` | `off`(사용 안 함) \| `custom`(사용자 지정) \| `builtin`(내장 차임) \| 시스템 사운드 이벤트명(예: `.Default`, `SystemAsterisk`) |
| `sound_file` | `""` | `sound == "custom"`일 때 재생할 파일 경로 (WAV/MP3) |
| `volume` | `100` | 사운드 볼륨 (0~100%) |

기존 레지스트리 load/save 로직(`load_cfg`/`save_cfg`)이 DEFAULTS 기반으로
동작하므로 키 추가만으로 저장/복원이 함께 처리된다.

## 재생 모듈 (src/sound.py)

- `play(cfg)`: 설정에 따라 비동기 재생.
  - `off` → 재생 안 함
  - `builtin` → `res/alarm.wav` (경로는 `fonts._base()` 기준, EXE 빌드 시
    `_MEIPASS` 자동 처리)
  - `custom` → 사용자 파일. WAV는 `winsound.PlaySound(SND_FILENAME|SND_ASYNC)`,
    MP3 등 그 외 확장자는 MCI(`winmm.mciSendStringW`)로 재생
  - 그 외 값 → 시스템 사운드 이벤트 별칭으로
    `winsound.PlaySound(SND_ALIAS|SND_ASYNC)`
  - 파일 재생 실패/파일 없음 시 기본 알림음(`.Default`)으로 대체
  - 볼륨: 재생 직전 `waveOutSetVolume`으로 앱 세션 볼륨(0~100%)을 설정
    (winsound/MCI 공통 적용), MP3는 MCI `setaudio volume`도 병행
- `list_system_sounds()`: 서로 다른 소리를 내는 대표 시스템 사운드 10종
  (기본 경고음/중대 경고/일반 알림/미리 알림/메시지/새 메일/알람 1~3/전화 벨)
  큐레이션 목록 중, 레지스트리에 사운드가 실제 지정된 이벤트만
  (이벤트명, 한글 표시명)으로 반환.
- 표준 라이브러리(winsound/winreg/ctypes)만 사용, 추가 의존성 없음.

## 내장 사운드 (res/alarm.wav)

벨 음색(기음+배음+미세 디튠)의 3음 상승 아르페지오(A5→C#6→E6, 약 2초)를
합성한 WAV. 시스템 알림음보다 덜 단조로운 기본 알림용. `build.bat`의
`--add-data`로 EXE에 포함.

## 재생 시점 (src/ui/toast.py)

- `fire()` 시작부에서 `sound.play(cfg)`를 1회 호출.
- "모든 모니터" 모드로 토스트가 여러 개 생성되어도 사운드는 1번만 재생.
- 설정창의 "테스트 알림"도 `fire()`를 거치므로 동일하게 재생됨.

## 설정 UI (src/ui/settings.py "사운드 설정" 섹션)

두 항목으로 구성: ① 알림 사운드(드롭다운), ② 사운드 볼륨(슬라이더 0~100%).
볼륨 조절 후 300ms 디바운스로 미리듣기 1회 재생.

- 드롭다운(tk.OptionMenu) 항목 순서:
  1. 사용 안 함
  2. 사용자 지정
  3. 내장 알림음 ← 기본값
  4. 이후 대표 시스템 사운드 10종 (기본 경고음부터)
- "사용자 지정" 선택용 "찾아보기…" 버튼(custom일 때만 활성)과 선택 파일명
  라벨. 파일 필터: WAV/MP3.
- 사용자 지정을 선택했는데 파일이 없으면 즉시 파일 대화상자를 연다.
- 선택 변경 시 해당 사운드를 즉시 1회 재생(미리듣기).
- 기존 패턴대로 `_instant()`로 즉시 반영, 저장/취소 동작 동일.

## 기타

- `fonts._base()`가 개발 모드에서 프로젝트 루트의 상위 폴더를 반환하던
  버그 수정(내장 사운드/폰트 경로가 이 함수에 의존).
- 버전 1.1.0.0으로 업 (version_info.txt).

## 검증

- `python -m py_compile`로 전체 소스 컴파일 확인.
- `play()` 각 경로(off/builtin/custom-wav/custom-mp3/시스템/폴백) 스모크 테스트.
- SettingsWin 생성 + 드롭다운 선택/찾아보기 상태 전환 테스트.
- 앱 실행 후 테스트 알림으로 사운드 재생 확인(수동).
