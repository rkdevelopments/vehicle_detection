from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QGridLayout, QFrame, QTableWidget, QTableWidgetItem, QDialog
from PySide6.QtGui import QImage, QPixmap, QFont
from PySide6.QtCore import Qt, QTimer
from vehicle_detection1 import VehicleDetection1
import time
import pytz
from datetime import datetime, timezone
from camera_selection import CameraSelectionDialog
import cv2
from PySide6.QtWidgets import QSlider, QPushButton, QLabel, QSizePolicy, QHeaderView
from settings import SettingsManager


def get_india_time():
    # Use time.time() to get the current time in seconds (since epoch)
    current_time = time.time()

    # Convert the timestamp to UTC and then to IST (India Standard Time)
    utc_time = datetime.fromtimestamp(current_time, tz=pytz.utc)  # Convert to UTC time
    india_tz = pytz.timezone('Asia/Kolkata')  # IST timezone
    india_time = utc_time.astimezone(india_tz)  # Convert to IST
    
    # Format the time as a string
    event_time = india_time.strftime('%Y-%m-%d %H:%M:%S')  # Save time in 'YYYY-MM-DD HH:MM:SS' format
    return event_time

class RouteOne(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        
        
        


        # Initialize vehicle detection
        self.detector = VehicleDetection1(video_path='videos/vid1.mp4', db_name='cam1.db')
        
        # Track last values of entry and exit counters
        self.last_entry_counter = 0
        self.last_exit_counter = 0

        # Create QTimer for updating video feed and counts
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_video_feed)
        self.timer.start(1000 / self.detector.fps)  # Updates based on the camera's FPS

        
        self.setStyleSheet("""
            QLabel {
                background-color: #f7f9fc;
                border-radius: 8px;
                padding: 15px;
                font-size: 14px;
                color: #333;
            }
            QLabel#header {
                font-weight: bold;
                font-size: 16px;
                text-align: center;
            }
            QTableWidget {
                background-color: #ffffff;
                border: 1px solid #ddd;
                border-radius: 8px;
                gridline-color: #ddd;
                font-size: 12px;
                color: #333;
            }
        """)


        # Header section
        header_layout = QHBoxLayout()
        self.total_entries_label = QLabel("Total Entries\n0", self)
        self.total_entries_label.setAlignment(Qt.AlignCenter)
        self.total_entries_label.setFont(QFont("Arial", 12))
        self.total_entries_label.setObjectName("header")
        
        
        self.total_exits_label = QLabel("Total Exits\n0", self)
        self.total_exits_label.setAlignment(Qt.AlignCenter)
        self.total_exits_label.setFont(QFont("Arial", 12))
        self.total_exits_label.setObjectName("header")
        
        header_layout.addWidget(self.total_entries_label)
        header_layout.addWidget(self.total_exits_label)
        layout.addLayout(header_layout)
        
        # Create a horizontal layout to hold both widgets
        horizontal_layout = QHBoxLayout()
        horizontal_layout.setSpacing(25)  # Add space between the two widgets (adjust as needed)

        # Live Camera Feed for Entry
        camera_layout = QGridLayout()
        self.live_feed_entry_label = QLabel("Live Entry Camera Feed")
        self.live_feed_entry_label.mousePressEvent = self.change_entry_camera
        self.live_feed_entry_label.setAlignment(Qt.AlignCenter)
        self.live_feed_entry_label.setStyleSheet("background-color: #eaeff5; border: 1px dashed #ccc;")
        camera_layout.addWidget(self.live_feed_entry_label, 0, 0)
        grid_widget = QWidget()
        grid_widget.setStyleSheet("QWidget { border: 1px solid #333; border-radius: 15px; background-color: #f9f9f9; }")
        grid_widget.setLayout(camera_layout)
        grid_widget.setFixedSize(700, 350)
        
        # Add the grid widget to the horizontal layout
        horizontal_layout.addWidget(grid_widget)
        horizontal_layout.setStretch(0, 3)  # 75% width for the camera view (3 parts)
        #layout.addWidget(grid_widget)

        # Vehicle Details
        vehicle_details_frame = QFrame()
        vehicle_details_layout = QVBoxLayout(vehicle_details_frame)
        self.vehicle_details_label = QLabel("Vehicle Details")
        self.plate_number_label = QLabel("Plate Number: -")
        self.entry_time_label = QLabel("Entry Time: -")
        self.exit_time_label = QLabel("Exit Time: -")
        self.snapshot_label = QLabel("Snapshot:")
        self.snapshot_image_label = QLabel()
        self.snapshot_image_label.setFixedSize(290, 110)
        self.snapshot_image_label.setStyleSheet("background-color: #eaeff5; border: 1px solid #ccc;")
        vehicle_details_layout.addWidget(self.vehicle_details_label)
        vehicle_details_layout.addWidget(self.plate_number_label)
        vehicle_details_layout.addWidget(self.entry_time_label)
        vehicle_details_layout.addWidget(self.exit_time_label)
        vehicle_details_layout.addWidget(self.snapshot_label)
        vehicle_details_layout.addWidget(self.snapshot_image_label)
        
        # Add the vehicle details frame to the horizontal layout
        horizontal_layout.addWidget(vehicle_details_frame)
        horizontal_layout.setStretch(1, 1)  # 25% width for the vehicle details (1 part)
        layout.addLayout(horizontal_layout)
        
        # ------- Slider for Line Y Adjustment -------- #
        slider_layout = QHBoxLayout()
        self.line_y_slider = QSlider(Qt.Horizontal)
        self.line_y_slider.setMinimum(0)
        self.line_y_slider.setMaximum(750)
        self.line_y_slider.setValue(self.detector.line_y)
        self.line_y_slider.setTickInterval(50)
        self.line_y_slider.setFixedWidth(300)  # Set smaller width for slider
        self.line_y_slider.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        self.slider_label = QLabel(f"Line Y Position: {self.detector.line_y}")
        self.slider_label.setAlignment(Qt.AlignCenter)
        self.slider_label.setFixedWidth(150)

        #self.apply_button = QPushButton("Apply")
        #self.apply_button.setFixedWidth(100)
        #self.apply_button.clicked.connect(self.update_line_y)
        self.line_y_slider.valueChanged.connect(self.update_line_y)
        
 
        
        slider_layout.addWidget(self.slider_label)
        slider_layout.addWidget(self.line_y_slider)
        #slider_layout.addWidget(self.apply_button)
        
        self.offset_slider = QSlider(Qt.Horizontal)
        self.offset_slider.setMinimum(0)
        self.offset_slider.setMaximum(150)
        self.offset_slider.setValue(self.detector.offset)
        self.offset_slider.setTickInterval(10)
        self.offset_slider.setFixedWidth(300)
        self.offset_slider.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        self.offset_label = QLabel(f"Offset: {self.detector.offset}")
        self.offset_label.setAlignment(Qt.AlignCenter)
        self.offset_label.setFixedWidth(150)

        self.offset_slider.valueChanged.connect(self.update_offset)

        slider_layout.addWidget(self.offset_label)
        slider_layout.addWidget(self.offset_slider)
        
        
        # Add Slider Layout under Camera View
        layout.addLayout(slider_layout)
        
        # Spacer to push to left side
        #offset_slider_layout.addStretch()
        
        # Add the Offset Slider Layout
        #layout.addLayout(offset_slider_layout)

        
        # Spacer to push to left side
        slider_layout.addStretch()
        
        self.setLayout(layout)
        
        

        # Table for Logs
        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(["Entry Counter", "Entry Time", "Exit Counter", "Exit Time", "Plate Number", "Snapshot"])
        layout.addWidget(self.table)
        
        # Set font for column headers
        header_font = QFont("Arial", 10, QFont.Bold)  # Set font family, size, and weight for headers
        self.table.horizontalHeader().setFont(header_font)
        
        # Set font for all table items
        font = QFont("Arial", 10, QFont.Normal)  # Set font for table items
        self.table.setFont(font)
        
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.verticalHeader().setVisible(False)

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # Column 0 resizes to content
        header.setSectionResizeMode(1, QHeaderView.Stretch)           # Column 1 stretches
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Column 2 resizes to content
        header.setSectionResizeMode(3, QHeaderView.Stretch)           # Column 3 stretches      
        #header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Column 2 resizes to content
        


        self.setLayout(layout)
        
        # Initialize the settings manager
        self.settings_manager = SettingsManager()
        self.load_settings()
        
        # Connect sliders to update functions
        self.line_y_slider.valueChanged.connect(lambda value: self.update_settings(value, self.offset_slider.value()))
        self.offset_slider.valueChanged.connect(lambda value: self.update_settings(self.line_y_slider.value(), value))
        
        # Load saved settings or use default values
        settings = self.settings_manager.load_settings()
        self.line_y_value = settings["line_y"]
        self.offset_value = settings["offset"]

    def update_video_feed(self):
        ret, frame = self.detector.cap.read()
        if ret:
            self.detector.process_frame(frame)
            print(f"Entry Counter: {self.detector.entry_counter}, Exit Counter: {self.detector.exit_counter}")
            height, width, _ = frame.shape
            byte_array = frame.tobytes()
            qimg = QImage(byte_array, width, height, QImage.Format_BGR888)
            pixmap = QPixmap.fromImage(qimg)
            self.live_feed_entry_label.setPixmap(pixmap.scaled(self.live_feed_entry_label.size(), Qt.KeepAspectRatio))
            self.total_entries_label.setText(f"Total Entries\n{self.detector.entry_counter}")
            self.total_exits_label.setText(f"Total Exits\n{self.detector.exit_counter}")
            
            # Get the current date and time for entry and exit in IST
            current_time = get_india_time()
            
            # Set the entry time when the entry counter increases
            if self.detector.entry_counter > self.last_entry_counter:
                self.last_entry_counter = self.detector.entry_counter
                self.entry_time_label.setText(f"Entry Time: {current_time}")
                
                # Add the entry details to the table
                self.add_vehicle_to_table(self.detector.vehicle_ids, current_time, "Entry")
                
            
            # Set the exit time when the exit counter increases
            if self.detector.exit_counter > self.last_exit_counter:
                self.last_exit_counter = self.detector.exit_counter
                self.exit_time_label.setText(f"Exit Time: {current_time}")
                
                # Add the exit details to the table
                self.add_vehicle_to_table(self.detector.vehicle_ids, current_time, "Exit")

            if self.detector.vehicle_ids:
                last_vehicle_id = list(self.detector.vehicle_ids.keys())[-1]
                self.plate_number_label.setText(f"Plate Number: {last_vehicle_id}")
                
                vehicle_snapshot = self.detector.get_last_vehicle_snapshot()
                self.display_snapshot(vehicle_snapshot)
  
    
    def add_vehicle_to_table(self, vehicle_ids, current_time, entry_or_exit):
        if vehicle_ids:
            last_vehicle_id = list(vehicle_ids.keys())[-1]  # Get the last vehicle ID (Plate Number)

            # Insert a new row in the table
            row_position = self.table.rowCount()
            self.table.insertRow(row_position)
            
            print(f"Added new row for {last_vehicle_id} at row {row_position}")

            # Set the plate number in the first column
            self.table.setItem(row_position, 0, QTableWidgetItem(str(self.detector.entry_counter)))

            # Set the entry/exit time in the second columns
            if entry_or_exit == "Entry":
                self.table.setItem(row_position, 1, QTableWidgetItem(current_time))
                self.table.setItem(row_position, 2, QTableWidgetItem("-"))  # Exit time is empty for entry
            else:
                self.table.setItem(row_position, 1, QTableWidgetItem("-"))  # Entry time is empty for exit
                
            # Set the exit counter in the third column (Exit Counter)
            self.table.setItem(row_position, 2, QTableWidgetItem(str(self.detector.exit_counter)))    

            # Set the snapshot in the fourth column (if there's a snapshot)
            if entry_or_exit == "Exit":
                self.table.setItem(row_position, 3, QTableWidgetItem(current_time))
                self.table.setItem(row_position, 1, QTableWidgetItem("-"))  # Entry time is empty for exit

            # Set the plate number in the fifth column (Plate Number)
            self.table.setItem(row_position, 4, QTableWidgetItem(last_vehicle_id))

            # Set the snapshot in the sixth column (Snapshot)
            vehicle_snapshot = self.detector.get_last_vehicle_snapshot()
            if vehicle_snapshot:
                image = QImage.fromData(vehicle_snapshot)
                pixmap = QPixmap.fromImage(image)
                snapshot_label = QLabel()
                snapshot_label.setAlignment(Qt.AlignCenter)
                # Stretch to fill the available cell space
                snapshot_label.setScaledContents(True)
                snapshot_label.setPixmap(pixmap) 
                #snapshot_label.setPixmap(pixmap.scaled(95, 95, Qt.KeepAspectRatio))  # Resize snapshot if needed
                self.table.setCellWidget(row_position, 5, snapshot_label)  # Set snapshot in the last column
                # Stretch the row height to fit the image (adjust according to your needs)
                self.table.setRowHeight(row_position, max(pixmap.height(), 95))
                # Ensure the column stretches too, if needed
                self.table.setColumnWidth(5, max(pixmap.width(), self.table.columnWidth(5)))
                # Set QSizePolicy for better resizing behavior
                snapshot_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
                # Adjust row height to match the snapshot size
                #self.table.setRowHeight(row_position,  45)
            
            


    
    
    
    def display_snapshot(self, snapshot_blob):
        if snapshot_blob:
            image = QImage.fromData(snapshot_blob)
            pixmap = QPixmap.fromImage(image)
            self.snapshot_image_label.setPixmap(pixmap.scaled(self.snapshot_image_label.size(), Qt.KeepAspectRatio))



    def change_entry_camera(self, event):
        dialog = CameraSelectionDialog(self)
        if dialog.exec() == QDialog.Accepted:
            selected_camera = dialog.get_selected_camera()
            self.detector.update_video_source(selected_camera)  # Update vehicle detection camera
        
    def open_camera_selection(self, camera_type):
        dialog = CameraSelectionDialog(self)
        if dialog.exec() == QDialog.Accepted:
            selected_camera = dialog.get_selected_camera()
            self.assign_camera(camera_type, selected_camera)
            
    def assign_camera(self, camera_type, camera_index):
    # Update the camera capture based on the type
        if camera_type == "entry":
            self.detector.update_video_source(camera_index)  # Update vehicle detection source
            self.entry_cap = cv2.VideoCapture(camera_index)  # Optional: keep local reference 
              
    def update_line_y(self):
        new_value = self.line_y_slider.value()
        self.detector.line_y = new_value
        self.slider_label.setText(f"Line Y Position: {new_value}")
        print(f"Updated line_y to: {new_value}")        
        # Save the updated settings to file
        self.settings_manager.save_settings(new_value, self.offset_slider.value(), self.detector.camera_index)    

    def update_offset(self):
        new_value = self.offset_slider.value()
        self.detector.offset = new_value
        self.offset_label.setText(f"Offset: {new_value}")
        print(f"Updated offset to: {new_value}")    
        # Save the updated settings to file
        self.settings_manager.save_settings(self.line_y_slider.value(), new_value, self.detector.camera_index)

    

    def load_settings(self):
        # Load persisted settings
        settings = self.settings_manager.load_settings()
        global line_y, offset
        line_y = settings.get("line_y", 500)
        offset = settings.get("offset", 20)

        # Apply to sliders
        self.line_y_slider.setValue(line_y)
        self.offset_slider.setValue(offset)

    def update_settings(self, new_line_y, new_offset):
        # Update global values and persist
        global line_y, offset
        line_y = new_line_y
        offset = new_offset
        self.settings_manager.save_settings(line_y, offset)
        
        # Debugging
        print(f"Settings updated: line_y = {line_y}, offset = {offset}")