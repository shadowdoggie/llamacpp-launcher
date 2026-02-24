import json
import os


class ProfileManager:
    def __init__(self, profiles_file="profiles.json"):
        self.profiles_file = profiles_file
        self.profiles = {}
        self.load_profiles()

    def load_profiles(self):
        if os.path.exists(self.profiles_file):
            try:
                with open(self.profiles_file, "r") as f:
                    self.profiles = json.load(f)
            except json.JSONDecodeError:
                self.profiles = {}
        else:
            self.profiles = {}

    def save_profiles(self):
        with open(self.profiles_file, "w") as f:
            json.dump(self.profiles, f, indent=4)

    def get_profile_names(self):
        return list(self.profiles.keys())

    def get_profile(self, name):
        return self.profiles.get(name)

    def save_profile(self, name, data):
        self.profiles[name] = data
        self.save_profiles()

    def delete_profile(self, name):
        if name in self.profiles:
            del self.profiles[name]
            self.save_profiles()

    def delete_all_profiles(self):
        self.profiles = {}
        self.save_profiles()
