from settings import BOT_VERSION

from django.utils import timezone
from django.conf import settings

from titandash.models.statistics import Statistics, PrestigeStatistics, ArtifactStatistics, Session, Log
from titandash.models.artifact import Artifact
from titandash.models.prestige import Prestige

from .maps import (
    STATS_COORDS, STAGE_COORDS, GAME_LOCS, PRESTIGE_COORDS,
    ARTIFACT_MAP, CLAN_RAID_COORDS, HERO_COORDS, EQUIPMENT_COORDS,
)
from .utilities import convert, delta_from_values, globals
from .constants import MELEE, SPELL, RANGED

from PIL import Image

import threading
import datetime
import pytesseract
import cv2
import numpy as np
import imagehash
import uuid
import logging


class Stats:
    """Stats class contains all possible stat values and can be updated dynamically."""
    def __init__(self, instance, images, window, grabber, configuration, logger):
        self.instance = instance
        self.images = images
        self.window = window
        self.logger = logger
        self.statistics = Statistics.objects.grab(instance=self.instance)

        # Prestige Statistics retrieved through database model.
        self.prestige_statistics = PrestigeStatistics.objects.grab(instance=instance)
        self.artifact_statistics = ArtifactStatistics.objects.grab(instance=instance)

        # Additionally, create a reference to the log file in question in the database so log files can
        # be retrieved directly from the dashboard and viewed.
        log_name = None
        for handle in self.logger.handlers:
            if type(handle) == logging.FileHandler:
                log_name = handle.baseFilename
                break

        if log_name:
            self.log = Log.objects.create(log_file=log_name)
        else:
            self.log = None

        # Generating a new Session to represent this instance being initialized.
        self.session = Session.objects.create(
            uuid=str(uuid.uuid4()),
            version=BOT_VERSION,
            start=timezone.now(),
            end=None,
            log=self.log,
            configuration=configuration,
            instance=self.instance
        )
        self.statistics.sessions.add(self.session)

        # Grabber is used to perform OCR updates when grabbing game statistics.
        self.grabber = grabber

        # Updating the pytesseract command that is used based on the one
        # present in the django settings... Which should be handled by our bootstrapper.
        pytesseract.pytesseract.tesseract_cmd = settings.TESSERACT_COMMAND

    def increment_ads(self):
        self.statistics.bot_statistics.ads += 1
        self.statistics.bot_statistics.save()

    @property
    def highest_stage(self):
        """
        Retrieve the highest stage reached from game stats, returning None if it is un parsable.
        """
        stat = self.statistics.game_statistics.highest_stage_reached
        value = convert(stat)
        self.logger.info("highest stage parsed: {before} -> {after}".format(before=stat, after=value))

        try:
            return int(value)
        except ValueError:
            return None
        except TypeError:
            return None

    def _process(self, image=None, scale=1, threshold=None, region=None, use_current=True, invert=False):
        """
        Process the grabbers current image before OCR extraction attempt.
        """
        _image = image or self.grabber.snapshot(region=region) if use_current else self.grabber.current
        _image = np.array(_image)

        # Scale and desaturate the image.
        _image = cv2.resize(_image, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
        _image = cv2.cvtColor(_image, cv2.COLOR_BGR2GRAY)

        # Performing thresholds on the image if it's enabled.
        # Threshold will ensure that certain colored pieces are removed.
        if threshold:
            retr, _image = cv2.threshold(_image, 230, 255, cv2.THRESH_BINARY)
            contours, hier = cv2.findContours(_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            # Drawing black over any contours smaller than our specified threshold.
            # Removing the un-wanted blobs from the image grabbed.
            for contour in contours:
                if cv2.contourArea(contour) < threshold:
                    cv2.drawContours(_image, [contour], 0, (0,), -1)

        if invert:
            _image = cv2.bitwise_not(_image)

        # Re-create the image from our numpy array through the Pillow Image module.
        # Threshold or not, an Image object is always returned.
        return Image.fromarray(_image)

    @staticmethod
    def images_duplicate(image_one, image_two, cutoff=2):
        """
        Determine if the specified images are the same or not through the use of the imagehash
        library.

        We can get an average hash of each image and compare them, using a cutoff to determine if
        they are similar enough to end the loop.
        """
        if imagehash.average_hash(image=image_one) - imagehash.average_hash(image=image_two) < cutoff:
            return True
        else:
            return False

    def parse_artifacts(self):
        """
        Parse artifacts in game through OCR, need to make use of mouse dragging here to make sure that all possible
        artifacts have been set to found/not found. This is an expensive function through the image recognition.

        Note that dragging will not be a full drag (all artifacts from last drag, now off of the screen). To make sure
        that missed artifacts have a chance to go again.

        Additionally, this method expects that the game screen is at the top of the expanded artifacts screen.
        """
        from titandash.bot.core.maps import ARTIFACT_COORDS

        from titandash.bot.core.utilities import sleep
        from titandash.bot.core.utilities import drag_mouse

        _threads = []
        _found = []

        def parse_image(_artifacts, _image):
            """
            Threaded Function.

            Initialize a thread with this function and specific image to search for the specified list of artifacts.
            """
            _local_found = []
            for artifact in _artifacts:
                if artifact.artifact.name in _found:
                    continue

                # Get cv2 re-sized version of the artifact image.
                # We use cv2 because the imagesearch library uses that image module.
                artifact_image = cv2.imread(ARTIFACT_MAP.get(artifact.artifact.name))
                if self.grabber.search(image=artifact_image, bool_only=True, im=_image):
                    _local_found.append(artifact.artifact.name)

            if _local_found:
                self.logger.info("{length} artifacts found".format(length=len(_local_found)))
                _found.extend(_local_found)

        # Region used when taking screenshots of the window of artifacts.
        capture_region = ARTIFACT_COORDS["parse_region"]
        locs = GAME_LOCS["GAME_SCREEN"]

        # Take an initial screenshot of the artifacts panel.
        self.grabber.snapshot(region=capture_region)
        # Creating a list that will be used to place image objects
        # into from the grabber.
        images_container = [self.grabber.current]

        # Looping forever until we break from our loop
        # due to us finding a duplicate image.
        loops = 0
        while True:
            loops += 1

            drag_mouse(start=locs["scroll_start"], end=locs["scroll_bottom_end"], window=self.window)
            sleep(1)

            # Take another screenshot of the screen now.
            self.logger.info("taking screenshot {loop} of current artifacts on screen.".format(loop=loops))
            self.grabber.snapshot(region=capture_region)

            if self.images_duplicate(image_one=self.grabber.current, image_two=images_container[-1]):
                # We should now have a list of all images available with the users entire
                # set of owned artifacts. We can use this during parsing.
                self.logger.info("duplicate images found, ending screenshot loop.")
                break
            else:
                images_container.append(self.grabber.current)

            if loops == 30:
                self.logger.warning("30 screenshots have been reached... breaking loop manually now.")
                break

        # Looping through each image, creating a new thread to parse the information
        # about the artifacts present.
        unowned = self.artifact_statistics.artifacts.filter(owned=False)
        for index, image in enumerate(images_container):
            # Firing and forgetting our threads... Functionality can continue while this runs.
            # Since a prestige never takes place right after a artifacts parse (or it shouldn't).
            _threads.append(threading.Thread(name="ParserThread{index}".format(index=index), target=parse_image, kwargs={
                "_artifacts": unowned,
                "_image": image
            }))
            self.logger.info("created new thread ({thread}) for artifact parsing.".format(thread=_threads[-1]))

        for thread in _threads:
            self.logger.info("starting thread {thread}".format(thread=thread))
            thread.start()

        self.logger.info("waiting for threads to finish...")
        for thread in _threads:
            thread.join()

        self.artifact_statistics.artifacts.filter(artifact__name__in=_found).update(owned=True)

    def skill_ocr(self, region):
        """
        Parse out a skills current level when given the region of the levels text on screen.
        """
        image = self._process(scale=5, region=region, use_current=True, invert=True)
        text = pytesseract.image_to_string(image=image, config="--psm 7")

        if "," in text:
            text = text.split(",")[1]
        elif "." in text:
            text = text.split(".")[1]

        text = text.lstrip().rstrip()
        try:
            return int(text)
        except ValueError:
            self.logger.warning("skill was parsed incorrectly, returning level 0.")
            return 0

    def update_stats_ocr(self):
        """
        Update the stats by parsing and extracting the text from the games stats page using the
        tesseract OCR engine to perform text parsing.

        Note that the current screen should be the stats page before calling this method.
        """
        # Create map to determine if keys should be treated as integers
        # only or not, this will decide whether or not to apply thresholds.
        integer_map = {
            "highest_stage_reached",
            "total_pet_level",
            "prestiges",
            "days_since_install",
        }

        for key, region in STATS_COORDS.items():
            is_integer = key in integer_map
            # Begin by looping through each key and region
            # used by our game statistics parsing.
            text = pytesseract.image_to_string(
                image=self._process(scale=5, threshold=150 if is_integer else None, region=region, invert=is_integer),
                config='--psm 7 --oem 0'
            )

            # Ensure our values that are expected to be in an integer
            # format (digits only) have characters parsed out (if present).
            if is_integer:
                text = ''.join(filter(lambda x: x.isdigit(), text))

                # Using a basic default to ensure integer based values
                # will at least use a value of zero if parsing fails.
                if text == "":
                    text = "0"

            self.logger.info("parsing result: {key} -> {text}".format(key=key, text=text))
            setattr(self.statistics.game_statistics, key, text)

        self.statistics.game_statistics.save()

    def stage_ocr(self, test_image=None):
        """
        Attempt to parse out the current stage in game through an OCR check.
        """
        region = STAGE_COORDS["region"]

        if test_image:
            image = self._process(image=test_image, scale=5, threshold=150, invert=True)
        else:
            image = self._process(scale=5, threshold=150, region=region, use_current=True, invert=True)

        text = pytesseract.image_to_string(image, config='--psm 7 --oem 0 nobatch digits')

        # Do some light parse work here to make sure only digit like characters are present
        # in the returned 'text' variable retrieved through tesseract.
        return ''.join(filter(lambda x: x.isdigit(), text))

    def get_advance_start(self, test_image=None):
        """
        Another portion of the functionality that should be used right before a prestige takes place.

        Grab the users advance start value. We can use this to improve the accuracy of our stage parsing
        within the Bot if we know what the users minimum stage value currently is.
        """
        self.logger.info("attempting to parse out the advance start value for current prestige")
        region = PRESTIGE_COORDS["event" if globals.events() else "base"]["advance_start"]

        if test_image:
            image = self._process(image=test_image, scale=5, threshold=150, invert=True)
        else:
            image = self._process(scale=5, threshold=150, region=region, use_current=True, invert=True)

        text = pytesseract.image_to_string(image, config="--psm 7 --oem 0 nobatch digits")
        self.logger.info("parsed value: {text}".format(text=text))

        # Doing some light parse work, similar to the stage ocr function to remove letters if present.
        return ''.join(filter(lambda x: x.isdigit(), text))

    def update_prestige(self, artifact, current_stage=None, test_image=None):
        """
        Right before a prestige takes place, we can generate and parse out some information from the screen
        present right before a prestige happens. This panel displays the time since the last prestige, we can store
        this, along with a timestamp for the prestige.

        A final stat can be modified as this is called to determine some overall statistics
        (# of prestige's, average time for prestige, etc)...

        This method expects the current in game panel to be the one right before a prestige takes place.
        """
        self.logger.info("Attempting to parse out the time since last prestige")
        region = PRESTIGE_COORDS["event" if globals.events() else "base"]["time_since"]

        if test_image:
            image = self._process(image=test_image, use_current=True)
        else:
            image = self._process(region=region, use_current=True)

        text = pytesseract.image_to_string(image, config='--psm 7')
        self.logger.info("parsed value: {text}".format(text=text))

        # We now have the amount of time that this prestige took place, appending it to the list of prestiges
        # present in the statistics instance.
        self.logger.info("attempting to parse hours, minutes and seconds from parsed text.")
        try:
            try:
                hours, minutes, seconds = [int(t) for t in text.split(":")]
            except ValueError:
                hours, minutes, seconds = None, None, None

            delta = None
            if hours or minutes or seconds:
                delta = datetime.timedelta(hours=hours, minutes=minutes, seconds=seconds)

            if artifact:
                try:
                    artifact = Artifact.objects.get(name=artifact)

                # Just in case...
                except Artifact.DoesNotExist:
                    self.logger.warning("artifact: '{artifact}' does not exist... Falling back to no artifact and continuing.")
                    artifact = None

            self.logger.info("generating new prestige instance")
            prestige = Prestige.objects.create(
                timestamp=timezone.now(),
                time=delta,
                stage=current_stage,
                artifact=artifact,
                session=self.session,
                instance=self.instance
            )

            self.logger.info("prestige generated successfully: {prestige}".format(prestige=str(prestige)))
            self.prestige_statistics.prestiges.add(prestige)
            self.prestige_statistics.save()

            # Additionally, we want to attempt to grab the users advanced start value.
            return prestige, self.get_advance_start()

        except Exception as exc:
            self.logger.error("error occurred while creating a prestige instance.")
            self.logger.error(str(exc))

    def get_raid_attacks_reset(self, test_image=None):
        """
        Parse out the current attacks reset value for the current clan raid.

        Assuming that the clan raid panel is currently open.
        """
        self.logger.info("attempting to parse out current clan raid attacks reset...")
        region = CLAN_RAID_COORDS["raid_attack_reset"]

        if test_image:
            image = self._process(image=test_image)
        else:
            image = self._process(scale=3, region=region, use_current=True, invert=True)

        text = pytesseract.image_to_string(image=image, config="--psm 7")
        self.logger.info("text parsed: {text}".format(text=text))

        delta = delta_from_values(values=text.split(" ")[3:])
        self.logger.info("delta generated: {delta}".format(delta=delta))

        if delta:
            return timezone.now() + delta
        else:
            return None

    def get_first_hero_information(self):
        """
        Given a tuple of coordinates that represents an individual "hero" present in the un-collapsed top
        of our heroes panel, we can loop until we find a hero that has been levelled at least one.
        """
        for hero_locations in HERO_COORDS["heroes"]:
            hero = None
            dps = False
            # Checking the first three heroes on our panel for the one with damage information.
            # This represents our first "valid" hero, gathering the damage type only.
            for loc, region in hero_locations.items():
                if loc == "type":
                    if self.grabber.search(image=self.images.melee_type, region=region, bool_only=True):
                        hero = MELEE
                    elif self.grabber.search(image=self.images.spell_type, region=region, bool_only=True):
                        hero = SPELL
                    elif self.grabber.search(image=self.images.ranged_type, region=region, bool_only=True):
                        hero = RANGED

                # Check for zero dps.
                # If the zero dps image is not present, this hero has levels.
                elif loc == "dps":
                    dps = not self.grabber.search(image=self.images.zero_dps, region=region, bool_only=True)

            # Returning the first non zero dps hero once one is found.
            # That damage type can be used if a locked piece of equipment is available.
            if dps and hero:
                return hero
        return None

    def get_first_gear_of(self, typ):
        """
        Attempt to find the first "locked" piece of gear of the specified type on the screen.

        We are expecting that the equipment tab is open at this point and at the top of the screen.
        """
        for index, gear_locations in enumerate(EQUIPMENT_COORDS["gear"], start=1):
            gear = {
                typ: False,
                "equip": None,
                "locked": False,
                "equipped": False,
            }
            for loc, region in gear_locations.items():
                if loc == "base":
                    gear["equipped"] = not self.grabber.search(image=self.images.equip, region=region, bool_only=True)
                elif loc == "locked":
                    gear["locked"] = self.grabber.search(image=self.images.locked, region=region, bool_only=True)
                elif loc == "bonus":
                    # Looking for the bonus "type" within the region for the "bonus" image.
                    # The specified type would be present (bonus=True) if this gear is of the right type.
                    gear[typ] = self.grabber.search(image=getattr(self.images, 'bonus_{typ}'.format(typ=typ)), region=region, bool_only=True)
                # Store location of equip button for each gear parsed.
                elif loc == "equip":
                    gear["equip"] = region  # Really a point here.

            self.logger.debug("information gathered about gear piece {index}...".format(index=index))
            self.logger.debug("type: {typ}: {type}".format(typ=typ, type=gear[typ]))
            self.logger.debug("equip point: {equip}".format(equip=gear["equip"]))
            self.logger.debug("locked: {locked}".format(locked=gear["locked"]))
            self.logger.debug("equipped: {equipped}".format(equipped=gear["equipped"]))

            # Gear is not locked, skip this piece...
            if not gear["locked"]:
                continue
            # Gear is not proper type.
            if not gear[typ]:
                continue
            if gear["equipped"]:
                return True, "EQUIPPED"
            else:
                return True, gear["equip"]

        # No specified gear of the type was found, return
        # invalid tuple of vales.
        return False, None

    def tournament_rank_ocr(self, region, threshold):
        """
        Attempt to parse and retrieve the current rank from the specified region.
        """
        return pytesseract.image_to_string(
            image=self._process(scale=4, threshold=threshold, region=region),
            config="--psm 7 --oem 0 nobatch digits"
        ).strip()

    def tournament_user_ocr(self, region):
        """
        Attempt to parse and retrieve the current username from the specified region.
        """
        return pytesseract.image_to_string(
            image=self._process(scale=3, region=region),
            config="--psm 7 --oem 0"
        ).strip()

    def tournament_stage_ocr(self, region):
        """
        Attempt to parse and retrieve the current stage from the specified region.
        """
        return pytesseract.image_to_string(
            image=self._process(scale=5, threshold=150, region=region, invert=True),
            config="--psm 7 --oem 0 nobatch digits"
        ).strip()
