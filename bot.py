from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from _datetime import datetime, timedelta
from lessons import DayOfWeek, get_lessons_message

import os
import telebot

token = os.getenv('TELEGRAM_BOT_TOKEN')

bot = telebot.TeleBot(token)


@bot.message_handler(regexp="|".join(["дз", "расписание"]))
def homework(message: Message):
    send_or_edit_main_message(message.chat.id)


@bot.callback_query_handler(func=lambda call: call.data.startswith("lessons_"))
def lessons(call):
    received_data = call.data.split("_")[1:]

    if len(received_data) < 1:
        return

    message = call.message
    date = datetime.fromisoformat(received_data[0])
    current_week = "week_" + received_data[1]

    edit_lesson_message(
        message.chat.id,
        message.message_id,
        date,
        current_week
    )


@bot.callback_query_handler(func=lambda call: call.data == "today")
def today(call):
    message = call.message
    date = get_right_date(datetime.today())

    edit_lesson_message(
        message.chat.id,
        message.message_id,
        date
    )


@bot.callback_query_handler(func=lambda call: call.data == "tomorrow")
def tomorrow(call):
    message = call.message
    date = get_right_date(datetime.today() + timedelta(1))

    edit_lesson_message(
        message.chat.id,
        message.message_id,
        date
    )


@bot.callback_query_handler(func=lambda call: call.data.startswith("week_"))
def get_week(call):
    week = int(call.data.split("_")[1])

    week_timedelta = timedelta(weeks=abs(week))
    date_today = datetime.today()
    date = get_right_date(date_today if week == 0 else date_today + (week_timedelta if week > 0 else -week_timedelta))

    message = call.message
    send_or_edit_main_message(
        message.chat.id,
        message.message_id,
        date
    )


def send_or_edit_main_message(chat_id, message_id=0, date=datetime.today()):
    current_week = datetime.today().isocalendar()[1]
    received_week = date.isocalendar()[1]

    week_different = received_week - current_week

    choose_day = date.strftime("%A, %d %B %Y г.")
    markup = get_main_markups(date.date(), week_different)

    bot.send_message(chat_id, choose_day, reply_markup=markup) \
        if message_id == 0 else \
        bot.edit_message_text(
            choose_day, chat_id, message_id,
            reply_markup=markup, parse_mode="Markdown"
        )


def edit_lesson_message(chat_id, message_id, date: datetime, current_week="week_0"):
    bot.edit_message_text(
        get_lessons_message(date), chat_id, message_id,
        parse_mode="Markdown", reply_markup=get_backward_markup(current_week)
    )


def get_main_markups(date, week=0):
    previous_week = "← Предыдущая неделя"
    next_week = "Следующая неделя →"

    weeks_switcher = {
        previous_week: f"week_{week - 1}",
        next_week: f"week_{week + 1}"
    }

    return build_markup(
        dict_to_buttons({
            "Сегодня": "today",
            "Завтра": "tomorrow"
        }) if week == 0 else [],
        dict_to_buttons(dict(
            zip(
                map(lambda day_of_week: day_of_week.value[1], DayOfWeek),
                map(lambda day_of_week:
                    f"lessons_{(date - timedelta(date.weekday() - day_of_week.value[0])).isoformat()}_{week}",
                    DayOfWeek)
            )
        )),
        dict_to_buttons(weeks_switcher)
    )


def get_backward_markup(week: str):
    return build_markup(
        dict_to_buttons({"← Назад": week})
    )


def build_markup(*args, row_width=5):
    markup = InlineKeyboardMarkup(row_width=row_width)
    [markup.add(*val) for val in args]

    return markup


def dict_to_buttons(dictionary: dict):
    return [InlineKeyboardButton(key, callback_data=value) for key, value in dictionary.items()]


def get_right_date(date: datetime):
    weekday = date.weekday()

    return date if weekday <= 4 else date - timedelta(weekday - 4)
