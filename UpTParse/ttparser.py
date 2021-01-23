#  Copyright (c) 2021.
#  Developed by SemD for "No Walls Production"

import re
import openpyxl
from modules.TimeTableStudyData import *


class Parser:
    """Class to work with a timetable excel files"""

    def __init__(self, current_book: openpyxl.workbook.Workbook, course: int, start_cell: str):
        self._current_book = current_book
        self._current_course = course
        self._output_JSON = {}
        self._cell = start_cell
        self._groups = ['ВВТ', 'ВИП']
        self._lesson = 0
        self._day = 0
        self._week = 0

    def _get_group_num(self, course: int, group: str) -> str:
        """
        Get group depending on course

        :param course: int
        :param group: int
        :return: str in a format: 206, 208, 306, 308
        """

        if group == self._groups[0]:
            return str(course) + '06'
        else:
            return str(course) + '08'

    def _get_cell_data(self, index: str) -> str:
        """

        :param index: str in excel format (exm: "L43")
        :return:
        """

        return self._current_book[index].value

    def _is_empty_cell(self, index: str) -> bool:
        """

        :param index: str in excel format (exm: "L43")
        :return: bool if cell empty
        """

        return self._get_cell_data(index) is None

    def _next_lesson(self, offset_lesson: int = 1) -> None:
        """

        :param offset_lesson: int
        """

        self._cell = Parser.next_row(self._cell, offset_lesson * 2)
        self._lesson += offset_lesson

    def _check_border(self, index: str, border_type: str) -> bool:
        """

        :param index: str in excel format (exm: "L43")
        :param border_type: str in a format: left, right, top, bottom
        :return: bool
        """

        border_obj = self._current_book[index].border
        if border_type == 'left':
            return border_obj.left.style is not None
        if border_type == 'right':
            return border_obj.right.style is not None
        if border_type == 'top':
            return border_obj.top.style is not None
        if border_type == 'bottom':
            return border_obj.bottom.style is not None

    def get_json(self) -> dict:
        """
        Get output dict obj (it's json, I promise)

        :return: dict
        """

        return self._output_JSON

    def _check_physical_day(self, start_day_index: str) -> bool:
        """

        :param start_day_index: str in excel format (exm: "L43")
        :return: bool if physical training day
        """

        num_lessons = 0
        if start_day_index.find('K') != -1:
            g_column_index = Parser.prev_column(start_day_index, 3)
        else:
            g_column_index = Parser.prev_column(start_day_index, 6)
        while num_lessons != 6:
            cell_data = self._get_cell_data(g_column_index)
            if cell_data and cell_data.find('Элективные дисциплины по физической культуре и спорту') != -1:
                return True
            num_lessons += 1
            g_column_index = Parser.next_row(g_column_index)
        return False

    @staticmethod
    def _change_cell(cell_index: str, num_rows: int, num_cols: int) -> str:
        """
        Change table cell

        :param cell_index: str in excel format (exm: "L43")
        :param num_cols: int
        :param num_rows: int
        :return: str new cell index
        """

        letter = re.split(r'\d+$', cell_index)[0]
        number = int(re.split(r'^[A-Z]+', cell_index)[1])
        return chr(ord(letter) + num_cols) + str(number + num_rows)

    @staticmethod
    def next_row(cell_index: str, num_rows: int = 1) -> str:
        """
        Shift forward through table rows

        :param cell_index: str in excel format (exm: "L43")
        :param num_rows: int
        :return: str new cell index
        """

        return Parser._change_cell(cell_index, num_rows, 0)

    @staticmethod
    def next_column(cell_index: str, num_cols: int = 1) -> str:
        """
        Shift forward through table columns

        :param cell_index: str in excel format (exm: "L43")
        :param num_cols: int
        :return: str new cell index
        """

        return Parser._change_cell(cell_index, 0, num_cols)

    @staticmethod
    def prev_column(cell_index: str, num_cols: int = 1) -> str:
        """
        Shift backward through table columns

        :param cell_index: str in excel format (exm: "L43")
        :param num_cols: int
        :return: str new cell index
        """

        return Parser._change_cell(cell_index, 0, -num_cols)

    @staticmethod
    def _duplicate_lesson(db_lesson: DbLesson, shift: int = 1) -> None:
        """

        :param db_lesson: DbLesson
        :param shift: int offset lesson number
        """

        new_lesson = DbLesson(day=db_lesson.day,
                              lesson_num=db_lesson.lesson_num + shift,
                              lesson_name=db_lesson.lesson_name,
                              lesson_date=db_lesson.lesson_date,
                              lesson_type=db_lesson.lesson_type,
                              lesson_classroom=db_lesson.lesson_classroom,
                              lesson_teacher=db_lesson.lesson_teacher)
        new_lesson.save()

    @staticmethod
    def _parse_lesson_data(cell: str) -> dict:
        """
        Parse the cell with main lesson data

        :param cell: str with cell data
        :return: dict with a lesson classroom, type and teacher
        """

        cell_data = cell.split()
        parse_result = {}
        for parse_word in cell_data:
            if parse_word.find('@') != -1 or \
                    re.fullmatch(r'[A-ZА-Я\d]-\d\d\d?\D?(,\d\d\d)?', cell_data[0]) is not None:
                parse_result['classroom'] = parse_word
            elif parse_word.find('.') != -1 and parse_word.find('.') == len(parse_word) - 1:
                parse_result['type'] = parse_word
            else:
                parse_result['teacher'] = parse_word

        if 'teacher' in parse_result and 'type' in parse_result and 'classroom' in parse_result:
            return parse_result
        else:
            print("Trouble with %s" % cell)
            exit(-1)

    def _parse_timetable_day(self, week_db: DbWeek, week_json: dict, num_day: int) -> None:
        """Parse one day in timetable"""

        self._lesson = 0
        check_empty_day = True
        start_day_index = self._cell
        db_day = DbDay(day_number=num_day, day_type=0, week=week_db)
        db_day.save()
        week_json[num_day] = {}
        while self._lesson != 6:
            db_lesson = DbLesson(day=db_day, lesson_num=self._lesson)
            week_json[num_day][self._lesson] = {}

            """Check for empty cell"""
            if not self._is_empty_cell(self._cell):
                check_empty_day = False

                # lesson name
                db_lesson.lesson_name = self._get_cell_data(self._cell)
                # lesson name for JSON output
                week_json[num_day][self._lesson]['name'] = db_lesson.lesson_name

                """Check for general lecture for VVT"""
                if self._check_border(Parser.next_column(self._cell, 2), 'right'):
                    next_row_index = Parser.next_row(self._cell)

                    """Check for lab lesson"""
                    if self._is_empty_cell(next_row_index) or not self._is_empty_cell(next_row_index) \
                            and not self._check_border(next_row_index, 'bottom'):

                        """Exactly lab lesson"""
                        # lesson teacher
                        teacher_name_index = Parser.next_row(next_row_index, 2)
                        db_lesson.lesson_teacher = self._get_cell_data(teacher_name_index)
                        # lesson teacher for JSON output
                        week_json[num_day][self._lesson]['teacher'] = db_lesson.lesson_teacher

                        # lesson classroom
                        classroom_index = Parser.next_row(next_row_index, 1)
                        db_lesson.lesson_classroom = self._get_cell_data(classroom_index)
                        # lesson classroom for JSON output
                        week_json[num_day][self._lesson]['classroom'] = db_lesson.lesson_classroom

                        # lesson date
                        date_index = next_row_index
                        db_lesson.lesson_date = self._get_cell_data(date_index)
                        # lesson date for JSON output
                        week_json[num_day][self._lesson]['date'] = db_lesson.lesson_date

                        # lesson type
                        db_lesson.lesson_type = 'лаб.'
                        # lesson type for JSON output
                        week_json[num_day][self._lesson]['type'] = db_lesson.lesson_type
                        db_lesson.save()
                        Parser._duplicate_lesson(db_lesson)
                        self._next_lesson(2)
                    else:

                        """Lecture or practice"""
                        lesson_data = Parser._parse_lesson_data(self._get_cell_data(next_row_index))

                        # lesson teacher
                        db_lesson.lesson_teacher = lesson_data['teacher']
                        # lesson teacher for JSON output
                        week_json[num_day][self._lesson]['teacher'] = db_lesson.lesson_teacher

                        # lesson classroom
                        db_lesson.lesson_classroom = lesson_data['classroom']
                        # lesson classroom for JSON output
                        week_json[num_day][self._lesson]['classroom'] = db_lesson.lesson_classroom

                        # lesson type
                        db_lesson.lesson_type = lesson_data['type']
                        # lesson type for JSON output
                        week_json[num_day][self._lesson]['type'] = db_lesson.lesson_type

                        db_lesson.save()
                        self._next_lesson()
                else:
                    """General lecture for two group"""

                    # lesson teacher
                    teacher_name_index = Parser.next_row(self._cell)
                    db_lesson.lesson_teacher = self._get_cell_data(teacher_name_index)
                    # lesson teacher for JSON output
                    week_json[num_day][self._lesson]['teacher'] = db_lesson.lesson_teacher

                    # lesson classroom
                    classroom_index = Parser.next_column(teacher_name_index, 2)
                    db_lesson.lesson_classroom = self._get_cell_data(classroom_index)
                    # lesson classroom for JSON output
                    week_json[num_day][self._lesson]['classroom'] = db_lesson.lesson_classroom

                    # lesson type
                    db_lesson.lesson_type = 'лек.'
                    # lesson type for JSON output
                    week_json[num_day][self._lesson]['type'] = db_lesson.lesson_type

                    db_lesson.save()
                    self._next_lesson()
            else:
                """Check for general lecture for VIP"""
                if not self._check_border(self._cell, 'left') and \
                        not self._check_border(Parser.prev_column(self._cell), 'right') and \
                        self._check_border(Parser.next_column(self._cell, 2), 'right'):
                    restored_cell = self._cell
                    self._cell = Parser.prev_column(self._cell, 3)
                    # lesson name
                    db_lesson.lesson_name = self._get_cell_data(self._cell)
                    # lesson name for JSON output
                    week_json[num_day][self._lesson]['name'] = db_lesson.lesson_name
                    # lesson teacher
                    teacher_name_index = Parser.next_row(self._cell)
                    db_lesson.lesson_teacher = self._get_cell_data(teacher_name_index)
                    # lesson teacher for JSON output
                    week_json[num_day][self._lesson]['teacher'] = db_lesson.lesson_teacher

                    # lesson classroom
                    classroom_index = Parser.next_column(teacher_name_index, 2)
                    db_lesson.lesson_classroom = self._get_cell_data(classroom_index)
                    # lesson classroom for JSON output
                    week_json[num_day][self._lesson]['classroom'] = db_lesson.lesson_classroom

                    # lesson type
                    db_lesson.lesson_type = 'лек.'
                    # lesson type for JSON output
                    week_json[num_day][self._lesson]['type'] = db_lesson.lesson_type

                    db_lesson.save()

                    """Restore cell index if VIP columns"""
                    self._cell = restored_cell
                    self._next_lesson()
                else:
                    db_lesson.save()
                    self._next_lesson()
        if check_empty_day:
            if self._check_physical_day(start_day_index):
                """Physical training day"""

                db_day.day_type = 1
            else:
                """Empty day"""

                db_day.day_type = 2
            db_day.save()

    def parse_timetable(self) -> None:
        """Parse the selected course timetable"""

        self._output_JSON[str(self._current_course)] = {}
        db_course = DbCourse(course_num=self._current_course)
        db_course.save()
        start_cell = self._cell
        for group in self._groups:
            self._output_JSON[str(self._current_course)][group] = {}
            db_group = DbGroup(group_num=self._get_group_num(self._current_course, group),
                               group_name=group,
                               course=db_course)
            db_group.save()
            if group == self._groups[1]:
                self._cell = Parser.next_column(start_cell, 3)
            self._week = 0
            for self._week in range(0, 2):
                self._day = 0
                db_week = DbWeek(week_study_num=self._week, group=db_group)
                db_week.save()
                self._output_JSON[str(self._current_course)][group][self._week] = {}
                for self._day in range(0, 6):
                    self._parse_timetable_day(db_week,
                                              self._output_JSON[str(self._current_course)][group][self._week],
                                              self._day)
                self._cell = Parser.next_row(self._cell)
