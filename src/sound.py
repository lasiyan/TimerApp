"""알림 사운드 재생 - winsound/MCI 기반 + 시스템 사운드 목록"""

import ctypes
import os
import winreg
import winsound

from src.fonts import _base

_SCHEMES = r"AppEvents\Schemes\Apps\.Default"

BUILTIN_LABEL = "내장 알림음"

# 서로 다른 소리를 내는 대표 시스템 사운드 10종
_SYSTEM_SOUNDS = [
    (".Default", "기본 경고음"),
    ("SystemHand", "중대 경고"),
    ("Notification.Default", "일반 알림"),
    ("Notification.Reminder", "미리 알림"),
    ("Notification.IM", "메시지"),
    ("MailBeep", "새 메일"),
    ("Notification.Looping.Alarm", "알람 1"),
    ("Notification.Looping.Alarm2", "알람 2"),
    ("Notification.Looping.Alarm3", "알람 3"),
    ("Notification.Looping.Call", "전화 벨"),
]

_mci = ctypes.windll.winmm.mciSendStringW


def builtin_path():
    return os.path.join(_base(), "res", "alarm.wav")


def list_system_sounds():
    """(이벤트명, 표시명) 목록. 대표 10종 중 사운드가 지정된 이벤트만."""
    items = []
    for ev, lbl in _SYSTEM_SOUNDS:
        try:
            key = _SCHEMES + "\\" + ev + r"\.Current"
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key) as k:
                snd, _ = winreg.QueryValueEx(k, "")
            if snd:
                items.append((ev, lbl))
        except OSError:
            continue
    return items or [(".Default", "기본 경고음")]


def _set_volume(pct):
    """앱 세션 볼륨(0~100%) 설정 - winsound/MCI 재생에 공통 적용."""
    lvl = int(max(0, min(100, pct)) * 0xFFFF / 100)
    try:
        ctypes.windll.winmm.waveOutSetVolume(0, (lvl << 16) | lvl)
    except Exception:
        pass


def _play_file(path, vol):
    """WAV는 winsound, 그 외(MP3 등)는 MCI로 비동기 재생. 성공 여부 반환."""
    if path.lower().endswith(".wav"):
        try:
            winsound.PlaySound(path, winsound.SND_FILENAME | winsound.SND_ASYNC)
            return True
        except RuntimeError:
            return False
    _mci("close timerapp_snd", None, 0, None)
    if _mci(f'open "{path}" alias timerapp_snd', None, 0, None):
        return False
    _mci(f"setaudio timerapp_snd volume to {int(max(0, min(100, vol)) * 10)}", None, 0, None)
    _mci("play timerapp_snd from 0", None, 0, None)
    return True


def play(cfg):
    """설정에 따라 알림 사운드를 비동기 재생. 파일 실패 시 기본음 대체."""
    snd = cfg.get("sound", "builtin")
    if snd == "off":
        return
    vol = cfg.get("volume", 100)
    _set_volume(vol)
    if snd == "builtin":
        if _play_file(builtin_path(), vol):
            return
        snd = ".Default"
    elif snd == "custom":
        path = cfg.get("sound_file", "")
        if path and os.path.exists(path) and _play_file(path, vol):
            return
        snd = ".Default"
    try:
        winsound.PlaySound(snd, winsound.SND_ALIAS | winsound.SND_ASYNC)
    except RuntimeError:
        pass
