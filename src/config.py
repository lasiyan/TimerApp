"""설정 - DEFAULTS + 레지스트리 기반 load/save"""

import json
import winreg

DEFAULTS = {
    "position": "bottom_right",  # bottom_right | bottom_left | center
    "width_pct": 15,
    "height_pct": 10,
    "opacity": 100,
    "offset_pct": 1,
    "monitor": "app",  # app | mouse | all
    "duration": 3,
    "win_w": 640,
    "win_h": 220,
    "theme": "system",  # dark | light | system
    "tray_on_close": 0,
    "sound": "builtin",  # off | custom | builtin | 시스템 사운드 이벤트명
    "sound_file": "",
    "volume": 100,
}

_REG_KEY = r"Software\TimerApp"


def load_cfg():
    s = dict(DEFAULTS)
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, _REG_KEY) as k:
            for key, default in DEFAULTS.items():
                try:
                    val, _ = winreg.QueryValueEx(k, key)
                    s[key] = type(default)(val)
                except FileNotFoundError:
                    pass
    except FileNotFoundError:
        pass
    return s


def save_cfg(s):
    try:
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, _REG_KEY) as k:
            for key, val in s.items():
                if isinstance(val, int):
                    winreg.SetValueEx(k, key, 0, winreg.REG_DWORD, val)
                else:
                    winreg.SetValueEx(k, key, 0, winreg.REG_SZ, str(val))
    except Exception:
        pass


def load_cards():
    """저장된 카드 목록 반환. 없으면 None."""
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, _REG_KEY) as k:
            val, _ = winreg.QueryValueEx(k, "cards")
            return json.loads(val)
    except Exception:
        return None


def save_cards(cards_data):
    try:
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, _REG_KEY) as k:
            winreg.SetValueEx(
                k, "cards", 0, winreg.REG_SZ, json.dumps(cards_data, ensure_ascii=False)
            )
    except Exception:
        pass
