"""토스트 알림 - Toplevel 기반, 클릭 통과 + 페이드 + 호버 활성화"""

import threading
import time
import tkinter as tk

from src import sound, theme
from src.constants import FADE_DELAY, FADE_STEP, HOVER_POLL
from src.config import DEFAULTS
from src.fonts import FONT_NAME, FS10
from src.win_utils import (
    all_mons,
    clickthrough_off,
    clickthrough_on,
    cursor_mon,
    hwnd,
    mon_from_pt,
)


class Toast(tk.Toplevel):
    _active = []  # 활성 토스트 목록 (겹침 처리)

    def __init__(self, root, msg, color, rect, cfg):
        super().__init__(root)
        self.overrideredirect(True)
        self.attributes("-topmost", True)
        self.attributes("-alpha", 0.0)
        self.configure(bg=theme.TOAST_BG)
        self._closed = False
        self._hovering = False
        self._max_alpha = cfg.get("opacity", 95) / 100

        ml, mt, mr, mb = rect
        mw, mh = mr - ml, mb - mt
        W = max(180, int(mw * cfg["width_pct"] / 100))
        H = max(50, int(mh * cfg["height_pct"] / 100))
        secs = int(cfg.get("duration", DEFAULTS["duration"]))

        op = cfg.get("offset_pct", 1) / 100
        if cfg["position"] == "center":
            px = ml + mw // 2 - W // 2
            py_base = mt + mh // 2 - H // 2
        elif cfg["position"] == "bottom_left":
            px = ml + int(mw * op)
            py_base = mb - H - int(mh * op)
        else:  # bottom_right
            px = mr - W - int(mw * op)
            py_base = mb - H - int(mh * op)

        # 같은 위치 기존 토스트만큼 위로 쌓기
        self._key = (cfg["position"], ml, mt, mr, mb)
        n = sum(1 for t in Toast._active if not t._closed and t._key == self._key)
        py = max(mt + 5, py_base - n * (H + 8))
        Toast._active.append(self)

        self.geometry(f"{W}x{H}+{px}+{py}")
        self._wx, self._wy, self._ww, self._wh = px, py, W, H

        f_size = max(9, min(20, W // 20))

        # 상단 컬러 바
        tk.Frame(self, bg=color, height=4).pack(fill="x", side="top")

        # 하단 진행 바
        bar = tk.Frame(self, bg=theme.BORDER, height=3)
        bar.pack(side="bottom", fill="x")
        self._bar = tk.Frame(bar, bg=color, height=3)
        self._bar.place(x=0, y=0, relwidth=1, height=3)

        # 본체
        body = tk.Frame(self, bg=theme.TOAST_BG)
        body.pack(fill="both", expand=True)
        body.rowconfigure(0, weight=1)
        body.rowconfigure(2, weight=1)
        body.columnconfigure(0, weight=1)

        self._x_btn = tk.Label(
            body,
            text="✕",
            bg=theme.TOAST_BG,
            fg=theme.SUBTEXT,
            font=FS10,
            cursor="hand2",
        )
        self._x_btn.place(relx=1.0, x=-4, y=2, anchor="ne")
        self._x_btn.bind("<Button-1>", lambda _: self._close())
        self._x_btn.bind("<Enter>", lambda _: self._x_btn.config(fg=theme.ACCENT2))
        self._x_btn.bind("<Leave>", lambda _: self._x_btn.config(fg=theme.SUBTEXT))

        body.bind("<Button-1>", lambda _: self._close())

        lbl = tk.Label(
            body,
            text=msg,
            bg=theme.TOAST_BG,
            fg=theme.TEXT,
            font=(FONT_NAME, f_size, "bold"),
            anchor="center",
            justify="center",
            wraplength=W - 24,
        )
        lbl.grid(row=1, column=0, sticky="ew", padx=12)
        lbl.bind("<Button-1>", lambda _: self._close())

        self._secs = secs
        self._fi()
        threading.Thread(target=self._cd, daemon=True).start()

    def _fi(self, a=0.0):
        if self._closed or a >= self._max_alpha:
            self.attributes("-alpha", self._max_alpha)
            self.after(HOVER_POLL, self._poll)
            return
        self.attributes("-alpha", a)
        self.after(FADE_DELAY, lambda: self._fi(a + FADE_STEP))

    def _poll(self):
        if self._closed:
            return
        try:
            mx = self.winfo_pointerx()
            my = self.winfo_pointery()
            inside = (
                self._wx <= mx <= self._wx + self._ww
                and self._wy <= my <= self._wy + self._wh
            )
            h = hwnd(self)
            if inside and not self._hovering:
                clickthrough_off(h)
                self._hovering = True
            elif not inside and self._hovering:
                clickthrough_on(h)
                self._hovering = False
            elif not inside and not self._hovering:
                clickthrough_on(h)
        except Exception:
            pass
        self.after(HOVER_POLL, self._poll)

    def _cd(self):
        steps = self._secs * 20
        for i in range(steps):
            if self._closed:
                return
            try:
                self._bar.place(relwidth=1 - i / steps)
            except Exception:
                return
            time.sleep(0.05)
        self.after(0, self._close)

    def _close(self):
        if self._closed:
            return
        self._closed = True
        try:
            Toast._active.remove(self)
        except ValueError:
            pass
        self._fo()

    def _fo(self, a=None):
        if a is None:
            a = self._max_alpha
        if a < 0:
            try:
                self.destroy()
            except Exception:
                pass
            return
        try:
            self.attributes("-alpha", a)
            self.after(FADE_DELAY, lambda: self._fo(a - FADE_STEP * 1.5))
        except Exception:
            pass


def fire(root, ax, ay, msg, color, cfg):
    """설정에 따른 모니터에 토스트 알림 발사"""
    sound.play(cfg)
    mode = cfg["monitor"]
    if mode == "all":
        rects = all_mons()
    elif mode == "mouse":
        rects = [cursor_mon()]
    else:
        rects = [mon_from_pt(ax, ay)]
    for r in rects:
        root.after(0, lambda rc=r: Toast(root, msg, color, rc, cfg))
