"""WinAPI 헬퍼: DPI, 모니터 정보, 클릭 통과"""

import ctypes
import ctypes.wintypes as wt

user32 = ctypes.windll.user32


def set_dpi_aware():
    """System DPI Aware 설정 (안정성 우선)"""
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        try:
            ctypes.windll.user32.SetProcessDPIAware()
        except Exception:
            pass


# -- 모니터 정보 ----------------------------------------------------------------
class _MONITORINFO(ctypes.Structure):
    _fields_ = [
        ("cbSize", ctypes.c_ulong),
        ("rcMonitor", wt.RECT),
        ("rcWork", wt.RECT),
        ("dwFlags", ctypes.c_ulong),
    ]


def _mi(hmon):
    mi = _MONITORINFO()
    mi.cbSize = ctypes.sizeof(_MONITORINFO)
    user32.GetMonitorInfoW(hmon, ctypes.byref(mi))
    r = mi.rcWork
    return r.left, r.top, r.right, r.bottom


def mon_from_pt(x, y):
    return _mi(user32.MonitorFromPoint(wt.POINT(x, y), 0x2))


def all_mons():
    mons = []
    PROC = ctypes.WINFUNCTYPE(
        ctypes.c_bool,
        ctypes.c_ulong,
        ctypes.c_ulong,
        ctypes.POINTER(wt.RECT),
        ctypes.c_ulong,
    )

    def cb(h, dc, r, d):
        mons.append(_mi(h))
        return True

    user32.EnumDisplayMonitors(None, None, PROC(cb), 0)
    return mons or [mon_from_pt(0, 0)]


def cursor_mon():
    pt = wt.POINT()
    user32.GetCursorPos(ctypes.byref(pt))
    return mon_from_pt(pt.x, pt.y)


# -- 클릭 통과 (WS_EX_TRANSPARENT) ---------------------------------------------
_GWL_EXSTYLE = -20
_WS_EX_LAYERED = 0x00080000
_WS_EX_TRANSPARENT = 0x00000020


def hwnd(widget):
    """tk Toplevel의 실제 Win32 HWND"""
    fid = widget.winfo_id()
    parent = user32.GetParent(fid)
    return parent if parent else fid


def clickthrough_on(h):
    s = user32.GetWindowLongW(h, _GWL_EXSTYLE)
    user32.SetWindowLongW(h, _GWL_EXSTYLE, s | _WS_EX_LAYERED | _WS_EX_TRANSPARENT)


def clickthrough_off(h):
    s = user32.GetWindowLongW(h, _GWL_EXSTYLE)
    user32.SetWindowLongW(h, _GWL_EXSTYLE, s & ~_WS_EX_TRANSPARENT)
