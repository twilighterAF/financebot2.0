import telebot
from datetime import datetime
from telebot import types
from .config import get_id, get_token
from .keyboards import Keyboard
from .money import Money
from .database import Database
from .utils import Validator
from src.logger import get_logger


bot = telebot.TeleBot(token=get_token())
keyboard = Keyboard()
income, expense = Money(), Money()
validator = Validator()
db = Database('money.db')
logger = get_logger(__name__)


@bot.message_handler(commands=['start'])
def send_welcome(message: types.Message):
    if message.chat.id != get_id():
        bot.send_message(message.chat.id, 'Access Denied', reply_to_message_id=False)
        logger.warning('Access denied')

    else:
        bot.send_message(
            message.chat.id, 'Humble bot servant for finance tracking. 🧐\n'
                             'Input money value for expense, the same for income, just with "+" literal.\n'
                             'I can add and delete categories, show statistics and delete values',
            reply_markup=keyboard.main_keyboard())


@bot.message_handler(commands=['cancel'])
def cancel(message: types.Message):
    income.clear_value()
    expense.clear_value()
    bot.send_message(message.chat.id, 'Return to main menu', reply_markup=keyboard.main_keyboard())


@bot.message_handler(content_types=['text'])
def main_choice(message: types.Message):
    if message.text.isdigit() or message.text.find('+') != -1:

        if validator.validate_value(message.text):
            add_money(message)

    elif message.text == 'Settings ⚙':
        settings(message)

    elif message.text == 'Statistics 📈':
        statistics(message)


@bot.message_handler(content_types=['text'])
def add_money(message: types.Message):
    num = int(validator.validate_value(message.text))

    if message.text.find('+') != -1:
        income.set_value(num)

    else:
        expense.set_value(num)

    bot.send_message(
        message.chat.id, f'Value {num} ₽ Now choose category',
        reply_markup=keyboard.category_keyboard(expense.get_categories()) if expense.get_value() != 0 else
        keyboard.category_keyboard(income.get_categories()))


@bot.message_handler(content_types=['text'])
def settings(message: types.Message):
    bot.send_message(message.chat.id, 'What i have to do?', reply_markup=keyboard.settings_keyboard())


@bot.callback_query_handler(func=lambda call: income.get_value() or expense.get_value())
def input_money_callback(call: types.CallbackQuery):
    now = datetime.strftime(datetime.now(), '%Y-%m-%d')

    if income.get_value() and call.data in income.get_categories():
        db_package = ('income', income.get_value(), call.data, now)
        db.insert(db_package)
        bot.send_message(call.message.chat.id, f'Income {income.get_value()} ₽ added')

    elif expense.get_value() and call.data in expense.get_categories():
        db_package = ('expense', expense.get_value(), call.data, now)
        db.insert(db_package)
        bot.send_message(call.message.chat.id, f'Expense {expense.get_value()} ₽ added')

    income.clear_value(), expense.clear_value()


@bot.callback_query_handler(func=lambda call: call.data in keyboard.settings_callback)
def settings_callback(call: types.CallbackQuery):
    if call.data == 'Category operations':
        bot.send_message(call.message.chat.id, 'Choose operation',
                         reply_markup=keyboard.category_operations_keyboard())

    elif call.data == 'Add category':
        bot.send_message(call.message.chat.id, 'Enter the name of category. \n'
                                               'If name with "+" literal, category will be created for income. \n'
                                               'Numbers are ignored, please choose usual name.')
        bot.register_next_step_handler(call.message, adding_category)

    elif call.data == 'Delete category':
        bot.send_message(
            call.message.chat.id, 'Deleting category',
            reply_markup=keyboard.delete_categories_keyboard(income.get_categories(), expense.get_categories()))

    elif call.data == 'Delete values':
        values_for_delete = db.select_10_values()

        if values_for_delete:
            bot.send_message(call.message.chat.id, 'Select value',
                             reply_markup=keyboard.delete_values_keyboard(values_for_delete))
        else:
            bot.send_message(call.message.chat.id, 'No values')

    elif call.data == 'Range statistic':
        bot.send_message(call.message.chat.id, 'Please input the range in format like "yyyy.mm.dd-yyyy.mm.dd"\n'
                                               'First date should be a start of the range and last - the end')
        bot.register_next_step_handler(call.message, range_statistic)


@bot.callback_query_handler(func=lambda call: call.data.find('income_category') != -1 or
                            call.data.find('expense_category') != -1)
def deleting_category_callback(call: types.CallbackQuery):
    category = call.data.split('-')[0]
    income.del_category(category) if call.data.find('income_category') != -1 else expense.del_category(category)
    bot.send_message(call.message.chat.id, f'Category {category} was deleted')


@bot.callback_query_handler(func=lambda call: call.data in [str(value[0]) for value in db.select_10_values()])
def deleting_values_callback(call: types.CallbackQuery):
    db.delete_value(call.data)
    bot.send_message(call.message.chat.id, 'Value deleted')


@bot.message_handler(content_types=['text'])
def adding_category(message: types.Message):
    if message.text == '/cancel':
        cancel(message)

    else:
        category = validator.validate_category(message.text)

        if category:
            income.set_category(category) if message.text.find('+') != -1 else expense.set_category(category)
            bot.send_message(message.chat.id, f'Category {category} was added')


@bot.message_handler(content_types=['text'])
def statistics(message: types.Message):
    statistic = statistic_calculate(db.get_current_month_statistic())
    bot.send_message(message.chat.id, 'Month statistic. Can show for range')
    statistics_report(message, statistic)


@bot.message_handler(content_types=['text'])
def statistics_report(message: types.Message, statistic: dict):
    income_values = statistic['income']
    expense_values = statistic['expense']
    report = f'Income all - {sum(income_values.values())}\n' + \
             '\n'.join(map(str, income_values.items())) + \
             f'\n\nExpenses all - {sum(expense_values.values())}\n' + \
             '\n'.join(map(str, expense_values.items()))

    fixed_report = report.replace('(', '').replace(')', '').replace("'", '').replace(',', ' -')
    bot.send_message(message.chat.id, fixed_report, reply_markup=keyboard.statistic_range_button())


def statistic_calculate(data: list) -> dict:
    generator = (row for row in data)
    income_values = {}
    expense_values = {}
    for value in generator:
        category = value[2]
        amount = int(value[1])
        no_value = 0

        if value[0] == 'income':
            current_amount = income_values[category] if category in income_values.keys() else no_value
            current_amount += amount
            income_values[category] = current_amount

        elif value[0] == 'expense':
            current_amount = expense_values[category] if category in expense_values.keys() else no_value
            current_amount += amount
            expense_values[category] = current_amount

    result = {'income': income_values, 'expense': expense_values}
    return result


@bot.message_handler(content_types=['text'])
def range_statistic(message: types.Message):
    if message.text == '/cancel':
        cancel(message)

    else:
        start, end = message.text.split('-')
        if validator.validate_datetime(start, end):
            statistic = statistic_calculate(db.get_range_statistic(start.replace('.', '-'), end.replace('.', '-')))
            statistics_report(message, statistic)


def start_init():
    """Default categories and command init"""
    income_category = ['Salary', 'Other']
    [income.set_category(x) for x in income_category]

    expense_category = ['Food', 'Needed', 'Joy', 'Other']
    [expense.set_category(x) for x in expense_category]

    bot.set_my_commands([
        telebot.types.BotCommand("/start", "Start bot and send main menu"),
        telebot.types.BotCommand("/cancel", "Canceling the current operation and return to main menu")])


def bot_run():
    start_init()
    logger.info('Start bot')

    try:
        db.create()
        bot.infinity_polling(timeout=60)
    except Exception as e:
        logger.exception(f'General exeption - {e}')
