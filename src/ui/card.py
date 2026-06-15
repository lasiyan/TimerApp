"""타이머 카드 - 단일 카운트다운 단위"""

import threading
import time
import tkinter as tk

from src import theme
from src.constants import BTN_W
from src.fonts import FONT_NAME, FS, FSB, FS10B, FS12, FS12B
from src.ui.toast import fire
from src.utils import compat_mmss, parse_mmss, secs_hint


class Card(tk.Frame):
    def __init__(
        self,
        parent,
        root,
        color,
        idx,
        on_del,
        get_cfg,
        on_change=None,
        data=None,
        **kw,
    ):
        super().__init__(
            parent,
            bg=theme.CARD,
            bd=0,
            highlightthickness=1,
            highlightbackground=color,
            **kw,
        )
        self.root = root
        self.color = color
        self.on_del = on_del
        self.get_cfg = get_cfg
        self.running = False
        self.remaining = 0
        self._cancelled = False
        self._build(idx)
        # 저장된 데이터 복원 (trace 등록 전)
        if data:
            self._min.set(compat_mmss(data.get("min", "01:00"), "01:00"))
            self._msg.set(data.get("msg", "타이머 알림"))
            self._ri.set(compat_mmss(data.get("ri", "00:00"), "00:00"))
            if data.get("rep", False):
                self._rep.set(True)
                self._tog()
        # 변경 콜백
        if on_change:
            for var in (self._min, self._msg, self._rep, self._ri):
                var.trace_add("write", lambda *_: on_change())

    def _build(self, idx):
        # 헤더
        hdr = tk.Frame(self, bg=theme.CARD)
        hdr.pack(fill="x", padx=12, pady=(8, 4))
        cv = tk.Canvas(hdr, width=8, height=8, bg=theme.CARD, highlightthickness=0)
        cv.create_oval(1, 1, 7, 7, fill=self.color, outline="")
        cv.pack(side="left", pady=2)
        self._lbl_idx = tk.Label(
            hdr,
            text=f"  타이머 {idx}",
            bg=theme.CARD,
            fg=self.color,
            font=FSB,
        )
        self._lbl_idx.pack(side="left")
        self._st = tk.Label(
            hdr, text="대기 중", bg=theme.CARD, fg=theme.SUBTEXT, font=FS
        )
        self._st.pack(side="left", padx=10)
        self._cd = tk.Label(hdr, text="", bg=theme.CARD, fg=self.color, font=FS12B)
        self._cd.pack(side="left")
        x = tk.Label(
            hdr,
            text="✕",
            bg=theme.CARD,
            fg=theme.SUBTEXT,
            font=FS12,
            cursor="hand2",
        )
        x.pack(side="right")
        x.bind("<Button-1>", lambda _: self.on_del(self))
        x.bind("<Enter>", lambda _: x.config(fg=theme.ACCENT2))
        x.bind("<Leave>", lambda _: x.config(fg=theme.SUBTEXT))

        # 메인 영역: 좌(필드 3행) + 우(토글 버튼)
        main = tk.Frame(self, bg=theme.CARD)
        main.pack(fill="x", padx=12, pady=(0, 10))

        left = tk.Frame(main, bg=theme.CARD)
        left.pack(side="left", fill="x", expand=True)

        # 행 1: 타이머 시간
        r1 = tk.Frame(left, bg=theme.CARD)
        r1.pack(fill="x", pady=2)
        self._min = tk.StringVar(value="01:00")
        self._entry(r1, self._min, 6).pack(side="left")
        self._min_hint = tk.Label(
            r1,
            text="= 1분",
            bg=theme.CARD,
            fg=theme.SUBTEXT,
            font=(FONT_NAME, 9),
        )
        self._min_hint.pack(side="left", padx=(6, 0))
        tk.Label(
            r1,
            text="시간이 지난 후 알림 발생",
            bg=theme.CARD,
            fg=theme.SUBTEXT,
            font=FS,
        ).pack(side="left", padx=(8, 0))
        self._min.trace_add(
            "write", lambda *_: self._upd_hint(self._min, self._min_hint)
        )

        # 행 2: 반복
        r2 = tk.Frame(left, bg=theme.CARD)
        r2.pack(fill="x", pady=2)
        self._rep = tk.BooleanVar(value=False)
        tk.Checkbutton(
            r2,
            text="반복 사용",
            variable=self._rep,
            command=self._tog,
            bg=theme.CARD,
            fg=theme.TEXT,
            selectcolor=theme.CARD,
            activebackground=theme.CARD,
            font=FS,
        ).pack(side="left")
        tk.Frame(r2, bg=theme.BORDER, width=1).pack(side="left", fill="y", padx=8)
        tk.Label(
            r2,
            text="반복 전 휴식:",
            bg=theme.CARD,
            fg=theme.SUBTEXT,
            font=FS,
        ).pack(side="left")
        self._ri = tk.StringVar(value="00:00")
        self._ren = self._entry(r2, self._ri, 6, dis=True)
        self._ren.pack(side="left", padx=(6, 0))
        self._ri_hint = tk.Label(
            r2,
            text="= 즉시 반복",
            bg=theme.CARD,
            fg=theme.SUBTEXT,
            font=(FONT_NAME, 9),
        )
        self._ri_hint.pack(side="left", padx=(6, 0))
        self._ri.trace_add("write", lambda *_: self._upd_ri_hint())

        # 행 3: 메시지
        r3 = tk.Frame(left, bg=theme.CARD)
        r3.pack(fill="x", pady=2)
        tk.Label(
            r3,
            text="메시지",
            bg=theme.CARD,
            fg=theme.SUBTEXT,
            font=FS,
        ).pack(side="left")
        self._msg = tk.StringVar(value="타이머 알림")
        self._entry(r3, self._msg, 20).pack(
            side="left", padx=(6, 0), fill="x", expand=True
        )

        # 우측 토글 버튼
        tk.Frame(main, bg=theme.BORDER, width=1).pack(side="left", fill="y", padx=10)
        bc = tk.Frame(main, bg=theme.CARD)
        bc.pack(side="left", fill="y")
        self._tb = tk.Button(
            bc,
            text="▶  시작",
            command=self._toggle,
            bg="#e8e8ec",
            fg="#1a1a24",
            font=FS10B,
            relief="flat",
            bd=0,
            width=BTN_W,
            cursor="hand2",
            highlightthickness=0,
            activebackground="#ffffff",
            activeforeground="#1a1a24",
        )
        self._tb.pack(fill="both", expand=True)

    def _entry(self, p, var, w, dis=False):
        return tk.Entry(
            p,
            textvariable=var,
            width=w,
            state="disabled" if dis else "normal",
            bg=theme.BG,
            fg=theme.SUBTEXT if dis else theme.TEXT,
            disabledbackground=theme.BG,
            disabledforeground=theme.SUBTEXT,
            insertbackground=theme.TEXT,
            font=FSB,
            relief="flat",
            justify="center",
            highlightthickness=1,
            highlightbackground=theme.BORDER,
            highlightcolor=self.color,
        )

    def _upd_hint(self, var, label):
        label.config(text=secs_hint(parse_mmss(var.get())))

    def _upd_ri_hint(self):
        secs = parse_mmss(self._ri.get())
        self._ri_hint.config(
            text="= 즉시 반복" if secs == 0 else secs_hint(secs) + " 대기"
        )

    def _tog(self):
        on = self._rep.get()
        self._ren.config(
            state="normal" if on else "disabled",
            fg=theme.TEXT if on else theme.SUBTEXT,
        )

    def _toggle(self):
        if self.running:
            self._stop()
        else:
            self._start()

    def _start(self):
        if parse_mmss(self._min.get()) <= 0:
            self._st.config(text="⚠ 시간 확인", fg=theme.ACCENT2)
            return
        self._cancelled = False
        self.running = True
        self._tb.config(
            text="■  정지",
            bg="#4a4f5c",
            fg="#e8e8ec",
            activebackground="#5c6370",
            activeforeground="#ffffff",
        )
        threading.Thread(target=self._run, daemon=True).start()

    def _stop(self):
        self._cancelled = True
        self.running = False
        self._tb.config(
            text="▶  시작",
            bg="#e8e8ec",
            fg="#1a1a24",
            activebackground="#ffffff",
            activeforeground="#1a1a24",
        )
        self._cd.config(text="")
        self._st.config(text="정지됨", fg=theme.SUBTEXT)

    def _tick(self, secs, label):
        total = secs
        for _ in range(secs):
            if self._cancelled:
                return False
            m, s = divmod(secs, 60)
            self._cd.config(text=f"{m:02d}:{s:02d}")
            pct = int((1 - secs / total) * 100) if total else 100
            self._st.config(text=f"{label} {pct}%", fg=theme.TEXT)
            time.sleep(1)
            secs -= 1
        return True

    def _run(self):
        while not self._cancelled:
            secs = parse_mmss(self._min.get())
            if not self._tick(secs, "진행 중"):
                break

            self._cd.config(text="00:00")
            self._st.config(text="완료", fg=theme.SUCCESS)
            msg = self._msg.get() or "시간이 됐어요!"
            cfg = self.get_cfg()
            self.root.update_idletasks()
            ax = self.root.winfo_x() + self.root.winfo_width() // 2
            ay = self.root.winfo_y() + self.root.winfo_height() // 2
            fire(self.root, ax, ay, msg, self.color, cfg)

            if not self._rep.get():
                self._tb.config(
                    text="▶  시작",
                    bg="#e8e8ec",
                    fg="#1a1a24",
                    activebackground="#ffffff",
                    activeforeground="#1a1a24",
                )
                self.running = False
                break

            ri_secs = parse_mmss(self._ri.get())
            if ri_secs > 0:
                if not self._tick(ri_secs, "반복 대기"):
                    break

        self.running = False
