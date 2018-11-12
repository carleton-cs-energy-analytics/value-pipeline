"""
    siemens_importer.py
    Alex Davis, 7 November 2018
    Eva Grench, 7 November 2018

    Imports Siemens reports into the database by organizing the data from the given CSV file.
"""

import csv
import requests
import re
from datetime import datetime

BASE_URL = "http://localhost:5000"


def main():
    # Currently only opens a test file
    with open('EvansTestFile.csv', 'r') as csv_file:
        reader = csv.reader(csv_file)
        next(reader)  # headers

        # Gets the given number associated with a point that the values are indexed on
        point_names = save_point_name_index(reader)

        next(reader)  # Date Range
        next(reader)  # Report Timings
        next(reader)  # empty
        next(reader)  # headers

        array_for_json = arrange_value_tuples(reader, point_names)

        post_values(array_for_json)


def save_point_name_index(reader):
    point_names = [None]
    # Gets the given number associated with a point that the values are indexed on
    for row in reader:
        point_name_index = re.match('Point_(\d+):', row[0])
        if point_name_index is None:
            break  # Time Interval
        point_names.insert(int(point_name_index.group(1)), row[1])

    return point_names


def arrange_value_tuples(reader, point_names):
    array_for_json = []
    # Gets the time stamp and value and adds it with the point name to be added to the database
    for row in reader:
        if len(row) == 1:  # End of File
            break
        timestamp = datetime.strptime(row[0] + row[1], '%m/%d/%Y%H:%M:%S')

        for i in range(2, len(row)):
            if row[i] != "No Data":
                array_for_json.append([point_names[i - 1], timestamp.timestamp(), row[i]])

    return array_for_json


def post_values(array_for_json):
    # Sends the values to the API in the correct format
    response = requests.post(BASE_URL + "/api/values", json=array_for_json)

    if response.status_code == 200:
        print("Success")
    else:
        print(response)


if __name__ == "__main__":
    main()
