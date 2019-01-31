"""
settings.py

Store all project specific settings here.
"""
import os

__VERSION__ = "0.0.1"

# Store the root directory of the project. May be used and appended to files in other directories without
# the need for relative urls being generated to travel to the file.
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
# Core bot file directory.
CORE_DIR = os.path.join(ROOT_DIR, "core")
# External library file directory.
EXT_DIR = os.path.join(ROOT_DIR, "external")
# Log files should be placed here.
LOG_DIR = os.path.join(ROOT_DIR, "logs")
# Any data files used directly by the bot should be placed in here.
DATA_DIR = os.path.join(ROOT_DIR, "data")
# Testing directory.
TEST_DIR = os.path.join(ROOT_DIR, "tests")
TEST_DATA_DIR = os.path.join(TEST_DIR, "data")
TEST_IMAGE_DIR = os.path.join(TEST_DIR, "images")

# Additional data directories.
IMAGE_DIR = os.path.join(DATA_DIR, "images")

# Some hardcoded, expected files here.
CONFIG_FILE = os.path.join(DATA_DIR, "config.ini")
STATS_FILE = os.path.join(DATA_DIR, "stats.json")

# Test files.
TEST_CONFIG_FILE = os.path.join(TEST_DATA_DIR, "test_config.ini")
TEST_STATS_FILE = os.path.join(TEST_DATA_DIR, "test_stats.json")

# Make sure a "logs" directory actually exists.
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

