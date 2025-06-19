from PyQt6.QtWidgets import QProgressBar
from PyQt6.QtCore import Qt  # Import Qt for alignment
from ..styles.theme import UltraModernColors  # Ensure UltraModernColors is imported


class HolographicProgressBar(QProgressBar):
    """
    แถบความคืบหน้าแบบ Holographic ที่มีการปรับปรุงสไตล์
    ให้เข้ากับโทนสีใหม่ และรองรับการแสดงผลเปอร์เซ็นต์
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(
            f"""
            QProgressBar {{
                background: {UltraModernColors.GLASS_BG_DARK};
                border: 1px solid {UltraModernColors.NEON_PURPLE};
                border-radius: 8px;
                height: 20px;
                text-align: center; /* Center the text */
                color: {UltraModernColors.TEXT_PRIMARY}; /* White text */
                font-weight: bold;
            }}
            QProgressBar::chunk {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 {UltraModernColors.NEON_PURPLE}, /* Purple start */
                    stop:1 {UltraModernColors.NEON_PINK} /* Pink end */
                );
                border-radius: 8px;
            }}
            """
        )
        self.setTextVisible(True)  # Ensure text is visible for percentage
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)  # Center the text
