#  Copyright (c) 2021.
#  Developed by SemD for "No Walls Production"
import os
import json


class JsonOutput:
    filename = "timetable.json"

    @staticmethod
    def check_file() -> bool:
        return os.path.exists(JsonOutput.filename)

    @staticmethod
    def get_json_from_file() -> dict:
        with open(JsonOutput.filename, 'r', encoding='utf-8') as file:
            output_data = json.load(file)
        return output_data

    @staticmethod
    def write_json(data: dict) -> None:
        with open(JsonOutput.filename, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False)

    @staticmethod
    def write_json_course(course_num: int, course_data: dict) -> None:
        if JsonOutput.check_file():
            json_data = JsonOutput.get_json_from_file()
            json_data[str(course_num)] = course_data[str(course_num)]
            JsonOutput.write_json(json_data)
        else:
            JsonOutput.write_json(course_data)
