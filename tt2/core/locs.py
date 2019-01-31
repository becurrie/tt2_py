"""
locs.py

Create a helper class that may be used by Bot instances to provide a more readable
interface when interfacing with the locations taken from the dictionaries in maps.py
"""


class Locs:
    """
    Locs class wraps all location points into a friendly wrapper class for use with the bot.
    """
    def __init__(self, locs):
        self._base()
        for group, d in locs.items():
            for key, value in d.items():
                setattr(self, key, value)

    def _base(self):
        """Manually set every expected value."""
        # BOTTOM_BAR.
        self.master = None
        self.heroes = None
        self.equipment = None,
        self.pets = None,
        self.artifacts = None
        self.shop = None

        # DAILY_REWARD.
        self.open_rewards = None
        self.open_rewards = None
        self.close_rewards = None

        # SKILL_BAR.
        self.collect_rewards = None
        self.heavenly_strike = None
        self.deadly_strike = None
        self.hand_of_midas = None
        self.fire_sword = None
        self.war_cry = None
        self.shadow_clone = None

        # GAME_SCREEN.
        self.fight_boss = None
        self.game_middle = None
        self.player = None
        self.pet_gold = None
        self.pet_attack = None
        self.clan_ship = None
        self.scroll_start = None
        self.scroll_top_end = None
        self.scroll_bottom_end = None
        self.scroll_quick_stop = None
        self.fairies_map = None

        # PANELS.
        self.expand_collapse_top = None
        self.expand_collapse_bottom = None
        self.close_top = None
        self.close_bottom = None

        # TOURNAMENT.
        self.tournament = None
        self.tournament_prestige = None
        self.collect_prize = None
        self.join = None

        # EGGS.
        self.hatch_egg = None

        # CLAN_BATTLE.
        self.clan_battle_ready = None
        self.clan_quest = None
        self.clan_fight = None
        self.diamond_okay = None
        self.clan_leave_screen = None
        self.clan_quest_exit = None

        # AD.
        self.collect_ad = None
        self.no_thanks = None
