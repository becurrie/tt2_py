"""
test_no_panels.py

Test any of the functionality related to the image parsing of the icons possibly present whether or
not a panel is open or not.

These icons would include things like tournaments, clan ship, settings.
"""
from settings import TEST_CONFIG_FILE, TEST_STATS_FILE
from titanbot.tt2.core import Bot
from titanbot.tt2.core import IMAGES as BOT_IMAGES
from tests.maps import IMAGES as TEST_IMAGES

from PIL import Image
import unittest


class TestNoPanelBotMethods(unittest.TestCase):
    """Test functionality related to no panels here."""
    @classmethod
    def setUpClass(cls):
        cls.bot = Bot(TEST_CONFIG_FILE, TEST_STATS_FILE)

    def test_clan_ship_not_ready(self):
        """Test that the bot can determine if the clan ship not ready icon is on the screen."""
        image = TEST_IMAGES["PANELS"]["no_panel_open"]
        clan_no_battle = BOT_IMAGES["NO_PANELS"]["clan_no_battle"]

        image = Image.open(image)
        self.bot.grabber.current = image
        self.assertTrue(self.bot.grabber.search(clan_no_battle, bool_only=True, testing=True))



