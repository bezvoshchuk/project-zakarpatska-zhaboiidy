from __future__ import annotations

from collections import defaultdict
import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from datamodels import Record


def get_birthdays_per_week(
    users_data: list[Record],
) -> dict[str, list[Record]]:
    """This function will return dictionary with all users that have birthday in following week.

    Args:
        users_data: List of user Records.

    Returns:
        A dictionary where key is week day and value is list of user full names.
    """
    # Initial values and consts
    result = defaultdict(list)
    next_monday_date = datetime.datetime.today().date() + datetime.timedelta(
        days=(7 - datetime.datetime.today().date().weekday()) % 7
    )

    for record in users_data:
        birthday_date = record.birthday.value.replace(year=next_monday_date.year)

        # Check if weekday is Sun or Sat
        if birthday_date.weekday() >= 5:
            birthday_date += datetime.timedelta(days=(7 - birthday_date.weekday()) % 7)

        # Advance by one year if birthday already passed
        if next_monday_date > birthday_date:
            birthday_date = birthday_date.replace(year=next_monday_date.year + 1)

        # If birthday is within the week, add to result
        if (birthday_date - next_monday_date).days < 7:
            result[birthday_date.strftime("%A")].append(record)

    return result
