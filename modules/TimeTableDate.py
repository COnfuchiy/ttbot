#  Copyright (c) 2021.
#  Developed by SemD for "No Walls Production"

from datetime import datetime
import math


class TimeTableDate:
    """Class for working with time

    A class using fot work with a date: calculating the study week,
    displaying the current date and time, displaying the current lesson
    check coffee break, displaying the start and end lesson time

    """

    def __init__(self):
        self._current_time = datetime.now()
        self._current_study_week = 0  # 0 as first study week, 1 as second study week
        self._current_lesson = 0
        self._coffee_break = {}

        # zhenya chose this time as a starting point
        # why? but it work
        self._start_time = datetime(2018, 9, 3, 0, 0, 0, 0)

        # format each lesson {start lesson time (hour,min), end lesson time (hour,min)}
        self._lesson_calls = [
            {'start': {'h': 8, 'm': 00}, 'end': {'h': 9, 'm': 30}},
            {'start': {'h': 9, 'm': 40}, 'end': {'h': 11, 'm': 10}},
            {'start': {'h': 11, 'm': 20}, 'end': {'h': 12, 'm': 50}},
            {'start': {'h': 13, 'm': 10}, 'end': {'h': 14, 'm': 40}},
            {'start': {'h': 14, 'm': 50}, 'end': {'h': 16, 'm': 20}},
            {'start': {'h': 16, 'm': 25}, 'end': {'h': 17, 'm': 55}}
        ]
        self._week_days = ["понедельник", "вторник", "среда", "четверг", "пятница", "суббота", "воскресенье"]
        self._months = ["января", "февраля", "марта", "апреля", "мая", "июня", "июля", "августа", "сентября", "октября",
                        "ноября", "декабря"]
        self._calculate_study_week()
        self._select_current_lesson()

    def _calculate_study_week(self) -> None:
        """Method for calculating the current study week"""

        num_days = (self._current_time - self._start_time).days
        self._current_study_week = int(num_days / 7 % 2)

    def get_current_time_str(self) -> str:
        """
        :return: string with current date and study week
        """

        return "Сегодня %d %s, %s\n%d учебная неделя" % (self._current_time.day,
                                                         self._months[self._current_time.month - 1],
                                                         self._week_days[self._current_time.weekday()],
                                                         self._current_study_week + 1)

    def get_current_time(self) -> dict:
        """
        :return: dictionary with current date and study week
        """

        time = dict()
        time['datetime'] = self._current_time
        time['study_week'] = self._current_study_week
        time['week_day'] = self._current_time.weekday()
        return time

    def check_coffee_break(self) -> bool:
        """Checking if there is a break now
        Break between lessons
        After the buffet is closed it is smoke break, not lunch
        :(
        :return: state smoke break
        """

        self._coffee_break = {}
        for i in range(0, len(self._lesson_calls) - 1):
            prev_lesson_time = datetime(self._current_time.year,
                                        self._current_time.month,
                                        self._current_time.day,
                                        self._lesson_calls[i]['end']['h'],
                                        self._lesson_calls[i]['end']['m'], 0, 0)
            next_lesson_time = datetime(self._current_time.year,
                                        self._current_time.month,
                                        self._current_time.day,
                                        self._lesson_calls[i + 1]['start']['h'],
                                        self._lesson_calls[i + 1]['start']['m'], 0, 0)
            if prev_lesson_time < self._current_time < next_lesson_time:
                self._coffee_break = {'prev': i, 'next': i + 1}
                return bool(self._coffee_break)
        return bool(self._coffee_break)

    def _select_current_lesson(self) -> None:
        """Method for selecting the current lesson"""

        for lesson_time in self._lesson_calls:
            if lesson_time['start']['h'] <= self._current_time.hour <= lesson_time['end']['h']:
                if self._current_time.hour == lesson_time['end']['h']:
                    if self._current_time.minute <= lesson_time['end']['m']:
                        self._current_lesson = self._lesson_calls.index(lesson_time)
                        return
                else:
                    self._current_lesson = self._lesson_calls.index(lesson_time)
                    return

    def check_study_time(self) -> bool:
        """
        Method for checking now study time
        :return: study state
        """

        if self._current_time.weekday() != 6 \
                and self._lesson_calls[0]['start']['h'] <= self._current_time.hour <= self._lesson_calls[5]['end']['h']:
            if self._current_time.hour == self._lesson_calls[5]['end']['h'] \
                    and self._current_time.minute > self._lesson_calls[5]['end']['m']:
                return False

            # if smoke break
            return not self.check_coffee_break()
        return False

    def get_not_study_code(self) -> int:
        """
        If not study time, returns one of the codes
        0 -> if now sunday
        1 -> if study not started yet
        2 -> if study ended
        3 -> if smoke break
        :return: code
        """

        if self._current_time.weekday() == 6:
            return 0
        elif self._current_time.hour < self._lesson_calls[0]['start']['h']:
            return 1
        elif self._current_time.hour > self._lesson_calls[5]['end']['h'] \
                or self._current_time.hour == self._lesson_calls[5]['end']['h'] \
                and self._current_time.minute > self._lesson_calls[5]['end']['m']:
            return 2
        elif self._coffee_break:
            return 3

    def get_start_lesson_time(self, num_lesson: int) -> dict:
        """:return start lesson time in format {'h':hour,'m':min}"""
        return self._lesson_calls[num_lesson]['start']

    def get_end_lesson_time(self, num_lesson: int) -> dict:
        """:return end lesson time in format {'h':hour,'m':min}"""
        return self._lesson_calls[num_lesson]['end']

    def get_delay_time_str(self, first_time: datetime, next_lesson_num: int) -> str:
        """
        :return: str with time delay
        """

        last_time = self.get_start_lesson_time(next_lesson_num)
        last_time = datetime(first_time.year, first_time.month, first_time.day, last_time['h'], last_time['m'])
        time_delta = last_time - first_time
        hour_delay = time_delta.seconds // 3600
        minute_delay = math.ceil(time_delta.seconds % 3600 / 60)
        hour_str = ""
        if hour_delay != 0:
            if hour_delay == 1:
                hour_str = "1 час"
            else:
                hour_str = "%d часа" % hour_delay
        if minute_delay != 0:
            return hour_str + "%d мин." % minute_delay
        else:
            return hour_str

    def to_end_lesson(self, lesson_num:int) -> str:
        """
        :return: str with end lesson time
        """

        lesson_end_time = self.get_end_lesson_time(lesson_num)
        return "До %d:%d" % (lesson_end_time['h'], lesson_end_time['m'])

    def get_current_lesson(self) -> int:
        """Getter for current lesson"""
        return self._current_lesson

    def get_prev_and_next_lessons(self) -> dict:
        """Getter for smoke break"""
        return self._coffee_break
