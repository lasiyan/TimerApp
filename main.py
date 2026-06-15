"""TimerApp 진입점

DPI 인식 설정 → 메인 윈도우 시작.
테마/cfg 로드는 App 내부에서 수행.
"""

from src.win_utils import set_dpi_aware

set_dpi_aware()

from src.ui.app import App  # noqa: E402

if __name__ == "__main__":
    App().mainloop()
