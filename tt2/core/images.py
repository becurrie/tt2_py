"""
images.py

Create a helper class that may be used by Bot instances to provide a more readable
interface when interfacing with the images taken from the dictionaries in maps.py
"""


class Images:
    """
    Images class wraps all images used by the bot into a helpful wrapper class.

    Giving bot access to more readable versions of every single image used to parse information.
    """
    def __init__(self, images):
        self._base()
        for group, d in images.items():
            for key, value in d.items():
                setattr(self, key, value)

    def _base(self):
        """Manually set every expected value, allows for easier access later on."""
        # ADS.
        self.collect_ad = None
        self.no_thanks = None

        # ARTIFACTS.
        self.artifacts_discovered = None
        self.book_of_shadows = None
        self.spend_max = None

        # CLAN_BATTLE.
        self.battle_available = None
        self.diamond = None
        self.goal_complete = None
        self.deal_110_next_attack = None

        # DAILY_REWARD.
        self.collect_reward = None

        # EQUIPMENT.
        self.crafting = None

        # GENERIC.
        self.artifacts_active = None
        self.buy_max = None
        self.buy_one = None
        self.buy_one_hundred = None
        self.buy_ten = None
        self.collapse_panel = None
        self.equipment_active = None
        self.exit_panel = None
        self.expand_panel = None
        self.heroes_active = None
        self.master_active = None
        self.max = None
        self.pets_active = None
        self.shop_active = None

        # HEROES.
        self.max_level = None
        self.maya_muerta = None
        self.stats = None
        self.story = None
        self.upgrades = None

        # MASTER.
        self.account = None
        self.achievements = None
        self.cancel_active_skill = None
        self.confirm_prestige = None
        self.deadly_strike = None
        self.fire_sword = None
        self.hand_of_midas = None
        self.heavenly_strike = None
        self.inbox = None
        self.master = None
        self.prestige = None
        self.shadow_clone = None
        self.skill_level_zero = None
        self.skill_max_level = None
        self.skill_tree = None
        self.war_cry = None

        # NO_PANELS.
        self.clan_battle_ready = None
        self.clan_no_battle = None
        self.daily_reward = None
        self.fight_boss = None
        self.hatch_egg = None
        self.leave_boss = None
        self.settings = None
        self.tournament = None

        # PETS.
        self.next_egg = None

        # SHOP.
        self.shop_keeper = None

        # TOURNAMENTS.
        self.join = None
        self.collect_prize = None
