import json
import os


DEFAULT_SETTINGS_FILE = 'settings.json'


class Settings:
    """Simple key-value dictionary stored in a file"""
    _instance = None

    def __new__(cls, file_path=DEFAULT_SETTINGS_FILE):
        """Initialize a singleton"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.file_path = file_path
            data = {"default": {}, "current": {}}
            if os.path.exists(file_path):
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                except Exception as e:
                    print(f"Error reading {file_path}: {e}")
            else:
                print(f"Not found: {file_path}")
            cls._instance.default = data["default"]
            cls._instance.current = data["current"]
        return cls._instance

    def get(self, field, default_val=None):
        """Get value by key"""
        if field in self.current:
            return self.current[field]
        if field in self.default:
            return self.default[field]
        return default_val

    def set(self, field, value):
        """Set value for a key"""
        self.current[field] = value
        self.dump()

    def dump(self) -> None:
        """Save all values"""
        with open(self.file_path, "w") as file:
            json.dump({"default": self.default, "current": self.current}, file, indent=2)

