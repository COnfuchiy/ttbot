#  Copyright (c) 2021.
#  Developed by SemD for "No Walls Production"
from datetime import datetime

from peewee import *
from .TimeTableDbBaseClass import db, DbBaseModel


class TgUser(DbBaseModel):
    user_id = AutoField()
    user_tg_id = IntegerField(null=False)
    user_name = TextField(null=True)
    user_date_registration = DateTimeField(default=datetime.now())
    user_last_request = DateTimeField(default=datetime.now())
    user_day_timetable = BooleanField(default=False)
    user_group = TextField(null=True)
    user_course = IntegerField(null=True)

    class Meta:
        db_table = "tg_user"


class TgUserAdapter:
    def __init__(self):
        self.db = db
        if not self.db.is_connection_usable():
            self.db.connect()
        TgUser.create_table()

    @staticmethod
    def create_user(user_id: int, name: str = None) -> None:
        new_user = TgUser(user_tg_id=user_id,
                          user_name=name)
        new_user.save()

    @staticmethod
    def check_user(user_id: int) -> bool:
        try:
            TgUser.select().where(TgUser.user_tg_id == user_id).get()
            return True
        except DoesNotExist:
            return False

    @staticmethod
    def get_user_data(user_id: int) -> TgUser:
        try:
            return TgUser.select().where(TgUser.user_tg_id == user_id).get()
        except DoesNotExist:
            pass

    @staticmethod
    def set_user_course(user_id: int,  course: int) -> None:
        user = TgUserAdapter.get_user_data(user_id)
        if user:
            user.user_course = course
            user.user_last_request = datetime.now()
            user.save()

    @staticmethod
    def set_user_group(user_id: int, group: str) -> None:
        user = TgUserAdapter.get_user_data(user_id)
        if user:
            user.user_group = group
            user.user_last_request = datetime.now()
            user.save()

    @staticmethod
    def set_user_name(user_id: int, name: str) -> None:
        user = TgUserAdapter.get_user_data(user_id)
        if user:
            user.user_name = name
            user.user_last_request = datetime.now()
            user.save()

    @staticmethod
    def set_user_day_timetable(user_id: int, value: bool) -> None:
        user = TgUserAdapter.get_user_data(user_id)
        if user:
            user.user_day_timetable = value
            user.user_last_request = datetime.now()
            user.save()
