"""메인 앱 윈도우"""

import os
import tkinter as tk

from src import theme
from src.config import DEFAULTS, load_cards, load_cfg, save_cards, save_cfg
from src.constants import HPAD
from src.fonts import FS, FSB, FS19B, _base
from src.ui.card import Card
from src.ui.settings import SettingsWin


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        try:
            dpi = self.winfo_fpixels("1i")
            self.tk.call("tk", "scaling", dpi / 72)
        except Exception:
            pass
        self.title("TimerApp")
        self.resizable(True, True)
        self._cfg = load_cfg()
        theme.apply_theme(self._cfg.get("theme", "dark"))
        self.configure(bg=theme.BG)
        self._cards = []
        try:
            ico = os.path.join(_base(), "res", "icon.ico")
            if os.path.exists(ico):
                self.iconbitmap(ico)
        except Exception:
            pass
        self._header()
        self._body()
        saved = load_cards()
        if saved:
            for d in saved:
                self._add(data=d)
        else:
            self._add()
        self.update_idletasks()
        min_w = self._inner.winfo_reqwidth() + HPAD * 2
        self.minsize(min_w, 160)
        w = max(min_w + 40, self._cfg.get("win_w", DEFAULTS["win_w"]))
        h = max(160, self._cfg.get("win_h", DEFAULTS["win_h"]))
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry(f"{w}x{h}+{(sw-w)//2}+{(sh-h)//2}")
        self._resize_job = None
        self.bind("<Configure>", self._on_win_resize)
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _header(self):
        h = tk.Frame(self, bg=theme.BG)
        h.pack(fill="x", padx=HPAD, pady=(14, 4))
        tk.Label(
            h,
            text="⏱",
            bg=theme.BG,
            fg=theme.ACCENT,
            font=("Segoe UI Emoji", 20),
        ).pack(side="left")
        tk.Label(
            h,
            text=" TimerApp",
            bg=theme.BG,
            fg=theme.TITLE,
            font=FS19B,
        ).pack(side="left")
        tk.Button(
            h,
            text="⚙ 설정",
            command=self._settings,
            bg=theme.BG,
            fg=theme.SUBTEXT,
            font=FS,
            relief="flat",
            bd=0,
            padx=10,
            pady=5,
            cursor="hand2",
            highlightthickness=0,
            highlightbackground=theme.BG,
            activebackground=theme.BORDER,
            activeforeground=theme.TEXT,
        ).pack(side="right", padx=(6, 0))
        tk.Button(
            h,
            text="＋ 추가",
            command=self._add,
            bg=theme.BG,
            fg=theme.SUBTEXT,
            font=FSB,
            relief="flat",
            bd=0,
            padx=10,
            pady=5,
            cursor="hand2",
            highlightthickness=0,
            highlightbackground=theme.BG,
            activebackground=theme.BORDER,
            activeforeground=theme.TEXT,
        ).pack(side="right")
        tk.Frame(self, bg=theme.BORDER, height=1).pack(fill="x", pady=(8, 0))

    def _body(self):
        outer = tk.Frame(self, bg=theme.BG)
        outer.pack(fill="both", expand=True)
        outer.rowconfigure(0, weight=1)
        outer.columnconfigure(0, weight=1)
        self._cv = tk.Canvas(outer, bg=theme.BG, bd=0, highlightthickness=0)
        self._sb = tk.Scrollbar(outer, orient="vertical", command=self._cv.yview)
        self._inner = tk.Frame(self._cv, bg=theme.BG)
        self._inner.bind("<Configure>", self._resize)
        self._wid = self._cv.create_window((0, 0), window=self._inner, anchor="nw")
        self._cv.bind("<Configure>", self._on_cv)
        self._cv.configure(yscrollcommand=self._sb.set)
        self._cv.grid(row=0, column=0, sticky="nsew")
        self._sb_on = False
        self._cv.bind(
            "<MouseWheel>",
            lambda e: self._cv.yview_scroll(-1 * (e.delta // 120), "units"),
        )

    def _on_cv(self, e):
        self._cv.itemconfig(self._wid, width=e.width)
        self._resize()

    def _resize(self, e=None):
        self._cv.configure(scrollregion=self._cv.bbox("all"))
        self.after(20, self._scroll_check)

    def _scroll_check(self):
        if self._inner.winfo_reqheight() > self._cv.winfo_height():
            if not self._sb_on:
                self._sb.grid(row=0, column=1, sticky="ns")
                self._sb_on = True
        else:
            if self._sb_on:
                self._sb.grid_forget()
                self._sb_on = False

    def _on_win_resize(self, e):
        if e.widget is not self:
            return
        if self._resize_job:
            self.after_cancel(self._resize_job)
        self._resize_job = self.after(300, self._save_win_size)

    def _save_win_size(self):
        self._cfg["win_w"] = self.winfo_width()
        self._cfg["win_h"] = self.winfo_height()
        save_cfg(self._cfg)

    def _save_cards(self):
        save_cards(
            [
                {
                    "min": c._min.get(),
                    "msg": c._msg.get(),
                    "rep": c._rep.get(),
                    "ri": c._ri.get(),
                }
                for c in self._cards
            ]
        )

    def _add(self, data=None):
        idx = len(self._cards) + 1
        color = theme.TIMER_COLORS[(idx - 1) % len(theme.TIMER_COLORS)]
        c = Card(
            self._inner,
            root=self,
            color=color,
            idx=idx,
            on_del=self._del,
            get_cfg=lambda: self._cfg,
            on_change=self._save_cards,
            data=data,
        )
        c.pack(fill="x", padx=HPAD, pady=6)
        self._cards.append(c)
        self._save_cards()

    def _del(self, c):
        if c.running:
            c._stop()
        c.destroy()
        self._cards.remove(c)
        for i, card in enumerate(self._cards, 1):
            card._lbl_idx.config(text=f"  타이머 {i}")
        self._save_cards()

    def _settings(self):
        for w in self.winfo_children():
            if isinstance(w, SettingsWin):
                w.lift()
                w.focus_set()
                return
        SettingsWin(self, self._cfg, self._apply)

    def _apply(self, cfg, persist=True):
        self._cfg = cfg
        if persist:
            save_cfg(cfg)

    def _on_close(self):
        if self._cfg.get("tray_on_close", 0):
            self.withdraw()
        else:
            self.destroy()
