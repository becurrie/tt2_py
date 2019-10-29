"""
core.py

Main bot initialization and script startup should take place here. All actions and main bot loops
will be maintained from this location.
"""
from settings import STAGE_CAP, GAME_VERSION, BOT_VERSION, GIT_COMMIT

from django.utils import timezone

from titandash.models.queue import Queue
from titandash.models.clan import Clan, RaidResult
from titandash.constants import SKILL_MAX_LEVEL

from titanauth.authentication.wrapper import AuthWrapper

from .maps import *
from .props import Props
from .grabber import Grabber
from .stats import Stats
from .wrap import Images, Locs, Colors
from .decorators import not_in_transition, wait_afterwards, wrap_current_function
from .shortcuts import ShortcutListener
from .utilities import (
    click_on_point, click_on_image, drag_mouse, make_logger, strfdelta,
    strfnumber, sleep, send_raid_notification
)
from .constants import (
    STAGE_PARSE_THRESHOLD, FUNCTION_LOOP_TIMEOUT, BOSS_LOOP_TIMEOUT,
    QUEUEABLE_FUNCTIONS, FORCEABLE_FUNCTIONS, PROPERTIES, BREAK_NEXT_PROPS,
    BREAK_NEXT_PROPS_ALL
)

from pyautogui import FailSafeException

import datetime
import random
import keyboard
import win32clipboard


class TerminationEncountered(Exception):
    pass


class Bot(object):
    """
    Main Bot Class.

    Initial setup is handled here, as well as some data setup for use during runtime.

    Statistics, Configurations and Logging is all setup here.
    """
    def __init__(self, configuration, window, instance, logger=None, start=False, debug=False):
        """
        Initialize a new Bot. Setting up base variables as well as performing some bootstrapping
        to ensure authentication is handled before moving on.
        """
        self.TERMINATE = False
        self.PAUSE = False
        self.ERRORS = 0
        self.ADVANCED_START = None
        self.configuration = configuration
        self.window = window
        self.instance = instance
        self.instance.configuration = configuration
        self.instance.window = window.json()
        self.instance.errors = self.ERRORS

        # Initialize and setup our Props object which is used to handle BotInstance
        # realtime updates using our Django Channels sockets.
        self.props = Props(instance=self.instance, props=PROPERTIES)
        self.last_stage = None

        self.logger = logger if logger else make_logger(instance, self.configuration.logging_level, log_file=None)
        if not self.configuration.enable_logging:
            self.logger.disabled = True

        # Bot utilities.
        self.grabber = Grabber(window=self.window, logger=self.logger)
        self.stats = Stats(instance=self.instance, window=self.window, grabber=self.grabber, configuration=self.configuration, logger=self.logger)
        # Statistics handles Log instance creation... Set BotInstance now.
        self.instance.log = self.stats.session.log
        # Data containers.
        self.images = Images(IMAGES, self.logger)
        self.locs = Locs(GAME_LOCS, self.logger)
        self.colors = Colors(GAME_COLORS, self.logger)

        self.instance.start(session=self.stats.session)
        self.instance_string = "bot (v{version}) (v{game_version}){git} has been initialized".format(
            version=BOT_VERSION,
            game_version=GAME_VERSION,
            git=" [{commit}]".format(commit=GIT_COMMIT[:10]) if GIT_COMMIT else " "
        )

        self.logger.info("==========================================================================================")
        self.logger.info(self.instance_string)
        self.logger.info("s: {session}".format(session=self.stats.session))
        self.logger.info("w: {window}".format(window=self.window))
        self.logger.info("c: {configuration}".format(configuration=self.configuration))
        self.logger.info("==========================================================================================")

        # Set authentication reference to an online state.
        if not debug:
            AuthWrapper().online()

        # Create a list of the functions called in there proper order
        # when actions are performed by the bot.
        self.minigame_order = self.order_minigames()

        # Store information about the artifacts in game.
        self.owned_artifacts = None
        self.next_artifact_index = None
        self.next_artifact_upgrade = None

        # Current prestige information, this should be reset on each prestige so that certain actions
        # can be performed a number of times, and be disabled when needed.
        self.current_prestige_master_levelled = False

        # Current prestige skill level values. We keep track of these to ensure that we can
        # very easily enable/disable skill levelling based on the configuration caps and current levels in game.
        self.current_prestige_skill_levels = {skill: 0 for skill in SKILLS}

        # Setup the datetime objects used initially to determine when the bot
        # will perform specific actions in game.
        self.calculate_next_prestige()
        self.calculate_next_stats_update()
        self.calculate_next_master_level()
        self.calculate_next_heroes_level()
        self.calculate_next_skills_level()
        self.calculate_next_miscellaneous_actions()
        self.calculate_next_skills_activation()
        self.calculate_next_daily_achievement_check()
        self.calculate_next_milestone_check()
        self.calculate_next_raid_notifications_check()
        self.calculate_next_clan_result_parse()
        self.calculate_next_break()

        if start:
            self.run()

    def click(self, point, clicks=1, interval=0.0, button="left", pause=0.0, offset=5, disable_padding=False):
        """
        Local click method for use with the bot, ensuring we pass the window being used into the click function.
        """
        click_on_point(point=point, window=self.window, clicks=clicks, interval=interval, button=button, pause=pause, offset=offset, disable_padding=disable_padding)

    def click_image(self, image, pos, button="left", pause=0.0):
        """
        Local image click method for use with the bot, ensuring we pass the window being used into the image click function.
        """
        click_on_image(window=self.window, image=image, pos=pos, button=button, pause=pause)

    def drag(self, start, end, button="left", pause=0.5):
        """
        Local drag method for use with the bot, ensuring we pass the window being used into the drag function.
        """
        drag_mouse(start=start, end=end, window=self.window, button=button, pause=pause)

    @wrap_current_function
    def get_upgrade_artifacts(self, testing=False):
        """
        Retrieve a list of all discovered/owned artifacts in game that will be iterated over
        and upgraded throughout runtime.

        The testing boolean is used to ignore the owned filter so all artifacts will be grabbed
        and can be tested thoroughly.
        """
        lst = []

        if not self.configuration.enable_artifact_purchase:
            self.logger.info("artifact purchase is disabled, artifact parsing is not required and will be skipped.")
            return lst

        # Grabbing all configuration values used to determine which artifacts are
        # upgraded when called.
        upgrade_tiers = self.configuration.upgrade_owned_tier.all()
        ignore_artifacts = self.configuration.ignore_artifacts.all()
        upgrade_artifacts = self.configuration.upgrade_artifacts.all()
        if len(upgrade_tiers) > 0:
                upgrade_tiers = upgrade_tiers.values_list("tier", flat=True)
        if len(ignore_artifacts) > 0:
                ignore_artifacts = ignore_artifacts.values_list("name", flat=True)
        if len(upgrade_artifacts) > 0:
                upgrade_artifacts = upgrade_artifacts.values_list("name", flat=True)

        if testing:
            artifacts = self.stats.artifact_statistics.artifacts.all()
        else:
            artifacts = self.stats.artifact_statistics.artifacts.filter(owned=True)

        for artifact in artifacts.exclude(artifact__name__in=ARTIFACT_WITH_MAX_LEVEL):
            if artifact.artifact.name in ignore_artifacts:
                continue
            if artifact.artifact.tier.tier in upgrade_tiers or artifact.artifact.name in upgrade_artifacts:
                lst.append(artifact.artifact.name)
                self.logger.debug("{artifact} will be upgraded".format(artifact=artifact))
                continue

        if len(lst) == 0:
            self.logger.error("no owned artifacts were found... parsed artifacts must be present before starting a session.")
            self.logger.info("attempting to force artifacts parse now...")
            self.parse_artifacts()
            lst = self.get_upgrade_artifacts()

            if len(lst) == 0:
                self.logger.error("no artifacts were parsed... disabling artifact purchase for this session.")
                self.configuration.enable_artifact_purchase = False

        if self.configuration.shuffle_artifacts:
            random.shuffle(lst)

        return lst

    @wrap_current_function
    def update_next_artifact_upgrade(self):
        """
        Update the next artifact to be upgraded to the next one in the list.
        """
        if self.next_artifact_index == len(self.owned_artifacts):
            self.next_artifact_index = 0

        self.next_artifact_upgrade = self.owned_artifacts[self.next_artifact_index]
        self.next_artifact_index += 1

        self.instance.next_artifact_upgrade = self.next_artifact_upgrade
        self.instance.save()

        self.logger.info("next artifact upgrade: {artifact}".format(artifact=self.next_artifact_upgrade))

    @wrap_current_function
    def parse_advanced_start(self, stage_text):
        """
        Attempt to parse out the advanced start stage value into a valid integer.
        """
        try:
            stage = int(stage_text)
            self.logger.info("advanced start stage: {stage_text} was successfully coerced into an integer: {stage}".format(
                stage_text=stage_text, stage=strfnumber(stage)))

            if stage > STAGE_CAP:
                self.logger.info("stage: {stage} is greater then {stage_cap}, resetting advanced start now.".format(
                    stage=strfnumber(stage), stage_cap=STAGE_CAP))
                self.ADVANCED_START = None
                return

            self.logger.info("current advanced start in game was successfully parsed: {stage}".format(stage=strfnumber(stage)))
            self.ADVANCED_START = stage

        except ValueError:
            self.logger.warning("ocr check could not parse out a proper string from image, resetting advanced start value...")
            self.ADVANCED_START = None
        except TypeError:
            self.logger.warning("ocr check could not be coerced properly into an integer, resetting advanced start value...")
            self.logger.warning("text: {text}".format(text=stage_text))
            self.ADVANCED_START = None

    @wrap_current_function
    def parse_current_stage(self):
        """
        Attempt to update the current stage attribute through an OCR check in game. The current_stage
        attribute is initialized as None, and if the current stage parsed here is unable to be coerced into
        an integer, it will be set back to None.

        When using the attribute, a check should be performed to ensure it isn't None before running
        numeric friendly conditionals.
        """
        self.ensure_collapsed()
        stage_parsed = self.stats.stage_ocr()

        try:
            stage = int(stage_parsed)
            self.logger.info("stage {stage_text} was successfully coerced into an integer: {stage}.".format(
                stage_text=stage_parsed, stage=strfnumber(stage)))
            if stage > STAGE_CAP:
                self.logger.info("stage {stage} is greater then the stage cap: {stage_cap}, resetting stage variables.".format(
                    stage=strfnumber(stage), stage_cap=STAGE_CAP))
                return

            if self.ADVANCED_START:
                if stage < self.ADVANCED_START:
                    self.logger.info("stage: {stage} is less then the advanced start: {advanced_start}, leaving current stage unchanged.".format(
                        stage=strfnumber(stage), advanced_start=self.ADVANCED_START))
                    return

            # Is the stage potentially way greater than the last check? Could mean the parse failed.
            if isinstance(self.last_stage, int):
                diff = stage - self.last_stage
                if diff > STAGE_PARSE_THRESHOLD:
                    self.logger.info(
                        "difference between current stage and last stage passes the stage change threshold: "
                        "{stage_thresh} ({stage} - {last_stage} = {diff}), resetting stage variables...".format(
                            stage_thresh=STAGE_PARSE_THRESHOLD, stage=strfnumber(stage), last_stage=strfnumber(self.last_stage), diff=strfnumber(diff)))

                    self.last_stage, self.props.current_stage = None, None
                    return

            self.logger.info("current stage in game was successfully parsed: {stage}".format(stage=strfnumber(stage)))
            self.last_stage = self.props.current_stage
            self.logger.info("last stage has been set to the previous current stage in game: {last_stage}".format(last_stage=strfnumber(self.last_stage)))
            self.props.current_stage = stage

        # ValueError when the parsed stage isn't able to be coerced.
        except ValueError:
            self.logger.error("ocr check could not parse out a proper string from image, leaving stage variables as they were before...")
            self.logger.info("current stage: {current}".format(current=strfnumber(self.props.current_stage)))
            self.logger.info("last stage: {last}".format(last=strfnumber(self.last_stage)))
            self.last_stage, self.props.current_stage = None, None

    @wrap_current_function
    def order_minigames(self):
        """
        Determine the order of minigame execution.
        """
        minigames = []

        if self.configuration.enable_coordinated_offensive:
            minigames.append("coordinated_offensive")
        if self.configuration.enable_astral_awakening:
            minigames.append("astral_awakening")
        if self.configuration.enable_heart_of_midas:
            minigames.append("heart_of_midas")
        if self.configuration.enable_flash_zip:
            minigames.append("flash_zip")

        return minigames

    @wrap_current_function
    def calculate_next_skill_execution(self, skill=None):
        """
        Calculate the datetimes that are attached to each skill in game and when they should be activated.
        """
        now = timezone.now()
        calculating = SKILLS if not skill else [skill]
        interval_key = "interval_{skill}"
        next_key = "next_{skill}"

        # Loop through all available skills and update their next execution
        # time as long as the interval is set to a value other than 0.
        for skill in calculating:
            interval = getattr(self.configuration, interval_key.format(skill=skill), 0)
            if interval != 0:
                dt = now + datetime.timedelta(seconds=interval)
                setattr(self.props, next_key.format(skill=skill), dt)
                self.logger.info("{skill} will be activated in {time}.".format(skill=skill, time=strfdelta(dt - now)))

    @wrap_current_function
    def bump_timed_variables(self, delta):
        """
        Bump the bot variables that are used to determine when functionality takes place (ie: next_xxx)
        by the specified delta.

        This is useful to us if a user has to wait for things to happens (ie: wait for an ad).
        """
        for attr in BREAK_NEXT_PROPS_ALL:
            # Ignore None attributes so that disabled functionality isn't
            # also bumped unnecessarily.
            if getattr(self.props, attr):
                setattr(self.props, attr, getattr(self.props, attr) + delta)

    def should_prestige(self):
        """
        Determine if prestige will take place. This value is based off of the configuration
        specified by the User.

        - After specified amount of time during run.
        - After a certain stage has been reached.
        - After max stage has been reached.
        - After a percent of max stage has been reached.
        """
        # Is a randomized threshold prestige already waiting to be executed?
        if self.configuration.enable_prestige_threshold_randomization:
            if self.props.next_randomized_prestige:
                now = timezone.now()
                if now > self.props.next_randomized_prestige:
                    self.logger.info("prestige randomization datetime has been surpassed, a prestige will now be executed.")
                    return True

                # Otherwise, we already know that a prestige is in a ready state...
                # We are just waiting on our randomization threshold to finish.
                else:
                    return False

        # Create a "ready" flag... Setting to true once any of our thresholds are
        # reached... This also determines whether or not we should generate the random
        # datetime until the prestige will really take place.
        ready = False

        if self.configuration.prestige_x_minutes != 0:
            now = timezone.now()
            self.logger.info("timed prestige is enabled, and should take place in {time}".format(time=strfdelta(self.props.next_prestige - now)))

            # Is the hard time limit set? If it is, perform prestige no matter what,
            # otherwise, look at the current stage conditionals present and prestige
            # off of those instead.
            if now > self.props.next_prestige:
                self.logger.info("timed prestige threshold has been reached.")
                ready = True

        # Our first timed threshold is one of our main thresholds, if that has not been reached yet,
        # then we go ahead and check the rest of our thresholds.
        if not ready:
            # Current stage must not be None, using time gate before this check. stage == None is only possible when
            # OCR checks are failing, this can happen when a stage change happens as the check takes place, causing
            # the image recognition to fail. OR if the parsed text doesn't pass the validation checks when parse is
            # malformed.
            if self.props.current_stage is None:
                self.logger.info("current stage is currently none, no stage conditionals can be checked...")
                return False

            # Any other conditionals will be using the current stage attribute of the bot.
            elif self.configuration.prestige_at_stage != 0:
                self.logger.info("prestige at specific stage: {current}/{needed}.".format(current=strfnumber(self.props.current_stage), needed=strfnumber(self.configuration.prestige_at_stage)))
                if self.props.current_stage >= self.configuration.prestige_at_stage:
                    self.logger.info("prestige stage has been reached, prestige will happen now.")
                    ready = True

            # These conditionals are dependant on the highest stage reached taken
            # from the bot's current game statistics.
            elif self.configuration.prestige_at_max_stage:
                self.logger.info("prestige at max stage: {current}/{needed}.".format(current=strfnumber(self.props.current_stage), needed=strfnumber(self.stats.highest_stage)))
                if self.props.current_stage >= self.stats.highest_stage:
                    self.logger.info("max stage has been reached, prestige will happen now.")
                    ready = True

            elif self.configuration.prestige_at_max_stage_percent != 0:
                percent = float(self.configuration.prestige_at_max_stage_percent) / 100
                threshold = int(self.stats.highest_stage * percent)
                self.logger.info("prestige at max stage percent ({percent}): {current}/{needed}".format(percent=percent, current=strfnumber(self.props.current_stage), needed=strfnumber(threshold)))
                if self.props.current_stage >= threshold:
                    self.logger.info("percent of max stage has been reached, prestige will happen now.")
                    ready = True

        # Using threshold randomization to ensure that prestiges are quite random.
        if ready:
            if self.configuration.enable_prestige_threshold_randomization:
                now = timezone.now()
                jitter = random.randint(self.configuration.prestige_random_min_time, self.configuration.prestige_random_max_time)
                dt = now + datetime.timedelta(minutes=jitter)
                self.props.next_randomized_prestige = dt
                self.logger.info("prestige threshold randomization is enabled, and the prestige process will be initiated in {time}".format(time=strfdelta(dt - now)))

                # Return false explicitly now... But our datetime is now set... The next time we enter
                # this function, we check if we've surpassed this datetime, in which case, we can
                # then finally initiate a prestige.
                return False

        # If this point is reached, just return whether or not the user has surpassed a threshold,
        # ignoring our prestige randomization entirely.
        return ready

    @wrap_current_function
    def calculate_next_prestige(self):
        """
        Calculate when the next timed prestige will take place.
        """
        now = timezone.now()
        dt = now + datetime.timedelta(seconds=self.configuration.prestige_x_minutes * 60)
        self.props.next_prestige = dt
        self.logger.info("the next timed prestige will take place in {time}".format(time=strfdelta(dt - now)))

    @wrap_current_function
    def calculate_next_master_level(self):
        """
        Calculate when the next sword master levelling process will be ran.
        """
        now = timezone.now()
        dt = now + datetime.timedelta(seconds=self.configuration.master_level_every_x_seconds)
        self.props.next_master_level = dt
        self.logger.info("sword master levelling process will be initiated in {time}".format(time=strfdelta(dt - now)))

    @wrap_current_function
    def calculate_next_heroes_level(self):
        """
        Calculate when the next heroes level process will be ran.
        """
        now = timezone.now()
        dt = now + datetime.timedelta(seconds=self.configuration.hero_level_every_x_seconds)
        self.props.next_heroes_level = dt
        self.logger.info("heroes levelling process will be initiated in {time}".format(time=strfdelta(dt - now)))

    @wrap_current_function
    def calculate_next_skills_level(self):
        """
        Calculate when the next skills level process will be ran.
        """
        now = timezone.now()
        dt = now + datetime.timedelta(seconds=self.configuration.level_skills_every_x_seconds)
        self.props.next_skills_level = dt
        self.logger.info("skills levelling process will be initiated in {time}".format(time=strfdelta(dt - now)))

    @wrap_current_function
    def calculate_next_miscellaneous_actions(self):
        """
        Calculate when the next miscellaneous function process will be ran.
        """
        now = timezone.now()
        dt = now + datetime.timedelta(minutes=15)
        self.props.next_miscellaneous_actions = dt
        self.logger.info("miscellaneous actions will be initiated in {time}".format(time=strfdelta(dt - now)))

    @wrap_current_function
    def calculate_next_skills_activation(self):
        """
        Calculate when the next skills activation process will be ran.
        """
        now = timezone.now()
        dt = now + datetime.timedelta(seconds=self.configuration.activate_skills_every_x_seconds)
        self.props.next_skills_activation = dt
        self.logger.info("skills activation process will be initiated in {time}".format(time=strfdelta(dt - now)))

    @wrap_current_function
    def calculate_next_stats_update(self):
        """
        Calculate when the next stats update should take place.
        """
        now = timezone.now()
        dt = now + datetime.timedelta(seconds=self.configuration.update_stats_every_x_minutes * 60)
        self.props.next_stats_update = dt
        self.logger.info("in game statistics update in game will be initiated in {time}".format(time=strfdelta(dt - now)))

    @wrap_current_function
    def calculate_next_daily_achievement_check(self):
        """
        Calculate when the next daily achievement check should take place.
        """
        now = timezone.now()
        dt = now + datetime.timedelta(hours=self.configuration.daily_achievements_check_every_x_hours)
        self.props.next_daily_achievement_check = dt
        self.logger.info("daily achievement check in game will be initiated in {time}".format(time=strfdelta(dt - now)))

    @wrap_current_function
    def calculate_next_milestone_check(self):
        """
        Calculate when the next milestone check should take place.
        """
        now = timezone.now()
        dt = now + datetime.timedelta(hours=self.configuration.milestones_check_every_x_hours)
        self.props.next_milestone_check = dt
        self.logger.info("milestone check in game will be initiated in {time}".format(time=strfdelta(dt - now)))

    @wrap_current_function
    def calculate_next_raid_notifications_check(self):
        """
        Calculate when the next raid notifications check should take place.
        """
        now = timezone.now()
        dt = now + datetime.timedelta(minutes=self.configuration.raid_notifications_check_every_x_minutes)
        self.props.next_raid_notifications_check = dt
        self.logger.info("raid notifications check will be initiated in {time}".format(time=strfdelta(dt - now)))

    @wrap_current_function
    def calculate_next_clan_result_parse(self):
        """
        Calculate when the next clan result parse should take place.
        """
        now = timezone.now()
        dt = now + datetime.timedelta(minutes=self.configuration.parse_clan_results_every_x_minutes)
        self.props.next_clan_results_parse = dt
        self.logger.info("clan results parse in game will be initiated in {time}".format(time=strfdelta(dt - now)))

    @wrap_current_function
    def calculate_next_break(self):
        """
        Calculate when the next break will take place in game.
        """
        if self.configuration.enable_breaks:
            now = timezone.now()

            # Calculating when the next break will begin.
            jitter = random.randint(-self.configuration.breaks_jitter, self.configuration.breaks_jitter)
            jitter = self.configuration.breaks_minutes_required + jitter

            next_break_dt = now + datetime.timedelta(minutes=jitter)

            # Calculate the datetime to determine when the bot will be resumed after a break takes place.
            resume_jitter = random.randint(self.configuration.breaks_minutes_min, self.configuration.breaks_minutes_max)
            next_break_res = next_break_dt + datetime.timedelta(minutes=resume_jitter + 10)

            self.props.next_break = next_break_dt
            self.props.resume_from_break = next_break_res

            self.logger.info("the next in game break will take place in {time_1} and resume in {time_2}".format(
                time_1=strfdelta(next_break_dt - now),
                time_2=strfdelta(next_break_res - now)
            ))

    @wrap_current_function
    @not_in_transition
    def level_heroes(self, force=False):
        """
        Perform all actions related to the levelling of all heroes in game.
        """
        if self.configuration.enable_heroes:
            now = timezone.now()
            if force or now > self.props.next_heroes_level:
                self.logger.info("{begin_force} heroes levelling process in game now.".format(
                    begin_force="beginning" if not force else "forcing"))

                if not self.goto_heroes(collapsed=False):
                    return False

                # A quick check can be performed to see if the top of the heroes panel contains
                # a hero that is already max level, if this is the case, it's safe to assume
                # that all heroes below have been maxed out. Instead of scrolling and levelling
                # all heroes, just level the top heroes.
                if self.grabber.search(self.images.max_level, bool_only=True):
                    self.logger.info("a max levelled hero has been found! Only first set of heroes will be levelled.")
                    for point in HEROES_LOCS["level_heroes"][::-1][1:9]:
                        self.click(point=point, clicks=self.configuration.hero_level_intensity, interval=0.07)

                    # Early exit as well.
                    self.calculate_next_heroes_level()
                    return True

                # Always level the first 5 heroes in the list.
                self.logger.info("levelling the first five heroes available.")
                for point in HEROES_LOCS["level_heroes"][::-1][1:10]:
                    self.click(point=point, clicks=self.configuration.hero_level_intensity, interval=0.07)

                # Travel to the bottom of the panel.
                for i in range(6):
                    self.drag(start=self.locs.scroll_start, end=self.locs.scroll_bottom_end)

                    # Have we found any max level heroes yet?
                    if self.grabber.search(image=self.images.max_level, bool_only=True):
                        self.logger.info("a max levelled hero has been found! levelling heroes now.")
                        break

                drag_start = HEROES_LOCS["drag_heroes"]["start"]
                drag_end = HEROES_LOCS["drag_heroes"]["end"]

                # Begin level and scrolling process. An assumption is made that all heroes
                # are unlocked, meaning that some un-necessary scrolls may take place.
                self.logger.info("scrolling and levelling all heroes present.")
                while not self.grabber.search(image=self.images.masteries, bool_only=True):
                    self.logger.info("levelling heroes on screen...")
                    for point in HEROES_LOCS["level_heroes"]:
                        self.click(point=point, clicks=self.configuration.hero_level_intensity, interval=0.07)

                    self.logger.info("dragging hero panel to next set of heroes...")
                    self.drag(start=drag_start, end=drag_end, pause=1)

                # Performing one additional heroes level after the top
                # has been reached...
                for point in HEROES_LOCS["level_heroes"]:
                    self.click(point=point, clicks=self.configuration.hero_level_intensity, interval=0.07)

                # Recalculate the next heroes level process.
                self.calculate_next_heroes_level()
                return True

    @wrap_current_function
    @not_in_transition
    def level_master(self, force=False):
        """
        Perform all actions related to the levelling of the sword master in game.
        """
        if self.configuration.enable_master:
            now = timezone.now()
            if force or now > self.props.next_master_level:
                self.logger.info("{begin_force} master levelling process in game now.".format(
                    begin_force="beginning" if not force else "forcing"))

                level = True
                # If the user has specified to only level the sword master once after every prestige
                # and once at the beginning of their session.
                if self.configuration.master_level_only_once:
                    if self.current_prestige_master_levelled:
                        level = False
                    else:
                        self.logger.info("levelling the sword master once until the next prestige...")
                        self.current_prestige_master_levelled = True
                else:
                    self.logger.info("levelling the sword master {clicks} time(s)".format(clicks=self.configuration.master_level_intensity))

                # Only actually executing the level process when our level boolean is true.
                if level:
                    # Travel to the master panel to allow the levelling up of our sword master.
                    if not self.goto_master(collapsed=False):
                        return False

                    # Level our sword master given the specified amount of clicks
                    # through the users configuration.
                    self.click(point=MASTER_LOCS["master_level"], clicks=self.configuration.master_level_intensity)

                # Recalculate the next sword master level process.
                self.calculate_next_master_level()
                return True

    @wrap_current_function
    @not_in_transition
    def parse_current_skills(self):
        """
        Do an explicit parse of the users current skill levels and assign them to our current prestige
        information for in game skills.
        """
        self.logger.info("parsing out current skill levels...")
        # Begin by ensuring that the master panel is open and not collapsed.
        self.goto_master(collapsed=False)

        # Looping through all in game skills, parsing out the current level.
        for skill in SKILLS:
            self.current_prestige_skill_levels[skill] = self.stats.skill_ocr(region=SKILL_LEVEL_COORDS[skill])
            self.logger.info("{skill} parsed as level {level}".format(
                skill=skill,
                level=self.current_prestige_skill_levels[skill]
            ))

    def enabled_skills(self):
        """
        Based on the users configurations, determine which skills are currently enabled, and which ones
        are disabled and should be ignored.
        """
        enabled = []
        interval_key = "interval_{skill}"

        for skill in SKILLS:
            if getattr(self.configuration, interval_key.format(skill=skill)) != 0:
                enabled.append(skill)

        return enabled

    def levels_capped(self):
        """
        Given the current in game skills list, determine if our levels are currently capped.

        Capped skills means we can skip skill levelling.

        We generate a list of skills that have not yet been capped.
        """
        capped, uncapped = {}, {}
        key = "level_{skill}_cap"

        # Looping through each available skill, comparing the specified cap value chosen by the user,
        # If "max" is chosen, we can go ahead and set the value to the available max skill level.
        # If "disabled" is chosen, we can go ahead and skip this key. Since we don't ever want to touch or level it.
        for skill in SKILLS:
            chosen = getattr(self.configuration, key.format(skill=skill))

            # Has the user chosen to either disable, or use the max level available?
            if chosen == "disable":
                continue
            elif chosen == "max":
                chosen = SKILL_MAX_LEVEL

            # Grab the current prestige skill levels value for the current
            # skill in our iteration.
            current = self.current_prestige_skill_levels[skill]

            if not isinstance(chosen, int):
                chosen = int(chosen)

            # Is the user defined cap currently reached?
            # Additionally, if a user starts a session with skills already levelled,
            # we treat it as capped if it's greater then the wanted amount. This would be fixed
            # for the next prestige though.
            if chosen == current or current > chosen:
                capped[skill] = {
                    "current": current,
                    "chosen": chosen
                }
            else:
                uncapped[skill] = {
                    "current": current,
                    "chosen": chosen,
                    "remaining": chosen - current
                }

        # Returning our list of capped/uncapped skills currently in game.
        return capped, uncapped

    @wrap_current_function
    @not_in_transition
    def level_skills(self, force=False):
        """
        Level in game skills.

        We make use of a current prestige dictionary to only ever attempt to level skills if uncapped skills
        are present, an uncapped skill means we need to add more levels, these are defined by the user.

        Some skills may also be disabled, in which case, we don't even bother dealing with these skills at all.
        """
        def level_skill(key, max_skill=False, clicks=1):
            """
            Helper method to perform the actual levelling process of the skill specified.

            We can choose to max a skill, which will perform the required color point checks
            to click the maximum purchase button when levelling skills.
            """
            point = MASTER_LOCS["skills"][key]
            color = MASTER_LOCS["skill_level_max"][key]

            # Click on our point top begin the level process
            # for the current in game skill.
            self.logger.info("levelling {skill} {clicks} time(s) now...".format(skill=key, clicks=clicks))
            self.click(point=point, pause=1, clicks=clicks, interval=0.3)

            # Should the skill in question be levelled to it's maximum amount available?
            if max_skill:
                if self.grabber.point_is_color(point=color, color=self.colors.WHITE):
                    self.click(point=color, pause=0.5)

        def can_level(key):
            """
            Check to see if a skill can currently be levelled or not.
            """
            if self.grabber.point_is_color(point=SKILL_CAN_LEVEL_LOCS[key], color=self.colors.SKILL_CANT_LEVEL):
                return False
            else:
                return True

        def active(key):
            """
            Check to see if a skill is currently active or not.
            """
            if self.grabber.search(image=self.images.cancel_active_skill, region=MASTER_COORDS["skills"][key], bool_only=True):
                return True
            else:
                return False

        # Actual skill levelling process begins here.
        if self.configuration.enable_level_skills:
            now = timezone.now()
            if force or now > self.props.next_skills_level:
                self.logger.info("{begin_force} skills levelling process in game now.".format(
                    begin_force="beginning" if not force else "forcing"))

                capped, uncapped = self.levels_capped()

                # Do we have any uncapped skills yet? If so, we should begin
                # the process to level those skills specifically to their specified level cap.
                if uncapped:
                    # Travelling to the master panel in a non collapsed state
                    # for use with the skill levelling events.
                    self.goto_master(collapsed=False)

                    # Looping through all available uncapped skills.
                    for skill, values in uncapped.items():
                        if active(key=skill):
                            self.logger.info("{skill} is currently active and will not be levelled yet.".format(skill=skill))
                            continue
                        # Can the skill even be levelled at this point?
                        # If we do not have enough gold, we should just skip this process.
                        if not can_level(key=skill):
                            self.logger.info("{skill} can not be levelled currently and will not be levelled yet.".format(skill=skill))
                            continue

                        # We first want to check to see if the skill that we are
                        # about to level should be levelled to it's max level. Which we can
                        # determine based on the chosen value == SKILL_MAX_LEVEL.
                        if values["chosen"] == SKILL_MAX_LEVEL:
                            level_skill(key=skill, max_skill=True)

                        # Otherwise, we want to level the current skill upto the
                        # cap set by our user.
                        else:
                            level_skill(key=skill, clicks=values["remaining"])

                        # After we have levelled our skill to it's appropriate values.
                        # We need to perform an OCR check on the skill in it's current state
                        # so that our current prestige level information is up to date.
                        self.current_prestige_skill_levels[skill] = self.stats.skill_ocr(region=SKILL_LEVEL_COORDS[skill])

                # Recalculate the next skill level process.
                self.calculate_next_skills_level()
                return True

    @wrap_current_function
    @not_in_transition
    def activate_skills(self, force=False):
        """
        Activate in game skills.

        Based on our available skills (not disabled), we can determine whether or not we should activate certain
        skills.

        We also only want to activate skills based on the interval chosen by the user.

        If chosen, skills should also wait to be activated until the longest interval is reached.
        """
        if self.configuration.enable_activate_skills:
            now = timezone.now()
            if force or now > self.props.next_skills_activation:
                self.logger.info("{begin_force} skills activation process in game now.".format(
                    begin_force="beginning" if not force else "forcing"))

                # Skill activation will take place now, we need to determine whether or not any skills
                # are enabled and ready to be activated.
                enabled = self.enabled_skills()

                # If we have enabled skills, begin our loop to activate them
                # if the intervals are correct.
                if enabled:
                    self.no_panel()

                    next_key = "next_{skill}"

                    # Looping through each skill that's enabled to be activated.
                    # Some skills are disabled based on their interval.
                    for skill in self.enabled_skills():
                        prop = getattr(self.props, next_key.format(skill=skill))

                        # Is this skill ready to be activated?
                        if force or now > prop:
                            self.logger.info("activating {skill} now...".format(skill=skill))
                            self.click(point=getattr(self.locs, skill), pause=0.2)
                            self.calculate_next_skill_execution(skill=skill)
                        else:
                            self.logger.info("{skill} will be activated in {time}".format(skill=skill, time=strfdelta(prop - now)))

                # Recalculate the next skill activation process.
                self.calculate_next_skills_activation()
                return True

    @wrap_current_function
    @not_in_transition
    def update_stats(self, force=False):
        """
        Update the bot stats by travelling to the stats page in the heroes panel and performing OCR update.
        """
        if self.configuration.enable_stats:
            now = timezone.now()
            if force or now > self.props.next_stats_update:
                self.logger.info("{force_or_initiate} in game statistics update now.".format(
                    force_or_initiate="forcing" if force else "beginning"))

                # Leaving boss fight here so that a stage transition does not take place
                # in the middle of a stats update.
                if not self.leave_boss():
                    return False

                # Sleeping slightly before attempting to goto top of heroes panel so that new hero
                # levels doesn't cause the 'top' of the panel to disappear after travelling.
                sleep(3)
                if not self.goto_heroes():
                    return False

                # Ensure we are at the top of the stats screen while collapsed.
                while not self.grabber.search(self.images.stats, bool_only=True):
                    self.drag(start=self.locs.scroll_start, end=self.locs.scroll_top_end)
                # Ensure the stats panel has been opened before continuing.
                while not self.grabber.search(self.images.stats_title, bool_only=True):
                    self.click(point=HEROES_LOCS["stats_collapsed"], pause=1)

                # Scrolling to the bottom of the stats panel.
                sleep(2)
                for i in range(5):
                    self.drag(start=self.locs.scroll_start, end=self.locs.scroll_bottom_end)

                self.stats.update_ocr()
                self.stats.statistics.bot_statistics.updates += 1
                self.stats.statistics.bot_statistics.save()

                self.calculate_next_stats_update()
                self.click(point=MASTER_LOCS["screen_top"], clicks=3)

    @wrap_current_function
    @not_in_transition
    def prestige(self, force=False):
        """
        Perform a prestige in game.
        """
        if self.configuration.enable_auto_prestige:
            if self.should_prestige() or force:
                self.logger.info("{begin_force} prestige process in game now.".format(
                    begin_force="beginning" if not force else "forcing"))

                # Reset the current prestige skill level values, since they all go back to
                # zero on a prestige, We can reset and be sure they're all zero.
                self.current_prestige_skill_levels = {skill: 0 for skill in SKILLS}

                # Reset the current prestige variables, so that after this prestige is finished,
                # we perform those functions then disable them when needed.
                self.current_prestige_master_levelled = False

                # Reset the prestige randomization variable if it is currently
                # being used, so that our next prestige process is reset.
                if self.configuration.enable_prestige_threshold_randomization:
                    if self.props.next_randomized_prestige:
                        self.props.next_randomized_prestige = None

                tournament = self.check_tournament()

                # If tournament==True, then a tournament was available to join (which means we prestiged, exit early).
                if tournament:
                    return False
                if not self.goto_master(collapsed=False, top=False):
                    return False

                # Click on the prestige button, and check for the prompt confirmation being present. Sleeping
                # slightly here to ensure that connections issues do not cause the prestige to be misfire.
                self.click(point=MASTER_LOCS["prestige"], pause=3)
                prestige_found, prestige_position = self.grabber.search(self.images.confirm_prestige)
                if prestige_found:
                    # Parsing the advanced start value that is present before a prestige takes place...
                    # This is used to improve stage parsing to not allow values < the advanced start value.
                    prestige, advanced_start = self.stats.update_prestige(artifact=self.next_artifact_upgrade, current_stage=self.props.current_stage)
                    self.props.last_prestige = prestige
                    self.parse_advanced_start(advanced_start)

                    self.click(point=MASTER_LOCS["prestige_confirm"], pause=1)
                    # Waiting for a while after prestiging, this reduces the chance
                    # of a game crash taking place due to many clicks while game is resetting.
                    self.click(point=MASTER_LOCS["prestige_final"], pause=35)

                    # If a timer is used for prestige. Reset this timer to the next timed prestige value.
                    if self.configuration.prestige_x_minutes != 0:
                        self.calculate_next_prestige()

                    # Ensure an artifact purchase check is performed so that an upgrade takes
                    # place properly once the prestige is complete.
                    self.artifacts()

                    # After a prestige, run all actions instantly to ensure that initial levels are gained.
                    # Also attempt to activate skills afterwards so that stage progression is started before
                    # any other actions or logic takes place in game.
                    self.level_master(force=True)
                    self.level_skills(force=True)
                    self.activate_skills(force=True)

                    # Shimming in a small wait period, so that our level heroes
                    # process has a second to let the bot deal damage.
                    # When all skills are active, it's likely that heroes will
                    # become available shortly after.
                    sleep(2)

                    # Level heroes last, once our master is levelled,
                    # and skills have been activated, saving some time here.
                    self.level_heroes(force=True)

                    # If the current stage currently is greater than the current max stage, lets update our stats
                    # to reflect that a new max stage has been reached. This allows for
                    if self.props.current_stage and self.stats.highest_stage:
                            if self.props.current_stage > self.stats.highest_stage:
                                self.logger.info("current stage is greater than your previous max stage {max}, forcing a stats update to reflect new max stage.".format(
                                    max=self.stats.highest_stage))
                                self.update_stats(force=True)

                    self.props.current_stage = self.ADVANCED_START

    @wrap_current_function
    @not_in_transition
    def parse_artifacts(self):
        """
        Begin the process to parse owned artifacts from in game.
        """
        self.logger.info("beginning artifact parsing process.")
        if not self.leave_boss():
            return False
        if not self.goto_artifacts(collapsed=False):
            return False

        # We are at the artifacts panel collapsed at this point... Begin parsing.
        self.stats.parse_artifacts()

    @wrap_current_function
    @not_in_transition
    def artifacts(self):
        """
        Determine whether or not any artifacts should be purchased, and purchase them.
        """
        def purchase_new(image, point, color):
            """
            Given an image, point and color, use as a helper function to either discover or enchant an artifact.
            """
            # Is the image on the screen?
            if self.grabber.search(image=image, bool_only=True):
                # Is the specified color present in the point chosen.
                if self.grabber.point_is_color(point=point, color=color):
                    # Click to enchant/discover artifact.
                    self.logger.info("performing...")
                    self.click(point=point, pause=1)
                    self.click(point=self.locs.purchase, pause=2)

                    self.click(point=self.locs.close_top, clicks=5, interval=0.5, pause=2)

        # Check for discovery/enchantment first.
        if self.configuration.enable_artifact_discover_enchant:
            self.logger.info("beginning artifact enchant/discover process.")
            if not self.goto_artifacts():
                return False

            # Checking for discover available.
            self.logger.info("checking if artifact discovery can be performed.")
            purchase_new(
                image=self.images.discover,
                point=self.locs.discover_point,
                color=self.colors.DISCOVER
            )
            # Checking for enchant available.
            self.logger.info("checking if artifact enchantment can be performed.")
            purchase_new(
                image=self.images.enchant,
                point=self.locs.enchant_point,
                color=self.colors.ENCHANT
            )

        if self.configuration.enable_artifact_purchase:
            self.logger.info("beginning artifact purchase process.")
            if not self.goto_artifacts(collapsed=False):
                return False

            artifact = self.next_artifact_upgrade

            # Access to current upgrade is present above,
            # go ahead and update the next artifact to purchase.
            self.update_next_artifact_upgrade()
            self.logger.info("attempting to upgrade {artifact} now.".format(artifact=artifact))

            # Make sure that the proper spend max multiplier is used to fully upgrade an artifact.
            # 1.) Ensure that the percentage (%) multiplier is selected.
            loops = 0
            while not self.grabber.search(self.images.percent_on, bool_only=True):
                loops += 1
                if loops == FUNCTION_LOOP_TIMEOUT:
                    self.logger.warning("unable to set the artifact buy multiplier to use percentage, skipping...")
                    self.ERRORS += 1
                    return False

                self.click(point=ARTIFACTS_LOCS["percent_toggle"], pause=0.5)

            # 2.) Ensure that the SPEND Max multiplier is selected.
            loops = 0
            while not self.grabber.search(self.images.spend_max, bool_only=True):
                loops += 1
                if loops == FUNCTION_LOOP_TIMEOUT:
                    self.logger.warning("unable to set the spend multiplier to spend max... skipping.")
                    self.ERRORS += 1
                    return False

                self.click(point=ARTIFACTS_LOCS["buy_multiplier"], pause=0.5)
                self.click(point=ARTIFACTS_LOCS["buy_max"], pause=0.5)

            # Looking for the artifact to upgrade here, dragging until it is finally found.
            loops = 0
            while not self.grabber.search(ARTIFACT_MAP.get(artifact), bool_only=True):
                loops += 1
                if loops == FUNCTION_LOOP_TIMEOUT:
                    self.logger.warning("artifact: {artifact} couldn't be found on screen... skipping.".format(artifact=artifact))
                    self.ERRORS += 1
                    return False

                self.drag(start=self.locs.scroll_start, end=self.locs.scroll_bottom_end, pause=0.5)

            # Making it here means the artifact in question has been found.
            found, position = self.grabber.search(ARTIFACT_MAP.get(artifact))
            new_x = position[0] + ARTIFACTS_LOCS["artifact_push"]["x"]
            new_y = position[1] + ARTIFACTS_LOCS["artifact_push"]["y"]

            # Currently just upgrading the artifact to it's max level. Future updates may include the ability
            # to determine how much to upgrade an artifact by.
            self.click(point=(new_x, new_y), pause=1, disable_padding=True)

    @not_in_transition
    def check_tournament(self):
        """
        Check that a tournament is available/active. Tournament will be joined if a new possible.
        """
        if self.configuration.enable_tournaments:
            self.logger.info("checking for tournament ready to join or in progress.")
            if not self.goto_master():
                return False

            # Looping to find tournament here, since there's a chance that the tournament is finished, which
            # causes a star trail circle the icon. May be hard to find, give it a couple of tries.
            tournament_found = False
            for i in range(5):
                tournament_found, tournament_position = self.grabber.search(self.images.tournament)
                if tournament_found:
                    break

                # Wait slightly before trying again.
                sleep(0.2)

            if tournament_found:
                self.click(point=self.locs.tournament, pause=2)
                found, position = self.grabber.search(self.images.join)
                if found:
                    # A tournament is ready to be joined. First, we must travel the the base
                    # prestige screen, perform a prestige update, before joining the tournament.
                    self.logger.info("tournament is available to join. generating prestige instance before joining.")
                    self.click(point=MASTER_LOCS["screen_top"], pause=1)
                    if not self.goto_master(collapsed=False, top=False):
                        return False

                    self.click(point=MASTER_LOCS["prestige"], pause=3)
                    prestige_found = self.grabber.search(self.images.confirm_prestige, bool_only=True)
                    if prestige_found:
                        # Parsing the advanced start value that is present before a prestige takes place...
                        # This is used to improve stage parsing to not allow values < the advanced start value.
                        self.parse_advanced_start(self.stats.update_prestige(current_stage=self.props.current_stage, artifact=self.next_artifact_upgrade))
                        self.click(point=MASTER_LOCS["screen_top"], pause=1)

                    # Collapsing the master panel... Then attempting to join tournament.
                    self.goto_master()
                    self.click(point=self.locs.tournament, pause=2)
                    self.logger.info("joining new tournament now...")
                    self.click(point=self.locs.join, pause=2)
                    self.click(point=self.locs.tournament_prestige, pause=35)
                    self.props.current_stage = self.ADVANCED_START

                    return True

                # Otherwise, maybe the tournament is over? Or still running.
                else:
                    collect_found, collect_position = self.grabber.search(self.images.collect_prize)
                    if collect_found:
                        self.logger.info("tournament is over, attempting to collect reward now.")
                        self.click(point=self.locs.collect_prize, pause=2)
                        self.click(point=self.locs.game_middle, clicks=10, interval=0.5)
                        return False

    @wrap_current_function
    @not_in_transition
    def daily_rewards(self):
        """
        Collect any daily gifts if they're available.
        """
        self.logger.info("checking if any daily rewards are currently available to collect.")
        if not self.ensure_collapsed():
            return False

        reward_found = self.grabber.search(self.images.daily_reward, bool_only=True)
        if reward_found:
            self.logger.info("daily rewards are available, collecting!")
            self.click(point=self.locs.open_rewards, pause=1)
            self.click(point=self.locs.collect_rewards, pause=1)
            self.click(point=self.locs.game_middle, clicks=5, interval=0.5, pause=1)
            self.click(point=MASTER_LOCS["screen_top"], pause=1)

        return reward_found

    @wrap_current_function
    @not_in_transition
    def hatch_eggs(self):
        """
        Hatch any eggs if they're available.
        """
        if self.configuration.enable_egg_collection:
            self.logger.info("checking if any eggs are available to be hatched in game.")
            if not self.ensure_collapsed():
                return False

            egg_found = self.grabber.search(self.images.hatch_egg, bool_only=True)
            if egg_found:
                self.logger.info("egg(s) are available, collecting!")
                self.click(point=self.locs.hatch_egg, pause=1)
                self.click(point=self.locs.game_middle, clicks=5, interval=0.5, pause=1)

            return egg_found

    @wrap_current_function
    @not_in_transition
    def clan_crate(self):
        """
        Check if a clan crate is currently available and collect it if one is.
        """
        if not self.ensure_collapsed():
            return False

        self.click(point=self.locs.clan_crate, pause=0.5)
        found, pos = self.grabber.search(self.images.okay)
        if found:
            self.logger.info("clan crate is available, collecting!")
            self.click_image(image=self.images.okay, pos=pos, pause=1)

        return found

    def miscellaneous_actions(self, force=False):
        """
        Miscellaneous actions can be activated here when the generic cooldown is reached.
        """
        if force or timezone.now() > self.props.next_miscellaneous_actions:
            self.logger.info("{force_or_initiate} miscellaneous actions now".format(
                force_or_initiate="forcing" if force else "beginning"))

            # Running through all generic functions that should only be available once
            # every once in a while, meaning we do not have to check for them at all times.
            self.clan_crate()
            self.daily_rewards()
            self.hatch_eggs()

            # Calculate when the next miscellaneous actions process
            # should take place again.
            self.calculate_next_miscellaneous_actions()

    @wrap_current_function
    @not_in_transition
    def breaks(self, force=False):
        """
        Check to see if a break should take place, if a break should take place, the emulator will
        be restarted and the bot will wait until the resume time has been reached, then the game
        will be opened once again and the bot will resume its functionality. A resume will also
        cause all calculable variables to be recalculated.
        """
        if self.configuration.enable_breaks:
            assert self.props.next_break and self.props.resume_from_break
            now = timezone.now()
            if force or now > self.props.next_break:
                # A break can now take place...
                time_break = self.props.next_break - now
                time_resume = self.props.resume_from_break - now
                delta = time_resume - time_break

                # Forcing a break should modify our next break values to now plus whatever
                # the most recent break was calculated as.
                if force:
                    self.props.next_break = now
                    self.props.resume_from_break = now + delta

                # Modify all next attributes to take place after their normal calculated
                # time with a bit of padding after a break ends.
                for prop in BREAK_NEXT_PROPS:
                    current = getattr(self.props, prop, None)
                    if current:
                        # Adding a bit of padding to next activation values.
                        new = current + delta + datetime.timedelta(seconds=30)
                        setattr(self.props, prop, new)

                break_log_dt = now + datetime.timedelta(seconds=60)
                self.logger.info("waiting for break to end... ({break_end})".format(break_end=strfdelta(self.props.resume_from_break - now)))
                while True:
                    now = timezone.now()
                    if now > self.props.resume_from_break:
                        self.logger.info("break has ended... opening game now.")
                        self.calculate_next_break()
                        return True

                    if now > break_log_dt:
                        break_log_dt = now + datetime.timedelta(seconds=60)
                        self.logger.info("waiting for break to end... ({break_end})".format(break_end=strfdelta(self.props.resume_from_break - now)))

                    sleep(1)

    @wrap_current_function
    @not_in_transition
    def daily_achievement_check(self, force=False):
        """
        Perform a check for any completed daily achievements, collecting them as long as any are present.
        """
        if self.configuration.enable_daily_achievements:
            now = timezone.now()
            if force or now > self.props.next_daily_achievement_check:
                self.logger.info("{force_or_initiate} daily achievement check now".format(
                    force_or_initiate="forcing" if force else "beginning"))

                if not self.goto_master():
                    return False
                if not self.leave_boss():
                    return False

                # Open the achievements tab in game.
                self.click(point=MASTER_LOCS["achievements"], pause=2)

                # Are there any completed daily achievements?
                # Note: The single "ad watch" daily is not completed here
                # unless a user explicitly goes in and watches the ad.
                while self.grabber.search(self.images.daily_collect, bool_only=True):
                    found, pos = self.grabber.search(self.images.daily_collect)
                    if found:
                        # Collect the achievement reward here.
                        self.logger.info("completed daily achievement found, collecting now.")
                        self.click_image(image=self.images.daily_collect, pos=pos)

                # Exiting achievements screen now.
                self.calculate_next_daily_achievement_check()
                self.click(point=MASTER_LOCS["screen_top"], clicks=3)

    @wrap_current_function
    @not_in_transition
    def milestone_check(self, force=False):
        """
        Perform a check for the collection of a completed milestone reward.
        """
        if self.configuration.enable_milestones:
            now = timezone.now()
            if force or now > self.props.next_milestone_check:
                self.logger.info("{force_or_initiate} milestone check now".format(
                    force_or_initiate="forcing" if force else "beginning"))

                if not self.goto_master():
                    return False
                if not self.leave_boss():
                    return False

                # Open the milestones tab in game.
                self.click(point=MASTER_LOCS["achievements"], pause=2)
                self.click(point=MASTER_LOCS["milestones"]["milestones_header"], pause=1)

                # Loop forever until no more milestones can be collected.
                while True:
                    # Is the collect button available and the correct color for collection?
                    if self.grabber.point_is_color(point=MASTER_LOCS["milestones"]["milestones_collect_point"], color=self.colors.COLLECT_GREEN):
                        self.logger.info("a completed milestone is complete, collecting now...")
                        self.click(point=MASTER_LOCS["milestones"]["milestones_collect_point"], pause=1)
                        self.click(point=self.locs.game_middle, clicks=5, interval=0.5)
                        sleep(3)
                    else:
                        self.logger.info("no milestone available for completion...")
                        break

                # Exiting milestones screen now.
                self.calculate_next_milestone_check()
                self.click(point=MASTER_LOCS["screen_top"], clicks=3)

    @wrap_current_function
    @not_in_transition
    def raid_notifications(self, force=False):
        """
        Perform all checks to see if a sms message will be sent to notify a user of an active raid.
        """
        if self.configuration.enable_raid_notifications:
            now = timezone.now()
            if force or now > self.props.next_raid_notifications_check:
                self.logger.info("{force_or_initiate} raid notifications check now".format(
                    force_or_initiate="forcing" if force else "beginning"))

                # Has an attack reset value already been parsed?
                if self.props.next_raid_attack_reset:
                    if self.props.next_raid_attack_reset > now:
                        self.logger.info("the next raid attack reset is still in the future, no notification will be sent.")
                        self.calculate_next_raid_notifications_check()
                        return False

                # Opening up the clan raid panel and checking if the fight button is available.
                # This would mean that we can perform some fights, if it is present, we also check to
                # see how much time until the attacks reset, once the current time has surpassed that
                # value, we allow another notification to be sent.
                if not self.goto_clan():
                    return False

                self.click(point=self.locs.clan_raid, pause=4)

                if self.grabber.search(self.images.raid_fight, bool_only=True):
                    # Fights are available, lets also parse out the next time that attacks will be reset.
                    self.props.next_raid_attack_reset = self.stats.get_raid_attacks_reset()
                    if not self.props.next_raid_attack_reset:
                        self.logger.info("The next raid attack reset could not be parsed correctly, a notification will not be sent...")

                    # Send out a notification to the user through Twilio.
                    notification = send_raid_notification(
                        sid=self.configuration.raid_notifications_twilio_account_sid,
                        token=self.configuration.raid_notifications_twilio_auth_token,
                        from_num=self.configuration.raid_notifications_twilio_from_number,
                        to_num=self.configuration.raid_notifications_twilio_to_number)

                    self.logger.info("a notification has been sent to {to_num} from {from_num}".format(
                        to_num=self.configuration.raid_notifications_twilio_to_number,
                        from_num=self.configuration.raid_notifications_twilio_from_number))

                    self.logger.info("message sid: {sid}".format(sid=notification.sid))
                    self.logger.info("message body: {body}".format(body=notification.body))
                    self.logger.info("the next notification will only be sent after the current raid attack reset has been reached...")
                    self.logger.info("next raid attack reset: {next_raid_attack}".format(next_raid_attack=self.props.next_raid_attack_reset))
                else:
                    self.logger.info("no raid fight is currently active or available! No notification will be sent.")

                self.calculate_next_raid_notifications_check()

    @wrap_current_function
    @not_in_transition
    def clan_results_parse(self, force=False):
        """
        If the time threshold has been reached and clan result parsing is enabled, initiate the process
        in game to grab and parse out the information from the most recent results data taken from the current
        in game guild.

        A clan results parse will take the following steps:

            - Determine the name and id of the users current clan, if no clan is available or the name and id
              can not be successfully parsed, the function will exit early.

            - Grab the most recent "results" CSV data and parse it into some readable data points.

            - If the results grabbed are a duplicate (This will happen if the interval between checks takes place
              multiple times before a different raid is completed).

            - A digested version of the CSV data is used as the primary key for our clan results.
        """
        if self.configuration.enable_clan_results_parse:
            if force or timezone.now() > self.props.next_clan_results_parse:
                self.logger.info("{force_or_initiate} clan results parsing now.".format(
                    force_or_initiate="forcing" if force else "beginning"))

                # The clan results parse should take place.
                if not self.no_panel():
                    return False
                if not self.leave_boss():
                    return False

                # Travel to the clan page and attempt to parse out some generic
                # information about the current users clan.
                if not self.goto_clan():
                    return False

                # Is the user in a clan or not? If no clan is present,
                # exiting early and not attempting to parse.
                if not self.grabber.search(self.images.clan_info, bool_only=True):
                    self.logger.warning("no clan is available to parse, giving up...")

                # A clan is available, begin by opening the information panel
                # to retrieve some generic information about the clan.
                self.click(point=self.locs.clan_info, pause=2)
                self.click(point=self.locs.clan_info_header, pause=2)

                self.logger.info("attempting to parse out generic clan information now...")

                # The clan info panel is open and we can attempt to grab the name and code
                # of the users current clan.
                name, code = self.stats.clan_name_and_code()

                if not name:
                    self.logger.warning("unable to parse clan name, giving up...")
                    return False
                if not code:
                    self.logger.warning("unable to parse clan code, giving up...")
                    return False

                # Getting or creating the initial clan objects. Updating the clan name
                # if it's changed since the last results parse, the code may not change.
                try:
                    clan = Clan.objects.get(code=code)
                except Clan.DoesNotExist:
                    clan = Clan.objects.create(code=code, name=name)

                if clan.name != name:
                    self.logger.info("clan name: {orig_name} has changed to {new_name}, updating clan information.".format(
                        orig_name=clan.name, new_name=name))
                    clan.name = name
                    clan.save()

                self.logger.info("{clan} was parsed successfully.".format(clan=clan))
                self.logger.info("attempting to parse out most recent raid results from clan...")

                self.click(point=self.locs.clan_previous_raid, pause=2)
                self.click(point=self.locs.clan_results_copy, pause=1)

                win32clipboard.OpenClipboard()
                results = win32clipboard.GetClipboardData()
                win32clipboard.CloseClipboard()

                if not results:
                    self.logger.warning("no clipboard data was retrieved, giving up...")
                    return False

                # Attempting to generate the raid result for logging purposes,
                # if the raid found already exists, we'll simply return a False
                # boolean to determine this and log some info.
                raid = RaidResult.objects.generate(clipboard=results, clan=clan, instance=self.instance)

                if not raid:
                    self.logger.warning("the parsed raid results already exist and likely haven't changed since the last parse.")
                else:
                    self.logger.info("successfully parsed and created a new raid result instance.")
                    self.logger.info("raid result: {raid}".format(raid=raid))

                self.calculate_next_clan_result_parse()

    def welcome_screen_check(self):
        """
        Check to see if the welcome panel is currently on the screen, and close it.
        """
        if self.grabber.search(self.images.welcome_header, bool_only=True):
            found, pos = self.grabber.search(self.images.welcome_collect_no_vip)
            if found:
                self.click_image(image=self.images.welcome_collect_no_vip, pos=pos, pause=1)
            else:
                found, pos = self.grabber.search(self.images.welcome_collect_vip)
                if found:
                    self.click_image(image=self.images.welcome_collect_vip, pos=pos, pause=1)

    def rate_screen_check(self):
        """
        Check to see if the game rate panel is currently on the screen, and close it.
        """
        if self.grabber.search(self.images.rate_icon, bool_only=True):
            found, pos = self.grabber.search(self.images.large_exit_panel)
            if found:
                self.click_image(image=self.images.large_exit_panel, pos=pos, pause=1)

    def ad(self):
        """
        Collect ad if one is available on the screen.

        Note: This function does not require a max loop (FUNCTION_LOOP_TIMEOUT) since it only ever loops
              while the collect panel is on screen, this provides only two possible options.

        This is the main ad function. Used in two places:
           - One instance is used by the transition functionality and decorator.
           - The other one allows the function to be called directly without decorators added.
        """
        while self.grabber.search(self.images.collect_ad, bool_only=True) or self.grabber.search(self.images.watch_ad, bool_only=True):
            # VIP Unlocked...
            if self.grabber.search(self.images.collect_ad, bool_only=True):
                self.logger.info("collecting vip ad now...")
                self.click(point=self.locs.collect_ad, pause=1, offset=5)
            # No VIP...
            if self.grabber.search(self.images.watch_ad, bool_only=True):
                self.logger.info("declining fairy ad now...")
                self.click(point=self.locs.no_thanks, pause=1, offset=5)

    @wrap_current_function
    @not_in_transition
    def collect_ad(self):
        self.ad()

    def collect_ad_no_transition(self):
        self.ad()

    @not_in_transition
    def fight_boss(self):
        """
        Ensure that the boss is being fought if it isn't already.
        """
        loops = 0
        while True:
            loops += 1
            if loops == BOSS_LOOP_TIMEOUT:
                self.logger.warning("unable to enter boss fight currently...")
                self.ERRORS += 1
                return False

            if self.grabber.search(self.images.fight_boss, bool_only=True):
                self.logger.info("attempting to initiate boss fight in game. ({tries}/{max})".format(tries=loops, max=BOSS_LOOP_TIMEOUT))
                self.click(point=self.locs.fight_boss, pause=0.8)
            else:
                break

        return True

    @not_in_transition
    def leave_boss(self):
        """
        Ensure that there is no boss being fought (avoids transition).
        """
        loops = 0
        while True:
            loops += 1
            if loops == BOSS_LOOP_TIMEOUT:
                self.logger.warning("unable to leave boss fight, assuming boss could not be reached...")
                self.ERRORS += 1
                return True

            if not self.grabber.search(self.images.fight_boss, bool_only=True):
                self.logger.info("attempting to leave active boss fight in game. ({tries}/{max})".format(
                    tries=loops, max=BOSS_LOOP_TIMEOUT))
                self.click(point=self.locs.fight_boss, pause=0.8)
            else:
                break

        # Sleeping for a bit after leaving boss fight in case some sort of
        # transition takes places directly after.
        sleep(3)
        return True

    @wrap_current_function
    @not_in_transition
    def tap(self):
        """
        Perform simple screen tap over entire game area.
        """
        if self.configuration.enable_tapping:
            self.logger.info("beginning generic tapping process...")

            # Ensure the game screen is currently displaying the titan correctly.
            self.ensure_collapsed()

            # Looping through all of our fairy map locations... Clicking and checking
            # for ads throughout the process.
            for index, point in enumerate(self.locs.fairies_map, start=1):
                self.click(point=point)

                # Every fifth click, we should check to see if an ad is present on the
                # screen now, since our clicks could potentially trigger a fairy ad.
                if index % 5 == 0:
                    self.collect_ad_no_transition()

            # If no transition state was found during clicks, wait a couple of seconds in case a fairy was
            # clicked just as the tapping ended.
            sleep(2)

    @wrap_current_function
    @not_in_transition
    def minigames(self):
        if self.configuration.enable_minigames:
            self.logger.info("beginning minigame execution process...")

            # Ensure the game screen is currently displaying the titan correctly.
            self.ensure_collapsed()

            tapping_map = []
            # Based on the enabled minigames, tapping locations are appended
            # and looped through after to ensure minigames are always up.
            for minigame in self.minigame_order:
                # Add (str) to the map, we check for this and output a informational
                # log when the point in our loop is a string. Can only ever be a minigame name.
                tapping_map += (minigame,)
                tapping_map += getattr(self.locs, minigame)

            for index, point in enumerate(tapping_map, start=1):
                if isinstance(point[0], str):
                    self.logger.info("executing/tapping {minigame}".format(minigame=point))
                else:
                    self.click(point=point)

                # Every fifth click, we should check to see if an ad is present on the
                # screen now, since our clicks could potentially trigger a fairy ad.
                if index % 5 == 0:
                    self.collect_ad_no_transition()

            # If no transition state was found during clicks, wait a couple of seconds in case a fairy was
            # clicked just as the tapping ended.
            sleep(2)

    @not_in_transition
    def ensure_collapsed(self):
        """
        Ensure that regardless of the current panel that is active, our game screen is present.

        We can do this by simply making sure that our settings icon is available on the screen,
        since this button is ALWAYS visible as long as no panel is expanded currently.
        """
        if self.grabber.search(image=[self.images.settings, self.images.clan_raid_ready, self.images.clan_no_raid], bool_only=True):
            return True

        # If we reach this point, it means our settings are not yet available, let's minimize
        # the panel that's currently expanded.
        while self.grabber.search(image=self.images.collapse_panel, bool_only=True):
            found, pos = self.grabber.search(image=self.images.collapse_panel)

            # The collapse button is found, let's click it and wait shortly before continuing.
            if found:
                self.click_image(
                    image=self.images.collapse_panel,
                    pos=pos,
                    pause=1
                )
                return True

        # Additionally, maybe the shop panel was opened for some reason. We should also
        # handle this edge case by closing it if the collapse panel is not visible.
        while self.grabber.search(image=self.images.exit_panel, bool_only=True):
            found, pos = self.grabber.search(image=self.images.exit_panel)

            if found:
                self.click_image(
                    image=self.images.exit_panel,
                    pos=pos,
                    pause=1
                )
                return True

    @not_in_transition
    def goto_panel(self, panel, icon, top_find, bottom_find, collapsed=True, top=True):
        """
        Goto a specific panel, panel represents the key of this panel, also used when determining what panel
        to click on initially.

        Icon represents the image in game that represents a panel being open. This image is searched
        for initially before attempting to move to the top or bottom of the specified panel.

        NOTE: This function will return a boolean to determine if the panel was reached successfully. This can be
              used to exit out of actions or other pieces of bot functionality early if something has gone wrong.
        """
        self.logger.debug("attempting to travel to the {collapse_expand} {top_bot} of {panel} panel".format(
            collapse_expand="collapsed" if collapsed else "expanded", top_bot="top" if top else "bottom", panel=panel))

        loops = 0
        while not self.grabber.search(icon, bool_only=True):
            loops += 1
            if loops == FUNCTION_LOOP_TIMEOUT:
                self.logger.warning("error occurred while travelling to {panel} panel, exiting function early.".format(panel=panel))
                self.ERRORS += 1
                return False

            self.click(point=getattr(self.locs, panel), pause=1)

        # The shop panel may not be expanded/collapsed. Skip when travelling to shop panel.
        if panel != "shop":
            # Ensure the panel is expanded/collapsed appropriately.
            loops = 0
            if collapsed:
                while not self.grabber.search(self.images.expand_panel, bool_only=True):
                    loops += 1
                    if loops == FUNCTION_LOOP_TIMEOUT:
                        self.logger.warning("unable to collapse panel: {panel}, exiting function early.".format(panel=panel))
                        self.ERRORS += 1
                        return False
                    self.click(point=self.locs.expand_collapse_top, pause=1, offset=1)
            else:
                while not self.grabber.search(self.images.collapse_panel, bool_only=True):
                    loops += 1
                    if loops == FUNCTION_LOOP_TIMEOUT:
                        self.logger.warning("unable to expand panel: {panel}, exiting function early.".format(panel=panel))
                        self.ERRORS += 1
                        return False
                    self.click(point=self.locs.expand_collapse_bottom, pause=1, offset=1)

        # At this point, the panel should at least be opened.
        find = top_find if top or bottom_find is None else bottom_find

        # Trying to travel to the top or bottom of the specified panel, trying a set number of times
        # before giving up and breaking out of loop.
        loops = 0
        end_drag = self.locs.scroll_top_end if top else self.locs.scroll_bottom_end
        while not self.grabber.search(find, bool_only=True):
            loops += 1
            if loops == FUNCTION_LOOP_TIMEOUT:
                self.logger.warning(
                    "error occurred while travelling to {panel} panel, exiting function early.".format(
                        panel=panel))
                self.ERRORS += 1
                return False

            self.drag(start=self.locs.scroll_start, end=end_drag, pause=0.5)

        # Reaching this point represents a successful panel travel to.
        return True

    def goto_master(self, collapsed=True, top=True):
        """
        Instruct the bot to travel to the sword master panel.
        """
        return self.goto_panel("master", self.images.master_active, self.images.raid_cards, self.images.prestige, collapsed=collapsed, top=top)

    def goto_heroes(self, collapsed=True, top=True):
        """
        Instruct the bot to travel to the heroes panel.
        """
        return self.goto_panel("heroes", self.images.heroes_active, self.images.masteries, self.images.maya_muerta, collapsed=collapsed, top=top)

    def goto_equipment(self, collapsed=True, top=True):
        """
        Instruct the bot to travel to the heroes panel.
        """
        return self.goto_panel("equipment", self.images.equipment_active, self.images.crafting, None, collapsed=collapsed, top=top)

    def goto_pets(self, collapsed=True, top=True):
        """
        Instruct the bot to travel to the pets panel.
        """
        return self.goto_panel("pets", self.images.pets_active, self.images.next_egg, None, collapsed=collapsed, top=top)

    def goto_artifacts(self, collapsed=True, top=True):
        """
        Instruct the bot to travel to the artifacts panel.
        """
        return self.goto_panel("artifacts", self.images.artifacts_active, self.images.salvaged, None, collapsed=collapsed, top=top)

    def goto_shop(self, collapsed=False, top=True):
        """
        Instruct the bot to travel to the shop panel.
        """
        return self.goto_panel("shop", self.images.shop_active, self.images.shop_keeper, None, collapsed=collapsed, top=top)

    @not_in_transition
    def goto_clan(self):
        """
        Open the clan panel in game.
        """
        self.logger.info("attempting to open the clan panel in game.")

        loops = 0
        while not self.grabber.search(self.images.clan, bool_only=True):
            if loops == FUNCTION_LOOP_TIMEOUT:
                self.logger.info("unable to open clan panel, giving up.")
                return False

            loops += 1
            self.click(point=self.locs.clan)
            sleep(3)

        return True

    @not_in_transition
    def no_panel(self):
        """
        Instruct the bot to make sure no panels are currently open.
        """
        loops = 0
        while self.grabber.search(self.images.exit_panel, bool_only=True):
            loops += 1
            if loops == FUNCTION_LOOP_TIMEOUT:
                self.logger.warning("error occurred while attempting to close all panels, exiting early.")
                self.ERRORS += 1
                return False

            found, pos = self.grabber.search(image=self.images.exit_panel)
            if found:
                self.click_image(image=self.images.exit_panel, pos=pos, pause=0.5)

        return True

    @wrap_current_function
    def soft_shutdown(self):
        """
        Perform a soft shutdown of the bot, taking care of any cleanup or related tasks.
        """
        self.logger.info("beginning soft shutdown...")
        self.update_stats(force=True)

    @wrap_current_function
    def pause(self):
        """
        Execute a pause for this Bot.
        """
        self.PAUSE = True
        self.instance.pause()

    @wrap_current_function
    def resume(self):
        """Execute a resume for this Bot."""
        self.PAUSE = False
        self.instance.resume()

    @wrap_current_function
    def terminate(self):
        """
        Execute a termination of this Bot instance.
        """
        self.TERMINATE = True

    @wrap_current_function
    def soft_terminate(self):
        """
        Execute a soft shutdown/termination of this Bot instance.
        """
        self.soft_shutdown()
        self.TERMINATE = True

    @wrap_current_function
    def setup_shortcuts(self):
        """
        Setup the keypress shortcut listener.
        """
        self.logger.info("initiating keyboard (shortcut) listener...")
        # Attach the ShortcutListener callback function that is called whenever a key is pressed.
        listener = ShortcutListener(logger=self.logger, instance=self.instance, cooldown=2)

        keyboard.on_press(callback=listener.on_press)
        keyboard.on_release(callback=listener.on_release)

    @wrap_current_function
    def setup_loop_functions(self):
        """
        Generate list of loop functions based on the enabled functions specified in the configuration.
        """
        lst = [
            k for k, v in {
                "fight_boss": True,
                "miscellaneous_actions": True,
                "tap": self.configuration.enable_tapping,
                "minigames": self.configuration.enable_minigames,
                "parse_current_stage": True,
                "level_master": self.configuration.enable_master,
                "level_heroes": self.configuration.enable_heroes,
                "level_skills": self.configuration.enable_level_skills,
                "activate_skills": self.configuration.enable_activate_skills,
                "prestige": self.configuration.enable_auto_prestige,
                "daily_achievement_check": self.configuration.enable_daily_achievements,
                "milestone_check": self.configuration.enable_milestones,
                "raid_notifications": self.configuration.enable_raid_notifications,
                "clan_results_parse": self.configuration.enable_clan_results_parse,
                "update_stats": self.configuration.enable_stats,
                "breaks": self.configuration.enable_breaks
            }.items() if v
        ]

        self.logger.info("loop functions have been setup...")
        self.logger.info("{loop_funcs}".format(loop_funcs=", ".join(lst)))
        return lst

    @wrap_current_function
    def initialize(self):
        """
        Run any initial functions as soon as a session is started.
        """
        # Parse current skill levels, done once on initialization
        # and taken care of by our prestige function for every prestige.
        self.parse_current_skills()

        # Initial skill execution calculation, ensuring that all
        # skills with interval > 0 have a next execution datetime.
        self.calculate_next_skill_execution()

        # Conditionally checked for functions to run on session start.
        if self.configuration.master_level_on_start:
            self.level_master(force=True)
        if self.configuration.hero_level_on_start:
            self.level_heroes(force=True)
        if self.configuration.level_skills_on_start:
            self.level_skills(force=True)
        if self.configuration.activate_skills_on_start:
            self.activate_skills(force=True)
        if self.configuration.update_stats_on_start:
            self.update_stats(force=True)
        if self.configuration.daily_achievements_check_on_start:
            self.daily_achievement_check(force=True)
        if self.configuration.milestones_check_on_start:
            self.milestone_check(force=True)
        if self.configuration.parse_clan_results_on_start:
            self.clan_results_parse(force=True)
        if self.configuration.raid_notifications_check_on_start:
            self.raid_notifications(force=True)

    @wrap_current_function
    def run(self):
        """
        A run encapsulates the entire bot runtime process into a single function that conditionally
        checks for different things that are currently happening in the game, then launches different
        automated action within the emulator.
        """
        try:
            self.setup_shortcuts()
            self.goto_master()
            self.initialize()

            # Update the initial bots artifacts information that is used when upgrading
            # artifacts in game. This is handled after stats have been updated.
            self.owned_artifacts = self.get_upgrade_artifacts()

            if self.configuration.enable_artifact_purchase:
                self.next_artifact_index = 0
                self.update_next_artifact_upgrade()

            # Setup main game loop variables.
            loop_funcs = self.setup_loop_functions()

            # Generating an initial datetime that will be checked when the bot has been paused.
            # If this datetime is surpassed when the pause functionality is checked, a log will be sent.
            # Otherwise, we continue the loop normally.
            pause_log_dt = timezone.now() + datetime.timedelta(seconds=5)

            # Main game loop.
            while True:
                for func in loop_funcs:
                    # Any explicit functions can be executed after the main game loop has finished.
                    # The Queue handles the validation to ensure only available functions can be created...
                    for qfunc in Queue.objects.filter(instance=self.instance).order_by("-created"):
                        if qfunc.function not in QUEUEABLE_FUNCTIONS:
                            self.logger.info("queued function: {func} encountered but this function does not exist on the bot... ignoring function!".format(
                                func=qfunc.function))

                            qfunc.finish()
                            continue

                        self.logger.info("queued function: {func} will be executed!".format(func=qfunc.function))
                        # Executing the function directly on the Bot. We can force the function if it requires it to be ran manually.
                        wait = wait_afterwards(
                            function=getattr(self, qfunc.function),
                            floor=self.configuration.post_action_min_wait_time,
                            ceiling=self.configuration.post_action_max_wait_time
                        )

                        if qfunc.function in FORCEABLE_FUNCTIONS:
                            wait(force=True)
                        else:
                            wait()

                        qfunc.finish()

                    if self.TERMINATE:
                        self.logger.info("terminate signal encountered, exiting...")
                        raise TerminationEncountered()
                    if self.PAUSE:
                        now = timezone.now()
                        if now > pause_log_dt:
                            pause_log_dt = now + datetime.timedelta(seconds=10)
                            self.logger.info("waiting for resume...")

                        # PAUSED. Continue loop forever unless resumed/stopped.
                        continue

                    wait_afterwards(getattr(self, func), floor=self.configuration.post_action_min_wait_time, ceiling=self.configuration.post_action_max_wait_time)()

        except TerminationEncountered:
            self.logger.info("manual termination encountered... terminating!")
        except FailSafeException:
            self.logger.info("failsafe termination encountered: terminating!")
        except Exception as exc:
            self.logger.critical("critical error encountered: {exc}".format(exc=exc), exc_info=True)
            self.logger.info("terminating!")
            if self.configuration.soft_shutdown_on_critical_error:
                self.logger.info("soft shutdown is enabled on critical error... attempting to shutdown softly...")
                self.soft_shutdown()

        # Cleaning up the BotInstance once a termination has been received.
        finally:
            self.stats.session.end = timezone.now()
            self.stats.session.save()
            self.instance.stop()
            Queue.flush()

            # Cleanup the keyboard listener to no longer use callbacks.
            keyboard.unhook_all()

            self.logger.info("==========================================================================================")
            self.logger.info("{session}".format(session=self.stats.session))
            self.logger.info("==========================================================================================")

            # Remove logging handles.
            self.logger.handlers = []

            # Update the users authentication reference to no longer be online.
            AuthWrapper().offline()
