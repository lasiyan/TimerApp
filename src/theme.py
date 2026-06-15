"""테마 색상 - apply_theme() 호출 후 module attribute 사용

main.py에서 cfg 로드 → apply_theme() 호출 → UI 모듈 import 순서 준수.
"""

import winreg

_THEMES = {
    "dark": {
        "BG": "#282c34",
        "CARD": "#2c313c",
        "ACCENT": "#e5c07b",
        "ACCENT2": "#e06c75",
        "TITLE": "#f5f7ff",
        "TEXT": "#e4e8f2",
        "SUBTEXT": "#adb4c4",
        "SUCCESS": "#98c379",
        "BORDER": "#3e4451",
        "SLIDER": "#5c6370",
        "TOAST_BG": "#2c313c",
    },
    "light": {
        "BG": "#f0f0f5",
        "CARD": "#ffffff",
        "ACCENT": "#6c5ce7",
        "ACCENT2": "#d63384",
        "TITLE": "#0d0d1a",
        "TEXT": "#1e1e2e",
        "SUBTEXT": "#6b7280",
        "SUCCESS": "#059669",
        "BORDER": "#dde1ec",
        "SLIDER": "#8890a4",
        "TOAST_BG": "#ffffff",
    },
}


def _sys_theme():
    try:
        with winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize",
        ) as k:
            val, _ = winreg.QueryValueEx(k, "AppsUseLightTheme")
            return "light" if val else "dark"
    except Exception:
        return "dark"


def apply_theme(name):
    """모듈 globals에 색상 변수를 설정한다."""
    global BG, CARD, ACCENT, ACCENT2, TITLE, TEXT, SUBTEXT, SUCCESS
    global BORDER, SLIDER, TOAST_BG, TIMER_COLORS
    t = _sys_theme() if name == "system" else name
    c = _THEMES.get(t, _THEMES["dark"])
    BG = c["BG"]
    CARD = c["CARD"]
    ACCENT = c["ACCENT"]
    ACCENT2 = c["ACCENT2"]
    TITLE = c["TITLE"]
    TEXT = c["TEXT"]
    SUBTEXT = c["SUBTEXT"]
    SUCCESS = c["SUCCESS"]
    BORDER = c["BORDER"]
    SLIDER = c["SLIDER"]
    TOAST_BG = c["TOAST_BG"]
    TIMER_COLORS = [ACCENT, ACCENT2, SUCCESS, "#f7a76a", "#6ab4f7"]


# 기본값(다크)으로 초기화 - import 순서 사고 방지용
apply_theme("dark")
