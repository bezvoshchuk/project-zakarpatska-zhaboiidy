from __future__ import annotations

from collections import defaultdict
import datetime
import os
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from datamodels import Record


def get_birthdays_per_days(users_data: list[Record], days) -> dict[str, list[Record]]:
    """This function will return dictionary with all users that have birthday in following next number of days.

    Args:
        users_data: List of user Records.
        days: Number of days to check for birthdays.

    Returns:
        A dictionary where key is date and value is list of user full names.
    """
    # Initial values and consts
    result = defaultdict(list)

    for record in users_data:
        if record.birthday.value is None or record.birthday.value == "None":
            continue

        birthday_date = record.birthday.value.replace(year=datetime.datetime.today().date().year)

        # Advance by one year if birthday already passed
        if datetime.datetime.today().date() > birthday_date:
            birthday_date = birthday_date.replace(year=datetime.datetime.today().date().year + 1)

        if (birthday_date - datetime.datetime.today().date()).days < days:
            result[birthday_date.strftime("%d %b (%A)")].append(record)

    return result


def get_root_path():
    return os.path.dirname(os.path.dirname(__file__))
