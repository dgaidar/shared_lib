from os import path
import json
from pathlib import Path


class History:
    """Adds history functionality to a control"""
    def __init__(self, file_name, limit=None):
        self.history_file = file_name
        self.values = self.load()
        self.limit = limit

    def load(self):
        """Load history from file"""
        if path.exists(self.history_file):
            with open(self.history_file, "r") as file:
                return json.load(file)
        return []

    def save(self):
        """Dump to file"""
        parent = Path(self.history_file).parent
        if not parent.is_dir():
            parent.mkdir()
        with open(self.history_file, "w") as file:
            json.dump(self.values, file)

    def update(self, record):
        """Update LRU"""
        if record in self.values:
            self.values.remove(record)
        self.values.append(record)

        if self.limit and len(self.values) > self.limit:
            self.history = self.values[-self.limit:]

        self.save()