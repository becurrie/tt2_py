"""
test_master.py

Test any of the functionality related to the image search functionality relating to the master panel in the game.

The master panel houses most most of the information in the game, The menu is here which contains buttons
to access the Users account, skill tree, achievements and inbox. As well as the ability to actually upgrade
the master from here. All of the skills are present here as well.
"""
from settings import TEST_CONFIG_FILE, TEST_STATS_FILE
from tt2.core.bot import Bot
from tt2.core.maps import IMAGES as BOT_IMAGES
from tests.maps import IMAGES as TEST_IMAGES

from PIL import Image
import unittest


class TestMasterPanelMethods(unittest.TestCase):
    """Test functionality related to the master panel here."""
    @classmethod
    def setUpClass(cls):
        """Initialize the test case with a Bot instance for testing purposes."""
        cls.bot = Bot(TEST_CONFIG_FILE, TEST_STATS_FILE)

        # Master panel image paths.
        cls.master_collapsed = TEST_IMAGES["MASTER"]["master_collapsed"]
        cls.master_expanded = TEST_IMAGES["MASTER"]["master_expanded"]

        # Bottom master panel image paths.
        cls.master_bottom_expanded = TEST_IMAGES["MASTER"]["master_bottom_expanded"]
        cls.master_bottom_collapsed = TEST_IMAGES["MASTER"]["master_bottom_collapsed"]

        cls.images = (cls.master_collapsed, cls.master_expanded)
        cls.bottom_images = (cls.master_bottom_expanded, cls.master_bottom_expanded)

    def test_raid_cards_on_screen(self):
        """Test that the bot can determine if the account icon is on the screen."""
        raid_cards = BOT_IMAGES["MASTER"]["raid_cards"]

        # Check that the images above contain the "account" icon.
        for path in self.images:
            image = Image.open(path)
            self.bot.grabber.current = image
            self.assertTrue(self.bot.grabber.search(raid_cards, bool_only=True, testing=True))

    def test_skill_tree_on_screen(self):
        """Test that the bot can determine if the skill tree icon is on the screen."""
        skill_tree = BOT_IMAGES["MASTER"]["skill_tree"]

        # Check that the images above contain the "skill_tree" icon.
        for path in self.images:
            image = Image.open(path)
            self.bot.grabber.current = image
            self.assertTrue(self.bot.grabber.search(skill_tree, bool_only=True, testing=True))

    def test_achievements_on_screen(self):
        """Test that the bot can determine if the achievements icon is on the screen."""
        achievements = BOT_IMAGES["MASTER"]["achievements"]

        # Check that the images above contain the "achievements" icon.
        for path in self.images:
            image = Image.open(path)
            self.bot.grabber.current = image
            self.assertTrue(self.bot.grabber.search(achievements, bool_only=True, testing=True))

    def test_inbox_on_screen(self):
        """Test that the bot can determine if the inbox icon is on the screen."""
        inbox = BOT_IMAGES["MASTER"]["inbox"]

        # Check that the images above contain the "inbox" icon.
        for path in self.images:
            image = Image.open(path)
            self.bot.grabber.current = image
            self.assertTrue(self.bot.grabber.search(inbox, bool_only=True, testing=True))

    def test_master_on_screen(self):
        """Test that the bot can determine if the master icon is on the screen."""
        master = BOT_IMAGES["MASTER"]["master"]

        # Check that the images above contain the "master" icon.
        for path in self.images:
            image = Image.open(path)
            self.bot.grabber.current = image
            self.assertTrue(self.bot.grabber.search(master, bool_only=True, testing=True))

    def test_skills_on_screen(self):
        """Test that the bot can determine if the skills are all on the screen."""
        skills = (
            BOT_IMAGES["MASTER"]["deadly_strike"], BOT_IMAGES["MASTER"]["fire_sword"],
            BOT_IMAGES["MASTER"]["hand_of_midas"], BOT_IMAGES["MASTER"]["heavenly_strike"],
            BOT_IMAGES["MASTER"]["shadow_clone"], BOT_IMAGES["MASTER"]["war_cry"],
        )

        image = Image.open(self.master_expanded)
        self.bot.grabber.current = image
        for skill in skills:
            self.assertTrue(self.bot.grabber.search(skill, bool_only=True, testing=True))

    def test_prestige_on_screen(self):
        """Test that the bot can determine if the prestige icon is on the screen."""
        prestige = BOT_IMAGES["MASTER"]["prestige"]

        # Check that the images above contain the "prestige" icon.
        for path in self.bottom_images:
            image = Image.open(path)
            self.bot.grabber.current = image
            self.assertTrue(self.bot.grabber.search(prestige, bool_only=True, testing=True))

    def test_prestige_confirm_on_screen(self):
        """Test that the bot can determine if the prestige confirm icon is on the screen."""
        image = Image.open(TEST_IMAGES["MASTER"]["master_prestige_open"])
        confirm = BOT_IMAGES["MASTER"]["confirm_prestige"]

        self.bot.grabber.current = image
        self.assertTrue(self.bot.grabber.search(confirm, bool_only=True, testing=True))
