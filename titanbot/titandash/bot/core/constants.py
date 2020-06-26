from settings import LOG_DIR

import datetime

# Raid notifications string used to template out the message sent to a user.
RAID_NOTIFICATION_MESSAGE = "Raid attacks are available! You may now attack the active titan!"

MELEE = "melee"
SPELL = "spell"
RANGED = "ranged"

# The lookup multiplier is used to convert in game values that are formatted with specific multipliers
# (K, M, T) into their respective float values, or the closest we can get to the actual value. These
# values can then be parsed and diffed.
STATS_LOOKUP_MULTIPLIER = {
    'K': 10**3,
    'M': 10**6,
}

# Format string used when converting time delta objects back into their respective format found in game.
STATS_TIMEDELTA_STR = "{D}d {H}:{M}:{S}"

# Logger name used when grabbing logger.
LOGGER_NAME = "tt2_py"
# Logging format string.
LOGGER_FORMAT = "[%(asctime)s] %(levelname)s [{instance}] [%(filename)s:%(lineno)s - %(funcName)s() ] %(message)s"
# Logging file name format string here.
LOGGER_FILE_NAME_STRFMT = "%Y-%m-%d_%H-%M-%S"
# Actual logger file name used when saving to filesystem.
LOGGER_FILE_NAME = "{log_dir}/{name}.log".format(
    log_dir=LOG_DIR,
    name=datetime.datetime.now().strftime(LOGGER_FILE_NAME_STRFMT)
)

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
BOSS_LOOP_TIMEOUT = int(FUNCTION_LOOP_TIMEOUT / 4)

NOX_WINDOW_FILTER = [
    "nox",
    "bignox",
    "noxplayer",
]
MEMU_WINDOW_FILTER = [
    "memu"
]

WINDOW_FILTER = NOX_WINDOW_FILTER + MEMU_WINDOW_FILTER
