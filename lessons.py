import requests
import json
import os

from datetime import datetime
from enum import Enum

personalArea = "https://школа.образование33.рф/personal-area/#diary"

session = requests.session()

loginCookies = session.cookies
loginCookies.set("sessionid", os.getenv('session_id'))

session.cookies = loginCookies


def get_lessons_message(date: datetime):
    day_json = get_day_json(date)

    if "lessons" not in day_json: return "Расписание не задано"

    day = get_day(day_json)

    strftime = date.strftime("%A, %d %B %Y г.")
    result = f"Расписание на _{strftime}_\n"
    index = 0

    for lesson in day.lessons:
        homework = lesson.homework
        formatted_homework = f":\n     `{homework}`" if len(homework) > 0 else ""

        index += 1
        result += f"{str(index)}. {lesson.name}{formatted_homework}\n"

    return result


def get_day(day_json): return Day(day_json)


def get_day_json(date):
    data = session.get(
            "https://школа.образование33.рф/api/ScheduleService/GetDiary",
            params={"date": date.date().isoformat(), "is_diary": True}
        ).text
    json_loaded = json.loads(data)

    return json_loaded["days"][date.weekday()]


def get_day_by_ordinal(ordinal):
    return tuple(filter(lambda day_of_week: day_of_week.value[0] == ordinal, DayOfWeek))[0]


class Day:
    def __init__(self, day_data):
        self.lessons = [Lesson(val) for val in day_data["lessons"]]
        self.date = day_data["date"]


class Lesson:
    def __init__(self, lesson_data):
        self.name = lesson_data["discipline"]
        self.homework = lesson_data["homework"]


class DayOfWeek(Enum):
    ПОНЕДЕЛЬНИК = (0, "Пн")
    ВТОРНИК = (1, "Вт")
    СРЕДА = (2, "Ср")
    ЧЕТВЕРГ = (3, "Чт")
    ПЯТНИЦА = (4, "Пт")
