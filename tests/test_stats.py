"""
test_stats.py

Test any of the functionality related to the image parsing of the stats window within
the heroes panel in game.

The stats page provides information to the user that may be useful when parsing and auditing
how much progress the bot has made. This may be useful in the future if this information
becomes accessible through different interfaces.
"""
from settings import TEST_CONFIG_FILE, TEST_STATS_FILE
from tt2.core.bot import Bot
from tt2.core.constants import STATS_GAME_STAT_KEYS, STATS_BOT_STAT_KEYS
from tests.maps import IMAGES as TEST_IMAGES

from PIL import Image

import unittest


class TestStatsParser(unittest.TestCase):
    """Test functionality related to the stats panel parsing here."""
    @classmethod
    def setUpClass(cls):
        """Initialize the test case with a Bot instance for testing purposes."""
        cls.bot = Bot(TEST_CONFIG_FILE, TEST_STATS_FILE)

    def test_stats_update_ocr(self):
        """Test that the bot is able to successfully parse and extract in game stats."""
        images = TEST_IMAGES["STATS_TEST"]

        # Passing the test images to the update method will use these images instead
        # of the usual grabber.snapshot() functionality which is un-needed while testing.
        self.bot.stats.update_ocr(test_set=images)

        expected = {
            "highest_stage_reached": "4.43K",
            "total_pet_level": "323",
            "gold_earned": "1.57e275",
            "taps": "4.30M",
            "titans_killed": "547.05K",
            "bosses_killed": "137.15K",
            "critical_hits": "110.86K",
            "chestersons_killed": "61.06K",
            "prestiges": "51",
            "play_time": "9d 15:58:46",
            "relics_earned": "19.26M",
            "fairies_tapped": "2.23K",
            "daily_achievements": "10",
        }

        for key, value in expected.items():
            self.assertTrue(getattr(self.bot.stats, key) == value)

    def test_stage_ocr(self):
        """Test that the stage ocr checks are able to parse different expected stage values."""
        expected = ("12493", "10651", "11289", "10411", "10920", "7111", "9840", "7284", "7180")
        for i in range(9):
            index = "0{index}".format(index=i + 1)
            key = "test_stage_{image_index}".format(image_index=index)

            image = Image.open(TEST_IMAGES["STAGE"][key])
            value = self.bot.stats.stage_ocr(test_image=image)

            self.assertEqual(expected[i], value)

    def test_stats_diff(self):
        """Test that the stats module can properly retrieve the differences between values."""
        game_changes = (
            "5.43K", "455", "1.59e277", "5.55M", "599.32K", "431.23K", "190.33K", "90.03K", "78", "10d 21:04:34",
            "23.33M", "8.44K", "11",
        )
        game_diffs_expected = (
            1000, 132, 1.5743000000000002e+277, 1250000, 52270, 294080, 79470,
            28970, 27, '1d 05:05:48', 4070000, 6210, 1,
        )
        bot_changes = (
            "76", "99", "6543", "25"
        )
        bot_diffs_expected = (
            43, 43, 2000, 5
        )

        for index, key in enumerate(STATS_GAME_STAT_KEYS):
            setattr(self.bot.stats, key, game_changes[index])

        for index, key in enumerate(STATS_BOT_STAT_KEYS):
            setattr(self.bot.stats, key, bot_changes[index])

        diffs = self.bot.stats.as_json()["sessions"][self.bot.stats.day][self.bot.stats.session]
        game_diffs = diffs["game_stat_differences"]
        bot_diffs = diffs["bot_stat_differences"]

        for index, key in enumerate(STATS_GAME_STAT_KEYS):
            self.assertTrue(game_diffs[key]["diff"] == game_diffs_expected[index])

        for index, key in enumerate(STATS_BOT_STAT_KEYS):
            self.assertTrue(bot_diffs[key]["diff"] == bot_diffs_expected[index])
