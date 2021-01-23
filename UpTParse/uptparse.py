#  Copyright (c) 2021.
#  Developed by SemD for "No Walls Production"

import argparse
from openpyxl import load_workbook
from modules.TimeTableStudyData import *
from UpTParse.ttparser import Parser
from UpTParse.ttjson import JsonOutput

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('filename', nargs='?')
    namespace = parser.parse_args()
    db_adapter = TimeTableStudyData()
    if namespace.filename:
        excel = load_workbook(namespace.filename)
        if excel:
            print(namespace.filename + ' now upload. Please, select course (2 or 3 or 23):')
            current_course = input()
            if current_course == '2' or current_course == '3' or current_course == '23':
                if current_course == '2':
                    db_adapter.trunc_course(2)
                    second_course = Parser(excel['2 курс'], 2, 'K11')
                    second_course.parse_timetable()
                    JsonOutput.write_json_course(2, second_course.get_json())
                elif current_course == '3':
                    db_adapter.trunc_course(3)
                    third_course = Parser(excel['3 курс '], 3, 'K11')
                    third_course.parse_timetable()
                    JsonOutput.write_json_course(3, third_course.get_json())
                elif current_course == '23':
                    db_adapter.trunc_all_courses()
                    second_course = Parser(excel['2 курс'], 2, 'K11')
                    third_course = Parser(excel['3 курс '], 3, 'K11')
                    second_course.parse_timetable()
                    third_course.parse_timetable()
                    JsonOutput.write_json_course(2, second_course.get_json())
                    JsonOutput.write_json_course(3, third_course.get_json())
