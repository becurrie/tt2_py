"""
test_heroes.py

Test any of the functionality related to the image search functionality relating to the heroes panel in the game.

The heroes panel houses all information about heroes in the game. Their is also some
additional information buttons here, the stats button is very useful and used during stats
OCR updates.
"""
from settings import TEST_CONFIG_FILE, TEST_STATS_FILE
from tt2.core.bot import Bot
from tt2.core.maps import IMAGES as BOT_IMAGES
from tests.maps import IMAGES as TEST_IMAGES

from PIL import Image
import unittest


class TestHeroesPanelMethods(unittest.TestCase):
    """Test functionality related to the heroes panel here."""
    @classmethod
    def setUpClass(cls):
        """Initialize the test case with a Bot instance for testing purposes."""
        cls.bot = Bot(TEST_CONFIG_FILE, TEST_STATS_FILE)

        # Hero panel image paths.
        cls.heroes_collapsed = TEST_IMAGES["PANELS"]["heroes_collapsed"]
        cls.heroes_expanded = TEST_IMAGES["PANELS"]["heroes_expanded"]
        cls.images = (cls.heroes_collapsed, cls.heroes_expanded)

    def test_upgrades_on_screen(self):
        """Test that the bot can determine if the upgrades icon is on the screen."""
        upgrades = BOT_IMAGES["HEROES"]["upgrades"]

        # Check that the heroes panel images contain the upgrades icon.
        for path in self.images:
            image = Image.open(path)
            self.bot.grabber.current = image
            self.assertTrue(self.bot.grabber.search(upgrades, bool_only=True, testing=True))

    def test_stats_on_screen(self):
        """Test that the bot can determine if the stats icon is on the screen."""
        stats = BOT_IMAGES["HEROES"]["stats"]

        # Check that the heroes panel images contain the stats icon.
        for path in self.images:
            image = Image.open(path)
            self.bot.grabber.current = image
            self.assertTrue(self.bot.grabber.search(stats, bool_only=True, testing=True))

    def test_story_on_screen(self):
        """Test that the bot can determine if the story icon is on the screen."""
        story = BOT_IMAGES["HEROES"]["story"]

        # Check that the heroes panel images contain the story icon.
        for path in self.images:
            image = Image.open(path)
            self.bot.grabber.current = image
            self.assertTrue(self.bot.grabber.search(story, bool_only=True, testing=True))
