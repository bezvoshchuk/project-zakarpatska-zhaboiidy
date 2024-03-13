from __future__ import annotations

import argparse
import datetime
from collections import UserDict
from datetime import date
import json
import warnings


from utils import get_birthdays_per_week


DATE_FORMAT = "%Y.%m.%d"
JSON_DB_PATH = "./users.json"


argument_parser = argparse.ArgumentParser(
    description=(
        "The script that displays work of added data classes. Can be run in two modes: "
        "default and db_mode, controlled by db_mode parameter. In db_mode address book will"
        "work with users.json file reading and adding data to it."
    )
)
argument_parser.add_argument(
    "--db_mode",
    dest="db_mode",
    type=str,
    default=False,
    required=False,
    help="Set this to true if you want to switch to db mode."
)
argument_parser.add_argument(
    "--reset_data",
    dest="reset_data",
    type=str,
    default=False,
    required=False,
    help="Set this to true if you want to reset db data."
)


class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class Name(Field):
    pass


class Birthday(Field):
    def __init__(self, value):
        validated_date = self.validate_date(value)
        super().__init__(value=validated_date)

    @staticmethod
    def validate_date(date_str: str) -> date:
        """Validate date string, raises ValueError if date cannot be parsed"""
        try:
            return datetime.datetime.strptime(date_str, DATE_FORMAT).date()
        except Exception:
            raise ValueError(f"Provided date {date_str} should follow format {DATE_FORMAT}, aborting ...")

    def __str__(self):
        return self.value.strftime(DATE_FORMAT)


class Phone(Field):
    def __init__(self, phone: str):
        validated_phone = self.validate_phone(phone)
        super().__init__(value=validated_phone)

    @staticmethod
    def validate_phone(phone: str):
        """Validate phone number, raises ValueError if phone length is less than 10 digits"""
        try:
            if len(phone) != 10:
                raise ValueError

            for char in phone:
                if not char.isdigit():
                    raise ValueError
        except ValueError as e:
            raise ValueError(f"Phone should have 10 digits, entered: {phone}") from e

        return phone
    

class Address(Field):
    def __init__(self, address: str):
        self.address = address
        super().__init__(value=address)


class Record:
    def __init__(self, name_: str, phones: list[str] = None, birthday: date = None, address: date = None):
        self.name: Name = Name(name_)
        self.phones: list[Phone] = [
            Phone(phone) for phone in (phones or [])
        ]
        self.birthday = (
            Birthday(birthday) if birthday is not None else None
        )
        self.address: Address = Address(address)

    def add_birthday(self, birthday_str: str):
        """Add birthday to record, overwrite if already exists."""
        self.birthday = Birthday(birthday_str)

    def add_phone(self, phone: str):
        """Add phone to record if not already present.

        Args:
            phone: Phone number to add.
        """
        try:
            self.find_phone(phone)
            warnings.warn(f"phone {phone} was already present for user {self.name}, skipping ...")
        except KeyError:
            self.phones.append(Phone(phone))

    def find_phone(self, phone: str):
        """Find phone record by value.

        Args:
            phone: Phone number to find.

        Raises:
            KeyError: if phone does not exist.

        Returns:
            A Phone object that is identical to the one being looked up.
        """
        for _phone in self.phones:
            if _phone.value == phone:
                return _phone
        else:
            raise KeyError(f"Phone {phone} is not present for user {self.name}")

    def remove_phone(self, phone: str):
        """Remove phone from record.

        Args:
            phone: Phone number to add.

        Raises:
            KeyError: if phone does not exist.
        """
        _phone = self.find_phone(phone)
        self.phones.remove(_phone)

    def edit_phone(self, phone: str, new_phone: str):
        """Edit phone record.

        Args:
            phone: Phone number value to edit.
            new_phone: Phone number value to change to.

        Raises:
            KeyError: if phone does not exist.
        """
        _phone = Phone.validate_phone(new_phone)

        self.remove_phone(phone)
        self.add_phone(_phone)
    
    def add_address(self, address_str: str):
        """Add address to record, overwrite if already exists."""
        self.address = Address(address_str)

    def __str__(self):
        return f"Contact name: {self.name.value}, phones: {'; '.join(p.value for p in self.phones)}"


class AddressBook(UserDict):
    data = {}

    def print_book(self):
        for name, record in self.data.items():
            print(record)

    def load_data_from_json(self, json_data):
        self.data = {
            _record_data["name_"]: Record(**_record_data)
            for _record_data in json_data
        }

    def dump_data_to_json(self):
        return [
            {
                "name_": _record.name.value,
                "phones": [phone.value for phone in _record.phones],
                "birthday": str(_record.birthday),
                "address": str(_record.address)
            }
            for _record in self.data.values()
        ]

    def add_record(self, record_: Record) -> Record | None:
        """Add a record to an address book if not already present.

        Args:
            record_: Record to add.
        """
        if record_.name.value not in self.data:
            self.data[record_.name.value] = record_
            return record_

    def get_birthdays_per_week(self) -> dict[str, list[Record]]:
        """Returns a list of records for users that have BD in a following week."""
        return get_birthdays_per_week(list(self.data.values()))

    def find(self, name_: str) -> Record:
        """Find a record in address book by username.

        Args:
            name_: Username of the user to find.

        Raises:
            KeyError: if record doesn't exist.
        """
        if name_ not in self.data:
            raise KeyError(f"Record for user {name_} was not found.")

        return self.data[name_]

    def delete(self, name_: str) -> None:
        """Delete a record in address book by username.

        Args:
            name_: Username of the user to find.

        Raises:
            KeyError: if record doesn't exist.
        """
        _record = self.find(name_)
        del self.data[name_]


class AddressBookReader:
    address_book: None | AddressBook = None

    def __enter__(self):
        self.address_book = AddressBook()
        self.load_existing_users()
        return self.address_book

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.save_existing_users()

    def load_existing_users(self):
        """Load existing data from JSON_DB_PATH, fallback to empty list, if file not present."""
        users_data = []

        try:
            print("Loading existing users data ...")
            json_in = open(JSON_DB_PATH, "r")
            users_data = json.load(json_in)
            json_in.close()
        except FileNotFoundError:
            print("Users data file don't exist, returning empty list ...")

        self.address_book.load_data_from_json(users_data)

    def save_existing_users(self):
        """Save existing data to JSON_DB_PATH."""
        with open(JSON_DB_PATH, "w") as json_out:
            print("Saving existing users data ...")
            json.dump(self.address_book.dump_data_to_json(), json_out)
