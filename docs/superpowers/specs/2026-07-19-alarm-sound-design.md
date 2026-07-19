# 알림 사운드 재생 기능 설계

날짜: 2026-07-19

## 목표

타이머 알림(토스트)이 발생할 때 사운드를 함께 재생한다. 환경설정에서 사운드
사용 여부(기본 체크)와 알림 사운드를 선택할 수 있다.

## 설정 값 (src/config.py DEFAULTS 추가)

| 키 | 기본값 | 설명 |
|----|--------|------|
| `sound_on` | `1` | 사운드 사용 여부 |
| `sound` | `"default"` | `default`(기본 알림음) \| `asterisk`(별표) \| `exclamation`(느낌표) \| `hand`(경고) \| `custom`(사용자 파일) |
| `sound_file` | `""` | `sound == "custom"`일 때 재생할 WAV 파일 경로 |

기존 레지스트리 load/save 로직(`load_cfg`/`save_cfg`)이 DEFAULTS 기반으로
동작하므로 키 추가만으로 저장/복원이 함께 처리된다.

## 재생 모듈 (신규 src/sound.py)

- `play(cfg)` 함수 하나.
  - `sound_on`이 꺼져 있으면 아무것도 하지 않음.
  - 시스템 사운드: `winsound.PlaySound(별칭, SND_ALIAS | SND_ASYNC)`
    - default → `SystemDefault`, asterisk → `SystemAsterisk`,
      exclamation → `SystemExclamation`, hand → `SystemHand`
  - 사용자 파일: `winsound.PlaySound(경로, SND_FILENAME | SND_ASYNC)`
    - 파일이 없거나 재생 실패 시 기본 알림음(`SystemDefault`)으로 대체.
- 표준 라이브러리(winsound)만 사용. WAV만 지원하므로 파일 선택 필터는 `*.wav`.

## 재생 시점 (src/ui/toast.py)

- `fire()` 시작부에서 `sound.play(cfg)`를 1회 호출.
- "모든 모니터" 모드로 토스트가 여러 개 생성되어도 사운드는 1번만 재생.
- 설정창의 "테스트 알림"도 `fire()`를 거치므로 동일하게 재생됨.

## 설정 UI (src/ui/settings.py "알림 사운드" 섹션 추가)

- "사운드 사용" 체크박스(기본 체크). 해제 시 사운드 선택 라디오/찾아보기
  버튼 비활성화.
- 라디오 5개: 기본 알림음 / 별표 / 느낌표 / 경고 / 사용자 파일
- "사용자 파일" 선택 시 사용할 "찾아보기…" 버튼과 선택된 파일명 라벨.
- 라디오 선택 변경 시 해당 사운드를 즉시 1회 재생(미리듣기).
- 기존 패턴대로 `_instant()`로 즉시 반영, 저장/취소 동작 동일.

## 검증

- `python -m py_compile`로 전체 소스 컴파일 확인.
- 앱 실행 후 테스트 알림으로 사운드 재생 확인(수동).
