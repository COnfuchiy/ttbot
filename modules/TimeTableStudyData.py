#  Copyright (c) 2021.
#  Developed by SemD for "No Walls Production"
from datetime import datetime
from peewee import *
from .TimeTableDbBaseClass import db, DbBaseModel


class DbCourse(DbBaseModel):
    course_id = AutoField()
    course_num = IntegerField(null=False)
    course_date_create = DateTimeField(default=datetime.now())

    class Meta:
        db_table = "course"


class DbGroup(DbBaseModel):
    group_id = AutoField()
    group_num = IntegerField(null=False)
    group_name = TextField(null=False)
    course = ForeignKeyField(DbCourse, null=False, on_delete='cascade')

    class Meta:
        db_table = "group"


class DbWeek(DbBaseModel):
    week_id = AutoField()
    week_study_num = IntegerField(null=False)
    group = ForeignKeyField(DbGroup, null=False, on_delete='cascade')

    class Meta:
        db_table = "week"


class DbDay(DbBaseModel):
    day_id = AutoField()
    day_number = IntegerField(null=False)
    day_type = IntegerField(null=False)
    week = ForeignKeyField(DbWeek, null=False, on_delete='cascade')

    class Meta:
        db_table = "day"


class DbLesson(DbBaseModel):
    lesson_id = AutoField()
    day = ForeignKeyField(DbDay, null=False, on_delete='cascade')
    lesson_num = IntegerField(null=False)
    lesson_name = TextField(null=True)
    lesson_date = TextField(null=True)
    lesson_type = TextField(null=True)
    lesson_classroom = TextField(null=True)
    lesson_teacher = TextField(null=True)

    class Meta:
        db_table = "lesson"


class TimeTableStudyData:
    def __init__(self):
        self.db = db
        if not self.db.is_connection_usable():
            self.db.connect()
        DbCourse.create_table()
        DbGroup.create_table()
        DbWeek.create_table()
        DbDay.create_table()
        DbLesson.create_table()

    def __del__(self):
        self.db.close()

    @staticmethod
    def trunc_course(num_course: int) -> None:
        try:
            course = DbCourse.select().where(DbCourse.course_num == int(num_course)).get()
            course.delete_instance()
        except DoesNotExist:
            pass

    @staticmethod
    def trunc_all_courses() -> None:
        TimeTableStudyData.trunc_course(2)
        TimeTableStudyData.trunc_course(3)

    @staticmethod
    def get_lessons(course: int, group: int, study_week: int, num_day: int) -> list:
        db_day = TimeTableStudyData.get_day(course, group, study_week, num_day)
        db_lessons = DbLesson.select().where(DbLesson.day == db_day).execute()
        return list(db_lessons)

    @staticmethod
    def get_day(course: int, group: int, study_week: int, num_day: int) -> DbDay:
        try:
            db_course = DbCourse.select().where(DbCourse.course_num == course).get()
            db_group = DbGroup.select().where(
                DbGroup.course == db_course).where(DbGroup.group_num == group).get()
            db_week = DbWeek.select().where(
                DbWeek.group == db_group).where(DbWeek.week_study_num == study_week).get()
            db_day = DbDay.select().where(DbDay.week == db_week).where(
                DbDay.day_number == num_day).get()
            return db_day
        except DoesNotExist:
            pass

    @staticmethod
    def check_empty_day(course: int, group: int, study_week: int, num_day: int) -> bool:
        db_day = TimeTableStudyData.get_day(course, group, study_week, num_day)
        if db_day.day_type == 2:
            return True
        return False

    @staticmethod
    def check_physical_day(course: int, group: int, study_week: int, num_day: int) -> bool:
        db_day = TimeTableStudyData.get_day(course, group, study_week, num_day)
        if db_day.day_type == 1:
            return True
        return False

    @staticmethod
    def is_equal_lesson_date(lesson: DbLesson, current_date: datetime) -> bool:
        """Compare lesson dates with current date for equals"""

        date_intervals = str(lesson.lesson_date).split(",")
        date_intervals = list(map(lambda interval: interval.split("."), date_intervals))
        for lesson_date in date_intervals:
            if current_date.month == int(lesson_date[1]) and current_date.day == int(lesson_date[0]):
                return True
        return False

    @staticmethod
    def assemble_lesson_line(lesson: DbLesson) -> str:
        """

        :param lesson: DbLesson
        :return: str db_lesson object in string format
        """

        if lesson.lesson_name is not None:
            lesson_field = [lesson.lesson_name,
                            lesson.lesson_teacher,
                            lesson.lesson_classroom,
                            lesson.lesson_type]
            return ' '.join(list(map(lambda field: str(field), lesson_field)))
        else:
            return 'Нет пары'

    @staticmethod
    def check_another_lessons(lessons: list, last_index: int)->int:
        for index in range(last_index, len(lessons)):
            if lessons[index].lesson_name is None:
                return index
        return 0
