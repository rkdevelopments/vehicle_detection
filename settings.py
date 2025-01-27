import json
import os



class SettingsManager:
    def __init__(self, file_path='settings.json'):
        self.file_path = file_path

    def load_settings(self):
        """Load the settings from the file if it exists, otherwise return default values."""
        try:
            if os.path.exists(self.file_path):
                with open(self.file_path, 'r') as f:
                    settings = json.load(f)
                
                # Validate and return settings, ensure the values are correct
                line_y = settings.get("line_y", 500)
                offset = settings.get("offset", 20)
                camera_index = settings.get("camera_index", 0)

                # Ensure values are within expected range
                settings["line_y"] = max(0, min(line_y, 750))  # Clamp line_y between 0 and 750
                settings["offset"] = max(0, min(offset, 150))  # Clamp offset between 0 and 150

                return settings
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error loading settings: {e}")

        # Return default if any issue occurs
        return {"line_y": 500, "offset": 20, "camera_index": 0}

    def save_settings(self, line_y, offset, camera_index):
        """Save the current settings to the file."""
        try:
            settings = {
                "line_y": max(0, min(line_y, 750)),  # Clamp value
                "offset": max(0, min(offset, 150)),
                "camera_index": camera_index
            }
            with open(self.file_path, 'w') as f:
                json.dump(settings, f, indent=4)
            print("Settings saved successfully.")
        except IOError as e:
            print(f"Error saving settings: {e}")
