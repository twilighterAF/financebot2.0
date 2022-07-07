
class Money:

    def __init__(self):
        self._categories = set()
        self._value = 0

    def set_category(self, category: str):
        self._categories.add(category)

    def get_categories(self) -> set:
        return self._categories

    def del_category(self, category: str):
        self._categories.remove(category)

    def set_value(self, value: int):
        self._value = value

    def get_value(self) -> int:
        return self._value

    def clear_value(self):
        self._value = 0