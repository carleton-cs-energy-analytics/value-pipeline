import csv
import requests
import re
from datetime import datetime

BASE_URL = "http://localhost:5000"

with open('EvansTestFile.csv', 'r') as csv_file:
    point_names = [None]

    reader = csv.reader(csv_file)
    next(reader)
    for row in reader:
        point_name_index = re.match('Point_(\d+):', row[0])
        if point_name_index is None:
            break  # Time Interval
        point_names.insert(int(point_name_index.group(1)), row[1])

    next(reader)  # Date Range
    next(reader)  # Report Timings
    next(reader)  # empty
    next(reader)  # headers

    array_for_json = []

    for row in reader:
        if len(row) == 1:
            break
        timestamp = datetime.strptime(row[0] + row[1], '%m/%d/%Y%H:%M:%S')

        for i in range(2, len(row)):
            if row[i] != "No Data":
                array_for_json.append([point_names[i-1], timestamp.timestamp(), row[i]])

    # print(array_for_json)

    requests.post(BASE_URL + "/api/values", json=array_for_json)
