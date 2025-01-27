import cv2
import numpy as np
from ultralytics import YOLO
import sqlite3
import time
import pytz
from datetime import datetime, timezone
from camera_selection import CameraSelectionDialog
from settings import SettingsManager

class VehicleDetection1:
    def __init__(self, db_name='cam1.db',camera_index=0, video_path='videos/vid1.mp4', model_path='yolov8n.pt'):
        
        self.settings_manager = SettingsManager()  # Initialize settings manager
        settings = self.settings_manager.load_settings()  # Load settings
        
        self.db_name = db_name
        self.video_path = video_path
        self.model_path = model_path
        
        #self.camera_index = camera_index
        self.camera_index = settings.get('camera_index', 0)  # Default to camera 0 if not set
        
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()
        self._create_table()

        self.model = YOLO(self.model_path)
        self.cap = cv2.VideoCapture(camera_index)

        if not self.cap.isOpened():
            raise Exception("Error: Could not open video.")

        self.vehicle_classes = [2, 3, 5, 7]
        self.entry_counter = 0
        self.exit_counter = 0
        self.line_y = 500
        self.offset = 20
        self.centroid_margin = 30
        self.timeout_seconds = 2
        self.vehicle_ids = {}
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        
        # Ensure fps is not zero, use a default value if it is
        if self.fps == 0:
            self.fps = 30  # Default fps value, adjust as needed
        self.delay = int(1000 / self.fps)
        

    def update_video_source(self, camera_index):
        if self.cap.isOpened():
            self.cap.release()  # Release the current camera
        self.cap = cv2.VideoCapture(camera_index)  # Open the new camera
        if not self.cap.isOpened():
            print(f"Failed to open camera {camera_index}")
        else:
            print(f"Camera switched to {camera_index}")
    
    
    def _create_table(self):
        self.cursor.execute(''' 
        CREATE TABLE IF NOT EXISTS vehicle_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            entry_count INTEGER,
            exit_count INTEGER,
            entry_time TEXT,
            exit_time TEXT,
            vehicle_snapshot BLOB
        )''')
        self.conn.commit()

    def image_to_blob(self, image):
        _, buffer = cv2.imencode('.jpg', image)
        return buffer.tobytes()

    def process_frame(self, frame):
        results = self.model(frame)
        current_time = cv2.getTickCount() / cv2.getTickFrequency()

        for result in results:
            detections = result.boxes

            for det in detections:
                x1, y1, x2, y2 = det.xyxy[0].tolist()
                conf = det.conf[0].item()
                cls = int(det.cls[0].item())

                if cls in self.vehicle_classes and conf > 0.5:
                    cx, cy = int((x1 + x2) / 2), int((y1 + y2) / 2)
                    cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
                    cv2.circle(frame, (cx, cy), 5, (255, 0, 0), -1)

                    if self.line_y - self.offset < cy < self.line_y + self.offset:
                        self.track_vehicle(cx, cy, x1, y1, x2, y2, frame, current_time)

        self.display_info(frame)

    def track_vehicle(self, cx, cy, x1, y1, x2, y2, frame, current_time):
        counted = False
        vehicle_id = None

        for vid, (px, py, last_time, prev_cy, direction) in self.vehicle_ids.items():
            if abs(cx - px) < self.centroid_margin and abs(cy - py) < self.centroid_margin:
                if current_time - last_time > self.timeout_seconds:
                    counted = False
                else:
                    counted = True
                    vehicle_id = vid
                    break

        if not counted:
            vehicle_id = len(self.vehicle_ids) + 1
            print(f"Vehicle ID: {vehicle_id}")

        if vehicle_id in self.vehicle_ids:
            _, _, _, prev_cy, prev_direction = self.vehicle_ids[vehicle_id]
            direction = 'Downward' if cy > prev_cy else 'Upward'

            if direction == 'Downward' and prev_direction != 'Downward':
                self.entry_counter += 1
                self.save_to_db(frame, x1, y1, x2, y2, entry=True, current_time=current_time)

            elif direction == 'Upward' and prev_direction != 'Upward':
                self.exit_counter += 1
                self.save_to_db(frame, x1, y1, x2, y2, entry=False, current_time=current_time)
        else:
            direction = 'Stationary'

        self.vehicle_ids[vehicle_id] = (cx, cy, current_time, cy, direction)
        cv2.putText(frame, f'ID: {vehicle_id} - {direction}', (int(x1), int(y1) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    def save_to_db(self, frame, x1, y1, x2, y2, entry, current_time):
        vehicle_region = frame[int(y1):int(y2), int(x1):int(x2)]
        snapshot_blob = self.image_to_blob(vehicle_region)
        
        # Use time.time() to get the current time in seconds (since epoch)
        current_time = time.time()

        # Convert the timestamp to UTC and then to IST (India Standard Time)
        utc_time = datetime.fromtimestamp(current_time, tz=timezone.utc)  # Convert to UTC time
        india_tz = pytz.timezone('Asia/Kolkata')  # IST timezone
        india_time = utc_time.astimezone(india_tz)  # Convert to IST
    
        # Format the time as a string
        event_time = india_time.strftime('%Y-%m-%d %H:%M:%S')  # Save time in 'YYYY-MM-DD HH:MM:SS' format

        self.cursor.execute('''INSERT INTO vehicle_data (entry_count, exit_count, entry_time, exit_time, vehicle_snapshot)
                               VALUES (?, ?, ?, ?, ?)''', 
                           (self.entry_counter if entry else None,
                            self.exit_counter if not entry else None,
                            event_time if entry else None,
                            event_time if not entry else None,
                            snapshot_blob))
        self.conn.commit()

    def display_info(self, frame):
        cv2.line(frame, (0, self.line_y), (frame.shape[1], self.line_y), (255, 0, 0), 2)
        cv2.putText(frame, f'Entry Count: {self.entry_counter}', (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
        cv2.putText(frame, f'Exit Count: {self.exit_counter}', (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
        #cv2.imshow('Vehicle Detection and Counting', frame)

    def run(self):
        while self.cap.isOpened():
            ret, frame = self.cap.read()
            if not ret:
                break
            self.process_frame(frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        self.cap.release()
        cv2.destroyAllWindows()
        self.conn.close()

    def get_last_vehicle_snapshot(self):
        self.cursor.execute("SELECT vehicle_snapshot FROM vehicle_data ORDER BY id DESC LIMIT 1")
        result = self.cursor.fetchone()
        if result:
            return result[0]
        return None
    
    def update_camera_index(self, camera_index):
        """Method to update camera index and save it to settings.json"""
        self.camera_index = camera_index
        self.cap.release()  # Release the current camera
        self.cap = cv2.VideoCapture(self.camera_index)  # Initialize the new camera
        if not self.cap.isOpened():
            print(f"Failed to open camera {camera_index}")
        else:
            print(f"Camera switched to {camera_index}")

        # Save the updated camera index to the settings file
        self.settings_manager.save_settings(self.line_y, self.offset, self.camera_index)

if __name__ == '__main__':
    detector1 = VehicleDetection1()
    detector1.run()
