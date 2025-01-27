import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QTabWidget, QMessageBox
from trial_logic import TrialManager
from dashboard import Dashboard
from raout_one import RouteOne
from raout_two import RouteTwo
from data import Data

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Initialize the TrialManager with the default trial period
        self.trial_manager = TrialManager()
        # Check trial status
        if not self.trial_manager.is_trial_valid():
            QMessageBox.critical(self, "Trial End", "Your trial period has end.")
            sys.exit(0)

        # Remaining days
        days_left = self.trial_manager.days_remaining()
        
        self.setWindowTitle("Vehicle Detection")
        
        
        tab_widget = QTabWidget()
        tab_widget.addTab(Dashboard(), "Dashboard")
        tab_widget.addTab(RouteOne(), "Route One")
        tab_widget.addTab(RouteTwo(), "Route Two")
        tab_widget.addTab(Data(), "Data")
        
        self.setCentralWidget(tab_widget)
        self.resize(800,600)
        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())       