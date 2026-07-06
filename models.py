import json
import os
from datetime import datetime


class Item:
    def __init__(self, item_id, title, description, category, location,
                 date_posted, status="lost", image_path=None, posted_by=None):
        self.item_id = item_id
        self.title = title
        self.description = description
        self.category = category
        self.location = location
        self.date_posted = date_posted
        self.status = status          # "lost", "found", or "resolved"
        self.image_path = image_path
        self.posted_by = posted_by

    def to_dict(self):
        return self.__dict__

    @classmethod
    def from_dict(cls, data):
        return cls(**data)


class User:
    def __init__(self, user_id, username, email, phone, password_hash):
        self.user_id = user_id
        self.username = username
        self.email = email
        self.phone = phone
        self.password_hash = password_hash

    def to_dict(self):
        return self.__dict__

    @classmethod
    def from_dict(cls, data):
        return cls(**data)


class Database:
    def __init__(self, data_dir="data"):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        os.makedirs(os.path.join(data_dir, "images"), exist_ok=True)
        self.items_file = os.path.join(data_dir, "items.json")
        self.users_file = os.path.join(data_dir, "users.json")
        self._init_files()

    def _init_files(self):
        for f in [self.items_file, self.users_file]:
            if not os.path.exists(f):
                with open(f, 'w') as fh:
                    json.dump([], fh)

    def load_items(self):
        with open(self.items_file, 'r') as f:
            return [Item.from_dict(d) for d in json.load(f)]

    def save_items(self, items):
        with open(self.items_file, 'w') as f:
            json.dump([i.to_dict() for i in items], f, indent=2, default=str)

    def load_users(self):
        with open(self.users_file, 'r') as f:
            return [User.from_dict(d) for d in json.load(f)]

    def save_users(self, users):
        with open(self.users_file, 'w') as f:
            json.dump([u.to_dict() for u in users], f, indent=2, default=str)
