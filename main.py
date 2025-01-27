import sys
import gc
from PySide6.QtWidgets import QApplication, QMainWindow, QTabWidget, QMessageBox
from trial_logic import TrialManager
from raout_one import RouteOne


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Initialize the TrialManager with the default trial period
        # self.trial_manager = TrialManager()
        # Check trial status
        # if not self.trial_manager.is_trial_valid():
        #     QMessageBox.critical(
        #         self, "Trial End", "Your trial period has end.")
        #     sys.exit(0)

        # Remaining days
        # days_left = self.trial_manager.days_remaining()

        self.setWindowTitle("Vehicle Detection")

        tab_widget = QTabWidget()
        tab_widget.addTab(RouteOne(), "Route One")

        self.setCentralWidget(tab_widget)
        self.resize(800, 600)

    def closeEvent(self, event):
        # Enhanced cleanup
        try:
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
