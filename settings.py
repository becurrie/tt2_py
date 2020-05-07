import os
import pathlib
import json
import shutil
import datetime
import socket


# Version file used to determine the current project version.
VERSION_FILE = "version.json"

# Store the root directory of the project. May be used and appended to files in other directories without
# the need for relative urls being generated to travel to the file.
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(ROOT_DIR, VERSION_FILE), "r") as version_file:
    BOT_VERSION = json.load(version_file)["version"]


def _get_port():
    """
    Automatically derive a port that will be used to start the web server.
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(("localhost", 0))

    return sock.getsockname()[1]


# Dynamically allocate a port that will be used with the web server.
# This will make starting/stopping the server much easier to deal with.
TITANDASH_PORT = _get_port()

# Specify the url used by the application to derive accessible status.
TITANDASH_DASHBOARD_URL = "http://localhost:%d/" % TITANDASH_PORT
TITANDASH_LOADER_URL = "http://localhost:%d/bootstrap" % TITANDASH_PORT

# Grab the windows local users directory (ie: C:/Users/<username>).
USER_DIR = str(pathlib.Path.home())
# Django project directory (titanbot).
PROJECT_DIR = os.path.join(ROOT_DIR, "titanbot")
# TitanDash project directory (titandash).
TITANDASH_DIR = os.path.join(PROJECT_DIR, "titandash")
# Bot directory (tt2).
BOT_DIR = os.path.join(TITANDASH_DIR, "bot")
# Core bot file directory.
CORE_DIR = os.path.join(BOT_DIR, "core")
# External library file directory.
EXT_DIR = os.path.join(BOT_DIR, "external")
# Log files should be placed here.
LOG_DIR = os.path.join(BOT_DIR, "logs")
# Any data files used directly by the bot should be placed in here.
DATA_DIR = os.path.join(BOT_DIR, "data")
# Additional data directories.
IMAGE_DIR = os.path.join(DATA_DIR, "images")

# Scripts.
PROGRAM_BAT = os.path.join(ROOT_DIR, "titandash.bat")
PROGRAM_SETUP_BAT = os.path.join(ROOT_DIR, "setup.bat")

# Additional data directories used to store local data
# on the users machine.
LOCAL_DATA_DIR = os.path.join(USER_DIR, ".titandash")
# Directory to store our database in.
LOCAL_DATA_DB_DIR = os.path.join(LOCAL_DATA_DIR, "db")
# Directory to store our database backups in.
LOCAL_DATA_DB_BACKUP_DIR = os.path.join(LOCAL_DATA_DB_DIR, "backup")
# Directory to store newly downloaded version in.
LOCAL_DATA_UPDATE_DIR = os.path.join(LOCAL_DATA_DIR, "update")
# Directory to store the latest backup in.
LOCAL_DATA_BACKUP_DIR = os.path.join(LOCAL_DATA_DIR, "backup")
# Directory to store our titandash logs in.
LOCAL_DATA_LOG_DIR = os.path.join(LOCAL_DATA_DIR, "logs")
# File name to store titandash logs in.
LOCAL_DATA_LOG_FILE = os.path.join(LOCAL_DATA_LOG_DIR, "titandash.log")
# Directory to store our titandash debug reports in.
LOCAL_DATA_DEBUG_DIR = os.path.join(LOCAL_DATA_DIR, "debug")
# File to store titandash debug json data in.
LOCAL_DATA_DEBUG_FILE = os.path.join(LOCAL_DATA_DEBUG_DIR, "debug.json")
# Directory to place our extracted tesseract data in.
LOCAL_DATA_DEPENDENCIES_DIR = os.path.join(LOCAL_DATA_DIR, "dependencies")
# Directory to place any screenshots in.
LOCAL_DATA_SCREENSHOTS_DIR = os.path.join(LOCAL_DATA_DIR, "screenshots")
# Directory that should be created dynamically when tesseract is extracted.
LOCAL_DATA_TESSERACT_DEPENDENCY_DIR = os.path.join(LOCAL_DATA_DEPENDENCIES_DIR, "tesseract")
# Directory that should be created dynamically when redis is extracted.
LOCAL_DATA_REDIS_DEPENDENCY_DIR = os.path.join(LOCAL_DATA_DEPENDENCIES_DIR, "redis")
# Command that is used by bot's to perform character recognition.
TESSERACT_COMMAND = os.path.join(LOCAL_DATA_TESSERACT_DEPENDENCY_DIR, "tesseract")
REDIS_COMMAND = os.path.join(LOCAL_DATA_REDIS_DEPENDENCY_DIR, "redis-server.exe")

# Testing directory.
TEST_DIR = os.path.join(TITANDASH_DIR, "tests")
TEST_BOT_DIR = os.path.join(TEST_DIR, "bot")
TEST_IMAGE_DIR = os.path.join(TEST_BOT_DIR, "images")

# Themes CSS directory.
THEMES_DIR = os.path.join(TITANDASH_DIR, "static/css/theme")

# Make sure a "logs" directory actually exists.
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

TITAN_DB_NAME = "titan.sqlite3"
TITAN_DB_PATH = os.path.join(LOCAL_DATA_DB_DIR, TITAN_DB_NAME)


def git_info():
    """
    Attempt to grab the git information so we can use a proper git commit.

    If git is not present or no repository is being used, we can fallback onto
    not using a git commit anywhere instead.
    """
    try:
        import git
        try:
            return git.Repo(ROOT_DIR).head.commit.hexsha
        except git.InvalidGitRepositoryError:
            return None
    except ImportError:
        return None


GIT_COMMIT = git_info()


def user_directory():
    """
    Perform some idempotent functionality to generate our user directory that contains
    some local data used by titandash. The goal here is to create a location to place files
    that remain even throughout updates to the program.
    """
    for path in [
        LOCAL_DATA_DIR, LOCAL_DATA_DB_DIR, LOCAL_DATA_DB_BACKUP_DIR, LOCAL_DATA_UPDATE_DIR,
        LOCAL_DATA_BACKUP_DIR, LOCAL_DATA_LOG_DIR, LOCAL_DATA_DEBUG_DIR, LOCAL_DATA_DEPENDENCIES_DIR,
        LOCAL_DATA_SCREENSHOTS_DIR
    ]:
        # Create the specified local data directory if it does not currently exist.
        if not os.path.exists(path):
            os.makedirs(path)

    # Our database directory definitely exists... Create a base database in the db location,
    # we will move it through the function below... But if one doesn't exist yet at all,
    # ensure an empty one does for use by other functionality.
    if not os.path.exists(TITAN_DB_PATH):
        open(TITAN_DB_PATH, "w")

    # Our local data directory is guaranteed to exist now, check for the existence of our actual
    # database within the codebase, and move it if one exists.
    existing = [p for p in pathlib.Path(ROOT_DIR).glob("**/{titan_db}".format(titan_db=TITAN_DB_NAME))]

    # Renaming and moving the database present into the local database directory.
    # If a database is already present, we can ignore this part so no overwrite of
    # the users database takes place.
    if existing:
        # We need to make sure we delete the empty database if we plan on moving
        # one over... Ensuring a FileExistsError doesn't effect anything.
        os.unlink(TITAN_DB_PATH)
        existing[0].rename(TITAN_DB_PATH)


user_directory()


def database_backup(limit=10):
    """
    Perform functionality used to create database backups, we do this lazily.

    We only attempt the backup when this file is imported. The database backup names will include
    a timestamp in their name so users can differentiate between the backups.
    """
    def create_backup():
        """
        Create a new database backup file with the current date appended to the end of the backup file.
        """
        shutil.copyfile(
            src=TITAN_DB_PATH,
            dst=os.path.join(
                LOCAL_DATA_DB_BACKUP_DIR,
                "titan_{date}.sqlite3".format(
                    date=datetime.datetime.now().date().strftime("%m-%d-%Y")
                )
            )
        )

    def backup_date(backup):
        """
        Given a backup, parse out the date string from the filename.
        """
        elems = [int(s) for s in backup.split("_")[1].split(".")[0].split("-")]

        # Coerce into date object and return.
        return datetime.date(month=elems[0], day=elems[1], year=elems[2])

    backups = [f for f in os.listdir(LOCAL_DATA_DB_BACKUP_DIR) if os.path.isfile(os.path.join(LOCAL_DATA_DB_BACKUP_DIR, f))]

    # No backups are present at all yet, let's go ahead and make one with the current database.
    if len(backups) == 0:
        create_backup()
    # Some backups are available, but we haven't yet hit our limit so none need to be deleted.
    # Check if one needs to be created if the day is not the same as the last backups date.
    elif len(backups) < limit:
        # If the current date is greater than the last available backup,
        # generate a new backup file.
        if datetime.datetime.now().date() > backup_date(backups[-1]):
            create_backup()

            # Now that a backups was created, check if the length would be equal to our limit,
            # if it is, remove the first backup.
            if len(backups) + 1 >= limit:
                os.remove(os.path.join(LOCAL_DATA_DB_BACKUP_DIR, backups[0]))


database_backup()

# In game specific settings should be stored here. As the game is updated, these will change
# and reflect the new constants that may be used by the bot.
# Note: This reflect what the project is currently setup to support. Newer versions may be
# released and be fine, but this is a good way to derive whether or not features may be missing.
STAGE_CAP = 96000
