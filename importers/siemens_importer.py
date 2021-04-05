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
ARCHIVE_WEIRD_DIRECTORY = os.environ.get("ARCHIVE_WEIRD_DIRECTORY") or "/var/data/uploads/siemens/archive-weird"

def main():
    """
    Loops through all the CSVs that have values that need to be imported into the database. The
    relevant information is stored in a nested list and then a call to the API imports the values to
    the database.
    """
    # All the files in the uploads/siemens directory
    file_iterator = glob.iglob(os.path.join(VALUE_REPORT_DIRECTORY, "*.csv"))
    # Reseeding the database, so we need to look at all values including already imported ones
    include_archive = len(sys.argv) > 1 and sys.argv[1] == 'all'
    if include_archive:
        # Also iterate over all the archived CSVs
        file_iterator = itertools.chain(file_iterator,
                                        glob.iglob(os.path.join(ARCHIVE_DIRECTORY, "*.csv")))

    for filename in file_iterator:
        print(filename, file=sys.stderr)
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

                # API call returns a boolean signifying if the import was successful
                success = post_values(array_for_json)
                # If is was successful and we are not reseeding, we want to move the files to the
                # archives folder so we aren't trying to reimport them every day.
                if success[0] and not include_archive:
                    os.system('mv %s %s' % (filename, ARCHIVE_DIRECTORY))
                if success[1] and not include_archive:
                    os.system('mv %s %s' % (filename, ARCHIVE_WEIRD_DIRECTORY))
            except Exception as e:
                print()
                print("Exception while reading file:", filename)
                print(e)


def save_point_name_index(reader):
    """
    The csv gives each point a CSV specific name (i.e. a number) and this function saves this link
    between index and name to use it later on when getting the values for a particular point.

    :param reader: The csv reader object
    :return: A list of point names and their specific index in the csv.
    """
    point_names = [None]
    # Gets the given number associated with a point that the values are indexed on
    for row in reader:
        point_name_index = re.match('Point_(\d+):', row[0])
        if point_name_index is None:
            break  # Time Interval
        point_names.insert(int(point_name_index.group(1)), row[1])

    return point_names


def arrange_value_tuples(reader, point_names):
    """
    Creates a list of lists that has the point name, timestamp, and value for each cell in the CSV.

    :param reader: The csv reader object
    :param point_names: A list of point names and their specific index in the csv.
    :return: A nested list that has all the information needed to import a value into the database:
    the point name, timestamp, and value.
    """
    array_for_json = []
    # Gets the time stamp and value and adds it with the point name to be added to the database
    for row in reader:
        if len(row) == 1:  # End of File
            break
        timestamp = datetime.strptime(row[0] + row[1], '%m/%d/%Y%H:%M:%S')

        for i in range(2, len(row)):
            # Currently we are simply ignoring cases of data loss
            if row[i] != "No Data" and row[i] != "Data Loss":
                array_for_json.append([point_names[i - 1], timestamp.timestamp(), row[i]])

    return array_for_json


def post_values(array_for_json):
    """
    Sends the values to the API to be imported into the database

    :param array_for_json: A nested list that has all the information needed to import a value into
    the database: the point name, timestamp, and value.
    :return: A boolean signifying if the values were imported successfully.
    """
    # Sends the values to the API in the correct format
    response = requests.post(BASE_URL + "values/add", json=array_for_json)

    if response.status_code == 200:  # Imported normally
        print("success", end="")
        sys.stdout.flush()
        return [True, False]
    elif response.status_code == 204:  # The file was already imported
        print("file already exists!", end="")
        sys.stdout.flush()
        return [True, False]
    elif response.status_code == 206: # The file had no datapoints in it
        print("file had no points!", end="")
        sys.stdout.flush()
        return [False, True]
    else:
        print("an error occured. Check backend logs")
        print(response, end="")
        return [False, False]


if __name__ == "__main__":
    main()
