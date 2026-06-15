"""환경설정 창"""

import tkinter as tk

from src import theme
from src.config import DEFAULTS
from src.fonts import FONT_NAME, FS, FSB, FS17B
from src.ui.toast import fire


class SettingsWin(tk.Toplevel):
    def __init__(self, root, cfg, on_save):
        super().__init__(root)
        self.title("환경설정")
        self.configure(bg=theme.BG)
        self.resizable(False, False)
        self._orig_cfg = dict(cfg)
        self._cfg = dict(cfg)
        self._on_save = on_save
        self._cur_cfg = dict(cfg)
        self.protocol("WM_DELETE_WINDOW", self._cancel)
        self._build()
        self.update_idletasks()
        req_h = self.winfo_reqheight()
        rx = root.winfo_x() + root.winfo_width() // 2
        ry = root.winfo_y() + root.winfo_height() // 2
        w = 754
        self.geometry(f"{w}x{req_h}+{rx-w//2}+{ry-req_h//2}")

    def _sec(self, text):
        tk.Frame(self, bg=theme.BORDER, height=1).pack(fill="x", pady=(14, 0))
        lf = tk.Frame(self, bg=theme.BG)
        lf.pack(fill="x", padx=20, pady=(6, 4))
        tk.Label(lf, text=text, bg=theme.BG, fg=theme.ACCENT, font=FSB).pack(anchor="w")
        f = tk.Frame(self, bg=theme.BG)
        f.pack(fill="x", padx=30, pady=4)
        return f

    def _build(self):
        tk.Label(self, text="환경설정", bg=theme.BG, fg=theme.TITLE, font=FS17B).pack(
            pady=(18, 0)
        )

        # 프로그램 옵션
        f = self._sec("프로그램 옵션")
        self._tray_close = tk.BooleanVar(value=bool(self._cfg.get("tray_on_close", 0)))
        tk.Checkbutton(
            f,
            text="프로그램을 종료할 때 트레이로 이동",
            variable=self._tray_close,
            command=self._instant,
            bg=theme.BG,
            fg=theme.TEXT,
            selectcolor=theme.CARD,
            activebackground=theme.BG,
            font=FS,
        ).pack(anchor="w")

        # 테마
        f = self._sec("테마")
        self._theme = tk.StringVar(value=self._cfg.get("theme", "dark"))
        self._theme.trace_add("write", self._instant)
        row = tk.Frame(f, bg=theme.BG)
        row.pack(fill="x")
        for val, lbl in [
            ("dark", "다크"),
            ("light", "라이트"),
            ("system", "시스템 설정 따름"),
        ]:
            tk.Radiobutton(
                row,
                text=lbl,
                variable=self._theme,
                value=val,
                bg=theme.BG,
                fg=theme.TEXT,
                selectcolor=theme.CARD,
                activebackground=theme.BG,
                font=FS,
            ).pack(side="left", expand=True)
        tk.Label(
            f,
            text="저장 후 재시작 시 적용됩니다",
            bg=theme.BG,
            fg=theme.SUBTEXT,
            font=(FONT_NAME, 9),
        ).pack(anchor="w", pady=(2, 0))

        # 출력 위치
        f = self._sec("출력 위치")
        self._pos = tk.StringVar(value=self._cfg["position"])
        self._pos.trace_add("write", self._instant)
        row = tk.Frame(f, bg=theme.BG)
        row.pack(fill="x")
        for val, lbl in [
            ("bottom_right", "우측 하단"),
            ("bottom_left", "좌측 하단"),
            ("center", "화면 중앙"),
        ]:
            tk.Radiobutton(
                row,
                text=lbl,
                variable=self._pos,
                value=val,
                bg=theme.BG,
                fg=theme.TEXT,
                selectcolor=theme.CARD,
                activebackground=theme.BG,
                font=FS,
            ).pack(side="left", expand=True)

        # 출력 크기 & 불투명도
        f = self._sec("출력 크기 / 불투명도 (모니터 해상도 기준 %)")
        self._wpct = self._slider(f, "가로 비율", self._cfg["width_pct"], 5, 80, "%")
        self._hpct = self._slider(f, "세로 비율", self._cfg["height_pct"], 4, 50, "%")
        self._opac = self._slider(
            f, "불투명도  ", self._cfg.get("opacity", 100), 10, 100, "%"
        )

        # 출력 모니터
        f = self._sec("출력 모니터")
        self._mon = tk.StringVar(value=self._cfg["monitor"])
        self._mon.trace_add("write", self._instant)
        for val, lbl in [
            ("app", "앱이 위치한 모니터"),
            ("mouse", "마우스가 위치한 모니터"),
            ("all", "모든 모니터"),
        ]:
            tk.Radiobutton(
                f,
                text=lbl,
                variable=self._mon,
                value=val,
                bg=theme.BG,
                fg=theme.TEXT,
                selectcolor=theme.CARD,
                activebackground=theme.BG,
                font=FS,
                anchor="w",
            ).pack(fill="x", pady=3, padx=4)

        # 출력 시간
        f = self._sec("출력 시간")
        self._dur = self._slider(
            f,
            "표시 시간",
            self._cfg.get("duration", DEFAULTS["duration"]),
            1,
            30,
            "초",
        )

        # 하단 버튼
        tk.Frame(self, bg=theme.BORDER, height=1).pack(fill="x", pady=(14, 0))
        br = tk.Frame(self, bg=theme.BG)
        br.pack(pady=(16, 0))
        tk.Button(
            br,
            text="  🔔 테스트 알림  ",
            command=self._test,
            bg=theme.BORDER,
            fg=theme.TEXT,
            font=FSB,
            relief="flat",
            bd=0,
            padx=16,
            pady=7,
            cursor="hand2",
            activebackground="#3a3a4d",
            activeforeground=theme.TEXT,
        ).pack(side="left", padx=(0, 8))
        tk.Button(
            br,
            text="  저장 후 닫기  ",
            command=self._save,
            bg=theme.ACCENT,
            fg="white",
            font=FSB,
            relief="flat",
            bd=0,
            padx=16,
            pady=7,
            cursor="hand2",
            activebackground="#9180ff",
            activeforeground="white",
        ).pack(side="left")
        tk.Frame(self, bg=theme.BG, height=20).pack()

    def _slider(self, parent, label, init, lo, hi, unit):
        row = tk.Frame(parent, bg=theme.BG)
        row.pack(fill="x", pady=3)
        tk.Label(
            row,
            text=label,
            bg=theme.BG,
            fg=theme.SUBTEXT,
            font=FS,
            width=12,
            anchor="w",
        ).pack(side="left")
        var = tk.IntVar(value=init)
        vl = tk.Label(
            row,
            text=f"{init:3d}{unit}",
            bg=theme.BG,
            fg=theme.TEXT,
            font=FSB,
            width=6,
        )
        vl.pack(side="right")

        def upd(v):
            vl.config(text=f"{int(float(v)):3d}{unit}")
            self._instant()

        sc = tk.Scale(
            row,
            from_=lo,
            to=hi,
            orient="horizontal",
            variable=var,
            bg=theme.SLIDER,
            fg=theme.TEXT,
            troughcolor=theme.BORDER,
            highlightthickness=0,
            sliderrelief="flat",
            command=upd,
            showvalue=False,
        )
        sc.pack(side="left", padx=6, fill="x", expand=True)

        def _key(e):
            cur = var.get()
            delta = {"Left": -1, "Right": 1, "Down": -10, "Up": 10}.get(e.keysym, 0)
            var.set(max(lo, min(hi, cur + delta)))
            upd(var.get())
            return "break"

        sc.bind("<Button-1>", lambda e: sc.focus_set())
        sc.bind("<Left>", _key)
        sc.bind("<Right>", _key)
        sc.bind("<Up>", _key)
        sc.bind("<Down>", _key)
        return var

    def _instant(self, *_):
        self._cur_cfg = {
            "position": self._pos.get(),
            "width_pct": self._wpct.get(),
            "height_pct": self._hpct.get(),
            "opacity": self._opac.get(),
            "monitor": self._mon.get(),
            "duration": self._dur.get(),
            "tray_on_close": int(self._tray_close.get()),
            "theme": self._theme.get(),
        }
        self._on_save(self._cur_cfg, persist=False)

    def _test(self):
        self._instant()
        root = self.master
        root.update_idletasks()
        ax = root.winfo_x() + root.winfo_width() // 2
        ay = root.winfo_y() + root.winfo_height() // 2
        fire(root, ax, ay, "테스트 알림", theme.ACCENT, self._cur_cfg)

    def _cancel(self):
        self._on_save(self._orig_cfg, persist=False)
        self.destroy()

    def _save(self):
        old_theme = self._orig_cfg.get("theme", "dark")
        self._instant()
        new_theme = self._cur_cfg.get("theme", "dark")
        self._on_save(self._cur_cfg, persist=True)
        self.destroy()
        if old_theme != new_theme:
            import tkinter.messagebox as mb

            mb.showinfo(
                "테마 변경", "테마가 저장되었습니다.\n앱을 재시작하면 적용됩니다."
            )
