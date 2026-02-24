import json
import os

class SettingsManager:
    def __init__(self, settings_file="settings.json"):
        self.settings_file = settings_file
        self.settings = {}
        self.load_settings()

    def load_settings(self):
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r') as f:
                    self.settings = json.load(f)
            except json.JSONDecodeError:
                self.settings = {}
        else:
            self.settings = {}

    def save_settings(self):
        with open(self.settings_file, 'w') as f:
            json.dump(self.settings, f, indent=4)

    def get(self, key, default=None):
        return self.settings.get(key, default)

    def set(self, key, value):
        self.settings[key] = value
        self.save_settings()
