class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class Name(Field):
    pass


class Birthday(Field):
    def __init__(self, value):
        if value is not None and value != 'None':
            value = self.validate_date(value)
        super().__init__(value=value)

    @staticmethod
    def validate_date(date_str: str) -> date:
        """Validate date string, raises ValueError if date cannot be parsed"""
        try:
            return datetime.datetime.strptime(date_str, DATE_FORMAT).date()
        except Exception:
            raise ValueError(
                f"Provided date {date_str} should follow format {DATE_FORMAT}, aborting ..."
            )

    def __str__(self):
        print('birthday', self.value, type(self.value))
        if not self.value or self.value == 'None':
            return "None"
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
        super().__init__(value=email)

    @staticmethod
    def validate_email(email: str):
        """Validate email, raises ValueError if email is not valid"""
        try:
            pattern = r"^[\w\.-]+@[a-zA-Z\d\.-]+\.[a-zA-Z]{2,}$"
            if re.match(pattern, email):
                return email
            else:
                raise ValueError

        except ValueError as e:
            raise ValueError(f"Email is not valid, entered: {email}") from e


class ProjectRole(Field):
    """Generic class for project roles"""

    pass


class ProjectTasks(Field):
    """Generic class for project tasks"""

    pass


class Hobby(Field):
    """Generic class for hobbies"""

    pass
