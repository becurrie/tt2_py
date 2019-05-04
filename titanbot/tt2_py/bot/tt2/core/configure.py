"""
configure.py

All values stored within the data/config.ini data file are parsed and placed into a readable Python class.
"""
import configparser


def _parse(config, section, key, value):
    """
    Parse a value taken from the ConfigParser.

    Possible parsed values may be an int, bool or string.
    """
    try:
        return int(value)
    except ValueError:
        try:
            return config.getboolean(section, key)
        except ValueError:
            return value


class Config:
    def __init__(self, f):
        self._base()

        config = configparser.ConfigParser()
        config.read(f)
        for section in config.sections():
            for (key, value) in config.items(section):
                setattr(self, key.upper(), _parse(config, section, key, value))

    def _base(self):
        """
        Manually set every configuration value to a default None value. This will make it easier
        to check values by providing an interface to select attributes through.

        i.e: Config.VALUE instead of getattr(Config, VALUE) when working with all values.
        """
        # RUNTIME.
        self.SOFT_SHUTDOWN_KEY = None
        self.SHUTDOWN_SECONDS = None
        self.SOFT_SHUTDOWN_ON_CRITICAL_ERROR = None
        self.UPDATE_STATS_ON_SOFT_SHUTDOWN = None

        # DEVICE.
        self.EMULATOR = None

        # GENERIC.
        self.ENABLE_PREMIUM_AD_COLLECT = None
        self.ENABLE_EGG_COLLECT = None
        self.ENABLE_TAPPING = None
        self.ENABLE_TOURNAMENTS = None

        # DAILY ACHIEVEMENTS
        self.ENABLE_DAILY_ACHIEVEMENTS = None
        self.RUN_DAILY_ACHIEVEMENT_CHECK_ON_START = None
        self.CHECK_DAILY_ACHIEVEMENTS_EVERY_X_HOURS = None

        # ACTIONS_GENERAL.
        self.RUN_ACTIONS_EVERY_X_SECONDS = None
        self.RUN_ACTIONS_ON_START = None
        self.ORDER_LEVEL_HEROES = None
        self.ORDER_LEVEL_MASTER = None
        self.ORDER_LEVEL_SKILLS = None

        # ACTIONS_MASTER.
        self.ENABLE_MASTER = None
        self.MASTER_LEVEL_INTENSITY = None

        # ACTIONS_HEROES.
        self.ENABLE_HEROES = None
        self.HERO_LEVEL_INTENSITY = None

        # ACTIONS_SKILLS.
        self.ENABLE_SKILLS = None
        self.ACTIVATE_SKILLS_ON_START = None
        self.INTERVAL_HEAVENLY_STRIKE = None
        self.INTERVAL_DEADLY_STRIKE = None
        self.INTERVAL_HAND_OF_MIDAS = None
        self.INTERVAL_FIRE_SWORD = None
        self.INTERVAL_WAR_CRY = None
        self.INTERVAL_SHADOW_CLONE = None
        self.FORCE_ENABLED_SKILLS_WAIT = None
        self.MAX_SKILL_IF_POSSIBLE = None
        self.SKILL_LEVEL_INTENSITY = None

        # ACTIONS_PRESTIGE.
        self.ENABLE_AUTO_PRESTIGE = None
        self.PRESTIGE_AFTER_X_MINUTES = None
        self.PRESTIGE_AT_STAGE = None
        self.PRESTIGE_AT_MAX_STAGE = None
        self.PRESTIGE_AT_MAX_STAGE_PERCENT = None

        # ACTIONS_ARTIFACTS.
        self.ENABLE_ARTIFACT_PURCHASE = None
        self.UPGRADE_ARTIFACT = None
        self.UPGRADE_OWNED_ARTIFACTS = None
        self.UPGRADE_OWNED_TIER = None
        self.SHUFFLE_OWNED_ARTIFACTS = None
        self.IGNORE_SPECIFIC_ARTIFACTS = None

        # STATS.
        self.ENABLE_STATS = None
        self.UPDATE_STATS_ON_START = None
        self.STATS_UPDATE_INTERVAL_MINUTES = None

        # ARTIFACT_PARSING.
        self.BOTTOM_ARTIFACT = None

        # RECOVERY.
        self.RECOVERY_CHECK_INTERVAL_MINUTES = 5
        self.RECOVERY_ALLOWED_FAILURES = 5

        # LOGGING.
        self.ENABLE_LOGGING = None
        self.LOGGING_LEVEL = None
