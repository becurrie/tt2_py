from django.db import models
from django.core.cache import cache
from django.utils.text import slugify
from django_paranoid.models import ParanoidModel

from titandash.models.mixins import ExportModelMixin
from titandash.models.artifact import Artifact
from titandash.models.artifact import Tier
from titandash.utils import import_model_kwargs
from titandash.constants import (
    SKILL_LEVEL_CHOICES, SKILL_MAX_CHOICE, GENERIC_BLACKLIST, DATETIME_FMT,
    NO_PERK, PERK_CHOICES
)

EXPORT_BLACKLIST = [
    "raid_notifications_twilio_account_sid",
    "raid_notifications_twilio_auth_token",
    "raid_notifications_twilio_from_number",
    "raid_notifications_twilio_to_number"
]

# Use the compression keys to compress/decompress the configuration export string.
# As more configuration options are added, we should add the field name to this list
# with the next incrementing number available. This will ensure that we future proof
# our export function without needing to worry about the number given.
COMPRESSION_KEYS = {
    "name": 0,
    "soft_shutdown_on_critical_error": 1,
    "soft_shutdown_update_stats": 2,
    "post_action_min_wait_time": 3,
    "post_action_max_wait_time": 4,
    "enable_egg_collection": 8,
    "enable_tapping": 9,
    "enable_tournaments": 10,
    "enable_breaks": 11,
    "breaks_jitter": 12,
    "breaks_minutes_required": 13,
    "breaks_minutes_max": 14,
    "breaks_minutes_min": 15,
    "enable_daily_achievements": 16,
    "daily_achievements_check_on_start": 17,
    "daily_achievements_check_every_x_hours": 18,
    "enable_milestones": 19,
    "milestones_check_on_start": 20,
    "milestones_check_every_x_hours": 21,
    "enable_raid_notifications": 22,
    "raid_notifications_check_on_start": 23,
    "raid_notifications_check_every_x_minutes": 24,
    "raid_notifications_twilio_account_sid": 25,
    "raid_notifications_twilio_auth_token": 26,
    "raid_notifications_twilio_from_number": 27,
    "raid_notifications_twilio_to_number": 28,
    "enable_master": 34,
    "master_level_intensity": 35,
    "enable_heroes": 36,
    "hero_level_intensity": 37,
    "activate_skills_on_start": 39,
    "interval_heavenly_strike": 40,
    "interval_deadly_strike": 41,
    "interval_hand_of_midas": 42,
    "interval_fire_sword": 43,
    "interval_war_cry": 44,
    "interval_shadow_clone": 45,
    "skill_level_intensity": 48,
    "enable_auto_prestige": 49,
    "prestige_x_minutes": 50,
    "prestige_at_stage": 51,
    "prestige_at_max_stage": 52,
    "prestige_at_max_stage_percent": 53,
    "enable_artifact_purchase": 54,
    "enable_artifact_discover_enchant": 55,
    "upgrade_owned_tier": 56,
    "shuffle_artifacts": 57,
    "ignore_artifacts": 58,
    "upgrade_artifacts": 59,
    "enable_stats": 60,
    "update_stats_on_start": 61,
    "update_stats_every_x_minutes": 62,
    "enable_clan_results_parse": 63,
    "parse_clan_results_on_start": 64,
    "parse_clan_results_every_x_minutes": 65,
    "master_level_only_once": 70,
    "enable_prestige_threshold_randomization": 71,
    "prestige_random_min_time": 72,
    "prestige_random_max_time": 73,
    "enable_minigames": 74,
    "enable_coordinated_offensive": 75,
    "enable_astral_awakening": 76,
    "enable_heart_of_midas": 77,
    "enable_flash_zip": 78,
    "enable_daily_rewards": 79,
    "enable_clan_crates": 80,
    "master_level_every_x_seconds": 81,
    "hero_level_every_x_seconds": 82,
    "enable_level_skills": 83,
    "level_skills_every_x_seconds": 84,
    "level_heavenly_strike_cap": 85,
    "level_deadly_strike_cap": 86,
    "level_hand_of_midas_cap": 87,
    "level_fire_sword_cap": 88,
    "level_war_cry_cap": 89,
    "level_shadow_clone_cap": 90,
    "enable_activate_skills": 91,
    "master_level_on_start": 92,
    "hero_level_on_start": 93,
    "level_skills_on_start": 94,
    "activate_skills_every_x_seconds": 95,
    "tapping_repeat": 96,
    "minigames_repeat": 97,
    "enable_perk_usage": 98,
    "enable_perk_diamond_purchase": 99,
    "enable_perk_only_tournament": 100,
    "use_perks_every_x_hours": 101,
    "use_perk_on_prestige": 102,
    "enable_power_of_swiping": 103,
    "enable_adrenaline_rush": 104,
    "enable_make_it_rain": 105,
    "enable_mana_potion": 106,
    "enable_doom": 107,
    "enable_clan_crate": 108,
    "use_perks_on_start": 109,
    "enable_mega_boost": 110,
    "enable_headgear_swap": 111,
    "headgear_swap_every_x_seconds": 112,
    "headgear_swap_on_start": 113,
    "enable_forbidden_contract": 114,
    "enable_summon_dagger": 115,
}

HELP_TEXT = {
    "name": "Specify a name for this configuration.",
    "soft_shutdown_on_critical_error": "Should a soft shutdown be performed if the bot runs into a critical error during a session.",
    "soft_shutdown_update_stats": "Perform a stats update when a soft shutdown is executed.",
    "post_action_min_wait_time": "Determine the minimum amount of seconds to wait after an in game function is finished executing.",
    "post_action_max_wait_time": "Determine the maximum amount of seconds to wait after an in game function is finished executing.",
    "enable_tapping": "Enable the ability to tap on titans (This also enables the clicking of fairies in game).",
    "tapping_repeat": "Specify how many times the tapping loop should run when executed.",
    "enable_daily_rewards": "Enable the ability to collect daily rewards in game when they become available.",
    "enable_clan_crates": "Enable the ability to collect clan crates in game when they are available.",
    "enable_egg_collection": "Enable the ability to collect and hatch eggs in game.",
    "enable_tournaments": "Enable the ability to enter and participate in tournaments.",
    "enable_minigames": "Enable the ability to enable/disable different skill minigames that can be executed.",
    "minigames_repeat": "Specify how many times the minigames loop should run when executed.",
    "enable_coordinated_offensive": "Enable coordinated offensive tapping skill minigame.",
    "enable_astral_awakening": "Enable astral awakening tapping skill minigame.",
    "enable_heart_of_midas": "Enable heart of midas tapping skill minigame.",
    "enable_flash_zip": "Enable flash zip tapping skill minigame.",
    "enable_forbidden_contract": "Enable forbidden contract tapping skill minigame.",
    "enable_summon_dagger": "Enable summon dagger tapping skill minigame.",
    "enable_breaks": "Enable the ability to take breaks in game.",
    "breaks_jitter": "Specify a jitter amount so that breaks take place at different intervals.",
    "breaks_minutes_required": "How many minutes of concurrent playtime is required before a break takes place.",
    "breaks_minutes_max": "Maximum amount of minutes to break for.",
    "breaks_minutes_min": "Minimum amount of minutes to break for.",
    "enable_daily_achievements": "Enable the ability to check and collect daily achievements in game.",
    "daily_achievements_check_on_start": "Should daily achievements be checked for completion when a session is started.",
    "daily_achievements_check_every_x_hours": "Determine how many hours between each daily achievement check.",
    "enable_milestones": "Enable the ability to check and collect milestones in game.",
    "milestones_check_on_start": "Should milestones be checked for completion when a session is started.",
    "milestones_check_every_x_hours": "Determine how many hours between each milestone check.",
    "enable_raid_notifications": "Should notifications be sent to a user when a clan raid starts or attacks are ready.",
    "raid_notifications_check_on_start": "Should a raid notifications check take place when a session is started.",
    "raid_notifications_check_every_x_minutes": "Determine how many minutes between each raid notifications check.",
    "raid_notifications_twilio_account_sid": "Specify the account sid associated with your twilio account.",
    "raid_notifications_twilio_auth_token": "Specify the auth token associated with your twilio account.",
    "raid_notifications_twilio_from_number": "Specify the from number associated with your twilio account",
    "raid_notifications_twilio_to_number": "Specify the phone number you would like to receive notifications at (ex: +19991234567)",
    "enable_master": "Enable the ability to level the sword master in game.",
    "master_level_every_x_seconds": "Specify the amount of seconds to wait in between each sword master level process.",
    "master_level_on_start": "Should the sword master be levelled once when a session is started.",
    "master_level_only_once": "Enable the option to only level the sword master once at the beginning of a session, and once after every prestige.",
    "master_level_intensity": "Determine the amount of clicks performed whenever the sword master is levelled.",
    "enable_heroes": "Enable the ability level heroes in game.",
    "hero_level_every_x_seconds": "Specify the amount of seconds to wait in between each heroes level process.",
    "hero_level_on_start": "Should heroes be levelled once when a session is started.",
    "hero_level_intensity": "Determine the amount of clicks performed on each hero when they are levelled.",
    "enable_level_skills": "Enable the ability to level skills in game.",
    "level_skills_every_x_seconds": "Specify the amount of seconds to wait in between each skills level process.",
    "level_skills_on_start": "Should skills be levelled once when a session is started.",
    "level_heavenly_strike_cap": "Choose the level cap for the heavenly strike skill.",
    "level_deadly_strike_cap": "Choose the level cap for the deadly strike skill.",
    "level_hand_of_midas_cap": "Choose the level cap for the hand of midas skill.",
    "level_fire_sword_cap": "Choose the level cap for the fire sword skill.",
    "level_war_cry_cap": "Choose the level cap for the war cry skill.",
    "level_shadow_clone_cap": "Choose the level cap for the shadow clone skill.",
    "enable_activate_skills": "Enable the ability to activate skills in game.",
    "activate_skills_every_x_seconds": "Specify the amount of seconds to wait in between each skills activation process.",
    "activate_skills_on_start": "Should skills be activated once when a session is started.",
    "interval_heavenly_strike": "How many seconds between each activation of the heavenly strike skill.",
    "interval_deadly_strike": "How many seconds between each activation of the deadly strike skill.",
    "interval_hand_of_midas": "How many seconds between each activation of the hand of midas skill.",
    "interval_fire_sword": "How many seconds between each activation of the fire sword skill.",
    "interval_war_cry": "How many seconds between each activation of the war cry skill.",
    "interval_shadow_clone": "How many seconds between each activation of the shadow clone skill.",
    "enable_headgear_swap": "Enable the ability to swap headgear in game based on the most recently parsed hero. This setting requires that you have locked the headgear you wish to use. The first one found of the newest heroes type will be equipped.",
    "headgear_swap_every_x_seconds": "Specify the amount of seconds to wait in between each headgear swap process.",
    "headgear_swap_on_start": "Should a headgear swap be initiated when a session is started.",
    "enable_perk_usage": "Enable the ability to use and purchase perks in game.",
    "enable_perk_diamond_purchase": "Enable the ability to purchase a perk with diamonds if you don't currently have one.",
    "enable_perk_only_tournament": "Enable the ability to only check and use perks when a tournament is joined initially.",
    "use_perks_every_x_hours": "Specify the amount of hours to wait in between each perk usage process.",
    "use_perk_on_prestige": "Choose a specific perk that you would like to use or purchase (if enabled) when a prestige occurs.",
    "use_perks_on_start": "Should perks be used or purchased when a session is started.",
    "enable_mega_boost": "Enable the mega boost perk. This perk can only be collected if vip or pihole ads are enabled.",
    "enable_power_of_swiping": "Enable the power of swiping perk.",
    "enable_adrenaline_rush": "Enable the adrenaline rush perk.",
    "enable_make_it_rain": "Enable the make it rain perk.",
    "enable_mana_potion": "Enable the mana potion perk.",
    "enable_doom": "Enable the doom perk.",
    "enable_clan_crate": "Enable the clan crate perk.",
    "skill_level_intensity": "Determine the amount of clicks performed on each skill when levelled.",
    "enable_auto_prestige": "Enable the ability to automatically prestige in game.",
    "enable_prestige_threshold_randomization": "Enable the ability to add additional time to a prestige once one of the thresholds below are reached. For example, if this setting is enabled and you choose to prestige every 30 minutes, the actual prestige may take place in 33 minutes depending on the settings below. Additionally, if you choose to prestige at a percent, once you reach your percentage, the bot will wait the calculated amount of time before prestiging.",
    "prestige_random_min_time": "Specify the lower floor that will be used when calculating an amount of time to wait after a prestige threshold is reached.",
    "prestige_random_max_time": "Specify the upper ceiling that will be used when calculating an amount of time to wait after a prestige threshold is reached.",
    "prestige_x_minutes": "Determine the amount of minutes between each auto prestige process. This can be used for farming, or as a hard limit that is used if the thresholds below aren't met within this time limit. (0 = off).",
    "prestige_at_stage": "Determine the stage needed before the prestige process is started (Once you reach/pass this stage, you will prestige). (0 = off).",
    "prestige_at_max_stage": "Should a prestige take place once your max stage has been reached? (Stats must be up to date).",
    "prestige_at_max_stage_percent": "Determine if you would like to perform an automatic prestige once a certain percent of your max stage has been reached. You may use values larger than 100 here to push your max stage. (ie: 99, 99.5, 101) (0 = off).",
    "enable_artifact_discover_enchant": "Enable the ability to discover or enchant artifacts if possible after a prestige.",
    "enable_artifact_purchase": "Enable the ability to purchase and upgrade discovered artifacts in game after a prestige has taken place.",
    "upgrade_owned_tier": "Upgrade a specific tier (or tiers) of artifacts only.",
    "shuffle_artifacts": "Should owned artifacts be shuffled once calculated.",
    "ignore_artifacts": "Should any specific artifacts be ignored regardless of them being owned or not.",
    "upgrade_artifacts": "Should any artifacts be specifically upgraded, disabling the above settings and choosing an artifact here will only upgrade the selected artifact(s).",
    "enable_stats": "Enable the ability to update statistics during game sessions.",
    "update_stats_on_start": "Should stats be updated when a session is started.",
    "update_stats_every_x_minutes": "Determine how many minutes between each stats update in game.",
    "enable_clan_results_parse": "Enable the ability to have the bot attempt to parse out clan raid results.",
    "parse_clan_results_on_start": "Should clan results be parsed when a session is started.",
    "parse_clan_results_every_x_minutes": "Determine how many minutes between each clan results parse attempt."
}


class Configuration(ParanoidModel, ExportModelMixin):
    """
    Configuration Model.

    Store set of configuration values here. These may be used by a user when starting a bot session.
    Multiple can be created and swapped out as needed.
    """
    class Meta:
        verbose_name = "Configuration"
        verbose_name_plural = "Configurations"

    name = models.CharField(max_length=255)

    # RUNTIME Settings.
    soft_shutdown_on_critical_error = models.BooleanField(verbose_name="Soft Shutdown On Critical Error", default=False, help_text=HELP_TEXT["soft_shutdown_on_critical_error"])
    soft_shutdown_update_stats = models.BooleanField(verbose_name="Update Stats On Soft Shutdown", default=True, help_text=HELP_TEXT["soft_shutdown_update_stats"])
    post_action_min_wait_time = models.PositiveIntegerField(verbose_name="Post Action Min Wait Time", default=0, help_text=HELP_TEXT["post_action_min_wait_time"])
    post_action_max_wait_time = models.PositiveIntegerField(verbose_name="Post Action Max Wait Time", default=1, help_text=HELP_TEXT["post_action_max_wait_time"])

    # GENERIC Settings.
    enable_tapping = models.BooleanField(verbose_name="Enable Tapping", default=True, help_text=HELP_TEXT["enable_tapping"])
    tapping_repeat = models.PositiveIntegerField(verbose_name="Repeat Tapping", default=1, help_text=HELP_TEXT["tapping_repeat"])
    enable_daily_rewards = models.BooleanField(verbose_name="Enable Daily Rewards", default=True, help_text=HELP_TEXT["enable_daily_rewards"])
    enable_clan_crates = models.BooleanField(verbose_name="Enable Clan Crates", default=True, help_text=HELP_TEXT["enable_clan_crates"])
    enable_egg_collection = models.BooleanField(verbose_name="Enable Egg Collection", default=True, help_text=HELP_TEXT["enable_egg_collection"])
    enable_tournaments = models.BooleanField(verbose_name="Enable Tournaments", default=True, help_text=HELP_TEXT["enable_tournaments"])

    # MINIGAME Settings.
    enable_minigames = models.BooleanField(verbose_name="Enable Skill Minigames", default=False, help_text=HELP_TEXT["enable_minigames"])
    minigames_repeat = models.PositiveIntegerField(verbose_name="Repeat Minigames", default=1, help_text=HELP_TEXT["minigames_repeat"])
    enable_coordinated_offensive = models.BooleanField(verbose_name="Enable Coordinated Offensive", default=False, help_text=HELP_TEXT["enable_coordinated_offensive"])
    enable_astral_awakening = models.BooleanField(verbose_name="Enable Astral Awakening", default=False, help_text=HELP_TEXT["enable_astral_awakening"])
    enable_heart_of_midas = models.BooleanField(verbose_name="Enable Heart Of Midas", default=False, help_text=HELP_TEXT["enable_heart_of_midas"])
    enable_flash_zip = models.BooleanField(verbose_name="Enable Flash Zip", default=False, help_text=HELP_TEXT["enable_flash_zip"])
    enable_forbidden_contract = models.BooleanField(verbose_name="Enable Forbidden Contract", default=False, help_text=HELP_TEXT["enable_forbidden_contract"])
    enable_summon_dagger = models.BooleanField(verbose_name="Enable Summon Dagger", default=False, help_text=HELP_TEXT["enable_summon_dagger"])

    # BREAKS Settings.
    enable_breaks = models.BooleanField(verbose_name="Enable Breaks", default=True, help_text=HELP_TEXT["enable_breaks"])
    breaks_jitter = models.PositiveIntegerField(verbose_name="Breaks Jitter Amount", default=40, help_text=HELP_TEXT["breaks_jitter"])
    breaks_minutes_required = models.PositiveIntegerField(verbose_name="Minutes Required Before Break Is Activated", default=180, help_text=HELP_TEXT["breaks_minutes_required"])
    breaks_minutes_max = models.PositiveIntegerField(verbose_name="Max Minutes For Break", default=60, help_text=HELP_TEXT["breaks_minutes_max"])
    breaks_minutes_min = models.PositiveIntegerField(verbose_name="Min Minutes For Break", default=20, help_text=HELP_TEXT["breaks_minutes_min"])

    # DAILY ACHIEVEMENT Settings.
    enable_daily_achievements = models.BooleanField(verbose_name="Enable Daily Achievements", default=True, help_text=HELP_TEXT["enable_daily_achievements"])
    daily_achievements_check_on_start = models.BooleanField(verbose_name="Check Daily Achievements On Session Start", default=False, help_text=HELP_TEXT["daily_achievements_check_on_start"])
    daily_achievements_check_every_x_hours = models.PositiveIntegerField(verbose_name="Check Daily Achievements Every X Hours", default=1, help_text=HELP_TEXT["daily_achievements_check_every_x_hours"])

    # MILESTONES Settings.
    enable_milestones = models.BooleanField(verbose_name="Enable Milestones", default=True, help_text=HELP_TEXT["enable_milestones"])
    milestones_check_on_start = models.BooleanField(verbose_name="Check Milestones On Session Start", default=False, help_text=HELP_TEXT["milestones_check_on_start"])
    milestones_check_every_x_hours = models.PositiveIntegerField(verbose_name="Check Milestones Every X Hours", default=1, help_text=HELP_TEXT["milestones_check_every_x_hours"])

    # RAID NOTIFICATION Settings.
    enable_raid_notifications = models.BooleanField(verbose_name="Enable Raid Notifications", default=False, help_text=HELP_TEXT["enable_raid_notifications"])
    raid_notifications_check_on_start = models.BooleanField(verbose_name="Check For Raid Notification On Session Start", default=False, help_text=HELP_TEXT["raid_notifications_check_on_start"])
    raid_notifications_check_every_x_minutes = models.PositiveIntegerField(verbose_name="Check For Raid Notification Every X Minutes", default=30, help_text=HELP_TEXT["raid_notifications_check_every_x_minutes"])

    raid_notifications_twilio_account_sid = models.CharField(verbose_name="Raid Notifications Twilio Account SID", blank=True, null=True, max_length=255, help_text=HELP_TEXT["raid_notifications_twilio_account_sid"])
    raid_notifications_twilio_auth_token = models.CharField(verbose_name="Raid Notifications Twilio Auth Token", blank=True, null=True, max_length=255, help_text=HELP_TEXT["raid_notifications_twilio_auth_token"])
    raid_notifications_twilio_from_number = models.CharField(verbose_name="Raid Notifications Twilio From Number", blank=True, null=True, max_length=255, help_text=HELP_TEXT["raid_notifications_twilio_from_number"])
    raid_notifications_twilio_to_number = models.CharField(verbose_name="Raid Notifications Twilio To Number", blank=True, null=True, max_length=255, help_text=HELP_TEXT["raid_notifications_twilio_to_number"])

    # MASTER ACTION Settings.
    enable_master = models.BooleanField(verbose_name="Enable Master", default=True, help_text=HELP_TEXT["enable_master"])
    master_level_every_x_seconds = models.PositiveIntegerField(verbose_name="Level Sword Master Every X Seconds", default=60, help_text=HELP_TEXT["master_level_every_x_seconds"])
    master_level_on_start = models.BooleanField(verbose_name="Level Sword Master On Session Start", default=True, help_text=HELP_TEXT["master_level_on_start"])
    master_level_only_once = models.BooleanField(verbose_name="Level Sword Master Once Per Prestige", default=False, help_text=HELP_TEXT["master_level_only_once"])
    master_level_intensity = models.PositiveIntegerField(verbose_name="Master Level Intensity", default=5, help_text=HELP_TEXT["master_level_intensity"])

    # HEROES ACTION Settings.
    enable_heroes = models.BooleanField(verbose_name="Enable Heroes", default=True, help_text=HELP_TEXT["enable_heroes"])
    hero_level_every_x_seconds = models.PositiveIntegerField(verbose_name="Level Heroes Every X Seconds", default=60, help_text=HELP_TEXT["hero_level_every_x_seconds"])
    hero_level_on_start = models.BooleanField(verbose_name="Level Heroes On Session Start", default=True, help_text=HELP_TEXT["hero_level_on_start"])
    hero_level_intensity = models.PositiveIntegerField(verbose_name="Hero Level Intensity", default=3, help_text=HELP_TEXT["hero_level_intensity"])

    # SKILLS LEVEL ACTION Settings
    enable_level_skills = models.BooleanField(verbose_name="Enable Level Skills", default=True, help_text=HELP_TEXT["enable_level_skills"])
    level_skills_every_x_seconds = models.PositiveIntegerField(verbose_name="Level Skills Every X Seconds", default=120, help_text=HELP_TEXT["level_skills_every_x_seconds"])
    level_skills_on_start = models.BooleanField(verbose_name="Level Skills On Session Start", default=True, help_text=HELP_TEXT["level_skills_on_start"])
    level_heavenly_strike_cap = models.CharField(verbose_name="Heavenly Strike Level Cap", choices=SKILL_LEVEL_CHOICES, max_length=255, default=SKILL_MAX_CHOICE, help_text=HELP_TEXT["level_heavenly_strike_cap"])
    level_deadly_strike_cap = models.CharField(verbose_name="Deadly Strike Level Cap", choices=SKILL_LEVEL_CHOICES, max_length=255, default=SKILL_MAX_CHOICE, help_text=HELP_TEXT["level_deadly_strike_cap"])
    level_hand_of_midas_cap = models.CharField(verbose_name="Hand Of Midas Level Cap", choices=SKILL_LEVEL_CHOICES, max_length=255, default=SKILL_MAX_CHOICE, help_text=HELP_TEXT["level_hand_of_midas_cap"])
    level_fire_sword_cap = models.CharField(verbose_name="Fire Sword Level Cap", choices=SKILL_LEVEL_CHOICES, max_length=255, default=SKILL_MAX_CHOICE, help_text=HELP_TEXT["level_fire_sword_cap"])
    level_war_cry_cap = models.CharField(verbose_name="War Cry Level Cap", choices=SKILL_LEVEL_CHOICES, max_length=255, default=SKILL_MAX_CHOICE, help_text=HELP_TEXT["level_war_cry_cap"])
    level_shadow_clone_cap = models.CharField(verbose_name="Shadow Clone Level Cap", choices=SKILL_LEVEL_CHOICES, max_length=255, default=SKILL_MAX_CHOICE, help_text=HELP_TEXT["level_shadow_clone_cap"])

    # SKILLS ACTIVATE ACTION Settings.
    enable_activate_skills = models.BooleanField(verbose_name="Enable Activate Skills", default=True, help_text=HELP_TEXT["enable_activate_skills"])
    activate_skills_every_x_seconds = models.PositiveIntegerField(verbose_name="Activate Skills Every X Seconds", default=30, help_text=HELP_TEXT["activate_skills_every_x_seconds"])
    activate_skills_on_start = models.BooleanField(verbose_name="Activate Skills On Session Start", default=True, help_text=HELP_TEXT["activate_skills_on_start"])
    interval_heavenly_strike = models.PositiveIntegerField(verbose_name="Heavenly Strike Interval", default=0, help_text=HELP_TEXT["interval_heavenly_strike"])
    interval_deadly_strike = models.PositiveIntegerField(verbose_name="Deadly Strike Interval", default=20, help_text=HELP_TEXT["interval_deadly_strike"])
    interval_hand_of_midas = models.PositiveIntegerField(verbose_name="Hand Of Midas Interval", default=30, help_text=HELP_TEXT["interval_hand_of_midas"])
    interval_fire_sword = models.PositiveIntegerField(verbose_name="Fire Sword Interval", default=40, help_text=HELP_TEXT["interval_fire_sword"])
    interval_war_cry = models.PositiveIntegerField(verbose_name="War Cry Interval", default=50, help_text=HELP_TEXT["interval_war_cry"])
    interval_shadow_clone = models.PositiveIntegerField(verbose_name="Shadow Clone Interval", default=60, help_text=HELP_TEXT["interval_shadow_clone"])

    # HEADGEAR SWAP Settings.
    enable_headgear_swap = models.BooleanField(verbose_name="Enable Headgear Swap", default=False, help_text=HELP_TEXT["enable_headgear_swap"])
    headgear_swap_every_x_seconds = models.PositiveIntegerField(verbose_name="Swap Headgear Every X Seconds", default=300, help_text=HELP_TEXT["headgear_swap_every_x_seconds"])
    headgear_swap_on_start = models.BooleanField(verbose_name="Headgear Swap On Session Start", default=False, help_text=HELP_TEXT["headgear_swap_on_start"])

    # PERK Settings.
    enable_perk_usage = models.BooleanField(verbose_name="Enable Perks", default=False, help_text=HELP_TEXT["enable_perk_usage"])
    enable_perk_diamond_purchase = models.BooleanField(verbose_name="Enable Perk Diamond Purchase", default=False, help_text=HELP_TEXT["enable_perk_diamond_purchase"])
    enable_perk_only_tournament = models.BooleanField(verbose_name="Enable Perks Only During Tournaments", default=False, help_text=HELP_TEXT["enable_perk_only_tournament"])
    use_perks_every_x_hours = models.PositiveIntegerField(verbose_name="Use Perks Every X Hours", default=12, help_text=HELP_TEXT["use_perks_every_x_hours"])
    use_perks_on_start = models.BooleanField(verbose_name="Use Perks On Session Start", default=False, help_text=HELP_TEXT["use_perks_on_start"])
    use_perk_on_prestige = models.CharField(verbose_name="Use Perk On Prestige", choices=PERK_CHOICES, default=NO_PERK, max_length=255, help_text=HELP_TEXT["use_perk_on_prestige"])
    enable_mega_boost = models.BooleanField(verbose_name="Enable Mega Boost", default=False, help_text=HELP_TEXT["enable_mega_boost"])
    enable_power_of_swiping = models.BooleanField(verbose_name="Enable Power Of Swiping", default=False, help_text=HELP_TEXT["enable_power_of_swiping"])
    enable_adrenaline_rush = models.BooleanField(verbose_name="Enable Adrenaline Rush", default=False, help_text=HELP_TEXT["enable_adrenaline_rush"])
    enable_make_it_rain = models.BooleanField(verbose_name="Enable Make It Rain", default=False, help_text=HELP_TEXT["enable_make_it_rain"])
    enable_mana_potion = models.BooleanField(verbose_name="Enable Mana Potion", default=False, help_text=HELP_TEXT["enable_mana_potion"])
    enable_doom = models.BooleanField(verbose_name="Enable Doom", default=False, help_text=HELP_TEXT["enable_doom"])
    enable_clan_crate = models.BooleanField(verbose_name="Enable Clan Crate", default=False, help_text=HELP_TEXT["enable_clan_crate"])

    # PRESTIGE ACTION Settings.
    enable_auto_prestige = models.BooleanField(verbose_name="Enable Auto Prestige", default=True, help_text=HELP_TEXT["enable_auto_prestige"])
    enable_prestige_threshold_randomization = models.BooleanField(verbose_name="Enable Prestige Threshold Randomization", default=True, help_text=HELP_TEXT["enable_prestige_threshold_randomization"])
    prestige_random_min_time = models.PositiveIntegerField(verbose_name="Prestige Threshold Random Min Time", default=2, help_text=HELP_TEXT["prestige_random_min_time"])
    prestige_random_max_time = models.PositiveIntegerField(verbose_name="Prestige Threshold Random Max Time", default=8, help_text=HELP_TEXT["prestige_random_max_time"])
    prestige_x_minutes = models.PositiveIntegerField(verbose_name="Prestige In X Minutes", default=45, help_text=HELP_TEXT["prestige_x_minutes"])
    prestige_at_stage = models.PositiveIntegerField(verbose_name="Prestige At Stage", default=0, help_text=HELP_TEXT["prestige_at_stage"])
    prestige_at_max_stage = models.BooleanField(verbose_name="Prestige At Max Stage", default=False, help_text=HELP_TEXT["prestige_at_max_stage"])
    prestige_at_max_stage_percent = models.DecimalField(verbose_name="Prestige At Max Stage Percent", default=0, decimal_places=3, max_digits=255, help_text=HELP_TEXT["prestige_at_max_stage_percent"])

    # ARTIFACTS ACTION Settings.
    enable_artifact_discover_enchant = models.BooleanField(verbose_name="Enable Artifact Discover/Enchant", default=True, help_text=HELP_TEXT["enable_artifact_discover_enchant"])
    enable_artifact_purchase = models.BooleanField(verbose_name="Enable Artifact Purchase", default=True, help_text=HELP_TEXT["enable_artifact_purchase"])
    shuffle_artifacts = models.BooleanField(verbose_name="Shuffle Artifacts", default=True, help_text=HELP_TEXT["shuffle_artifacts"])
    upgrade_owned_tier = models.ManyToManyField(verbose_name="Upgrade Owned Tier", to="Tier", blank=True, related_name='upgrade_tiers', help_text=HELP_TEXT["upgrade_owned_tier"])
    ignore_artifacts = models.ManyToManyField(verbose_name="Ignore Artifacts", to="Artifact", blank=True, related_name='ignore_artifacts', help_text=HELP_TEXT["ignore_artifacts"])
    upgrade_artifacts = models.ManyToManyField(verbose_name="Upgrade Artifacts", to="Artifact", blank=True, related_name='upgrade_artifacts', help_text=HELP_TEXT["upgrade_artifacts"])

    # STATS Settings.
    enable_stats = models.BooleanField(verbose_name="Enable Stats", default=True, help_text=HELP_TEXT["enable_stats"])
    update_stats_on_start = models.BooleanField(verbose_name="Update Stats On Session Start", default=False, help_text=HELP_TEXT["update_stats_on_start"])
    update_stats_every_x_minutes = models.PositiveIntegerField(verbose_name="Update Stats Every X Minutes", default=60, help_text=HELP_TEXT["update_stats_every_x_minutes"])

    # RAID PARSING Settings.
    enable_clan_results_parse = models.BooleanField(verbose_name="Enable Clan Results Parsing", default=True, help_text=HELP_TEXT["enable_clan_results_parse"])
    parse_clan_results_on_start = models.BooleanField(verbose_name="Parse Clan Results On Session Start", default=False, help_text=HELP_TEXT["parse_clan_results_on_start"])
    parse_clan_results_every_x_minutes = models.PositiveIntegerField(verbose_name="Attempt To Parse Clan Results Every X Minutes", default=300, help_text=HELP_TEXT["parse_clan_results_every_x_minutes"])

    def __str__(self):
        return "{name}".format(name=self.name)

    @property
    def cache_key(self):
        return slugify("{model_name}{pk}".format(
            model_name=self._meta.model_name,
            pk=self.pk
        ))

    def export_key(self):
        return self.name

    def export_model(self, compression_keys=None, blacklist=None):
        return super(Configuration, self).export_model(compression_keys=COMPRESSION_KEYS, blacklist=EXPORT_BLACKLIST)

    @staticmethod
    def import_model_kwargs(export_string, compression_keys=None):
        return import_model_kwargs(export_string=export_string, compression_keys=COMPRESSION_KEYS)

    @staticmethod
    def import_model(export_kwargs):
        """
        Configuration implementation for importing a new model instance.

        The set of kwargs here should be in the format required. We can use the names we expect to derive specific
        functionality. Since M2M fields don't support creation on objects that don't exist, as well as the fact
        that some of our export keys will need to be used to get the model and attach it to the new configuration.
        """
        relation_fields = [field.name for field in Configuration._meta.get_fields() if field.name not in GENERIC_BLACKLIST and field.many_to_many or field.many_to_one]
        relational_kwargs = {k: v for k, v in export_kwargs.items() if k in relation_fields}

        # Remove relation fields from our base kwargs set.
        for field in relation_fields:
            del export_kwargs[field]

        # Update the name of the configuration.
        export_kwargs["name"] = "Imported " + export_kwargs["name"]

        # Go ahead and attempt to create the new configuration, stripped of relational fields
        # information, it will default to our normal default options.
        configuration = Configuration.objects.create(**export_kwargs)

        try:
            configuration.upgrade_owned_tier.clear()
            configuration.ignore_artifacts.clear()
            configuration.upgrade_artifacts.clear()

            # Parsing the foreign key information and m2m data needed.
            # Upgrade Owned Tier Information (Using "Tier" Value).
            relational_kwargs["upgrade_owned_tier"] = [t.pk for t in Tier.objects.filter(tier__in=relational_kwargs["upgrade_owned_tier"])]
            # Ignore Artifacts Information (Using "Key" Value).
            relational_kwargs["ignore_artifacts"] = [a.pk for a in Artifact.objects.filter(key__in=relational_kwargs["ignore_artifacts"])]
            # Upgrade Artifacts Information (Using "Key" Value).
            relational_kwargs["upgrade_artifacts"] = [a.pk for a in Artifact.objects.filter(key__in=relational_kwargs["upgrade_artifacts"])]

            configuration.upgrade_owned_tier.add(*relational_kwargs["upgrade_owned_tier"])
            configuration.ignore_artifacts.add(*relational_kwargs["ignore_artifacts"])
            configuration.upgrade_artifacts.add(*relational_kwargs["upgrade_artifacts"])
            configuration.save()

            return configuration

        # Catch any exceptions post the creation of the new configuration,
        # so we can safely delete the invalid config.
        except Exception:
            configuration.delete()
            raise

    @property
    def created(self):
        return self.created_at.astimezone().strftime(DATETIME_FMT)

    @property
    def updated(self):
        return self.updated_at.astimezone().strftime(DATETIME_FMT)

    def form_dict(self):
        """
        Return a contextual dictionary with information used to create configuration forms.
        """
        return {
            "config": self,
            "help": HELP_TEXT,
            "choices": {
                "skill_levels": SKILL_LEVEL_CHOICES,
                "artifacts": Artifact.objects.all(),
                "tiers": Tier.objects.all(),
                "perks": PERK_CHOICES,
            }
        }

    def json(self, condense=False, hide_sensitive=False):
        """
        Return a JSON compliant dictionary for current configuration.

        Use the condense flag to ensure that foreign key or many to many fields are condensed into simple values.
        """
        from titandash.utils import title
        dct = {
            "Runtime": {
                "name": self.name,
                "soft_shutdown_on_critical_error": self.soft_shutdown_on_critical_error,
                "soft_shutdown_update_stats": self.soft_shutdown_update_stats,
                "post_action_min_wait_time": self.post_action_min_wait_time,
                "post_action_max_wait_time": self.post_action_max_wait_time
            },
            "Generic": {
                "enable_tapping": self.enable_tapping,
                "tapping_repeat": self.tapping_repeat,
                "enable_daily_rewards": self.enable_daily_rewards,
                "enable_clan_crates": self.enable_clan_crates,
                "enable_egg_collection": self.enable_egg_collection,
                "enable_tournaments": self.enable_tournaments
            },
            "Minigames": {
                "enable_minigames": self.enable_minigames,
                "minigames_repeat": self.minigames_repeat,
                "enable_coordinated_offensive": self.enable_coordinated_offensive,
                "enable_astral_awakening": self.enable_astral_awakening,
                "enable_heart_of_midas": self.enable_heart_of_midas,
                "enable_flash_zip": self.enable_flash_zip,
                "enable_forbidden_contract": self.enable_forbidden_contract,
                "enable_summon_dagger": self.enable_summon_dagger
            },
            "Breaks": {
                "enable_breaks": self.enable_breaks,
                "breaks_jitter": self.breaks_jitter,
                "breaks_minutes_required": self.breaks_minutes_required,
                "breaks_minutes_max": self.breaks_minutes_max,
                "breaks_minutes_min": self.breaks_minutes_min
            },
            "Daily Achievement": {
                "enable_daily_achievements": self.enable_daily_achievements,
                "daily_achievements_check_on_start": self.daily_achievements_check_on_start,
                "daily_achievements_check_every_x_hours": self.daily_achievements_check_every_x_hours
            },
            "Raid Notifications": {
                "enable_raid_notifications": self.enable_raid_notifications,
                "raid_notifications_check_on_start": self.raid_notifications_check_on_start,
                "raid_notifications_check_every_x_minutes": self.raid_notifications_check_every_x_minutes,
                "raid_notifications_twilio_account_sid": self.raid_notifications_twilio_account_sid,
                "raid_notifications_twilio_auth_token": self.raid_notifications_twilio_auth_token,
                "raid_notifications_twilio_from_number": self.raid_notifications_twilio_from_number,
                "raid_notifications_twilio_to_number": self.raid_notifications_twilio_to_number
            },
            "Master Action": {
                "enable_master": self.enable_master,
                "master_level_every_x_seconds": self.master_level_every_x_seconds,
                "master_level_on_start": self.master_level_on_start,
                "master_level_only_once": self.master_level_only_once,
                "master_level_intensity": self.master_level_intensity
            },
            "Heroes Action": {
                "enable_heroes": self.enable_heroes,
                "hero_level_every_x_seconds": self.hero_level_every_x_seconds,
                "hero_level_on_start": self.hero_level_on_start,
                "hero_level_intensity": self.hero_level_intensity
            },
            "Level Skills Action": {
                "enable_level_skills": self.enable_level_skills,
                "level_skills_every_x_seconds": self.level_skills_every_x_seconds,
                "level_skills_on_start": self.level_skills_on_start,
                "level_heavenly_strike_cap": self.level_heavenly_strike_cap,
                "level_deadly_strike_cap": self.level_deadly_strike_cap,
                "level_hand_of_midas_cap": self.level_hand_of_midas_cap,
                "level_fire_sword_cap": self.level_fire_sword_cap,
                "level_war_cry_cap": self.level_war_cry_cap,
                "level_shadow_clone_cap": self.level_shadow_clone_cap,
            },
            "Activate Skills Action": {
                "enable_activate_skills": self.enable_activate_skills,
                "activate_skills_every_x_seconds": self.activate_skills_every_x_seconds,
                "activate_skills_on_start": self.activate_skills_on_start,
                "interval_heavenly_strike": self.interval_heavenly_strike,
                "interval_deadly_strike": self.interval_deadly_strike,
                "interval_hand_of_midas": self.interval_hand_of_midas,
                "interval_fire_sword": self.interval_fire_sword,
                "interval_war_cry": self.interval_war_cry,
                "interval_shadow_clone": self.interval_shadow_clone,
            },
            "Perks": {
                "enable_perk_usage": self.enable_perk_usage,
                "enable_perk_diamond_purchase": self.enable_perk_diamond_purchase,
                "enable_perk_only_tournament": self.enable_perk_only_tournament,
                "use_perks_on_start": self.use_perk_on_prestige,
                "use_perks_every_x_hours": self.use_perks_every_x_hours,
                "use_perk_on_prestige": self.use_perk_on_prestige,
                "enable_mega_boost": self.enable_mega_boost,
                "enable_power_of_swiping": self.enable_power_of_swiping,
                "enable_adrenaline_rush": self.enable_adrenaline_rush,
                "enable_make_it_rain": self.enable_make_it_rain,
                "enable_mana_potion": self.enable_mana_potion,
                "enable_doom": self.enable_doom,
                "enable_clan_crate": self.enable_clan_crate,
            },
            "Prestige Action": {
                "enable_auto_prestige": self.enable_auto_prestige,
                "enable_prestige_threshold_randomization": self.enable_prestige_threshold_randomization,
                "prestige_random_min_time": self.prestige_random_min_time,
                "prestige_random_max_time": self.prestige_random_max_time,
                "prestige_x_minutes": self.prestige_x_minutes,
                "prestige_at_stage": self.prestige_at_stage,
                "prestige_at_max_stage": self.prestige_at_max_stage,
                "prestige_at_max_stage_percent": self.prestige_at_max_stage_percent
            },
            "Artifacts Action": {
                "enable_artifact_discover_enchant": self.enable_artifact_discover_enchant,
                "enable_artifact_purchase": self.enable_artifact_purchase,
                "upgrade_owned_tier": [tier.json() for tier in self.upgrade_owned_tier.all()],
                "shuffle_artifacts": self.shuffle_artifacts,
                "ignore_artifacts": [art.json() for art in self.ignore_artifacts.all()],
                "upgrade_artifacts": [art.json() for art in self.upgrade_artifacts.all()]
            },
            "Stats": {
                "enable_stats": self.enable_stats,
                "update_stats_on_start": self.update_stats_on_start,
                "update_stats_every_x_minutes": self.update_stats_every_x_minutes
            },
            "Raid Parsing": {
                "enable_clan_results_parse": self.enable_clan_results_parse,
                "parse_clan_results_on_start": self.parse_clan_results_on_start,
                "parse_clan_results_every_x_minutes": self.parse_clan_results_every_x_minutes
            }
        }

        if condense:
            dct["Artifacts Action"]["upgrade_owned_tier"] = ", ".join([title(t.name) for t in self.upgrade_owned_tier.all()])
            dct["Artifacts Action"]["ignore_artifacts"] = ", ".join([title(a.name) for a in self.ignore_artifacts.all()])
            dct["Artifacts Action"]["upgrade_artifacts"] = ", ".join([title(a.name) for a in self.upgrade_artifacts.all()])

        if hide_sensitive:
            if dct["Raid Notifications"]["raid_notifications_twilio_account_sid"]:
                dct["Raid Notifications"]["raid_notifications_twilio_account_sid"] = "************"
            if dct["Raid Notifications"]["raid_notifications_twilio_auth_token"]:
                dct["Raid Notifications"]["raid_notifications_twilio_auth_token"] = "************"
            if dct["Raid Notifications"]["raid_notifications_twilio_from_number"]:
                dct["Raid Notifications"]["raid_notifications_twilio_from_number"] = "************"
            if dct["Raid Notifications"]["raid_notifications_twilio_to_number"]:
                dct["Raid Notifications"]["raid_notifications_twilio_to_number"] = "************"

        return dct

    def save(self, *args, **kwargs):
        """
        Overriding the save method to ensure we reset the cache of our configuration objects
        if we are updating an existing configuration.

        This ensures that we can reload configurations in real time through our live configuration utility.
        """
        super(Configuration, self).save(*args, **kwargs)

        # If a primary key is available, we're updating at this point. Ensure cache
        # key is deleted if one is present.
        if self.pk:
            cache.delete(key=self.cache_key)


THEME_CONFIG_HELP_TEXT = {
    "theme": "Determine the name of the theme that will be activated on the dashboard."
}


class ThemeConfigManager(models.Manager):
    """
    Attempt to grab the current theme config instance. We only ever want one single instance. If one does not exist,
    we generate a new one with some default values.
    """
    def grab(self):
        if len(self.all()) == 0:
            self.create()

        # Returning the existing instance.
        return self.all().first()


class ThemeConfig(models.Model):
    """
    ThemeConfig Model.

    Use this model to store the currently selected theme used within the dashboard.
    """
    class Meta:
        verbose_name = "Theme Config"
        verbose_name_plural = "Theme Config's"

    objects = ThemeConfigManager()
    theme = models.CharField(verbose_name="Theme", default="default", max_length=255, help_text=THEME_CONFIG_HELP_TEXT["theme"])
