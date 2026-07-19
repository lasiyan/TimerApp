"""Pretendard 폰트 로딩 (없으면 Consolas) + 폰트 튜플 정의"""

import ctypes
import os
import sys

_font_buffers = []  # GC 방지


def _base():
    if getattr(sys, "frozen", False):
        return getattr(sys, "_MEIPASS", os.path.dirname(sys.executable))
    return os.path.abspath(os.path.join(__file__, "..", ".."))


def _load_pretendard():
    try:
        gdi32 = ctypes.windll.gdi32
        path = os.path.join(_base(), "res", "Pretendard-Regular.ttf")
        if not os.path.exists(path):
            return False
        data = open(path, "rb").read()
        buf = ctypes.create_string_buffer(data)
        _font_buffers.append(buf)
        n = ctypes.c_uint32(0)
        return bool(gdi32.AddFontMemResourceEx(buf, len(data), None, ctypes.byref(n)))
    except Exception:
        return False


FONT_NAME = "Pretendard" if _load_pretendard() else "Consolas"

FS = (FONT_NAME, 11)
FSB = (FONT_NAME, 11, "bold")
FS10 = (FONT_NAME, 10)
FS10B = (FONT_NAME, 10, "bold")
FS12 = (FONT_NAME, 12)
FS12B = (FONT_NAME, 12, "bold")
FS17B = (FONT_NAME, 17, "bold")
FS19B = (FONT_NAME, 19, "bold")
