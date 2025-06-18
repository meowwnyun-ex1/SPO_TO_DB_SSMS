# app.py
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QVBoxLayout
from PyQt5.QtCore import QTimer
from sharepoint_sync import sync_data


class MainApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Dearquiz SharePoint Sync Tool")
        self.setStyleSheet(
            """
            background-color: #2e1a47;
            color: white;
            font-size: 18px;
        """
        )
        self.resize(600, 400)

        layout = QVBoxLayout()

        self.status_label = QLabel("Ready to sync data")
        layout.addWidget(self.status_label)

        self.btn_clear = QPushButton("🧹 CLEAR PC (จำลองล้างค่า)")
        self.btn_clear.clicked.connect(self.clear_settings)
        layout.addWidget(self.btn_clear)

        self.btn_start = QPushButton("🚀 START (Sync Data Now)")
        self.btn_start.clicked.connect(self.start_sync)
        layout.addWidget(self.btn_start)

        self.setLayout(layout)

        # ตั้งเวลาอัปเดตอัตโนมัติทุก 1 ชั่วโมง
        self.timer = QTimer()
        self.timer.timeout.connect(self.start_sync)
        self.timer.start(3600 * 1000)

    def start_sync(self):
        self.status_label.setText("🔄 Syncing...")
        try:
            sync_data()
            self.status_label.setText("✅ Sync completed!")
        except Exception as e:
            self.status_label.setText(f"❌ Error: {e}")

    def clear_settings(self):
        # ตรงนี้จำลองเฉยๆ ยังไม่มีอะไรต้องล้างจริง
        self.status_label.setText("🧹 Settings cleared!")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainApp()
    window.show()
    sys.exit(app.exec_())
