import datetime
import unittest

from projects import parsing


class DatetimeTestCase(unittest.TestCase):

    def test_parse_date(self):
        date_string = 'Day 1: December 26, 2020 +08:00'
        d = parsing.parse_date(date_string=date_string)
        self.assertEqual(d, datetime.date(2020, 12, 26))

    def test_parse_time(self):
        time_string = '08:30'
        t = parsing.parse_time(time_string=time_string)
        self.assertEqual(t, datetime.time(8, 30))
