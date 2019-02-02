"""
stats.py

The stats module will encapsulate all functionality related to the stats
panel located inside of the heroes panel in game.
"""
from settings import __VERSION__
from tt2.core.maps import STATS_COORDS, ARTIFACT_TIER_MAP
from tt2.core.constants import (
    STATS_JSON_TEMPLATE, STATS_GAME_STAT_KEYS, STATS_BOT_STAT_KEYS, LOGGER_FILE_NAME,
    STATS_DATE_FMT, STATS_UN_PARSABLE
)
from tt2.core.utilities import convert, diff

from PIL import Image

import datetime
import pytesseract
import cv2
import numpy as np
import uuid
import json

pytesseract.pytesseract.tesseract_cmd = "C:\\Program Files (x86)\\Tesseract-OCR\\tesseract.exe"

_KEY_MAP = {
    "game_statistics": STATS_GAME_STAT_KEYS,
    "bot_statistics": STATS_BOT_STAT_KEYS,
}


class Stats:
    """Stats class contains all possible stat values and can be updated dynamically."""
    def __init__(self, grabber, config, stats_file, logger):
        self.logger = logger
        self._base()

        # Game statistics.
        for key in STATS_GAME_STAT_KEYS:
            setattr(self, key, 0)

        # Bot statistics.
        for key in STATS_BOT_STAT_KEYS:
            setattr(self, key, 0)

        # Artifacts objects initializing as empty.
        self.artifact_statistics = {
            "discovered": "0/90",
            "artifacts": {}
        }
        for k, v in ARTIFACT_TIER_MAP.items():
            self.artifact_statistics["artifacts"][k] = {}
            for k1 in v:
                self.artifact_statistics["artifacts"][k][k1] = False

        # Session statistics.
        self.started = datetime.datetime.now()
        self.day = datetime.datetime.strftime(self.started, STATS_DATE_FMT)
        self.last_update = self.started
        self.config = config

        # Grabber is used to perform OCR updates when grabbing game statistics.
        self.grabber = grabber

        # Generate a key that matches the currently specified height and width that's configured.
        # Key is used by the update method to grab proper regions when taking screenshots.
        self.key = "{0}x{1}".format(self.grabber.width, self.grabber.height)

        # File name specified by configurations.
        self.file = stats_file
        self.content = self.retrieve()

        # Additionally, including a session id here that may be appended to the stats file
        # if the id isn't already present, this allows the configuration options being used
        # to be stored alongside any extra information about the bots runtime.
        self.session = str(uuid.uuid4())
        self.session_data = None

        # Log file associated with current stats session.
        self.log_file = LOGGER_FILE_NAME
        # Version of Bot running this current session.
        self.version = __VERSION__

        # Update instance to reflect any available values in the content attr.
        self.update_from_content()

    def _base(self):
        """Manually set every expected value, allows for easier access later on."""
        self.premium_ads = None
        self.clan_ship_battles = None
        self.actions = None
        self.updates = None

    def _process(self):
        """Process the grabbers current image before OCR extraction attempt."""
        image = self.grabber.current
        image = np.array(image)

        # Resize and desaturate.
        image = cv2.resize(image, None, fx=3, fy=3, interpolation=cv2.INTER_CUBIC)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        # Apply dilation and erosion.
        kernel = np.ones((1, 1), np.uint8)
        image = cv2.dilate(image, kernel, iterations=1)
        image = cv2.erode(image, kernel, iterations=1)

        return Image.fromarray(image)

    def stat_diff(self, ctx):
        """
        Determine the difference between the game stats instance attribute values, and the original
        values that were captures when the instance was initialized.

        ctx Should equal a value present in the global _X_STAT_KEYS that are used to determine what values are diffed.
        """
        keys = _KEY_MAP[ctx]
        new_attrs = {key: getattr(self, key, 0) for key in keys}
        old_attrs = {key: self.content.get(ctx).get(key, 0) for key in keys}

        new_attrs_converted = {}
        old_attrs_converted = {}
        # Is the value formatted with a conversion key? (i.e: K, M).
        for key, value in new_attrs.items():
            new_attrs_converted[key] = convert(value)

        for key, value in old_attrs.items():
            old_attrs_converted[key] = convert(value)

        # Session stats should also contain relevant information about the difference between initial
        # values, and the current values of the game.
        return {
            key:
                {
                    "old": old_attrs.get(key),
                    "new": new_attrs.get(key),
                    "diff": diff(old_attrs_converted.get(key, 0), new_attrs_converted.get(key, 0))
                }
            for key in keys
        }

    def as_json(self, update_artifacts=False):
        """Convert the stats instance into a JSON compliant dictionary."""
        sessions = self.content.get("sessions")
        if sessions.get(self.day):
            sessions[self.day][self.session] = {
                "version": self.version,
                "start_date": str(self.started),
                "last_update": str(self.last_update),
                "log_file": self.log_file,
                "game_stat_differences": self.stat_diff("game_statistics"),
                "bot_stat_differences": self.stat_diff("bot_statistics"),
                "config": vars(self.config)
            }
        else:
            sessions[self.day] = {
                self.session: {
                    "version": self.version,
                    "start_date": str(self.started),
                    "last_update": str(self.last_update),
                    "log_file": self.log_file,
                    "game_stat_differences": self.stat_diff("game_statistics"),
                    "bot_stat_differences": self.stat_diff("bot_statistics"),
                    "config": vars(self.config)
                }
            }

        # If artifact update has been specified, update the artifacts on the stats instance.
        # Any previous artifact data will be present and may speed up processing as more are
        # unlocked.
        if update_artifacts:
            self.parse_artifacts()

        # Create final dictionary of all of game statistics.
        stats = {
            "game_statistics": {key: getattr(self, key, "None") for key in STATS_GAME_STAT_KEYS},
            "bot_statistics": {key: getattr(self, key, "None") for key in STATS_BOT_STAT_KEYS},
            "artifacts": self.artifact_statistics,
            "sessions": sessions
        }
        return stats

    def parse_artifacts(self):
        """
        Parse artifacts in game through OCR, need to make use of mouse dragging here to make sure that all possible
        artifacts have been set to found/not found. This is an expensive function through the image recognition.

        Note that dragging will not be a full drag (all artifacts from last drag, now off of the screen). To make sure
        that missed artifacts have a chance to go again.

        Additionally, this method expects that the game screen is at the top of the expanded artifacts screen.
        """
        from tt2.core.maps import ARTIFACT_TIER_MAP, GAME_LOCS, IMAGES
        from tt2.core.utilities import sleep
        from tt2.core.utilities import drag_mouse

        # Game locations based on current size of game.
        locs = GAME_LOCS[self.key]["GAME_SCREEN"]
        images = IMAGES["GENERIC"]

        discovered = 0
        # Loop twenty times, a mouse drag happens during each loop.
        for i in range(20):
            for tier, d in ARTIFACT_TIER_MAP.items():
                for artifact, path in d.items():
                    # Break early if the artifact has already been discovered.
                    if self.artifact_statistics["artifacts"][tier][artifact]:
                        continue

                    try:
                        # Do a quick check to ensure that the artifacts screen is still open (no transition state).
                        while not self.grabber.search(images["artifacts_active"], bool_only=True):
                            continue

                        if self.grabber.search(path, bool_only=True):
                            self.logger.info("artifact: {artifact} was successfully found, marking as owned".format(
                                artifact=artifact)
                            )
                            self.artifact_statistics["artifacts"][tier][artifact] = True
                            discovered += 1

                    except ValueError:
                        self.logger.error("artifact: {artifact} could not be searched for, leaving false".format(
                            artifact=artifact)
                        )

            # Scroll down slightly and check for artifacts again.
            drag_mouse(locs["scroll_start"], locs["scroll_bottom_end"], quick_stop=locs["scroll_quick_stop"])
            sleep(1)

            # Update the total discovered amount of artifacts.
            self.artifact_statistics["discovered"] = "{discovered}/90".format(discovered=discovered)

    def update_from_content(self):
        """Update self based on the JSON content taken from stats file."""
        game_stats = self.content.get("game_statistics")
        if game_stats:
            for key, value in game_stats.items():
                setattr(self, key, value)

        bot_stats = self.content.get("bot_statistics")
        if bot_stats:
            for key, value in bot_stats.items():
                setattr(self, key, value)

        artifact_stats = self.content.get("artifact_statistics")
        if artifact_stats:
            for tier, d in artifact_stats["artifacts"].items():
                for artifact, value in artifact_stats[tier].items():
                    self.artifact_statistics["artifacts"][tier][artifact] = value

        sessions = self.content.get("sessions")
        if sessions:
            if self.session in sessions:
                self.session_data = sessions[self.session]

    def update_ocr(self, test_set=None):
        """
        Update the stats by parsing and extracting the text from the games stats page using the
        tesseract OCR engine to perform text parsing.

        Note that the current screen should be the stats page before calling this method.
        """
        for key, region in STATS_COORDS[self.key].items():
            if test_set:
                image = Image.open(test_set[key])
            else:
                self.grabber.snapshot(region=region)
                image = self._process()

            text = pytesseract.image_to_string(image, config='--psm 7')
            self.logger.info("{key}: OCR result: {text}".format(key=key, text=text))

            # The images do not always parse correctly, so we can attempt to parse out our expected
            # value from the STATS_COORD tuple being used.

            # Firstly, confirm that a number is present in the text result, if no numbers are present
            # at all, safe to assume the OCR has failed wonderfully.
            if not any(char.isdigit() for char in text):
                self.logger.warning("no digits found in OCR result, skipping key: {key}".format(key=key))
                setattr(self, key, STATS_UN_PARSABLE)
                continue

            # Otherwise, attempt to parse out the proper value.
            try:
                if len(text.split(':')) == 2:
                    value = text.split(':')[-1].replace(" ", "")
                else:
                    if key == "play_time":
                        value = " ".join(text.split(" ")[-2:])
                    else:
                        value = text.split(" ")[-1].replace(" ", "")

                # Finally, a small check to see that a value can successfully made into an
                # integer, float with either its last character taken off (K, M, %, etc).
                # This check is not required for the "play_time" key.
                if not key == "play_time":
                    if not value[-1].isdigit():
                        try:
                            int(value[:-1])
                        except ValueError:
                            try:
                                float(value[:-1])
                            except ValueError:
                                setattr(self, key, STATS_UN_PARSABLE)
                                continue

                    # Last character is a digit, value may be pure digit of some sort?
                    else:
                        try:
                            int(value)
                        except ValueError:
                            try:
                                float(value)
                            except ValueError:
                                setattr(self, key, STATS_UN_PARSABLE)
                                continue

                self.logger.info("{key}: parsed value: {value}".format(key=key, value=value))
                setattr(self, key, value)

            # Gracefully continuing loop if failure occurs.
            except ValueError:
                self.logger.error("{key} was unable to be parsed (OCR: {text})".format(key=key, text=text))
                return "Not parsable"

    def retrieve(self):
        """Attempt to retrieve the stats JSON file with all current data."""
        try:
            # Open the stats file, parse data and set self attrs.
            with open(self.file) as file:
                return json.load(file)

        # If the file doesn't exist at all, build one.
        except EnvironmentError:
            self.build()

        # If the file is new, the json contents will not exist and throw a decode
        # error, new file template will be placed into the file and no retrieval.
        except json.JSONDecodeError:
            self.build()

        return self.retrieve()

    def build(self):
        """Build an empty JSON stats file, only used if one doesn't exist yet."""
        with open(self.file, "w+") as file:
            json.dump(STATS_JSON_TEMPLATE, file, indent=4)

    def write(self, update_artifacts=False):
        """Write the stats object to a JSON file, overwriting all old values in the process."""
        self.last_update = datetime.datetime.now()
        self.logger.info("writing statistics to json file")
        contents = self.as_json(update_artifacts=update_artifacts)
        with open(self.file, "w+") as file:
            json.dump(contents, file, indent=4)

        self.logger.info("stats were successfully written to {file}".format(file=self.file))
