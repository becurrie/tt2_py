"""
test_panels.py

Test any functionality related to the image search functionality relating to the panels within the game.

Panels in the game are represented by the six buttons available at the bottom most portion of the game,
these panels house basically all the functionality within the game. The goal of these tests is to ensure
that the image searching and methods available on the bot can determine what state the game is in at all times.
"""
from settings import TEST_CONFIG_FILE, TEST_STATS_FILE
from titanbot.tt2.core.bot import Bot
from titanbot.tt2.core.maps import IMAGES as BOT_IMAGES
from tests.maps import IMAGES as TEST_IMAGES

from PIL import Image
import unittest


class TestPanelBotMethods(unittest.TestCase):
    """Test functionality related to in-game panels here."""
    @classmethod
    def setUpClass(cls):
        """Initialize the test case with a Bot instance for testing purposes."""
        cls.bot = Bot(TEST_CONFIG_FILE, TEST_STATS_FILE)

    def test_any_panels_on_screen(self):
        """Test that the bot can determine if any panels are currently on the screen or not."""
        images = TEST_IMAGES["PANELS"]
        exit_panel = BOT_IMAGES["GENERIC"]["exit_panel"]

        # These images should contain the "exit_panel" image when checked.
        true = (
            images["artifacts_collapsed"], images["artifacts_expanded"], images["equipment_collapsed"],
            images["equipment_expanded"], images["heroes_collapsed"], images["heroes_expanded"],
            images["master_collapsed"], images["master_expanded"], images["pets_collapsed"],
            images["pets_expanded"], images["shop_open"],
        )
        # These images should not contain the "exit_panel" image when checked.
        false = (
            images["no_panel_open"],
        )

        for true_path in true:
            image = Image.open(true_path)
            self.bot.grabber.current = image
            self.assertTrue(self.bot.grabber.search(exit_panel, bool_only=True, testing=True))

        for false_path in false:
            image = Image.open(false_path)
            self.bot.grabber.current = image
            self.assertFalse(self.bot.grabber.search(exit_panel, bool_only=True, testing=True))

    def test_panel_collapse_on_screen(self):
        """Test that the bot can determine if the collapse button is present on the screen."""
        images = TEST_IMAGES["PANELS"]
        collapse_panel = BOT_IMAGES["GENERIC"]["collapse_panel"]

        # These images should contain the "collapse_panel" image when checked.
        true = (
            images["artifacts_expanded"], images["equipment_expanded"], images["heroes_expanded"],
            images["master_expanded"], images["pets_expanded"],
        )
        # These images should not contain the "collapse_panel" image when checked.
        false = (
            images["artifacts_collapsed"], images["equipment_collapsed"], images["heroes_collapsed"],
            images["master_collapsed"], images["no_panel_open"], images["shop_open"],
        )

        for true_path in true:
            image = Image.open(true_path)
            self.bot.grabber.current = image
            self.assertTrue(self.bot.grabber.search(collapse_panel, bool_only=True, testing=True))

        for false_path in false:
            image = Image.open(false_path)
            self.bot.grabber.current = image
            self.assertFalse(self.bot.grabber.search(collapse_panel, bool_only=True, testing=True))

    def test_panel_expand_on_screen(self):
        """Test that the bot can determine if the expand button is present on the screen."""
        images = TEST_IMAGES["PANELS"]
        expand_panel = BOT_IMAGES["GENERIC"]["expand_panel"]

        # These images should contain the "expand_panel" image when checked.
        true = (
            images["artifacts_collapsed"], images["equipment_collapsed"], images["heroes_collapsed"],
            images["master_collapsed"],
        )
        # These images should not contain the "expand_panel" image when checked.
        false = (
            images["artifacts_expanded"], images["equipment_expanded"], images["heroes_expanded"],
            images["master_expanded"], images["pets_expanded"], images["no_panel_open"],
            images["shop_open"]
        )

        for true_path in true:
            image = Image.open(true_path)
            self.bot.grabber.current = image
            self.assertTrue(self.bot.grabber.search(expand_panel, bool_only=True, testing=True))

        for false_path in false:
            image = Image.open(false_path)
            self.bot.grabber.current = image
            self.assertFalse(self.bot.grabber.search(expand_panel, bool_only=True, testing=True))

    def test_panel_buy_options(self):
        """Test that the bot can determine if the different buy option buttons are present on the screen."""
        images = (
            TEST_IMAGES["PANELS"]["master_buy_option_open_collapsed"],
            TEST_IMAGES["PANELS"]["master_buy_option_open_collapsed"],
        )

        # These images should all be present in the images above.
        buy_options = (
            BOT_IMAGES["GENERIC"]["buy_max"], BOT_IMAGES["GENERIC"]["buy_one"],
            BOT_IMAGES["GENERIC"]["buy_one_hundred"], BOT_IMAGES["GENERIC"]["buy_ten"],
            BOT_IMAGES["GENERIC"]["max"],
        )

        for path in images:
            image = Image.open(path)
            self.bot.grabber.current = image
            for find in buy_options:
                self.assertTrue(self.bot.grabber.search(find, bool_only=True, testing=True))
