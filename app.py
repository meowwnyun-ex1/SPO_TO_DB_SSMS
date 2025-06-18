# app.py
import sys
import os
import logging
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QPushButton,
    QLabel,
    QVBoxLayout,
    QWidget,
    QHBoxLayout,
    QProgressBar,
    QTextEdit,
    QFrame,
)
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QPixmap, QFont, QPalette, QBrush, QColor


class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SharePoint to SQL by เฮียตอม😎")
        self.setGeometry(100, 100, 1000, 700)

        # ตั้งค่าระบบล็อก
        self.setup_logging()
        self.setup_ui()

        # ตั้งค่าทริกเกอร์เวลา
        self.timer = QTimer()
        self.timer.timeout.connect(self.start_sync)
        self.timer.start(3600 * 1000)  # ทุก 1 ชั่วโมง

    def setup_logging(self):
        """ตั้งค่าระบบล็อก"""
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            handlers=[logging.FileHandler("system.log"), logging.StreamHandler()],
        )
        self.logger = logging.getLogger(__name__)

    def setup_ui(self):
        """ตั้งค่า UI หลัก"""
        # ใช้ QWidget กลาง
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Layout หลักแบบแนวนอน
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # 1. ส่วนซ้าย (Dashboard)
        left_panel = QFrame()
        left_panel.setStyleSheet(
            """
            QFrame {
                background-color: rgba(30, 30, 60, 180);
                border-radius: 15px;
                border: 2px solid #4A4A8F;
            }
        """
        )
        left_panel.setFixedWidth(350)

        # Layout ส่วนซ้าย
        left_layout = QVBoxLayout()
        left_layout.setAlignment(Qt.AlignTop)
        left_layout.setSpacing(20)
        left_layout.setContentsMargins(20, 20, 20, 20)

        # ส่วนหัว
        header = QLabel("SharePoint to SQL")
        header.setFont(QFont("Segoe UI", 24, QFont.Bold))
        header.setStyleSheet("color: #FFD700;")
        left_layout.addWidget(header, alignment=Qt.AlignCenter)

        # โลโก้
        logo = QLabel()
        logo.setPixmap(QPixmap("assets/logo.png").scaled(200, 200, Qt.KeepAspectRatio))
        logo.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(logo)

        # สถานะระบบ
        self.status_label = QLabel("🟢 System Ready")
        self.status_label.setFont(QFont("Segoe UI", 14))
        self.status_label.setStyleSheet(
            """
            QLabel {
                color: #00FFAA;
                background-color: rgba(0, 0, 0, 120);
                padding: 15px;
                border-radius: 10px;
                border: 1px solid #00FFAA;
            }
        """
        )
        left_layout.addWidget(self.status_label)

        # Progress Bar
        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.progress.setTextVisible(False)
        self.progress.setStyleSheet(
            """
            QProgressBar {
                height: 20px;
                border-radius: 10px;
                background: rgba(0, 0, 0, 100);
                border: 1px solid #4A4A8F;
            }
            QProgressBar::chunk {
                background: qlineargradient(
                    spread:pad, x1:0, y1:0, x2:1, y2:0, 
                    stop:0 #00BFFF, stop:1 #0066FF
                );
                border-radius: 10px;
            }
        """
        )
        left_layout.addWidget(self.progress)

        # ปุ่มควบคุม
        button_container = QWidget()
        button_layout = QVBoxLayout()
        button_layout.setSpacing(15)

        self.btn_start = self.create_button("🚀 START SYNC", "#0066FF", "#00BFFF")
        self.btn_start.clicked.connect(self.start_sync)

        self.btn_clear = self.create_button("🧹 CLEAR LOGS", "#FF5555", "#FF0000")
        self.btn_clear.clicked.connect(self.clear_logs)

        button_layout.addWidget(self.btn_start)
        button_layout.addWidget(self.btn_clear)
        button_container.setLayout(button_layout)
        left_layout.addWidget(button_container)

        # ลิขสิทธิ์
        copyright = QLabel("© Thammaphon Chittasuwanna (SDM) | Innovation")
        copyright.setFont(QFont("Segoe UI", 8))
        copyright.setStyleSheet("color: #AAAAAA;")
        left_layout.addWidget(copyright, alignment=Qt.AlignCenter)

        left_panel.setLayout(left_layout)

        # 2. ส่วนขวา (Log Console)
        right_panel = QFrame()
        right_panel.setStyleSheet(
            """
            QFrame {
                background-color: rgba(20, 20, 40, 200);
                border-radius: 15px;
                border: 2px solid #4A4A8F;
            }
            QTextEdit {
                background-color: rgba(10, 10, 20, 200);
                color: #E0E0E0;
                border: none;
                font-family: 'Consolas';
                font-size: 12px;
            }
        """
        )

        # Console Log
        self.log_console = QTextEdit()
        self.log_console.setReadOnly(True)

        right_layout = QVBoxLayout()
        right_layout.addWidget(QLabel("📜 SYSTEM LOGS"))
        right_layout.addWidget(self.log_console)
        right_panel.setLayout(right_layout)

        # เพิ่มทั้งสองส่วนเข้า Layout หลัก
        main_layout.addWidget(left_panel)
        main_layout.addWidget(right_panel)
        central_widget.setLayout(main_layout)

        # ตั้งค่าพื้นหลัง
        self.set_background()

        # Redirect logging ไปที่ console
        self.log_handler = LogHandler(self.log_console)
        logging.getLogger().addHandler(self.log_handler)

    def create_button(self, text, color1, color2):
        """สร้างปุ่มแบบกำหนดเอง"""
        btn = QPushButton(text)
        btn.setFont(QFont("Segoe UI", 12, QFont.Bold))
        btn.setFixedHeight(50)
        btn.setStyleSheet(
            f"""
            QPushButton {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 {color1}, stop:1 {color2}
                );
                color: white;
                border-radius: 10px;
                border: 2px solid {color2};
            }}
            QPushButton:hover {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 {color2}, stop:1 {color1}
                );
            }}
            QPushButton:pressed {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #555555, stop:1 #777777
                );
            }}
        """
        )
        return btn

    def set_background(self):
        """ตั้งค่าพื้นหลัง"""
        palette = self.palette()
        bg_path = "assets/background.jpg"

        if os.path.exists(bg_path):
            bg = QPixmap(bg_path)
            if not bg.isNull():
                palette.setBrush(
                    QPalette.Window,
                    QBrush(
                        bg.scaled(
                            self.size(), Qt.IgnoreAspectRatio, Qt.SmoothTransformation
                        )
                    ),
                )
        else:
            # พื้นหลังสีดำแบบ gradient
            gradient = QLinearGradient(0, 0, 0, self.height())
            gradient.setColorAt(0, QColor(10, 10, 30))
            gradient.setColorAt(1, QColor(30, 10, 50))
            palette.setBrush(QPalette.Window, QBrush(gradient))

        self.setPalette(palette)

    def start_sync(self):
        """เริ่มกระบวนการซิงค์"""
        self.btn_start.setEnabled(False)
        self.logger.info("Starting synchronization process...")
        self.update_status("🔄 Connecting to SharePoint...", 25)

        try:
            # ดึงข้อมูล
            self.update_status("⬇️ Downloading data...", 50)
            sync_data()

            # สำเร็จ
            self.update_status("✅ Sync completed!", 100)
            self.logger.info("Synchronization completed successfully")
        except Exception as e:
            self.update_status(f"❌ Error: {str(e)}", 0)
            self.logger.error(f"Synchronization failed: {str(e)}")
        finally:
            self.btn_start.setEnabled(True)
            QTimer.singleShot(5000, self.reset_status)

    def clear_logs(self):
        """ล้าง Log Console"""
        self.log_console.clear()
        self.logger.info("Log console cleared")

    def update_status(self, message, progress):
        """อัปเดตสถานะและความคืบหน้า"""
        self.status_label.setText(message)
        self.progress.setValue(progress)
        QApplication.processEvents()

    def reset_status(self):
        """รีเซ็ตสถานะ"""
        self.update_status("🟢 System Ready", 0)

    def resizeEvent(self, event):
        """ปรับพื้นหลังเมื่อหน้าต่างเปลี่ยนขนาด"""
        self.set_background()
        super().resizeEvent(event)


class LogHandler(logging.Handler):
    """Custom handler สำหรับแสดง Log ใน UI"""

    def __init__(self, text_widget):
        super().__init__()
        self.text_widget = text_widget

    def emit(self, record):
        msg = self.format(record)
        self.text_widget.append(msg)
        self.text_widget.verticalScrollBar().setValue(
            self.text_widget.verticalScrollBar().maximum()
        )


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # ตั้งค่า Font หลัก
    font = QFont("Segoe UI", 10)
    app.setFont(font)

    window = MainApp()
    window.show()
    sys.exit(app.exec_())
