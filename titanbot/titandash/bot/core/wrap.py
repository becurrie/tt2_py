"""
wrap.py

Place all helper/wrapper classes here that are used to specify coords/images and locations in game.
"""


class Images:
    """Images class wraps all images used by the bot into a helpful wrapper class."""
    def __init__(self, images, logger):
        self._base()
        self.logger = logger
        for group, d in images.items():
            for key, value in d.items():
                setattr(self, key, value)
                self.logger.debug("images.{attr}: {value}".format(attr=key, value=value))

    def _base(self):
        """
        Manually set every expected value, allows for easier access later on.
        """
        # ACHIEVEMENTS.
        self.achievements_title = None
        self.daily_collect = None
        self.daily_watch = None

        # ADS.
        self.collect_ad = None
        self.watch_ad = None
        self.no_thanks = None

        # ARTIFACTS.
        self.artifacts_discovered = None
        self.book_of_shadows = None
        self.spend_max = None
        self.salvaged = None
        self.percent_on = None
        self.discover: None
        self.enchant: None

        # CLAN_BATTLE.
        self.diamond = None
        self.goal_complete = None
        self.deal_110_next_attack = None
        self.fight = None

        # CLAN.
        self.clan = None
        self.clan_info = None

        # RAID.
        self.raid_fight = None

        # STATS.
        self.stats_title = None

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
        self.large_exit_panel = None
        self.master_active = None
        self.max = None
        self.pets_active = None
        self.shop_active = None

        # HEROES.
        self.max_level = None
        self.maya_muerta = None
        self.stats = None
        self.story = None
        self.masteries = None

        # MASTER.
        self.raid_cards = None
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
        self.clan_raid_ready = None
        self.clan_no_raid = None
        self.daily_reward = None
        self.fight_boss = None
        self.hatch_egg = None
        self.leave_boss = None
        self.settings = None
        self.tournament = None
        self.pet_damage = None
        self.master_damage = None

        # PETS.
        self.next_egg = None

        # SHOP.
        self.shop_keeper = None

        # TOURNAMENTS.
        self.join = None
        self.collect_prize = None

        # CLAN CRATE.
        self.okay = None

        # WELCOME
        self.welcome_header = None
        self.welcome_collect_no_vip = None
        self.welcome_collect_vip = None

        # RATE
        self.rate_icon = None


class Locs:
    """Locs class wraps all location points into a friendly wrapper class for use with the bot."""
    def __init__(self, locs, logger):
        self._base()
        self.logger = logger
        for group, d in locs.items():
            for key, value in d.items():
                setattr(self, key, value)
                self.logger.debug("locs.{attr}: {value}".format(attr=key, value=value))

    def _base(self):
        """
        Manually set every expected value.
        """
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
        self.clan_crate = None

        # MINIGAMES.
        self.coordinated_offensive = None
        self.astral_awakening = None
        self.heart_of_midas = None
        self.flash_zip = None

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
        self.clan = None
        self.clan_info = None
        self.clan_info_header = None
        self.clan_info_close = None
        self.clan_previous_raid = None
        self.clan_results_copy = None
        self.clan_raid = None

        # AD.
        self.collect_ad = None
        self.no_thanks = None

        # ARTIFACTS
        self.discover_point = None
        self.enchant_point = None
        self.purchase = None


class Colors:
    """Colors class wraps all colors into a friendly wrapper class for use with the bot."""
    def __init__(self, colors, logger):
        self._base()
        self.logger = logger
        for key, value in colors.items():
            setattr(self, key, value)
            self.logger.debug("colors.{attr}: {value}".format(attr=key, value=value))

    def _base(self):
        self.WHITE = None
        self.DISCOVER = None
        self.ENCHANT = None
        self.COLLECT_GREEN = None
        self.SKILL_CANT_LEVEL = None
