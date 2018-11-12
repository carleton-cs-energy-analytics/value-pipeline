import csv
import unittest
from siemens_importer import save_point_name_index, arrange_value_tuples


class SiemensImporterTests(unittest.TestCase):
    def test_point_names(self):
        with open('EvansTestFile.csv', 'r') as csv_file:
            reader = csv.reader(csv_file)
            next(reader)  # headers

            self.assertEqual(save_point_name_index(reader), [None,
                                                             'CMC.328.RT',
                                                             'CMC.328.SP',
                                                             'EV.RM107.RT',
                                                             'EV.RM107.SP',
                                                             'CMC.102.SP',
                                                             'EV.RM003.V',
                                                             'EV.RM102.V'])

    def test_arrange_value_tuples(self):
        with open('EvansTestFile.csv', 'r') as csv_file:
            reader = csv.reader(csv_file)
            next(reader)  # headers

            # Gets the given number associated with a point that the values are indexed on
            point_names = save_point_name_index(reader)

            next(reader)  # Date Range
            next(reader)  # Report Timings
            next(reader)  # empty
            next(reader)  # headers

            self.assertEquals(arrange_value_tuples(reader, point_names),
                              [['CMC.328.RT', 1514354400.0, '25'],
                               ['CMC.328.SP', 1514354400.0, 'ON'],
                               ['EV.RM107.RT', 1514354400.0, '25'],
                               ['EV.RM107.SP', 1514354400.0, '22.2'],
                               ['CMC.102.SP', 1514354400.0, '25'],
                               ['EV.RM003.V', 1514354400.0, '0'],
                               ['EV.RM102.V', 1514354400.0, '100'],
                               ['CMC.328.RT', 1514355300.0, '9'],
                               ['CMC.328.SP', 1514355300.0, 'ON'],
                               ['EV.RM107.RT', 1514355300.0, '9'],
                               ['EV.RM107.SP', 1514355300.0, '13.82'],
                               ['CMC.102.SP', 1514355300.0, '9'],
                               ['EV.RM003.V', 1514355300.0, '0'],
                               ['EV.RM102.V', 1514355300.0, '100'],
                               ['CMC.328.RT', 1514791800.0, '20'],
                               ['CMC.328.SP', 1514791800.0, 'ON'],
                               ['EV.RM107.RT', 1514791800.0, '20'],
                               ['EV.RM107.SP', 1514791800.0, '18.57'],
                               ['CMC.102.SP', 1514791800.0, '20'],
                               ['EV.RM003.V', 1514791800.0, '0'],
                               ['EV.RM102.V', 1514791800.0, '100'],
                               ['CMC.328.RT', 1514792700.0, '33'],
                               ['CMC.328.SP', 1514792700.0, 'ON'],
                               ['EV.RM107.RT', 1514792700.0, '33'],
                               ['EV.RM107.SP', 1514792700.0, '19.62'],
                               ['CMC.102.SP', 1514792700.0, '33'],
                               ['EV.RM003.V', 1514792700.0, '0'],
                               ['EV.RM102.V', 1514792700.0, '100'],
                               ['CMC.328.SP', 1514885400.0, 'ON']])


if __name__ == '__main__':
    unittest.main()
