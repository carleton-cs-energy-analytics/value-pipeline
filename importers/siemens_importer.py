"""
    siemens_importer.py
    Alex Davis, 7 November 2018
    Eva Grench, 7 November 2018

    Imports Siemens reports into the database by organizing the data from the given CSV file.
"""

import os
import sys
import csv
import requests
import re
from datetime import datetime
import glob
import itertools

BASE_URL = os.environ.get("BASE_URL") or "http://energycomps.its.carleton.edu/api/"
VALUE_REPORT_DIRECTORY = os.environ.get("VALUE_REPORT_DIRECTORY") or "/var/data/uploads/siemens"
ARCHIVE_DIRECTORY = os.environ.get("ARCHIVE_DIRECTORY") or "/var/data/uploads/siemens/archive"


def main():
    file_iterator = glob.iglob(os.path.join(VALUE_REPORT_DIRECTORY, "*.csv"))
    include_archive = len(sys.argv) > 1 and sys.argv[1] == 'all'
    if include_archive:
        file_iterator = itertools.chain(file_iterator,
                                        glob.iglob(os.path.join(ARCHIVE_DIRECTORY, "*.csv")))

    for filename in file_iterator:
        with open(filename, 'r') as csv_file:
            try:
                reader = csv.reader(csv_file)
                next(reader)  # headers

                # Gets the given number associated with a point that the values are indexed on
                point_names = save_point_name_index(reader)

                next(reader)  # Date Range
                next(reader)  # Report Timings
                next(reader)  # empty
                next(reader)  # headers

                array_for_json = arrange_value_tuples(reader, point_names)

                success = post_values(array_for_json)
                if success and not include_archive:
                    os.system('mv %s %s' % (filename, ARCHIVE_DIRECTORY))
            except Exception as e:
                print()
                print("Exception while reading file:", filename)
                print(e)


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
            if row[i] != "No Data" and row[i] != "Data Loss":
                array_for_json.append([point_names[i - 1], timestamp.timestamp(), row[i]])

    return array_for_json


def post_values(array_for_json):
    # Sends the values to the API in the correct format
    response = requests.post(BASE_URL + "values/add", json=array_for_json)

    if response.status_code == 200:
        print(".", end="")
        sys.stdout.flush()
        return True
    elif response.status_code == 204:
        print("!", end="")
        sys.stdout.flush()
        return True
    else:
        print()
        print(response)
        return False


if __name__ == "__main__":
    main()
