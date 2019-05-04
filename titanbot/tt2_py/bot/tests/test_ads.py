"""
test_ads.py

Test any of the functionality related to the image search functionality relating to the ad prompts in game.

The ad prompts may occur when a fairy is pressed. If a user has premium ad collection
turned on, we can accept these rewards instantly without having to watch an ad.
"""
from settings import TEST_CONFIG_FILE, TEST_STATS_FILE
from titanbot.tt2_py.bot.tt2.core.bot import Bot
from titanbot.tt2_py.bot.tt2.core.maps import IMAGES as BOT_IMAGES
from titanbot.tt2_py.bot.tests.maps import IMAGES as TEST_IMAGES

from PIL import Image
import unittest


class TestAdPromptMethods(unittest.TestCase):
    """Test functionality related to the ad prompts in game here."""
    @classmethod
    def setUpClass(cls):
        """Initialize the test case with a Bot instance for testing purposes."""
        cls.bot = Bot(TEST_CONFIG_FILE, TEST_STATS_FILE)

    def test_collect_on_screen(self):
        """Test that the bot can determine if the collect icon is on the screen."""
        image = TEST_IMAGES["ADS"]["skill_prompt"]
        collect = BOT_IMAGES["ADS"]["collect_ad"]

        image = Image.open(image)
        self.bot.grabber.current = image
        self.assertTrue(self.bot.grabber.search(collect, bool_only=True, testing=True))

    def test_no_thanks_on_screen(self):
        """Test that the bot can determine if the no thanks icon is on the screen."""
        image = TEST_IMAGES["ADS"]["skill_prompt"]
        no_thanks = BOT_IMAGES["ADS"]["no_thanks"]

        image = Image.open(image)
        self.bot.grabber.current = image
        self.assertTrue(self.bot.grabber.search(no_thanks, bool_only=True, testing=True))
