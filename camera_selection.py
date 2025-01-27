import sys
from PySide6.QtWidgets import QDialog, QVBoxLayout, QComboBox, QPushButton, QLabel, QDialogButtonBox
from PySide6.QtCore import Qt, Signal
import cv2
from settings import SettingsManager  # Assuming SettingsManager is imported


class CameraSelectionDialog(QDialog):
    # Signal to pass the selected camera index
    camera_selected = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Select Camera")
        self.setGeometry(200, 200, 300, 200)

        self.layout = QVBoxLayout()

        self.label = QLabel("Select Camera:")
        self.layout.addWidget(self.label)

        self.camera_dropdown = QComboBox(self)
        self.layout.addWidget(self.camera_dropdown)

        # Initialize settings manager to load saved camera index
        self.settings_manager = SettingsManager()
        self.settings = self.settings_manager.load_settings()

        # Load saved camera index and populate dropdown
        self.detect_cameras()

        # Set the dropdown to the saved camera index
        saved_camera_index = self.settings.get("camera_index", 0)
        index = self.camera_dropdown.findData(saved_camera_index)
        if index != -1:
            self.camera_dropdown.setCurrentIndex(index)

        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)
        self.layout.addWidget(self.buttons)

        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)

        self.setLayout(self.layout)

    def detect_cameras(self):
        """Detect available cameras and populate the dropdown."""
        for i in range(10):  # Adjust the range based on the max cameras expected
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                self.camera_dropdown.addItem(f"Camera {i}", i)
                cap.release()

    def get_selected_camera(self):
        """Return the selected camera index from the dropdown."""
        selected_index = self.camera_dropdown.currentIndex()
        return self.camera_dropdown.itemData(selected_index)

    def accept(self):
        """Override accept method to save the selected camera index."""
        selected_camera_index = self.get_selected_camera()

        # Save the selected camera index to settings
        self.settings_manager.save_settings(self.settings["line_y"], self.settings["offset"], selected_camera_index)

        # Emit the signal with the selected camera index
        self.camera_selected.emit(selected_camera_index)

        super().accept()  # Proceed with the default accept behavior
