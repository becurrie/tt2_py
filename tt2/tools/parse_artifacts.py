"""
parse_artifacts.py

Make use of this file to manually start a check to determine what artifacts are currently owned and the levels of
each one. Can be useful for keeping track of progress in the game. This also takes care of modifying the logging
used by the bot to place logs during the parsing into a different log file for tracking artifact parsing logs.
"""
from settings import TOOL_LOG_DIR, CONFIG_FILE
from tt2.core.bot import Bot
from tt2.core.utilities import make_logger

import datetime

LOGGER_FILE_NAME_STRFMT = "%Y-%m-%d_%H-%M-%S"
INIT_DATE_FMT = datetime.datetime.strftime(datetime.datetime.now(), LOGGER_FILE_NAME_STRFMT)
LOGGER_FILE_NAME = "{log_dir}/{file}-{name}.log".format(
    file="parse_artifacts", log_dir=TOOL_LOG_DIR, name=INIT_DATE_FMT
)
logger = make_logger(log_file=LOGGER_FILE_NAME)


def parse_artifacts():
    """Begin artifact parsing here through the use of a Bot object."""
    logger.info("beginning artifact parsing process")
    logger.info("generating a bot instance to perform screen grabs and comparisons.")

    bot = Bot(CONFIG_FILE, logger=logger)

    # Having access to the bot now, we can begin looking through artifacts and determining
    # which ones are present, and their levels.
    bot.goto_artifacts(collapsed=False)
    bot.stats.parse_artifacts()

    bot.stats.write()
    logger.info("artifacts have been parsed successfully, check your stats file for output")
