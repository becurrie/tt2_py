"""
test_bot.py

Test any of the functionality present within the Bot class that does not
require any interaction between the in game screen. Small utility type
functions present within the Bot can be tested here.
"""
from settings import TEST_CONFIG_FILE, TEST_STATS_FILE
from tt2.core.bot import Bot

import unittest


class TestBotArtifactRetrieval(unittest.TestCase):
    """Test functionality related to the bot class that does not interact with the in game screen."""
    def setUp(self):
        """Initialize the test case with a Bot instance for testing purposes."""
        self.bot = Bot(TEST_CONFIG_FILE, TEST_STATS_FILE)
        # Tier S Expected Artifacts.
        self.expected_s = ['book_of_shadows', 'stone_of_the_valrunes', 'flute_of_the_soloist', 'heart_of_storms',
                           'ring_of_calisto', 'invaders_gjalarhorn']
        # Tier A Expected Artifacts.
        self.expected_a = ['book_of_prophecy', 'khrysos_bowl', 'the_bronzed_compass', 'heavenly_sword', 'divine_retribution',
                           'drunken_hammer', 'samosek_sword', 'the_retaliator', "stryfe's_peace", "hero's_blade",
                           'the_sword_of_storms', 'furies_bow', 'charm_of_the_ancient', 'tiny_titan_tree', 'helm_of_hermes',
                           "o'ryans_charm", 'apollo_orb', 'earrings_of_portara', 'helheim_skull', "oath's_burden",
                           'crown_of_the_constellation', "titania's_sceptre", "fagin's_grip", 'blade_of_damocles',
                           'helmet_of_madness', 'titanium_plating', 'moonlight_bracelet', 'amethyst_staff',
                           "spearit's_vigil", 'sword_of_the_royals', 'the_cobalt_plate', 'sigils_of_judgement',
                           'foilage_of_the_keeper', 'royal_toxin', "laborer's_pendant", 'bringer_of_ragnarok',
                           'parchment_of_foresight']
        # Tier B Expected Artifacts.
        self.expected_b = ['chest_of_contentment', 'heroic_shield', 'zakynthos_coin', 'great_fay_medallion',
                           'neko_sculpture', 'coins_of_ebizu', 'fruit_of_eden', 'influential_elixir', 'avian_feather',
                           "titan's_mask", 'elixir_of_eden']
        # Tier C Expected Artifacts.
        self.expected_c = ['corrupted_rune_heart', 'durendal_sword', 'essence_of_kitsune']

    def test_tier_s(self):
        """Test that the tier S artifacts are correct."""
        self.bot.config.UPGRADE_OWNED_TIER = "S"
        self.assertEqual(self.expected_s, self.bot.get_owned_artifacts())

    def test_tier_a(self):
        """Test that the tier A artifacts are correct."""
        self.bot.config.UPGRADE_OWNED_TIER = "A"
        self.assertEqual(self.expected_a, self.bot.get_owned_artifacts())

    def test_tier_b(self):
        """Test that the tier B artifacts are correct."""
        self.bot.config.UPGRADE_OWNED_TIER = "B"
        self.assertEqual(self.expected_b, self.bot.get_owned_artifacts())

    def test_tier_c(self):
        """Test that the tier C artifacts are correct."""
        self.bot.config.UPGRADE_OWNED_TIER = "C"
        self.assertEqual(self.expected_c, self.bot.get_owned_artifacts())

    def test_all_tiers(self):
        """Test that the tiers S, A, B, C artifacts are correct."""
        self.bot.config.UPGRADE_OWNED_TIER = "S,A,B,C"
        expected = self.expected_s + self.expected_a + self.expected_b + self.expected_c

        # Since the artifact lists are combined, loop through each one and make sure it
        # present in the bots calculated artifacts.
        artifacts = self.bot.get_owned_artifacts()
        for i in range(len(expected)):
            self.assertTrue(expected[i] in artifacts)

    def test_next_artifact_update(self):
        """Test that the next upgrade iteration works as intended."""
        self.bot.config.UPGRADE_OWNED_TIER = "S"
        self.bot.owned_artifacts = self.bot.get_owned_artifacts()
        self.bot.next_artifact_index = 0
        self.bot.next_artifact_upgrade = self.bot.owned_artifacts[self.bot.next_artifact_index]
        num_prestiges = 20

        expected = self.expected_s + self.expected_s + self.expected_s + ["book_of_shadows", "stone_of_the_valrunes"]
        for i in range(num_prestiges):
            self.assertEqual(expected[i], self.bot.next_artifact_upgrade)
            self.bot.update_next_artifact_upgrade()

    def test_ignore_artifacts(self):
        self.bot.config.UPGRADE_OWNED_TIER = "S"
        self.bot.config.IGNORE_SPECIFIC_ARTIFACTS = "book_of_shadows,flute_of_the_soloist"

        expected = ['stone_of_the_valrunes', 'heart_of_storms', 'ring_of_calisto', 'invaders_gjalarhorn']
        self.assertEqual(expected, self.bot.get_owned_artifacts())
