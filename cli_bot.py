from __future__ import annotations

import re
from typing import Any
from functools import wraps

from datamodels import AddressBookReader, AddressBook, Record


class BaseCliHelperException(Exception):
    """This is a generic Cli Helper exception."""


class CommandNotSupported(BaseCliHelperException):
    """This exception is to be raised when Cli Helper encounters a non-supported command."""


class CliHelperSigStop(BaseCliHelperException):
    """This exception is to be raised whenever we need to immediately stop the bot."""


class CommandOperationalError(BaseCliHelperException):
    """This exception is raised whenever we try to do an operation that is not allowed."""


def input_error(error_msg_base):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except (CommandOperationalError, CommandNotSupported, ValueError) as e:
                return f"{error_msg_base}: {e}"

        return wrapper
    return decorator


class CliHelperBot:
    _address_book: AddressBook = None

    def __init__(self, address_book: AddressBook):
        self.supported_commands = {
            "close": self.stop,
            "exit": self.stop,
            "hello": self.say_hello,
            "add": self.add_contact,
            "change": self.change_contact,
            "phone": self.get_contact,
            "search": self.search_contact,
            "all": self.print_all_contacts,
            "add-birthday": self.add_birthday,
            "show-birthday": self.show_birthday,
            "birthdays": self.birthdays,
            "add-address": self.add_address,
            "add-email": self.add_email,
        }
        self._address_book = address_book

    def stop(self, message: str):
        """Stop the bot execution.

        Args:
            message: Explanation why bot needs to stop

        Raises:
            CliHelperSigStop: with explanation message
        """
        raise CliHelperSigStop(message)

    @staticmethod
    def parse_input(user_input: str) -> (str, list[Any]):
        command, *args = user_input.split()
        command = command.casefold()

        if command in ["close", "exit"]:
            args = [f"Command '{command}' received. Good buy!"]

        return command, args

    @staticmethod
    def say_hello(*args: str) -> str:
        """Outputs a hello message for user."""
        command_output = ""
        if args:
            command_output += (
                "Warning: Command doesn't expect any arguments. "
                f"Received: {' '.join(args)}\n"
            )

        return command_output + "How can I help you?"

    @input_error(error_msg_base="Command 'add-birthday' failed")
    def add_birthday(self, *args: str) -> str:
        """Add birthday date to already existing record.

        Args:
            args: List with username and date to parse.

        Returns:
            Command output

        Raises:
            CommandOperationalError if user does not exist.
            ValueError if date is invalid.
        """
        if len(args) != 2:
            raise CommandOperationalError(
                "command expects an input of two arguments: username and date, separated by a space. "
                f"Received: {' '.join(args)}"
            )
        username, date_str = args
        try:
            record = self._address_book.find(username)

        except KeyError as e:
            raise CommandOperationalError(
                f"user with username {username} doesn't exist. "
                f"If you want to add number, please use 'add' command."
            ) from e

        record.add_birthday(date_str)
        return f"Contact {username} updated with date: {date_str}."

    @input_error(error_msg_base="Command 'add' failed")
    def add_contact(self, *args: str) -> str:
        """Add contact into Address Book.

        Args:
            args: List with username and phone of user to add.

        Returns:
            Command output.

        Raises:
            CommandOperationalError: if wrong arguments or user already exist
        """
        if len(args) != 2:
            raise CommandOperationalError(
                "command expects an input of two arguments: username and phone, separated by a space. "
                f"Received: {' '.join(args)}"
            )

        username, phone = args
        record = self._address_book.add_record(
            Record(
                name_=username,
                phones=[phone]
            )
        )

        if record is None:
            raise CommandOperationalError(
                f"user with username {username} already exist. "
                f"If you want to update number, please use 'change' command."
            )

        return f"Contact {username} created with phone: {phone}."

    @input_error(error_msg_base="Command 'update' failed")
    def change_contact(self, *args: str) -> str:
        """Change contact in Address Book.

        Args:
            args: List with username and phone of user to add.

        Returns:
            Command output.

        Raises:
            CommandOperationalError: if wrong arguments or user doesn't exist
        """
        if len(args) != 2:
            raise CommandOperationalError(
                "command expects an input of two arguments: username and phone, separated by a space. "
                f"Received: {' '.join(args)}"
            )

        username, phone = args
        try:
            record = self._address_book.find(username)

        except KeyError as e:
            raise CommandOperationalError(
                f"user with username {username} doesn't exist. "
                f"If you want to add number, please use 'add' command."
            ) from e

        record.edit_phone(record.phones[0].value, phone)
        return f"Contact {username} updated with phone: {phone}."

    @input_error(error_msg_base="Command 'show-birthday' failed")
    def show_birthday(self, *args: str) -> str:
        """Get user birthday by username.

        Args:
            args: List of one argument - username

        Returns:
            Command output.

        Raises:
            CommandOperationalError: if wrong arguments or user doesn't exist
        """
        if len(args) != 1:
            raise CommandOperationalError(
                "command expects an input of one argument: username. "
                f"Received: {' '.join(args)}"
            )

        username = args[0]
        try:
            record = self._address_book.find(username)

        except KeyError as e:
            raise CommandOperationalError(
                f"user with username {username} doesn't exist. Try another username."
            ) from e

        return f"User's {username} birthday is: {record.birthday}"

    @input_error(error_msg_base="Command 'search' failed")
    def search_contact(self, *args: str) -> str:
        """Search user data by search query.

        Args:
            args: List of one argument - search query

        Returns:
            Command output.

        Raises:
            CommandOperationalError: if wrong arguments
        """
        if len(args) != 1:
            raise CommandOperationalError(
                "command expects an input of one argument: search query. "
                f"Received: {' '.join(args)}"
            )

        query = args[0]
        records = self._address_book.search(query)

        if not records:
            return "No records found with provided query."

        command_output = "Found Records: "
        for record in records:
            command_output += f"\n{record}"

        return command_output

    @input_error(error_msg_base="Command 'phone' failed")
    def get_contact(self, *args: str) -> str:
        """Get user phone by username.

        Args:
            args: List of one argument - username

        Returns:
            Command output.

        Raises:
            CommandOperationalError: if wrong arguments or user doesn't exist
        """
        if len(args) != 1:
            raise CommandOperationalError(
                "command expects an input of one argument: username. "
                f"Received: {' '.join(args)}"
            )

        username = args[0]
        try:
            record = self._address_book.find(username)

        except KeyError as e:
            raise CommandOperationalError(
                f"user with username {username} doesn't exist. Try another username."
            ) from e

        return f"Record found: \n{record}"

    @input_error(error_msg_base="Command 'birthdays' failed")
    def birthdays(self, *args: str) -> str:
        """Prepares all contacts to be outputted into console that have BD in a following week.

        Args:
            args: Command doesn't expect any args, list should be empty.

        Returns:
            Command output.
        """
        command_output = ""
        if len(args) != 1:
            raise CommandOperationalError (
                "Warning: Command expect one argument: number of days. "
                f"Received: {' '.join(args)}\n"
            )
        days = int(args[0])

        results = self._address_book.get_birthdays_per_days(days).items()
        if not results:
            return "No contacts found"

        command_output += "Contacts per day: "
        for date, records in results:
            records_str = '| ' + '\n | '.join(str(r) for r in records)
            command_output += f"\nHave BD on {date}:\n {records_str}"

        return command_output

    def print_all_contacts(self, *args: str) -> str:
        """Prepares contacts to be outputted into console.

        Args:
            args: Command doesn't expect any args, list should be empty.

        Returns:
            Command output.
        """
        command_output = ""
        if args:
            command_output += (
                "Warning: Command doesn't expect any arguments. "
                f"Received: {' '.join(args)}\n"
            )

        command_output += "All Records: "
        for record in self._address_book.values():
            command_output += f"\n{record}"

        return command_output

    @input_error(error_msg_base="Command execution failed")
    def execute_command(self, command: str, args: list[str]) -> str:
        if command not in self.supported_commands:
            raise CommandNotSupported(f"command '{command}' is not supported!")

        command_handler = self.supported_commands[command]
        return command_handler(*args)

    @input_error(error_msg_base="Command 'add-address' failed")
    def add_address(self, *args: str):
        """Add address to already existing record.

        Args:
            args: List with username and address.

        Returns:
            Command output

        Raises:
            CommandOperationalError if user does not exist.
            ValueError if date is invalid.
        """
        if len(args) != 2:
            raise CommandOperationalError(
                "command expects an input of two arguments: username and address, separated by a space. "
                f"Received: {' '.join(args)}"
            )
        username, address_str = args
        try:
            record = self._address_book.find(username)

        except KeyError as e:
            raise CommandOperationalError(
                f"user with username {username} doesn't exist. "
                f"If you want to add address, please use 'add-address' command."
            ) from e

        record.add_address(address_str)
        return f"Contact {username} updated with address: {address_str}."
    
    @input_error(error_msg_base="Command 'add-email' failed")
    def add_email(self, *args: str):
        """Add email to already existing record.

        Args:
            args: List with username and email.

        Returns:
            Command output

        Raises:
            CommandOperationalError if user does not exist.
            ValueError if date is invalid.
        """
        if len(args) != 2:
            raise CommandOperationalError(
                "command expects an input of two arguments: username and email, separated by a space. "
                f"Received: {' '.join(args)}"
            )
        username, email_str = args
        try:
            record = self._address_book.find(username)

        except KeyError as e:
            raise CommandOperationalError(
                f"user with username {username} doesn't exist. "
                f"If you want to add email, please use 'add-email' command."
            ) from e

        record.add_email(email_str)
        return f"Contact {username} updated with email: {email_str}."

    def main(self) -> None:
        while True:
            try:
                user_input = input("Enter a command with arguments separated with a ' ' character: ")

                command, args = self.parse_input(user_input)
                command_output = self.execute_command(command, args)
                print(
                    f"Command '{command}' executed successfully. Result is:"
                    f"\n{command_output}"
                )

            except CliHelperSigStop as e:
                print(e)
                break

            except Exception as e:
                print(
                    f"Unknown exception was encountered during execution: {e}"
                    "The bot will stop ..."
                )
                raise


if __name__ == "__main__":
    with AddressBookReader() as book:
        cli_helper = CliHelperBot(book)
        cli_helper.main()
