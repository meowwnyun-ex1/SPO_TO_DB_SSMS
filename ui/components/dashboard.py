# main.py - Entry point (30 บรรทัด)
import sys
from PyQt5.QtWidgets import QApplication
from ui.main_window import MainWindow
from core.app_controller import AppController


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    # Initialize controller และ main window
    controller = AppController()
    window = MainWindow(controller)

    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()

# ===============================================
# ui/main_window.py - Main UI (200 บรรทัด)
from PyQt5.QtWidgets import QMainWindow, QHBoxLayout, QWidget, QSplitter
from PyQt5.QtCore import Qt
from .components.dashboard import Dashboard
from .components.config_panel import ConfigPanel
from .styles.theme import apply_gradient_theme


class MainWindow(QMainWindow):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("SharePoint to SQL by เฮียตอม😎")
        self.setGeometry(100, 100, 1400, 900)

        # Apply theme
        apply_gradient_theme(self)

        # Main layout with splitter
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QHBoxLayout(central_widget)
        splitter = QSplitter(Qt.Horizontal)

        # Components
        self.dashboard = Dashboard(self.controller)
        self.config_panel = ConfigPanel(self.controller)

        splitter.addWidget(self.dashboard)
        splitter.addWidget(self.config_panel)
        splitter.setSizes([400, 800])

        layout.addWidget(splitter)

        # Connect signals
        self.controller.status_changed.connect(self.dashboard.update_status)
        self.controller.progress_updated.connect(self.dashboard.update_progress)


# ===============================================
# ui/components/dashboard.py - Dashboard widget (150 บรรทัด)
from PyQt5.QtWidgets import QWidget, QVBoxLayout
from PyQt5.QtCore import pyqtSlot
from ..widgets.status_card import StatusCard
from ..widgets.progress_card import ProgressCard
from ..widgets.control_panel import ControlPanel
from ..widgets.connection_status import ConnectionStatusWidget


class Dashboard(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)

        # Header card
        self.header_card = StatusCard("SharePoint to SQL\nby เฮียตอม😎")
        layout.addWidget(self.header_card)

        # Connection status
        self.connection_status = ConnectionStatusWidget()
        layout.addWidget(self.connection_status)

        # Progress tracking
        self.progress_card = ProgressCard()
        layout.addWidget(self.progress_card)

        # Control buttons
        self.control_panel = ControlPanel(self.controller)
        layout.addWidget(self.control_panel)

        layout.addStretch()

    @pyqtSlot(str, str)
    def update_status(self, service, status):
        self.connection_status.update_service_status(service, status)

    @pyqtSlot(str, int)
    def update_progress(self, message, progress):
        self.progress_card.update_progress(message, progress)
