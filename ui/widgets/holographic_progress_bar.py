from PyQt6.QtWidgets import QProgressBar
from ..styles.theme import UltraModernColors


class HolographicProgressBar(QProgressBar):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(
            f"""
            QProgressBar {{
                background: rgba(0, 0, 0, 0.3);
                border: 1px solid {UltraModernColors.NEON_BLUE};
                border-radius: 8px;
                height: 20px;
            }}
            QProgressBar::chunk {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 {UltraModernColors.NEON_BLUE},
                    stop:1 {UltraModernColors.NEON_PURPLE}
                );
                border-radius: 8px;
            }}
        """
        )
        self.setTextVisible(False)
