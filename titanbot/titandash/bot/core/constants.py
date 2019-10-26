"""
constants.py

Store any bot specific values here that should not change at any point.
"""
from settings import LOG_DIR
import re
import datetime

# Raid notifications string used to template out the message sent to a user.
RAID_NOTIFICATION_MESSAGE = "Raid attacks are available! You may now attack the active titan!"

# The lookup multiplier is used to convert in game values that are formatted with specific multipliers
# (K, M, T) into their respective float values, or the closest we can get to the actual value. These
# values can then be parsed and diffed.
STATS_LOOKUP_MULTIPLIER = {
    'K': 10**3,
    'M': 10**6,
}

# Regex used to extract the days, hours, minutes and seconds out of the strings used in game to
# determine time deltas.
STATS_DURATION_RE = re.compile(
    r'^((?P<days>[.\d]+?)d) ?((?P<hours>[.\d]+?):)?((?P<minutes>[.\d]+?):)?((?P<seconds>[.\d]+?)?$)'
)

# Format string used when converting time delta objects back into their respective format found in game.
STATS_TIMEDELTA_STR = "{D}d {H}:{M}:{S}"
# Stats date format for session keys.
STATS_DATE_FMT = "%Y-%m-%d"

# Logger name used when grabbing logger.
LOGGER_NAME = "tt2_py"
# Logging format string.
LOGGER_FORMAT = "[%(asctime)s] %(levelname)s [{instance}] [%(filename)s:%(lineno)s - %(funcName)s() ] %(message)s"
# Logging file name format string here.
LOGGER_FILE_NAME_STRFMT = "%Y-%m-%d_%H-%M-%S"
INIT_DATE_FMT = datetime.datetime.strftime(datetime.datetime.now(), LOGGER_FILE_NAME_STRFMT)
LOGGER_FILE_NAME = "{log_dir}/{name}.log".format(log_dir=LOG_DIR, name=INIT_DATE_FMT)

# imagesearch.py will make use of these constants to determine which button to press.
LEFT_CLICK = "left"
RIGHT_CLICK = "right"
MIDDLE_CLICK = "middle"

# Threshold used to determine if the value of the next parsed stage is obviously malformed.
# This can be determined by looking at the new value, subtracting it from the old value and seeing
# if it crosses the threshold, in which case we can skip the current parse attempt.
STAGE_PARSE_THRESHOLD = 10000

# Determine how many loops are possible before giving up functionality
# (due to an error in game that causes the ui to lag and the bot to miss an image check).
# Now, ideally, no UI errors should come up if the bots functionality is working as intended.
# Although some issues still sneak by as every use case can not be totally locked down. This is a final fallback.
# Also, this value represents the UPPER limit of a failed case. Since some loops may take numerous attempts
# before succeeding (artifact scrolling in particular). So this can be set to a decently large value.
FUNCTION_LOOP_TIMEOUT = 40
# Used for entering/leaving boss fights in game. Can be made a bit smaller
# than the base FUNCTION_LOOP_TIMEOUT since after about 7-10 tries, if we haven't
# succeeded, the bot is likely stuck due to in game damage being too low currently.
# In which case, we can continue and attempt to up this damage and try again later.
BOSS_LOOP_TIMEOUT = int(FUNCTION_LOOP_TIMEOUT / 2)

# Specify any functions that may be forced.
FORCEABLE_FUNCTIONS = [
    "level_master", "level_heroes", "level_skills", "miscellaneous_actions", "update_stats", "prestige",
    "daily_achievement_check", "milestone_check", "raid_notifications", "activate_skills", "clan_results_parse", "breaks"
]

# Specify functions that can be activated through keyboard shortcuts.
# The key present should represent a function that's present on the Bot.
# The value should be the name of a key (or keys with a + used as a delimiter).
SHORTCUT_FUNCTIONS = {
    # Utility shortcuts.
    "pause": "p",
    "resume": "r",
    "terminate": "e",
    "soft_terminate": "shift+e",
    # Functional shortcuts.
    "actions": "shift+a",
    "breaks": "shift+b",
    "level_heroes": "shift+h",
    "level_master": "shift+m",
    "level_skills": "shift+s",
    "artifacts": "shift+a",
    "daily_rewards": "shift+d",
    "hatch_eggs": "shift+h",
    "fight_boss": "shift+f",
    "leave_boss": "shift+l",
    "update_stats": "shift+u",
    "prestige": "shift+p",
    "daily_achievement_check": "ctrl+d",
    "milestone_check": "ctrl+m",
    "clan_results_parse": "ctrl+p",
    "raid_notifications": "ctrl+r",
    "activate_skills": "ctrl+a",
}

# Reverse the original SHORTCUT_FUNCTIONS dictionary, so we can access functions by their shortcut value.
FUNCTION_SHORTCUTS = {v: k for k, v in SHORTCUT_FUNCTIONS.items()}

# Specify any functions that be queued. These will be grabbed by the TitanDashboard to provide a user
# with the ability to manually add functions that will be executed by the Bot.
QUEUEABLE_FUNCTIONS = FORCEABLE_FUNCTIONS + [
    "calculate_next_master_level", "calculate_next_heroes_level", "calculate_next_skills_level", "calculate_next_skills_activation",
    "calculate_next_stats_update", "calculate_next_daily_achievement_check", "calculate_next_raid_notifications_check",
    "calculate_next_skill_execution",  "calculate_next_prestige", "update_next_artifact_upgrade", "calculate_next_break",
    "parse_current_stage", "artifacts", "parse_artifacts", "check_tournament",
    "daily_rewards", "hatch_eggs", "clan_crate", "collect_ad", "fight_boss", "leave_boss", "tap", "minigames",
    "pause", "resume", "terminate", "soft_terminate"
]

# Also generating a dictionary of tooltips or help texts associated with each queueable function.
QUEUEABLE_TOOLTIPS = {
    "calculate_next_master_level": "Calculate the next time that the master level process will take place.",
    "calculate_next_heroes_level": "Calculate the next time that the heroes level process will take place.",
    "calculate_next_skills_level": "Calculate the next time that the skills level process will take place.",
    "calculate_next_skills_activation": "Calculate the next time that the skills activation process will take place.",
    "calculate_next_stats_update": "Calculate the next time a statistics update will take place.",
    "calculate_next_daily_achievement_check": "Calculate the next time a daily achievement check will take place",
    "calculate_next_raid_notifications_check": "Calculate the next time raid notification check will take place.",
    "calculate_next_skill_execution": "Calculate the next time a skill execution will take place.",
    "calculate_next_prestige": "Calculate the next time a prestige will take place.",
    "calculate_next_break": "Calculate the next time a break will take place.",
    "update_next_artifact_upgrade": "Update the next artifact that will be upgraded.",
    "parse_current_stage": "Parse the current stage in game.",
    "level_heroes": "Level heroes in game.",
    "level_master": "Level sword master in game.",
    "level_skills": "Level skills in game.",
    "miscellaneous_actions": "Initiate miscellaneous_actions in game.",
    "artifacts": "Begin the upgrade discover/enchant/purchase process in game.",
    "parse_artifacts": "Begin a parse of all owned artifacts in game.",
    "check_tournament": "Check for a tournament and join/prestige if one is available.",
    "daily_rewards": "Check for daily rewards in game and collect if available.",
    "hatch_eggs": "Check for eggs in game and hatch them if available.",
    "clan_crate": "Check for a clan crate in game and collect if available.",
    "collect_ad": "Collect an ad in game if one is available.",
    "fight_boss": "Attempt to begin the boss fight in game.",
    "leave_boss": "Attempt to leave the boss fight in game.",
    "tap": "Begin generic tapping process in game.",
    "minigames": "Begin minigame tapping process in game.",
    "pause": "Pause all bot functionality.",
    "resume": "Resume all bot functionality.",
    "terminate": "Terminate all bot functionality.",
    "soft_terminate": "Perform a soft termination of all bot functionality.",
    "actions": "Force all actions to be executed in game.",
    "update_stats": "Force a statistics update in game.",
    "prestige": "Force a prestige in game.",
    "daily_achievement_check": "Force a daily achievement check in game.",
    "milestone_check": "Force a milestone check in game.",
    "clan_results_parse": "Force a clan results parse in game.",
    "raid_notifications": "Force a raid notifications check in game.",
    "activate_skills": "Force a skill activation in game.",
    "breaks": "Force a manual break in game."
}

# Place any properties here that will be present on both the Bot and BotInstance
# simultaneously, this is required to allow the Bot to update the value and at the
# same time, update the current BotInstance and send out socket updates to the dashboard.
PROPERTIES = [
    "current_stage", "current_function", "last_prestige", "next_prestige", "next_randomized_prestige",
    "next_stats_update", "next_daily_achievement_check", "next_milestone_check", "next_break",
    "resume_from_break", "next_raid_notifications_check", "next_raid_attack_reset", "next_clan_results_parse",
    "next_master_level", "next_heroes_level", "next_skills_level", "next_skills_activation", "next_miscellaneous_actions",
    "next_heavenly_strike", "next_deadly_strike", "next_hand_of_midas", "next_fire_sword", "next_war_cry", "next_shadow_clone"
]

# Creating a list of all properties that should be modified when a break takes place so that
# their next execution time take place at the proper time when a break finishes.
BREAK_NEXT_PROPS = [
    prop for prop in PROPERTIES if prop.split("_")[0] == "next" and prop not in ["next_break", "next_raid_attack_reset"]
]

# Create an additional list containing all of the properties we can modify when needed including
# the next break variable. This is useful when functionality occurs that needs all timed variables to change.
BREAK_NEXT_PROPS_ALL = BREAK_NEXT_PROPS + ["next_break", "resume_from_break"]

# Specify the filter strings used to find emulator windows.
NOX_WINDOW_FILTER = [
    "nox", "noxplayer",
]
MEMU_WINDOW_FILTER = [
    "memu"
]
