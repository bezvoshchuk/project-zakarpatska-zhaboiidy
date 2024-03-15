from __future__ import annotations

import argparse
import datetime
from collections import UserDict
from datetime import date
import json
import warnings
import re

from utils import get_birthdays_per_days

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


class Email(Field):
    def __init__(self, email: str):
        validated_email = self.validate_email(email)
        super().__init__(value=validated_email)

    @staticmethod
    def validate_email(email: str):
        """Validate email, raises ValueError if email is not valid"""
        try:
            pattern = r'^[\w\.-]+@[a-zA-Z\d\.-]+\.[a-zA-Z]{2,}$'
            if re.match(pattern, email):
                return email
            else:
                raise ValueError

        except ValueError as e:
            raise ValueError(f"Email is not valid, entered: {email}") from e


class Record:
    def __init__(self, name_: str, phones: list[str] = None, birthday: date = None, address: date = None,
                 email: date = None):
        self.name: Name = Name(name_)
        self.phones: list[Phone] = [
            Phone(phone) for phone in (phones or [])
        ]
        self.birthday = (
            Birthday(birthday) if birthday is not None else None
        )
        self.address: Address = Address(address)
        self.email = (
            Email(email) if email is not None else None
        )

    def __hash__(self):
        return hash(self.name.value)

    def __eq__(self, other):
        return self.name.value == other.self.value

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

    def search_phone(self, query: str):
        """Find phone record by search query.

        Args:
            query: Search query

        Returns:
            A first phone object match if any.
        """
        # The query is too long, phone has 10 chars at max
        if len(query) > 10:
            return

        for _phone in self.phones:
            if re.search(query, _phone.value) is not None:
                return _phone

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

    def add_email(self, email_str: str):
        """Add email to record, overwrite if already exists."""
        self.email = Email(email_str)

    def remove_email(self):
        """Remove email from record."""
        self.email = None

    def update_email(self, new_email: str):
        """Update email in record.

        Raises:
            ValueError: if email is invalid.
        """
        self.email = Email(new_email)

    def remove_address(self):
        """Remove address from record."""
        self.address = None

    def update_address(self, new_address: str):
        """Update address in record."""
        self.address = Address(new_address)

    def remove_birthday(self):
        """Remove birthday from record."""
        self.birthday = None

    def update_birthday(self, new_birthday: str):
        """Update birthday in record.

        Raises:
            ValueError: if birthday is invalid.
        """
        self.birthday = Birthday(new_birthday)

    def __str__(self):
        return (
            f"Contact name: {self.name.value}, "
            f"contact email: {self.email.value} "
            f"phones: {'; '.join(p.value for p in self.phones)}"
        )


class AddressBook(UserDict):
    data: dict[str, Record] = {}

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
                "address": str(_record.address),
                "email": str(_record.email)
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

    def get_birthdays_per_days(self, days) -> dict[str, list[Record]]:
        """Returns a list of records for users that have BD in a following week."""
        return get_birthdays_per_days(list(self.data.values()), days)

    def search_by_number(self, number_query: str) -> list[Record]:
        """Find all records in address book by number query.

        Args:
            number_query: Number search term

        Returns:
            All matched records if any.
        """
        results = [
            record for record in self.data.values()
            if record.search_phone(number_query)
        ]

        # Advanced search will make too much false positives if input term is too short.
        if not results and len(number_query) > 3:
            results = set()

            for char in number_query:
                # Replace a single search character with any digit to account for input error
                updated_query = number_query.replace(char, r"\d")
                results.update([
                    record for record in self.data.values()
                    if record.search_phone(updated_query)
                ])

        return list(results)

    def search_by_name_or_email(self, query: str):
        """Find all records in address book by number query.

        Args:
            query: Search term

        Returns:
            All matched records if any.
        """
        results = [
            record for record in self.data.values()
            if (
                query in record.name.value
                or query in record.email.value
            )
        ]

        # Advanced search will make too much false positives if input term is too short.
        if not results and len(query) > 3:
            results = set()

            try:
                re.compile(query)
            except re.error:
                # String cannot be used as a regex pattern, because of some bad characters.
                return []

            for char in query:
                updated_query = query.replace(char, ".")
                results.update([
                    record for record in self.data.values()
                    if (
                        re.search(updated_query, record.name.value) is not None
                        or re.search(updated_query, record.email.value) is not None
                    )
                ])

        return list(results)

    def search(self, query: str) -> list[Record]:
        """Find all records in address book that meet search criteria.

        Args:
            query: Username of the user to find.

        Returns:
            A list of all found records.
        """
        # The input query is a number
        if len(query) <= 10 and all(c.isdigit() for c in query):
            return self.search_by_number(query)

        # The input query is a name or an email
        return self.search_by_name_or_email(query)

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
