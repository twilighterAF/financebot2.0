from telebot import types


class Keyboard:

    def __init__(self):
        self.settings_callback = ('Category operations', 'Delete values', 'Add category',
                                  'Delete category', 'Range statistic')  # pool of callbacks for func conditions

    @staticmethod
    def main_keyboard() -> types.ReplyKeyboardMarkup:
        markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
        button1 = types.KeyboardButton('Statistics 📈')
        button2 = types.KeyboardButton('Settings ⚙')
        markup.add(button1, button2)
        return markup

    @staticmethod
    def settings_keyboard() -> types.InlineKeyboardMarkup:
        markup = types.InlineKeyboardMarkup(row_width=2)
        categories = types.InlineKeyboardButton('Category operations', callback_data='Category operations')
        delete = types.InlineKeyboardButton('Delete values', callback_data='Delete values')
        markup.add(categories, delete)
        return markup

    @staticmethod
    def category_operations_keyboard() -> types.InlineKeyboardMarkup:
        markup = types.InlineKeyboardMarkup(row_width=2)
        add_category = types.InlineKeyboardButton('Add category', callback_data='Add category')
        delete_category = types.InlineKeyboardButton('Delete category', callback_data='Delete category')
        markup.add(add_category, delete_category)
        return markup

    @staticmethod
    def category_keyboard(categories: set) -> types.InlineKeyboardMarkup:
        keyboard = []
        row = []

        for category in categories:
            row.append(types.InlineKeyboardButton(category, callback_data=category))

        keyboard.append(row)
        return types.InlineKeyboardMarkup(keyboard)

    @staticmethod
    def delete_categories_keyboard(income_categories: set, expense_categories: set) -> types.InlineKeyboardMarkup:
        keyboard = []
        expns, incm = [], []

        for income in income_categories:
            incm.append(types.InlineKeyboardButton(f'{income}-income', callback_data=f'{income}-income_category'))

        for expense in expense_categories:
            expns.append(types.InlineKeyboardButton(f'{expense}-expense', callback_data=f'{expense}-expense_category'))

        keyboard.append(incm)
        keyboard.append(expns)

        return types.InlineKeyboardMarkup(keyboard)

    @staticmethod
    def delete_values_keyboard(values: list) -> types.InlineKeyboardMarkup:
        markup = types.InlineKeyboardMarkup()
        for value in values:
            value_data = f'{value[1]} {value[2]} {value[3]} {value[4]}'
            button = types.InlineKeyboardButton(value_data, callback_data=str(value[0]))
            markup.add(button)
        return markup

    @staticmethod
    def statistic_range_button() -> types.InlineKeyboardMarkup:
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton('Range statistic', callback_data='Range statistic'))
        return markup