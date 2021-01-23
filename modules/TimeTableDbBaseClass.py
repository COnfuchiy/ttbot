#  Copyright (c) 2021.
#  Developed by SemD for "No Walls Production"

from peewee import *

DB_PATH = 'main.sqlite'
db = SqliteDatabase(DB_PATH,  pragmas={'foreign_keys': 1})


class DbBaseModel(Model):
    class Meta:
        database = db
