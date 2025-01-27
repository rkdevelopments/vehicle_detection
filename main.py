import sys
import gc
from PySide6.QtWidgets import QApplication, QMainWindow, QTabWidget, QMessageBox, QLabel, QVBoxLayout, QWidget
from PySide6.QtCore import QTimer, Qt, QThread, Signal
import psutil
from trial_logic import TrialManager
from raout_one import RouteOne
from vehicle_detection1 import VehicleDetection1


class StatsThread(QThread):
    stats_updated = Signal(str)

    def __init__(self, detector):
        super().__init__()
        self.detector = detector

    def run(self):
        while True:
            stats = self.detector.get_stats()
            self.stats_updated.emit(stats)
            self.msleep(1000)  # Sleep for 1 second


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Initialize the TrialManager with the default trial period
        self.trial_manager = TrialManager()
        # Check trial status
        if not self.trial_manager.is_trial_valid():
            QMessageBox.critical(
                self, "Trial End", "Your trial period has end.")
            sys.exit(0)

        # Remaining days
        days_left = self.trial_manager.days_remaining()

        self.setWindowTitle("Vehicle Detection")

        self.tab_widget = QTabWidget()
        self.tab_widget.addTab(RouteOne(), "Route One")

        # Add the debug stats area
        self.stats_label = QLabel()
        self.stats_label.setAlignment(Qt.AlignLeft)
        self.stats_label.setWordWrap(True)

        self.detector = VehicleDetection1()

        # Create a layout for the main window
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.tab_widget)
        main_layout.addWidget(self.stats_label)

        # Create a central widget and set the layout
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        self.resize(800, 600)

        # Start the stats thread
        self.stats_thread = StatsThread(self.detector)
        self.stats_thread.stats_updated.connect(self.update_stats_label)
        self.stats_thread.start()

    def update_stats_label(self, stats):
        self.stats_label.setText(stats)

    def closeEvent(self, event):
        # Enhanced cleanup
        try:
            self.stats_thread.terminate()
            central_widget = self.centralWidget()
            if isinstance(central_widget, QTabWidget):
                for i in range(central_widget.count()):
                    tab = central_widget.widget(i)
                    if hasattr(tab, 'cleanup'):
                        tab.cleanup()
                    # Force immediate cleanup of the tab
                    tab.deleteLater()

            # Force garbage collection
            gc.collect()
        except Exception as e:
            print(f"Error during cleanup: {e}")
        event.accept()

    def __del__(self):
        # Additional cleanup when object is destroyed
        try:
            self.close()
            gc.collect()
        except:
            pass


if __name__ == "__main__":
    try:
        # Enable garbage collection debugging
        gc.set_debug(gc.DEBUG_LEAK)
        app = QApplication(sys.argv)
        window = MainWindow()
        window.show()
        sys.exit(app.exec())
    except MemoryError:
        QMessageBox.critical(
            None, "Error", "Out of memory error occurred. Please restart the application.")
        sys.exit(1)
    except Exception as e:
        QMessageBox.critical(
            None, "Error", f"An unexpected error occurred: {str(e)}")
        sys.exit(1)
