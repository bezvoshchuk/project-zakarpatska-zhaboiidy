from __future__ import annotations

import json
import os

from source.datamodels import AddressBook, NotesBook
from source.utils import get_root_path


DATE_FORMAT = "%Y.%m.%d"
ROOT_PROJECT_PATH = get_root_path()
JSON_DB_PATH = os.path.join(ROOT_PROJECT_PATH, "users.json")
NOTES_JSON_DB_PATH = os.path.join(ROOT_PROJECT_PATH, "notes.json")


class BookReader:
    address_book: None | AddressBook = None
    notes_book: None | NotesBook = None

    def __enter__(self):
        self.notes_book = NotesBook()
        self.load_existing_notes()
        self.address_book = AddressBook()
        self.load_existing_users()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.save_existing_notes()
        self.save_existing_users()

    def load_existing_notes(self):
        """Load existing data from NOTES_JSON_DB_PATH, fallback to empty list, if file not present."""
        notes_data = []

        try:
            print("Loading existing notes data ...")
            with open(NOTES_JSON_DB_PATH, "r") as json_in:
                notes_data = json.load(json_in)
        except FileNotFoundError:
            print("Notes data file don't exist, returning empty list ...")
        except json.JSONDecodeError:
            print("Users data file is not a valid JSON, returning empty list ...")

        self.notes_book.load_data_from_json(notes_data)

    def save_existing_notes(self):
        """Save existing notes data to NOTES_JSON_DB_PATH."""
        with open(NOTES_JSON_DB_PATH, "w") as json_out:
            print("Saving existing notes data ...")
            json.dump(self.notes_book.dump_data_to_json(), json_out)

    def load_existing_users(self):
        """Load existing data from JSON_DB_PATH, fallback to empty list, if file not present."""
        users_data = []

        try:
            print("Loading existing users data ...")
            with open(JSON_DB_PATH, "r") as json_in:
                users_data = json.load(json_in)
        except FileNotFoundError:
            print("Users data file don't exist, returning empty list ...")
        except json.JSONDecodeError:
            print("Users data file is not a valid JSON, returning empty list ...")

        self.address_book.load_data_from_json(users_data)

    def save_existing_users(self):
        """Save existing data to JSON_DB_PATH."""
        with open(JSON_DB_PATH, "w") as json_out:
            print("Saving existing users data ...")
            json.dump(self.address_book.dump_data_to_json(), json_out)
