"""MM:SS 시간 입력 헬퍼"""


def parse_mmss(s):
    """MM:SS 또는 숫자(분) 문자열 -> 총 초(int). 파싱 실패 시 0."""
    s = str(s).strip()
    if ":" in s:
        parts = s.split(":", 1)
        try:
            return max(0, int(parts[0])) * 60 + max(0, int(parts[1]))
        except ValueError:
            return 0
    try:
        return int(float(s) * 60)
    except ValueError:
        return 0


def secs_hint(total):
    """초 -> '= 1분 30초' 형태 힌트"""
    total = int(total)
    if total <= 0:
        return ""
    m, s = divmod(total, 60)
    if m and s:
        return f"= {m}분 {s}초"
    if m:
        return f"= {m}분"
    return f"= {s}초"


def compat_mmss(v, default):
    """구버전 소수(분) 형식 -> MM:SS 변환"""
    v = str(v)
    if ":" in v:
        return v
    try:
        total = int(float(v) * 60)
        return f"{total // 60:02d}:{total % 60:02d}"
    except Exception:
        return default
