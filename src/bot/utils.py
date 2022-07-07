from typing import Union
from itertools import chain

class Validator:

    @staticmethod
    def validate_value(value: str) -> Union[int, None]:
        msg = value.replace(' ', '', len(value))

        for num in [x for x in msg.split('+') if x.isdigit()]:
            return num

    @staticmethod
    def validate_category(category: str) -> Union[str, None]:
        msg = category.replace(' ', '', len(category))

        for string in [x for x in msg.split('+') if x.isalpha()]:
            return string if string.isalpha() else None

    @staticmethod
    def validate_datetime(start: str, end: str) -> Union[str, None]:
        validate = [x for x in chain(start.split('.'), end.split('.')) if x.isdigit()]
        return validate if len(validate) == 6 else None




