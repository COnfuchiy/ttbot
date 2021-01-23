#  Copyright (c) 2021.
#  Developed by SemD for "No Walls Production"
import telebot
from .TimeTableUserData import TgUserAdapter
from .TimeTableStudyData import TimeTableStudyData
from .TimeTableDate import TimeTableDate
import random


class FunStickers:
    """Class with fun stickers. Fun!"""

    for_non_parsable_message = [
        'CAACAgIAAxkBAAKzBGADNiF9VqQygNbO6v6H9lCcy14ZAALGPgAC6VUFGE6pyz4dCQ1PHgQ',
        'CAACAgQAAxkBAAKzB2ADNjhluix7lXA_6eHdHDJKwvdGAAJKAwACq1aAFk8XsFH-qSwdHgQ',
        'CAACAgIAAxkBAAKzCmADNklwdmPtkfXkwLAVPhhHnbOHAAKVCwACdOq4SUAniaWIQDqKHgQ',
        'CAACAgIAAxkBAAKzC2ADNkkOpJjJ2-4UpNwLEmGnJJYGAALuBQAC6wNNAAHmVaaSgGuoyx4E',
        'CAACAgIAAxkBAAKzDGADNklhtMKuUivTDLIKxaH1lnR2AALqBQAC6wNNAAFL6yVFEpO3NB4E',
        'CAACAgIAAxkBAAKzE2ADNl09bzaej1EBQ2irQHCtAcXSAAIOBgAC6wNNAAFJRgjXVZNbhh4E',
        'CAACAgIAAxkBAAKzFmADNl3EGlegGsQx_2GrnHOUpkSpAAJmAAO83U8RzNKqZQIhRBkeBA',
        'CAACAgIAAxkBAAKzFGADNl06GQ2A0Cg25XgYsXtTqw0_AAIwAAOvXQE0tbogJMVpslIeBA',
        'CAACAgIAAxkBAAKzFWADNl0BBulqM9KqOfRWSJ5uAjtlAAL4AAMI7FAjXmDdn2VjdeMeBA',
        'CAACAgIAAxkBAAKzGWADNl3_c-NeCWZtyv4NKNOsGpz7AAIsAAOwCk0MSGziXj2W1UoeBA',
        'CAACAgIAAxkBAAKzGGADNl2NX-g84dNkKrmmCdxQFBfFAAIIAAOwCk0Md6H0SOr4f6geBA',
        'CAACAgIAAxkBAAKzF2ADNl2JeqWOFKuqNPG33v2-Kg6lAAJmAgACzcBIGF7yv0XtcDvUHgQ',
    ]

    @staticmethod
    def what_sticker() -> str:
        """
        if not understand user message
        :return: str code sticker
        """
        return FunStickers.for_non_parsable_message[random.randint(0, len(FunStickers.for_non_parsable_message) - 1)]


class BotCommands:
    start = '/start'
    day_timetable = '/day'
    current_lesson = '/now'
    commands = '/help'
    about = '/about'


class TgBotAdapter:
    """Class for Telegram bot"""

    def __init__(self, bot: telebot.TeleBot):
        self._bot = bot
        self._user_db = TgUserAdapter()  # use only for connect to db
        self._timetable_db = TimeTableStudyData()  # use only for connect to db
        self._date_handler = TimeTableDate()
        self._group_variants = ['ВИП', 'ВВТ']
        self._course_variants = ['Второй', 'Третий']

    def tg_user(self, user_id: int) -> bool:
        """

        :param user_id: int
        :return: bool if the user is in the database and has course and group
        """
        if not TgUserAdapter.check_user(user_id):
            self.start_handler(user_id)
            return False
        else:
            user_data = TgUserAdapter.get_user_data(user_id)

            if user_data.user_course is None:
                self.send_message(user_id, "Выбери свой курс:",
                                  TgBotAdapter.set_keymap(self._course_variants))
                return False

            if user_data.user_group is None:
                self.send_message(user_id, "Выбери свою группу:",
                                  TgBotAdapter.set_keymap(self._course_variants))
                return False

            return True

    def about(self, user_id: int) -> None:
        """Some text about me and my bot"""

        self.send_message(user_id, "Бот для расписания. Если чё писать сюды https://vk.com/nottnn")

    def help(self, user_id: int) -> None:
        """Main commands"""

        self.send_message(user_id, "/day - расписание дня\n/now - текущая пара")

    def start_handler(self, user_id: int) -> None:
        """User registration"""
        if not TgUserAdapter.check_user(user_id):
            TgUserAdapter.create_user(user_id)
            self.send_message(user_id, "Дарова. Выбери свой курс, котя:",
                              TgBotAdapter.set_keymap(self._course_variants))
        else:
            self.send_message(user_id, "Используй /help для просмотра доступных команд")

    def parse_other_message(self, user_id: int, message: str) -> None:
        """Parse non command messages"""

        if TgUserAdapter.check_user(user_id):
            if message in self._course_variants:
                TgUserAdapter.set_user_course(user_id, self._course_variants.index(message) + 2)
                user_data = TgUserAdapter.get_user_data(user_id)
                if user_data.user_group is None:
                    self.send_message(user_id, "Выбери свою группу:",
                                      TgBotAdapter.set_keymap(self._group_variants))
                else:
                    self.send_message(user_id, "Используй /help для просмотра доступных команд")

            elif message in self._group_variants:
                user_data = TgUserAdapter.get_user_data(user_id)
                if user_data.user_course is not None:
                    group_num = str(user_data.user_course) + ("08" if message == self._group_variants[0] else "06")
                    TgUserAdapter.set_user_group(user_id, group_num)
                    self.send_message(user_id, "Используй /help для просмотра доступных команд")
                else:
                    self.send_message(user_id, "Выбери свой курс:",
                                      TgBotAdapter.set_keymap(self._course_variants))
            else:
                self._bot.send_sticker(user_id, FunStickers.what_sticker(), disable_notification=True)
        else:
            self.start_handler(user_id)

    def send_message(self, user_id: int, message: str, markup=None) -> None:
        self._bot.send_message(user_id, message, reply_markup=markup, disable_notification=True)

    @staticmethod
    def set_keymap(variants: list) -> telebot.types.ReplyKeyboardMarkup:
        """
        Create telegram keyboard

        :param variants: list
        :return: reply keyboard
        """

        keymap = telebot.types.ReplyKeyboardMarkup(True, True)
        for variant in variants:
            keymap.row(variant)
        return keymap

    def send_day_lessons(self, user_id: int) -> None:
        """Send user current day lessons"""

        if self.check_not_study_day(user_id):
            lessons = self.get_day_lessons(user_id)
            output_message = [i for i in range(1, 7)]
            output_message = list(map(lambda pos, les:
                                      str(pos) + ". " + TimeTableStudyData.assemble_lesson_line(les), output_message,
                                      lessons))
            header_message = self._date_handler.get_current_time_str()
            self.send_message(user_id, header_message + '\r\n' + '\r\n'.join(output_message))

    def send_current_lesson(self, user_id: int) -> None:
        """Send user current lesson"""

        if self.check_not_study_day(user_id) and self.check_not_study_time(user_id):
            lessons = self.get_day_lessons(user_id)
            current_lesson_index = self._date_handler.get_current_lesson()
            current_lesson = lessons[current_lesson_index]

            # if lesson not today
            if current_lesson.lesson_date and not \
                    TimeTableStudyData.is_equal_lesson_date(current_lesson,
                                                            self._date_handler.get_current_time()['datetime']):
                current_lesson.lesson_name = None
            output_message = self._date_handler.get_current_time_str()
            output_message += "\nПара " + str(current_lesson_index + 1) + ": " + \
                              TimeTableStudyData.assemble_lesson_line(current_lesson) + "\n" + \
                              self._date_handler.to_end_lesson(current_lesson_index)
            self.send_message(user_id, output_message)

    def check_not_study_time(self, user_id: int) -> bool:
        """Check study time and handle if not"""

        if not self._date_handler.check_study_time():
            not_study_code = self._date_handler.get_not_study_code()
            current_date = self._date_handler.get_current_time()['datetime']
            all_lessons = self.get_day_lessons(user_id)

            # if lesson not start or now ended
            if not_study_code == 1 or not_study_code == 2:
                self.send_message(user_id, "Какие пары, ало, на часах " + current_date.strftime('%H:%M'))

            # if coffee break
            if not_study_code == 3:
                prev_and_next_lessons = self._date_handler.get_prev_and_next_lessons()
                prev_lesson = all_lessons[prev_and_next_lessons['prev']]
                next_lesson = all_lessons[prev_and_next_lessons['next']]
                if prev_lesson.lesson_name is None:
                    next_lesson_index = prev_and_next_lessons['next']
                    if next_lesson.lesson_name is None:
                        next_lesson_index = TimeTableStudyData.check_another_lessons(all_lessons,
                                                                                     prev_and_next_lessons['next'])
                    if next_lesson_index != 0:
                        output_message = "Сейчас перерыв. Следующая пара через " + \
                                         self._date_handler.get_delay_time_str(current_date, next_lesson_index)
                        output_message += "\n" + str(next_lesson_index + 1) + ". " + \
                                          TimeTableStudyData.assemble_lesson_line(next_lesson)
                    else:
                        output_message = "Больше пар не будет))"
                elif next_lesson.lesson_name is None:
                    output_message = "Больше пар не будет))\nСейчас была:\n" + \
                                     str(prev_and_next_lessons['prev'] + 1) + ". " + \
                                     TimeTableStudyData.assemble_lesson_line(prev_lesson)
                else:
                    output_message = "Перекурчик))\nСейчас была:\nПара " + \
                                     str(prev_and_next_lessons['prev'] + 1) + ": " + \
                                     TimeTableStudyData.assemble_lesson_line(prev_lesson) + \
                                     "\nСледующая пара через " + \
                                     self._date_handler.get_delay_time_str(current_date,
                                                                           prev_and_next_lessons['next']) + \
                                     "\nПара " + str(prev_and_next_lessons['next'] + 1) + ": " + \
                                     TimeTableStudyData.assemble_lesson_line(next_lesson)
                self.send_message(user_id, output_message)
            return False
        else:
            return True

    def get_day_lessons(self, user_id: int) -> list:
        """
        Get current day lessons

        :param user_id:
        :return: list with lessons
        """
        date = self._date_handler.get_current_time()
        user_data = TgUserAdapter.get_user_data(user_id)
        lessons = self._timetable_db.get_lessons(course=user_data.user_course, group=user_data.user_group,
                                                 study_week=date['study_week'], num_day=date['week_day'])
        return lessons

    def check_not_study_day(self, user_id: int) -> bool:
        """Check if now physical, or empty day or sunday"""

        date = self._date_handler.get_current_time()
        if date['week_day'] == 6:
            self.send_message(user_id, "Сегодня воскресение, отдыхай, студентус")
            return False

        user_data = TgUserAdapter.get_user_data(user_id)
        physical_day = self._timetable_db.check_physical_day(course=user_data.user_course, group=user_data.user_group,
                                                             study_week=date['study_week'], num_day=date['week_day'])
        if physical_day:
            self.send_message(user_id, "Сегодня была физра, но ты на неё не пошёл...")
            return False

        empty_day = self._timetable_db.check_empty_day(course=user_data.user_course, group=user_data.user_group,
                                                       study_week=date['study_week'], num_day=date['week_day'])
        if empty_day:
            self.send_message(user_id, "Пар нету, отдыхай, студентус")
            return False
        return True
