"""
test_utils.py

Test any of the functionality relating to the utilities present and used by different pieces of the bot.

Utilities should represent different functions or methods that are generic and usable by
specific pieces of the bot. Ideally, these methods should be fail safe and always gracefully exit.
"""
from titanbot.tt2_py.bot.tt2.core.utilities import convert, diff, strfdelta

from datetime import timedelta
import unittest


class TestBotUtilityMethods(unittest.TestCase):
    """Test functionality related to bot utilities here."""
    def test_convert(self):
        """Test the convert utility works with appropriate values."""
        data = [
            123, 934, 99999, 12345, 123445, 10.00, 1.0, 9834.0, 123, 1.0,
            "323", "14", "9999", "1212", "3210", "1.4K", "1200K", "433K", "1K", "9090K",
            "93.4M", "100M", "1.34M", "954M", "2M", "Noop", None, "1d 11:11:11", "222d 03:03:05", "Test",
            127e140, 174e227, 111e21, 444e22, 37e211,
        ]

        # Expecting all conversion values to match up to this list.
        expected = [
            123, 934, 99999, 12345, 123445, 10, 1, 9834, 123, 1,
            323, 14, 9999, 1212, 3210, 1400, 1200000, 433000, 1000, 9090000,
            93400000, 100000000, 1340000, 954000000, 2000000, "Noop", None, "1d 11:11:11", "222d 03:03:05",
            "Test", 1.27e+142, 1.74e+229, 1.11e+23, 4.44e+24, 3.7e+212
        ]

        for index, value in enumerate(data):
            self.assertTrue(expected[index] == convert(value))

    def test_diff(self):
        """Test the diff utility works with appropriate values."""
        data = [
            (100, 200, 100), (500, 876, 376), (34576, 37485, 2909),
            (2.0, 8.0, 6), (45.32, 98.56, 53), (100.11, 9090.0, 8989),
        ]

        # Looping through data set here, last index is expected. First is old, second is new.
        for s in data:
            self.assertTrue(s[2] == diff(s[0], s[1]))

    def test_timedelta_formatting(self):
        """Test the strftdelta functionality works with timedelta objects."""
        data = [
            (timedelta(days=1, seconds=45267), timedelta(days=2, seconds=1234), "0d 11:46:07"),
            (timedelta(days=0, seconds=546), timedelta(days=7, seconds=5346), "7d 01:20:00"),
            (timedelta(days=43, seconds=9878), timedelta(days=49, seconds=321), "5d 21:20:43"),
        ]

        for s in data:
            self.assertTrue(s[2] == strfdelta(s[1] - s[0]))
