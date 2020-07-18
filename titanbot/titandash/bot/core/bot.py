from settings import (
    STAGE_CAP, BOT_VERSION, GIT_COMMIT, LOCAL_DATA_SCREENSHOTS_DIR
)

from django.utils import timezone
from django.db.models import Q

from titandash.models.queue import Queue
from titandash.models.tournament import Tournament, Participant
from titandash.constants import SKILL_MAX_LEVEL, PERK_CHOICES, NO_PERK, MEGA_BOOST

from titandash.bot.core import shortcuts

from titanauth.authentication.wrapper import AuthWrapper

from .maps import *
from .props import Props
from .grabber import Grabber
from .stats import Stats
from .wrap import DynamicAttrs
from .decorators import BotProperty as bot_property
from .decorators import not_in_transition, wait_afterwards
from .utilities import (
    click_on_point, click_on_image, drag_mouse, strfdelta,
    strfnumber, sleep, send_raid_notification, globals
)
from .constants import FUNCTION_LOOP_TIMEOUT, BOSS_LOOP_TIMEOUT
from .live import LiveConfiguration, LiveLogger

from pyautogui import FailSafeException

from apscheduler.schedulers.base import STATE_PAUSED, STATE_RUNNING, STATE_STOPPED
from apscheduler.schedulers.background import BackgroundScheduler

import datetime
import random
import uuid


class TerminationEncountered(Exception):
    """
    Basic exception raised when a termination is encountered while a bot session is running.
    """
    pass


class InvalidAuthenticationError(Exception):
    """
    Basic exception raised when an invalid authentication is found while a bot session is running.
    """
    pass


class Bot(object):
    """
    Main Bot Class.

    Initialization of the core "bot" object. Handling many core functions and setup steps at this point.

    Anything that requires an initial value or "flag" is handled here, once, when a new session is started within
    the Bot.__init__ method. Additionally, many variables are set at this point that are used throughout a sessions
    runtime.
    """
    def __init__(self,
                 configuration,
                 window,
                 enable_shortcuts,
                 instance,
                 start=False,
                 debug=False):

        self.ADVANCED_START = None
        self.TERMINATE = False
        self.PAUSE = False
        self.VALID_AUTHENTICATION = True
        self.PRESTIGE_STAGE_THRESHOLD = 3

        self._threshold_stage = 0
        self._threshold_max = 0
        self._threshold_percent = 0

        self.last_stage = None
        self.owned_artifacts = None
        self.next_artifact_index = None
        self.next_artifact_upgrade = None
        self.minigame_order = None
        self.enabled_perks = None
        self.scheduler = None
        self.authenticator = AuthWrapper()

        self.current_prestige_master_levelled = False
        self.current_prestige_skill_levels = {
            skill: 0 for skill in SKILLS
        }

        self.window = window
        self.enable_shortcuts = enable_shortcuts
        self.instance = instance
        self.instance.configuration = configuration
        self.instance.window = window.json()
        self.instance.shortcuts = enable_shortcuts

        self.configuration = LiveConfiguration(
            instance=self.instance,
            configuration=configuration,
        )
        self.logger = LiveLogger(
            instance=self.instance,
            configuration=self.configuration
        )
        # Data Containers.
        self.images = DynamicAttrs(
            attrs=IMAGES,
            logger=self.logger
        )
        self.locs = DynamicAttrs(
            attrs=GAME_LOCS,
            logger=self.logger
        )
        self.colors = DynamicAttrs(
            attrs=GAME_COLORS,
            logger=self.logger
        )
        self.props = Props(
            instance=self.instance
        )
        self.grabber = Grabber(
            window=self.window,
            logger=self.logger
        )
        self.stats = Stats(
            instance=self.instance,
            images=self.images,
            window=self.window,
            grabber=self.grabber,
            configuration=configuration,
            logger=self.logger.logger
        )

        self.instance.log = self.stats.session.log
        self.instance.start(session=self.stats.session)

        self.logger.info("==========================================================================================")
        self.logger.info("bot (v{version}) {git} has been initialized".format(
            version=BOT_VERSION, git="[{commit}]".format(
                commit=GIT_COMMIT[:10] if GIT_COMMIT else " ")
        ))
        self.logger.info("s: {session}".format(session=self.stats.session))
        self.logger.info("w: {window}".format(window=self.window))
        self.logger.info("c: LIVE: {configuration}".format(configuration=configuration))
        self.logger.info("==========================================================================================")

        if not debug:
            self.authenticator.online()

        self.calculate_minigames_order()
        self.calculate_enabled_perks()

        self.calculate_next_prestige()
        self.calculate_next_headgear_swap()
        self.calculate_next_perk_check()
        self.calculate_next_stats_update()
        self.calculate_next_master_level()
        self.calculate_next_heroes_level()
        self.calculate_next_skills_level()
        self.calculate_next_miscellaneous_actions()
        self.calculate_next_skills_activation()
        self.calculate_next_daily_achievement_check()
        self.calculate_next_milestone_check()
        self.calculate_next_raid_notifications_check()
        self.calculate_next_break()

        self.setup_scheduler()
        self.run(
            start=start
        )

    def click(self, point, clicks=1, interval=0.0, button="left", pause=0.0, offset=5):
        """
        Local click method for use with the bot, ensuring we pass the window being used into the click function.
        """
        click_on_point(
            point=point,
            window=self.window,
            clicks=clicks,
            interval=interval,
            button=button,
            pause=pause,
            offset=offset
        )

    def click_image(self, image, pos, button="left", pause=0.0):
        """
        Local image click method for use with the bot, ensuring we pass the window being used into the image click function.
        """
        click_on_image(
            window=self.window,
            image=image,
            pos=pos,
            button=button,
            pause=pause
        )

    def find_and_click(self, image, region=None, precision=0.8, button="left", pause=0.3, padding=None, log=None):
        """
        Local image find and click method for use with the bot. Allowing us to "fire and forget" to look for the image and click it.
        """
        found, position, found_image = self.grabber.search(
            image=image,
            region=region,
            precision=precision,
            return_image=True
        )

        # Is the image specified (or one of them), currently on the screen?
        if found:
            if log:
                self.logger.info(log)
            if not padding:
                self.click_image(
                    image=found_image,
                    pos=position,
                    button=button,
                    pause=pause
                )
            else:
                self.click(
                    point=(
                        position[0] + padding[0],
                        position[1] + padding[1]
                    ),
                    pause=pause
                )
            return True

        # The image wasn't found, return false for use with
        # any conditional checks within the bot.
        return False

    def drag(self, start, end, button="left", pause=0.5):
        """
        Local drag method for use with the bot, ensuring we pass the window being used into the drag function.
        """
        drag_mouse(
            start=start,
            end=end,
            window=self.window,
            button=button,
            pause=pause
        )

    @bot_property(queueable=True, tooltip="Reload and run functions that set local variables that are usually set once, this should be ran whenever a configuration is changed.")
    def reload(self):
        """
        Reload any variables that are "usually" generated initially when a bot is started.

        Looping through all of our properties that have been designated as "reload" functions,
        and executing them normally, this function should be called when information from the database has changed,
        ie: A configuration update.
        """
        self.logger.info("reloading bot variables now...")
        for prop in bot_property.reloads():
            getattr(self, prop["name"])()

    def setup_scheduler(self):
        """
        Setup the background scheduler object present on a bot instance, ensuring that jobs with defined
        intervals are successfully added to the scheduler.
        """
        self.scheduler = BackgroundScheduler()

        # Add each individual job to the background scheduler that should
        # happen every X seconds based on the interval present int he property.
        for prop in bot_property.intervals():
            self.scheduler.add_job(
                func=getattr(self, prop["name"]),
                seconds=prop["interval"],
                trigger="interval",
                id=prop["name"]
            )

    @bot_property(interval=180, wrap_name=False)
    def authenticate(self):
        """
        Attempt to authenticate the user currently attempting to start a bot instance.
        """
        if self.authenticator.authenticate_runner() is False:
            self.VALID_AUTHENTICATION = False

    @bot_property(queueable=True, reload=True, tooltip="Parse selected artifacts to upgrade, generating a list of artifacts that will be upgraded on prestige.")
    def get_upgrade_artifacts(self, testing=False):
        """
        Retrieve a list of all discovered/owned artifacts in game that will be iterated over
        and upgraded throughout runtime.

        The testing boolean is used to ignore the owned filter so all artifacts will be grabbed
        and can be tested thoroughly.
        """
        if not self.configuration.enable_artifact_purchase:
            self.logger.info("artifact purchase is disabled, artifact parsing is not required and will be skipped.")
            self.owned_artifacts = []
            return

        # Grabbing all configuration values used to determine which artifacts are upgraded when called.
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

        if len(artifacts) == 0:
            self.logger.error("no owned artifacts were found... parsed artifacts must be present before starting a session.")
            self.logger.info("attempting to force artifacts parse now...")

            # Perform an automatic artifact parsing process.
            # Afterwards, we can safely run our function again
            # to set the owned artifacts properly.
            self.parse_artifacts()
            self.get_upgrade_artifacts()

            if not self.owned_artifacts:
                self.logger.error("no artifacts were parsed or none are selected that are currently owned. artifact purchasing will be disabled for this session.")
                self.configuration.enable_artifact_purchase = False
                self.owned_artifacts = []
                return

        lst = list(artifacts.exclude(
            # Combining the max level artifacts and ignore artifacts specified.
            # We must coerce to list to extend.
            artifact__name__in=list(ARTIFACT_WITH_MAX_LEVEL) + list(ignore_artifacts)
        ).filter(
            Q(artifact__tier__tier__in=upgrade_tiers) |
            Q(artifact__name__in=upgrade_artifacts)
        ).values_list("artifact__name", flat=True))

        # Perform truthy check on the "lst" of artifacts validated
        # and enabled for purchase.
        if lst:
            # Shuffle list to add some randomness to artifacts
            # purchased throughout each prestige.
            if self.configuration.shuffle_artifacts:
                random.shuffle(lst)

            # Set bot level owned artifacts variable
            # (only if lst contains elements).
            self.owned_artifacts = lst
        else:
            self.owned_artifacts = []

    @bot_property(queueable=True, tooltip="Update the next artifact that will be upgraded on prestige.")
    def update_next_artifact_upgrade(self):
        """
        Update the next artifact to be upgraded to the next one in the list.
        """
        if self.owned_artifacts:
            if self.next_artifact_index == len(self.owned_artifacts):
                self.next_artifact_index = 0

            self.next_artifact_upgrade = self.owned_artifacts[self.next_artifact_index]
            self.next_artifact_index += 1

            self.instance.next_artifact_upgrade = self.next_artifact_upgrade
            self.instance.save()

            self.logger.info("next artifact upgrade: {artifact}".format(artifact=self.next_artifact_upgrade))

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
            self.logger.warning("text: {text}".format(text=stage_text))
            self.ADVANCED_START = None
        except TypeError:
            self.logger.warning("ocr check could not be coerced properly into an integer, resetting advanced start value...")
            self.logger.warning("text: {text}".format(text=stage_text))
            self.ADVANCED_START = None

    @bot_property(interval=3, wrap_name=False)
    def parse_current_stage(self):
        """
        Attempt to update the current stage attribute through an OCR check in game. The current_stage
        attribute is initialized as None, and if the current stage parsed here is unable to be coerced into
        an integer, it will be set back to None.

        When using the attribute, a check should be performed to ensure it isn't None before running
        numeric friendly conditionals.

        Note, we do not wrap our current function implementation since we use this function
        through our background scheduler implementation.
        """
        try:
            stage = int(self.stats.stage_ocr())
            if stage > STAGE_CAP:
                return
            if self.ADVANCED_START and stage < self.ADVANCED_START:
                return

            self.last_stage = self.props.current_stage
            self.props.current_stage = stage

        # ValueError when the parsed stage isn't able to be coerced.
        except ValueError:
            pass

    @bot_property(queueable=True, reload=True, tooltip="Calculate the enabled minigames as well as the order they are executed.")
    def calculate_minigames_order(self):
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
        if self.configuration.enable_forbidden_contract:
            minigames.append("forbidden_contract")
        if self.configuration.enable_summon_dagger:
            minigames.append("summon_dagger")

        self.minigame_order = minigames

    @bot_property(queueable=True, reload=True, tooltip="Calculate the enabled perks that are used when using perks.")
    def calculate_enabled_perks(self):
        """
        Retrieve a list of all enabled perks based on the configuration specified.
        """
        enabled_perks = []

        for perk in PERK_CHOICES:
            if perk[0] != NO_PERK:
                if getattr(self.configuration, "enable_{key}".format(key=perk[0]), False):
                    enabled_perks.append(perk[0])

        self.enabled_perks = enabled_perks

    def _calculate(self, attr, interval=None, dt=None, log=True):
        """
        Base calculation method for any bot functions that should be ran on an interval configured by the user or bot.
        """
        if interval and dt:
            raise ValueError("Only one of 'interval' or 'dt' should be present, but not both.")

        # Calculate current datetime for use with interval based
        # datetimes, the timestamp is also used if a log is outputted.
        now = timezone.now()

        # Interval based calculations require an interval to be specified
        # in seconds only.
        if interval is not None:
            dt = now + datetime.timedelta(
                seconds=interval
            )

        # Props.attr = dt
        setattr(self.props, attr, dt)

        if log:
            self.logger.info("{attr} should be executed in {time}".format(attr=attr, time=strfdelta(timedelta=(dt - now))))

    @bot_property(queueable=True, tooltip="Calculate the next time that skills will be executed at.")
    def calculate_next_skill_execution(self, skill=None):
        """
        Calculate the datetimes that are attached to each skill in game and when they should be activated.
        """
        calculating = SKILLS if not skill else [skill]
        interval_key = "interval_{skill}"
        next_key = "next_{skill}"

        # Loop through all available skills and update their next execution
        # time as long as the interval is set to a value other than 0.
        for skill in calculating:
            interval = getattr(self.configuration, interval_key.format(skill=skill), 0)
            if interval != 0:
                self._calculate(
                    attr=next_key.format(skill=skill),
                    interval=interval
                )

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
                if timezone.now() > self.props.next_randomized_prestige:
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
        now = timezone.now()

        if self.configuration.prestige_x_minutes != 0:
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
                    self._threshold_stage += 1
                    self.logger.info("prestige at specific stage threshold: {current}/{needed}".format(current=self._threshold_stage, needed=self.PRESTIGE_STAGE_THRESHOLD))
                    if self._threshold_stage >= self.PRESTIGE_STAGE_THRESHOLD:
                        self.logger.info("prestige stage has been reached, prestige will happen now.")
                        ready = True
                else:
                    self._threshold_stage = 0

            # These conditionals are dependant on the highest stage reached taken
            # from the bot's current game statistics.
            elif self.configuration.prestige_at_max_stage:
                self.logger.info("prestige at max stage: {current}/{needed}.".format(current=strfnumber(self.props.current_stage), needed=strfnumber(self.stats.highest_stage)))
                if self.props.current_stage >= self.stats.highest_stage:
                    self._threshold_max += 1
                    self.logger.info("prestige at max stage threshold: {current}/{needed}".format(current=self._threshold_max, needed=self.PRESTIGE_STAGE_THRESHOLD))
                    if self._threshold_max >= self.PRESTIGE_STAGE_THRESHOLD:
                        self.logger.info("max stage has been reached, prestige will happen now.")
                        ready = True
                else:
                    self._threshold_max = 0

            elif self.configuration.prestige_at_max_stage_percent != 0:
                percent = float(self.configuration.prestige_at_max_stage_percent) / 100
                threshold = int(self.stats.highest_stage * percent)
                self.logger.info("prestige at max stage percent ({percent}): {current}/{needed}".format(percent=percent, current=strfnumber(self.props.current_stage), needed=strfnumber(threshold)))
                if self.props.current_stage >= threshold:
                    self._threshold_percent += 1
                    self.logger.info("prestige at max stage percent threshold: {current}/{needed}".format(current=self._threshold_percent, needed=self.PRESTIGE_STAGE_THRESHOLD))
                    if self._threshold_percent >= self.PRESTIGE_STAGE_THRESHOLD:
                        self.logger.info("percent of max stage has been reached, prestige will happen now.")
                        ready = True
                else:
                    self._threshold_percent = 0

        # Using threshold randomization to ensure that prestiges are quite random.
        if ready:
            # Ensure we reset our threshold flags back to zero once a prestige
            # is "ready". Next time we check for prestige, these are back at zero.
            self._threshold_stage = 0
            self._threshold_max = 0
            self._threshold_percent = 0

            if self.configuration.enable_prestige_threshold_randomization:
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

    @bot_property(queueable=True, tooltip="Calculate the next time that the prestige process will take place.")
    def calculate_next_prestige(self):
        """
        Calculate when the next timed prestige will take place.
        """
        self._calculate(
            attr="next_prestige",
            interval=self.configuration.prestige_x_minutes * 60
        )

    @bot_property(queueable=True, tooltip="Calculate the next time that headgear swap will take place.")
    def calculate_next_headgear_swap(self):
        """
        Calculate when the next timed headgear swap will take place.
        """
        self._calculate(
            attr="next_headgear_swap",
            interval=self.configuration.headgear_swap_every_x_seconds
        )

    @bot_property(queueable=True, tooltip="Calculate the next time that a perk check will take place.")
    def calculate_next_perk_check(self):
        """
        Calculate when the next timed perk check will take place.
        """
        if self.configuration.enable_perk_usage:
            if self.configuration.enable_perk_only_tournament:
                return

            self._calculate(
                attr="next_perk_check",
                interval=self.configuration.use_perks_every_x_hours * 60 * 60
            )

    @bot_property(queueable=True, tooltip="Calculate the next time that the master level process will take place.")
    def calculate_next_master_level(self):
        """
        Calculate when the next sword master levelling process will be ran.
        """
        self._calculate(
            attr="next_master_level",
            interval=self.configuration.master_level_every_x_seconds
        )

    @bot_property(queueable=True, tooltip="Calculate the next time that the heroes level process will take place.")
    def calculate_next_heroes_level(self):
        """
        Calculate when the next heroes level process will be ran.
        """
        self._calculate(
            attr="next_heroes_level",
            interval=self.configuration.hero_level_every_x_seconds
        )

    @bot_property(queueable=True, tooltip="Calculate the next time that the skills level process will take place.")
    def calculate_next_skills_level(self):
        """
        Calculate when the next skills level process will be ran.
        """
        self._calculate(
            attr="next_skills_level",
            interval=self.configuration.level_skills_every_x_seconds
        )

    @bot_property(queueable=True, tooltip="Calculate the next time that the miscellaneous actions will take place.")
    def calculate_next_miscellaneous_actions(self):
        """
        Calculate when the next miscellaneous function process will be ran.
        """
        self._calculate(
            attr="next_miscellaneous_actions",
            interval=900
        )

    @bot_property(queueable=True, tooltip="Calculate the next time that the skills activation process will take place.")
    def calculate_next_skills_activation(self):
        """
        Calculate when the next skills activation process will be ran.
        """
        self._calculate(
            attr="next_skills_activation",
            interval=self.configuration.activate_skills_every_x_seconds
        )

    @bot_property(queueable=True, tooltip="Calculate the next time a statistics update will take place.")
    def calculate_next_stats_update(self):
        """
        Calculate when the next stats update should take place.
        """
        self._calculate(
            attr="next_stats_update",
            interval=self.configuration.update_stats_every_x_minutes * 60
        )

    @bot_property(queueable=True, tooltip="Calculate the next time a daily achievement check will take place")
    def calculate_next_daily_achievement_check(self):
        """
        Calculate when the next daily achievement check should take place.
        """
        self._calculate(
            attr="next_daily_achievement_check",
            interval=self.configuration.daily_achievements_check_every_x_hours * 60 * 60
        )

    @bot_property(queueable=True, tooltip="Calculate the next time a milestone check will take place.")
    def calculate_next_milestone_check(self):
        """
        Calculate when the next milestone check should take place.
        """
        self._calculate(
            attr="next_milestone_check",
            interval=self.configuration.milestones_check_every_x_hours * 60 * 60
        )

    @bot_property(queueable=True, tooltip="Calculate the next time raid notification check will take place.")
    def calculate_next_raid_notifications_check(self):
        """
        Calculate when the next raid notifications check should take place.
        """
        self._calculate(
            attr="next_raid_notifications_check",
            interval=self.configuration.raid_notifications_check_every_x_minutes * 60
        )

    @bot_property(queueable=True, tooltip="Calculate the next time a break will take place.")
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

            self._calculate(
                attr="next_break",
                dt=next_break_dt,
                log=False
            )
            self._calculate(
                attr="resume_from_break",
                dt=next_break_res,
                log=False
            )

            # Using a custom log message to ensure proper, readable information is outputted
            # about the current breaks datetimes.
            self.logger.info("the next in game break will take place in {time_1} and resume in {time_2}".format(
                time_1=strfdelta(next_break_dt - now),
                time_2=strfdelta(next_break_res - now)
            ))

    @not_in_transition
    @bot_property(forceable=True, shortcut="shift+h", tooltip="Level heroes in game.")
    def level_heroes(self, force=False):
        """
        Perform all actions related to the levelling of all heroes in game.
        """
        if self.configuration.enable_heroes:
            if force or timezone.now() > self.props.next_heroes_level:
                self.logger.info("{begin_force} heroes levelling process in game now.".format(begin_force="beginning" if not force else "forcing"))

                if not self.goto_heroes(collapsed=False):
                    return False

                # A quick check can be performed to see if the top of the heroes panel contains
                # a hero that is already max level, if this is the case, it's safe to assume
                # that all heroes below have been maxed out. Instead of scrolling and levelling
                # all heroes, just level the top heroes.
                if self.grabber.search(self.images.max_level, bool_only=True):
                    self.logger.info("a max levelled hero has been found! Only first set of heroes will be levelled.")
                    for point in HEROES_LOCS["level_heroes"][::-1][1:]:
                        self.click(
                            point=point,
                            clicks=self.configuration.hero_level_intensity,
                            interval=0.07
                        )

                    # Early exit as well.
                    self.calculate_next_heroes_level()
                    self.parse_newest_hero()
                    return True

                self.logger.info("levelling the first set of heroes available...")
                # Always level the first set of heroes in the list.
                # HEROES_LOCS "level_heroes" is a tuple of coords.
                # [::-1] reverses out set of tuples.
                # [1:] skips the first index present in the reversed list.
                for point in HEROES_LOCS["level_heroes"][::-1][1:]:
                    self.click(
                        point=point,
                        clicks=self.configuration.hero_level_intensity,
                        interval=0.07
                    )

                # Travel to the bottom of the panel.
                for i in range(6):
                    self.drag(
                        start=self.locs.scroll_start,
                        end=self.locs.scroll_bottom_end
                    )

                    # Have we found any max level heroes yet?
                    if self.grabber.search(image=self.images.max_level, bool_only=True):
                        self.logger.info("a max levelled hero has been found! levelling heroes now.")
                        break

                drag_start = HEROES_LOCS["drag_heroes"]["start"]
                drag_end = HEROES_LOCS["drag_heroes"]["end"]

                # Begin level and scrolling process. An assumption is made that all heroes
                # are unlocked, meaning that some un-necessary scrolls may take place.
                self.logger.info("scrolling and levelling all heroes present.")

                _loops = 0
                _last = self.grabber.snapshot(region=PANEL_COORDS["panel_check"])
                _current = _last

                while True:
                    if _loops == FUNCTION_LOOP_TIMEOUT:
                        self.logger.warning("reached limit allowed for hero levelling, finishing now...")
                        break

                    _loops += 1

                    for point in HEROES_LOCS["level_heroes"]:
                        self.click(
                            point=point,
                            clicks=self.configuration.hero_level_intensity,
                            interval=0.07
                        )

                    self.logger.info("dragging hero panel to next set of heroes...")
                    self.drag(
                        start=drag_start,
                        end=drag_end,
                        pause=2
                    )

                    _last = _current
                    _current = self.grabber.snapshot(region=PANEL_COORDS["panel_check"])

                    if self.stats.images_duplicate(image_one=_last, image_two=_current):
                        break

                # Performing one additional heroes level after the top
                # has been reached...
                for point in HEROES_LOCS["level_heroes"]:
                    self.click(
                        point=point,
                        clicks=self.configuration.hero_level_intensity,
                        interval=0.07
                    )

                # Recalculate the next heroes level process.
                self.calculate_next_heroes_level()
                self.parse_newest_hero()
                return True

    @not_in_transition
    @bot_property(forceable=True, shortcut="shift+m", tooltip="Level sword master in game.")
    def level_master(self, force=False):
        """
        Perform all actions related to the levelling of the sword master in game.
        """
        if self.configuration.enable_master:
            if force or timezone.now() > self.props.next_master_level:
                self.logger.info("{begin_force} master levelling process in game now.".format(begin_force="beginning" if not force else "forcing"))

                # Creating base "level" flag. Since master levelling can be configured to either take place
                # every x seconds, or once per prestige, we determine once based on prestige settings.
                level = True
                # Levelling sword master once when a prestige takes place.
                if self.configuration.master_level_only_once:
                    if self.current_prestige_master_levelled:
                        level = False
                    else:
                        self.logger.info("levelling the sword master once until the next prestige...")
                        self.current_prestige_master_levelled = True

                # Levelling the sword master every x seconds.
                else:
                    self.logger.info("levelling the sword master {clicks} time(s)".format(clicks=self.configuration.master_level_intensity))

                # Only actually executing the level process when our level boolean is true.
                if level:
                    # Travel to the master panel to allow the levelling up of our sword master.
                    if not self.goto_master(collapsed=False):
                        return False

                    # Level our sword master given the specified amount of clicks
                    # through the users configuration.
                    self.click(
                        point=MASTER_LOCS["master_level"],
                        clicks=self.configuration.master_level_intensity
                    )

                # Recalculate the next sword master level process.
                self.calculate_next_master_level()
                return True

    @not_in_transition
    @bot_property(queueable=True, tooltip="Parse out the newest hero in game, that contains a non zero dps value.")
    def parse_newest_hero(self):
        """
        Attempting to parse information from the screen about the newest hero and whether or not
        the damage type has changed. This can be used to properly enable and disable the switching
        of head gear to support a users strongest hero during a run.
        """
        if self.configuration.enable_headgear_swap:
            if not self.goto_heroes(collapsed=False):
                return False

            old = None
            # Grab the newest hero information
            if self.props.newest_hero:
                old = self.props.newest_hero

            # Let's attempt to grab the first hero with a dps value from the list of heroes.
            # We can determine what "type" this hero is, and store the value.
            self.props.newest_hero = self.stats.get_first_hero_information()

            if old and self.props.newest_hero and old != self.props.newest_hero:
                self.logger.info("new highest level hero has been found: {hero}".format(hero=self.props.newest_hero))

    @not_in_transition
    @bot_property(queueable=True, tooltip="Parse out current in game skill levels.")
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
            self.current_prestige_skill_levels[skill] = self.stats.skill_ocr(
                region=SKILL_LEVEL_COORDS[skill]
            )
            self.logger.info("{skill} parsed as level {level}".format(skill=skill, level=self.current_prestige_skill_levels[skill]))

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

    @not_in_transition
    @bot_property(forceable=True, shortcut="shift+s", tooltip="Level skills in game.")
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
            self.click(
                point=point,
                clicks=clicks,
                interval=0.3,
                pause=1,
            )

            # Should the skill in question be levelled to it's maximum amount available?
            if max_skill:
                if self.grabber.point_is_color(point=color, color=self.colors.WHITE):
                    self.click(
                        point=color,
                        pause=0.5
                    )

        def can_level(key):
            """
            Check to see if a skill can currently be levelled or not.
            """
            return not self.grabber.point_is_color(point=SKILL_CAN_LEVEL_LOCS[key], color=self.colors.SKILL_CANT_LEVEL)

        def active(key):
            """
            Check to see if a skill is currently active or not.
            """
            return self.grabber.search(image=self.images.cancel_active_skill, region=MASTER_COORDS["skills"][key], bool_only=True)

        # Actual skill levelling process begins here.
        if self.configuration.enable_level_skills:
            if force or timezone.now() > self.props.next_skills_level:
                self.logger.info("{begin_force} skills levelling process in game now.".format(begin_force="beginning" if not force else "forcing"))

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
                            level_skill(
                                key=skill,
                                max_skill=True
                            )

                        # Otherwise, we want to level the current skill upto the
                        # cap set by our user.
                        else:
                            level_skill(
                                key=skill,
                                clicks=values["remaining"]
                            )

                        # After we have levelled our skill to it's appropriate values.
                        # We need to perform an OCR check on the skill in it's current state
                        # so that our current prestige level information is up to date.
                        if self.grabber.search(image=self.images.skill_max_level, region=MASTER_COORDS["skills"][skill], bool_only=True):
                            self.logger.info("skill: {skill} is currently maxed, setting to {max_level}".format(skill=skill, max_level=SKILL_MAX_LEVEL))
                            self.current_prestige_skill_levels[skill] = SKILL_MAX_LEVEL
                        else:
                            self.current_prestige_skill_levels[skill] = self.stats.skill_ocr(
                                region=SKILL_LEVEL_COORDS[skill]
                            )

                # Recalculate the next skill level process.
                self.calculate_next_skills_level()
                return True

    @not_in_transition
    @bot_property(forceable=True, shortcut="ctrl+a", tooltip="Force a skill activation in game.")
    def activate_skills(self, force=False):
        """
        Activate in game skills.

        Based on our available skills (not disabled), we can determine whether or not we should activate certain
        skills.

        We also only want to activate skills based on the interval chosen by the user.

        If chosen, skills should also wait to be activated until the longest interval is reached.
        """
        if self.configuration.enable_activate_skills:
            if force or timezone.now() > self.props.next_skills_activation:
                self.logger.info("{begin_force} skills activation process in game now.".format(begin_force="beginning" if not force else "forcing"))

                # Skill activation will take place now, we need to determine whether or not any skills
                # are enabled and ready to be activated.
                enabled = self.enabled_skills()
                # If we have enabled skills, begin our loop to activate them
                # if the intervals are correct.
                if enabled:
                    self.ensure_no_panel()
                    next_key = "next_{skill}"

                    # Looping through each skill that's enabled to be activated.
                    # Some skills are disabled based on their interval.
                    for skill in self.enabled_skills():
                        prop = getattr(self.props, next_key.format(skill=skill))

                        # Is this skill ready to be activated?
                        if force or timezone.now() > prop:
                            self.logger.info("activating {skill} now...".format(skill=skill))
                            self.click(
                                point=getattr(self.locs, skill),
                                clicks=3,
                                pause=0.2
                            )
                            self.calculate_next_skill_execution(skill=skill)
                        else:
                            self.logger.info("{skill} will be activated in {time}".format(skill=skill, time=strfdelta(prop - timezone.now())))

                # Recalculate the next skill activation process.
                self.calculate_next_skills_activation()
                return True

    @not_in_transition
    def use_perk(self, perk):
        """
        Attempt to use or purchase the specified perk in game.

        Based on the users configuration, we may or may not use the perk if the user does
        not own one currently.
        """
        self.logger.info("attempting to use {perk} perk.".format(perk=perk))
        # We also travel to the bottom of the expanded master panel for each purchase, since some
        # perks may close the panel after activation.
        self.goto_master(collapsed=False, top=False)

        perk_image = getattr(self.images, "perks_{perk}".format(perk=perk))
        # Dragging until perk is on the screen.
        while not self.grabber.search(image=perk_image, bool_only=True):
            self.drag(
                start=self.locs.scroll_start,
                end=self.locs.scroll_top_end,
            )

        # Dynamically derive the point that will be used to click on the
        # current perk.
        found, position = self.grabber.search(image=perk_image)

        # Add our proper padding amounts to the perk image found.
        # ensuring that the point is on the "use" button for the perk.
        click_point = (
            position[0] + PERK_LOCS["perk_push"]["x"],
            position[1] + PERK_LOCS["perk_push"]["y"]
        )

        # Our mega boost perk currently functions differently then the other
        # perks present and available.
        if perk == MEGA_BOOST:
            # Do we have our vip option unlocked to activate this perk?
            if self.grabber.search(image=[self.images.perks_vip_watch, self.images.perks_pass_watch], bool_only=True):
                # Just activate the perk.
                self.logger.info("using {perk} with vip now...".format(perk=perk))
                self.click(
                    point=click_point,
                    pause=1
                )
            # Otherwise, we need to check to see if we can collect the perk with our
            # pi hole ad settings, otherwise, this perk may not be activated.
            else:
                if globals.pihole_ads():
                    self.logger.info("attempting to use {perk} through pi hole now...".format(perk=perk))
                    self.click(
                        point=click_point,
                        pause=1
                    )
                    # If our perk header is now present, we can loop and wait until it's disappeared,
                    # which would represent the ad being finished and the perk being activated.
                    if self.grabber.search(image=self.images.perk_header, bool_only=True):
                        while self.grabber.search(image=self.images.perk_header, bool_only=True):
                            self.click(
                                point=self.locs.perks_okay,
                                pause=2
                            )
                            self.logger.info("waiting for pi hole to finish ad...")
                        # Out of while loop, means the ad has been collected successfully.
                        self.logger.info("{perk} has been successfully used.".format(perk=perk))

        else:
            # Attempting to open the purchase panel for this perk.
            # If it is already active, no window will be opened, which we
            # can use to determine whether or not to continue.
            self.click(
                point=click_point,
                pause=1
            )

            if not self.grabber.search(image=self.images.perks_header, bool_only=True):
                self.logger.info("unable to open {perk} purchase panel, it's probably already active...".format(perk=perk))
                return True

            # Check for the diamond icon in the opened window,
            # based on it being present or not, we can choose to either
            # purchase the perk or not.
            if self.grabber.search(image=self.images.perks_diamond, region=PERK_COORDS["purchase"], bool_only=True):
                if self.configuration.enable_perk_diamond_purchase:
                    self.logger.info("purchasing {perk} now.".format(perk=perk))
                    return self.click(
                        point=self.locs.perks_okay,
                        pause=1
                    )
                else:
                    self.logger.info("{perk} requires diamonds to use, this is disabled currently, skipping...".format(perk=perk))
                    return self.click(
                        point=self.locs.perks_cancel,
                        pause=1
                    )

            # Otherwise, go ahead with normal perk purchase.
            self.logger.info("using {perk} now.".format(perk=perk))
            return self.click(
                point=self.locs.perks_okay,
                pause=1
            )

    @not_in_transition
    @bot_property(forceable=True, shortcut="shift+c", tooltip="Force a perk check in game.")
    def perks(self, force=False):
        """
        Perform the periodic perks usage function.

        This only ever happens if the interval has been surpassed. This interval is also only ever set
        if the user has disabled the ability to check for perks outside of the tournament perk functionality.
        """
        if self.configuration.enable_perk_usage:
            if self.configuration.enable_perk_only_tournament and not force:
                return False

            if self.props.next_perk_check:
                if force or timezone.now() > self.props.next_perk_check:
                    self.logger.info("{force_or_initiate} perks check now.".format(force_or_initiate="forcing" if force else "beginning"))
                    # Travel to the bottom of the master panel, expanded so we
                    # can view all of the perks in game.
                    self.goto_master(collapsed=False, top=False)

                    # Looping through enabled perks in game, attempting to use each one.
                    for perk in self.enabled_perks:
                        self.use_perk(
                            perk=perk
                        )

                    self.calculate_next_perk_check()
                    return True

    @not_in_transition
    @bot_property(forceable=True, shortcut="shift+u", tooltip="Force a statistics update in game.")
    def update_stats(self, force=False):
        """
        Update the bot stats by travelling to the stats page in the heroes panel and performing OCR update.
        """
        if self.configuration.enable_stats:
            if force or timezone.now() > self.props.next_stats_update:
                self.logger.info("{force_or_initiate} in game statistics update now.".format(force_or_initiate="forcing" if force else "beginning"))
                # Leaving boss fight here so that a stage transition does not take place
                # in the middle of a stats update.
                if not self.leave_boss():
                    return False

                # Sleeping slightly before attempting to goto top of heroes panel so that new hero
                # levels doesn't cause the 'top' of the panel to disappear after travelling.
                sleep(2)
                if not self.goto_heroes():
                    return False

                # Ensure we are at the top of the stats screen while collapsed.
                while not self.grabber.search(self.images.stats, bool_only=True):
                    self.drag(
                        start=self.locs.scroll_start,
                        end=self.locs.scroll_top_end
                    )
                # Ensure the stats panel has been opened before continuing.
                while not self.grabber.search(self.images.stats_title, bool_only=True):
                    self.click(
                        point=HEROES_LOCS["stats_collapsed"],
                        pause=1
                    )

                # Scrolling to the bottom of the stats panel.
                sleep(1)
                for i in range(5):
                    self.drag(
                        start=self.locs.scroll_start,
                        end=self.locs.scroll_bottom_end
                    )

                self.stats.update_stats_ocr()
                self.stats.statistics.bot_statistics.updates += 1
                self.stats.statistics.bot_statistics.save()

                self.calculate_next_stats_update()
                self.click(
                    point=MASTER_LOCS["screen_top"],
                    clicks=3
                )

    @not_in_transition
    @bot_property(forceable=True, shortcut="shift+p", tooltip="Force a prestige in game.")
    def prestige(self, force=False):
        """
        Perform a prestige in game.
        """
        if self.configuration.enable_auto_prestige:
            if self.should_prestige() or force:
                self.logger.info("{begin_force} prestige process in game now.".format(begin_force="beginning" if not force else "forcing"))

                # Leaving boss fight if one is available, and waiting slightly to ensure out current
                # stage is up to date before we begin the prestige.
                self.leave_boss()
                sleep(5)

                # Pausing our scheduler while a prestige is taking place.
                # We do not want the current stage being modified while this takes place.
                if self.scheduler.state == STATE_RUNNING:
                    self.scheduler.pause()

                # Reset any bot properties that are prestige specific.
                self.props.newest_hero = None

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

                # Perform a tournament check, if a user has tournaments enabled, we will perform the normal
                # prestige process in this function instead of below, which means we can set some values and exit early
                # if a tournament is available and was joined.
                tournament_prestige, advanced_start = self.check_tournament()

                if tournament_prestige:
                    # Tournament would have handled the prestige generation, set last prestige
                    # and our correct advanced start parsing.
                    self.props.last_prestige = tournament_prestige
                    self.parse_advanced_start(stage_text=advanced_start)
                    self.props.current_stage = advanced_start or 0
                    # Sleeping explicitly if a tournament was joined, since we update the last
                    # prestige and advanced start right after it happens.
                    sleep(35)

                    if self.scheduler.state == STATE_PAUSED:
                        self.scheduler.resume()

                    # If we have chosen to only use perks when a tournament takes place,
                    # we perform that here.
                    if self.configuration.enable_perk_usage:
                        if self.configuration.enable_perk_only_tournament:
                            for perk in self.enabled_perks:
                                self.use_perk(
                                    perk=perk
                                )

                    return True

                # Performing the base prestige functionality, no tournament is available to join.
                if not self.goto_master():
                    return False

                # Click on the prestige button, and check for the prompt confirmation being present. Sleeping
                # slightly here to ensure that connections issues do not cause the prestige to be misfire.
                self.click(
                    point=MASTER_LOCS["prestige"],
                    pause=3
                )
                prestige_found, prestige_position = self.grabber.search(self.images.confirm_prestige)
                if prestige_found:
                    # Parsing the advanced start value that is present before a prestige takes place...
                    # This is used to improve stage parsing to not allow values < the advanced start value.
                    # Also handling the prestige generation here, which is set on our instance.
                    prestige, advanced_start = self.stats.update_prestige(
                        artifact=self.next_artifact_upgrade,
                        current_stage=self.props.current_stage
                    )
                    self.props.last_prestige = prestige
                    self.parse_advanced_start(stage_text=advanced_start)
                    self.props.current_stage = self.ADVANCED_START

                    # Click on the prestige confirmation box.
                    self.click_image(
                        image=self.images.confirm_prestige,
                        pos=prestige_position,
                        pause=1
                    )
                    # Waiting for a while after prestiging, this reduces the chance
                    # of a game crash taking place due to many clicks while game is resetting.
                    prestige_final_found, prestige_final_position = self.grabber.search(image=self.images.confirm_prestige_final)
                    self.click_image(
                        image=self.images.confirm_prestige_final,
                        pos=prestige_final_position,
                        pause=35
                    )

                    if self.scheduler.state == STATE_PAUSED:
                        self.scheduler.resume()

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

                    # Once our prestige has finished, let's check if we should
                    # activate one of the perks chosen.
                    if self.configuration.enable_perk_usage:
                        if self.configuration.use_perk_on_prestige != NO_PERK:
                            self.use_perk(
                                perk=self.configuration.use_perk_on_prestige
                            )

                    # If the current stage currently is greater than the current max stage, lets update our stats
                    # to reflect that a new max stage has been reached. This allows for
                    if self.props.current_stage and self.stats.highest_stage:
                        if self.props.current_stage > self.stats.highest_stage:
                            self.logger.info("current stage is greater than your previous max stage {max}, forcing a stats update to reflect new max stage.".format(max=self.stats.highest_stage))
                            self.update_stats(force=True)

    @not_in_transition
    @bot_property(forceable=True, tooltip="Force a headgear swap in game, based on the newest hero that has been parsed.")
    def swap_headgear(self, force=False):
        """
        Attempt to swap the users headgear to match the newest hero's damage type.

        For example, if our newest hero is a "melee" type hero, we can open up our equipment panel, and attempt
        to equip the users "locked" melee type weapon.

        For this to work, users must ensure that only three headgear equipments are locked within their game.
        """
        if self.configuration.enable_headgear_swap:
            if force or timezone.now() > self.props.next_headgear_swap:
                self.logger.info("{force_or_initiate} headgear swap process in game now.".format(force_or_initiate="forcing" if force else "beginning"))

                self.parse_newest_hero()
                self.props.current_function = self.swap_headgear.__name__

                # If no actual new hero is available, attempt to parse out the newest hero once
                # before giving up.
                if not self.props.newest_hero:
                    self.logger.info("no newest hero is currently present, skipping headgear swap...")
                    self.calculate_next_headgear_swap()
                    return True

                # We must travel to the equipment panel at this point.
                # Then we can also open up the headgear panel.
                if not self.goto_equipment(collapsed=False, top=True, tab="headgear"):
                    return False

                # Search for any of our locked equipment that matches the newest
                # parsed hero. Swapping headgear if available.
                newest_hero = self.props.newest_hero
                found, point = self.stats.get_first_gear_of(typ=newest_hero)

                # No headgear could be found for the newest hero's type?
                # Quit early.
                if not found:
                    self.logger.warning("no locked headgear of type: {typ} could be found, skipping headgear swap...".format(typ=newest_hero))
                    self.calculate_next_headgear_swap()
                    return False

                # Gear index has been found, based on this, we can equip the gear now
                # by using the index to determine the "equip" buttons location.
                if isinstance(point, tuple):
                    self.logger.info("headgear of type: {typ} was found, equipping now!".format(typ=newest_hero))
                    self.click(
                        point=point,
                        pause=1
                    )
                else:
                    if point == "EQUIPPED":
                        self.logger.info("headgear of type: {typ} is already equipped, skipping headgear swap...".format(typ=newest_hero))

                self.calculate_next_headgear_swap()
                return True

    @not_in_transition
    @bot_property(queueable=True, tooltip="Attempt to parse all artifacts from in game.")
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

    @not_in_transition
    @bot_property(queueable=True, shortcut="shift+a", tooltip="Begin the artifact discover/enchant/purchase process in game.")
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
                    self.click(
                        point=point,
                        pause=1
                    )
                    self.click(
                        point=self.locs.purchase,
                        pause=2
                    )
                    self.click(
                        point=self.locs.close_top,
                        clicks=5,
                        interval=0.5,
                        pause=2
                    )

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

            # Ensure no artifact available just skips the current
            # artifact purchase.
            if artifact is None:
                self.logger.info("no artifact to upgrade, skipping purchase...")
                return
            
            # Access to current upgrade is present above,
            # go ahead and update the next artifact to purchase.
            self.update_next_artifact_upgrade()
            self.logger.info("attempting to upgrade {artifact} now.".format(artifact=artifact))

            # Make sure that the proper spend max multiplier is used to fully upgrade an artifact.
            # 1.) Ensure that the percentage (%) multiplier is selected.
            while not self.grabber.search(self.images.percent_on, bool_only=True, precision=0.9):
                self.logger.info("turning percent toggle on for artifact purchase...")
                self.click(
                    point=ARTIFACTS_LOCS["percent_toggle"],
                    pause=0.5
                )

            # 2.) Ensure that the SPEND Max multiplier is selected.
            while not self.grabber.search(self.images.spend_max, bool_only=True, precision=0.9):
                self.logger.info("turning spend max on in buy multiplier for artifacts...")
                self.click(
                    point=ARTIFACTS_LOCS["buy_multiplier"],
                    pause=0.5
                )
                self.click(
                    point=ARTIFACTS_LOCS["buy_max"],
                    pause=0.5
                )

            # Looking for the artifact to upgrade here, dragging until it is finally found.
            # Looping until our limit is reached, using a "global" found boolean to ensure we
            # log when an artifact could not be found.
            loops = 0
            found = False
            while loops != FUNCTION_LOOP_TIMEOUT:
                found = self.find_and_click(
                    image=ARTIFACT_MAP.get(artifact),
                    precision=0.7,
                    padding=(ARTIFACTS_LOCS["artifact_push"]["x"], ARTIFACTS_LOCS["artifact_push"]["y"]),
                    log="artifact: {artifact} has been found, purchasing now...".format(artifact=artifact)
                )
                # Break early if we've already found and purchased the artifact.
                if found:
                    break
                # Drag and try again.
                loops += 1
                self.drag(
                    start=self.locs.scroll_start,
                    end=self.locs.scroll_bottom_end,
                    pause=1.5
                )

            # No artifact could be found and our loops have been reached, we can skip
            # and log a warning for users.
            if not found:
                self.logger.warning("unable to find artifact: {artifact}, skipping purchase...".format(artifact=artifact))

    @not_in_transition
    def check_tournament(self):
        """
        Check that a tournament is available/active. Tournament will be joined if a new possible.

        Expecting a tuple to be returned here with the (prestige, advanced start) values.
        """
        if self.configuration.enable_tournaments:
            self.logger.info("checking for tournament ready to join or in progress.")
            if not self.ensure_collapsed_closed():
                return False, None

            # Looping to find tournament here, since there's a chance that the tournament is finished, which
            # causes a star trail circle the icon. May be hard to find, give it a couple of tries.
            tournament_found = False
            for i in range(5):
                tournament_found = self.grabber.search(image=self.images.tournament, bool_only=True)
                if tournament_found:
                    break

                # Wait slightly before trying again.
                sleep(0.2)

            if tournament_found:
                self.click(
                    point=self.locs.tournament,
                    pause=2
                )
                if self.grabber.search(self.images.join, bool_only=True):
                    # A tournament is ready to be joined. First, we must travel the the base
                    # prestige screen, perform a prestige update, before joining the tournament.
                    self.logger.info("tournament is available to join. generating prestige instance before joining.")
                    self.click(
                        point=MASTER_LOCS["screen_top"],
                        pause=1
                    )
                    if not self.goto_master():
                        return False, None

                    self.click(
                        point=MASTER_LOCS["prestige"],
                        pause=3
                    )
                    if self.grabber.search(self.images.confirm_prestige, bool_only=True):
                        # Parsing the advanced start value that is present before a prestige takes place...
                        # This is used to improve stage parsing to not allow values < the advanced start value.
                        prestige, advanced_start = self.stats.update_prestige(
                            current_stage=self.props.current_stage,
                            artifact=self.next_artifact_upgrade
                        )
                        self.click(
                            point=MASTER_LOCS["screen_top"],
                            pause=1
                        )

                        # Ensuring that any panels are collapsed, then attempting to join
                        # the tournament through the interface.
                        self.ensure_collapsed_closed()

                        self.click(
                            point=self.locs.tournament,
                            pause=2
                        )
                        self.logger.info("joining new tournament now...")
                        self.click(
                            point=self.locs.join,
                            pause=2
                        )

                        # Looking for the final prestige join confirmation. Replicating base prestige functionality.
                        self.find_and_click(
                            image=self.images.confirm_prestige_final
                        )

                        # Return generated prestige and advanced start right away,
                        # setting values in the prestige function directly. Wait should
                        # take place there instead of here.
                        return prestige, advanced_start

                # Otherwise, maybe the tournament is over? Or still running.
                else:
                    if self.grabber.search(image=self.images.collect_prize, bool_only=True):
                        # Perform a parse of the current tournament screen once the tournament
                        # has ended. We can collect data about who won and the stage each user
                        # got to if this functionality is enabled.
                        self.parse_tournament()

                        self.find_and_click(
                            image=self.images.collect_prize,
                            pause=2
                        )
                        self.click(
                            point=self.locs.game_middle,
                            clicks=10,
                            interval=0.5
                        )

            # No tournament was joined, and regardless of the reward being available
            # or not, if we reach this point, return our flags as False, None.
            return False, None

        # Explicitly return (False, None) if a user has tournaments disabled, because our tournaments
        # are the only function that expects multiple variables returned, we only need do it in this function currently.
        else:
            return False, None

    def parse_tournament(self):
        """
        Perform a parse of the current in game tournament.

        Collecting and storing information about the placing for the current user in the tournament,
        as well as information about each tournament participant.

        The reward earned should also be included in the results.
        """
        if self.configuration.enable_tournament_parsing:
            self.logger.info("attempting to parse tournament results now...")

            # First, let's determine if our user is in the top ten or not in this tournament.
            # This changes how we should handle the parsing here.
            in_top_ten = not self.grabber.search(image=self.images.in_top_ten, bool_only=True)

            # Determine which coords we will use to loop through to grab info about each person
            # current in the tournament (either top 5 + users current placing), or the entire
            # top 9 users in the tournament.
            coords = TOURNAMENT_COORDS["in_top_ten"] if in_top_ten else TOURNAMENT_COORDS["not_in_top_ten"]
            count = 9 if in_top_ten else 8  # 8 participants are displayed if user is not in the top ten.

            _current = self.grabber.snapshot()
            _identifier = uuid.uuid4()
            _path = "{dir}/{identifier}.png".format(dir=LOCAL_DATA_SCREENSHOTS_DIR, identifier=_identifier)

            # Make sure the current screenshot is also saved so it can be viewed
            # later in the dashboard to see a real view of the tournament results.
            _current.save(_path)

            tournament = Tournament.objects.create(
                instance=self.instance,
                identifier=_identifier,
            )

            # Loop through each expected available participant in the tournament.
            # Each one has an index associated for each expected location to search through.
            for i in range(count):
                # Generate a new participant for each iteration we take.
                # We can use our index to determine which participant we're on.
                if in_top_ten:
                    _rank = i + 1
                # Non top-ten tournament means we can manually grab up to 5th place.
                # After that, we'll need to parse using OCR.
                else:
                    if i <= 4:
                        _rank = i + 1
                    else:
                        _rank = self.stats.tournament_rank_ocr(region=coords["ranks"][i], threshold=150)

                _user = self.stats.tournament_user_ocr(region=coords["usernames"][i])
                _stage = self.stats.tournament_stage_ocr(region=coords["stages"][i])
                _is_user = self.grabber.point_is_color(point=coords["user_check_points"][i], color=self.colors.TOURNAMENT_USER)

                # Strip out the "W" from the winning users username.
                # This is what the "crown" should be parsed into.
                if i == 0 and _user[-1] == "W":
                    _user = _user[:-1].strip()

                self.logger.info("tournament participant: {index} parsed rank: {rank}".format(index=i + 1, rank=_rank))
                self.logger.info("tournament participant: {index} parsed user: {user}".format(index=i + 1, user=_user))
                self.logger.info("tournament participant: {index} parsed stage: {stage}".format(index=i + 1, stage=_stage))
                self.logger.info("tournament participant: {index} parsed is user: {is_user}".format(index=i + 1, is_user=_is_user))

                # All potential information is parsed for out participants, should be noted
                # that this information isn't guaranteed to be correct, since the ocr accuracy
                # may not be 100%.
                tournament.participants.add(Participant.objects.create(
                    rank=_rank,
                    username=_user,
                    stage=_stage,
                    is_user=_is_user
                ))

            self.logger.info("tournament: {identifier} was parsed successfully.".format(identifier=_identifier))
            self.logger.info("{parsed_participants} participant(s) were parsed successfully.".format(parsed_participants=tournament.participants.count()))

            # Return true boolean in case of conditionals based on the
            # returned value.
            return True

    @not_in_transition
    @bot_property(queueable=True, shortcut="shift+d", tooltip="Check for daily rewards in game and collect if available.")
    def daily_rewards(self):
        """
        Collect any daily gifts if they're available.
        """
        if self.configuration.enable_daily_rewards:
            self.logger.info("checking if any daily rewards are currently available to collect.")
            if not self.ensure_collapsed_closed():
                return False

            self.click(
                point=self.locs.open_rewards,
                pause=0.5
            )
            rewards_found = self.grabber.search(self.images.daily_rewards_header, bool_only=True)
            if rewards_found:
                self.logger.info("daily rewards are available, collecting!")
                self.click(
                    point=self.locs.collect_rewards,
                    pause=1
                )
                self.click(
                    point=self.locs.game_middle,
                    clicks=5,
                    interval=0.5,
                    pause=1
                )
                self.click(
                    point=MASTER_LOCS["screen_top"],
                    pause=1
                )

            return rewards_found

    @not_in_transition
    @bot_property(queueable=True, tooltip="Check for eggs in game and hatch them if available.")
    def hatch_eggs(self):
        """
        Hatch any eggs if they're available.
        """
        if self.configuration.enable_egg_collection:
            self.logger.info("checking if any eggs are available to be hatched in game and hatching them.")
            if not self.ensure_collapsed_closed():
                return False

            self.click(
                point=self.locs.hatch_egg,
                pause=0.5
            )
            self.click(
                point=self.locs.game_middle,
                clicks=5,
                interval=0.5,
                pause=1
            )

            return True

    @not_in_transition
    @bot_property(queueable=True, tooltip="Check for a clan crate in game and collect if available.")
    def clan_crate(self):
        """
        Check if a clan crate is currently available and collect it if one is.
        """
        if self.configuration.enable_clan_crates:
            if not self.ensure_collapsed_closed():
                return False

            for i in range(5):
                self.click(
                    point=self.locs.collect_clan_crate,
                    pause=1
                )
                if self.find_and_click(image=self.images.okay):
                    return True

            # No clan crate was found or collected, return false.
            return False

    @not_in_transition
    @bot_property(queueable=True, tooltip="Open the messages panel in game, and attempt to mark all messages as read.")
    def inbox(self):
        """
        Open up the inbox if it's available on the screen, clicking from header to header, ensuring that the icon is gone.
        """
        if not self.ensure_collapsed_closed():
            return False

        self.click(
            point=self.locs.inbox,
            pause=0.5
        )

        if self.grabber.search(self.images.inbox_header, bool_only=True):
            for i in range(2):
                for location in [self.locs.inbox_clan, self.locs.inbox_news]:
                    self.click(
                        point=location,
                        pause=0.2
                    )

            # Close the inbox screen now.
            self.click(
                point=MASTER_LOCS["screen_top"],
                pause=0.5
            )
            return True

        return False

    @not_in_transition
    @bot_property(forceable=True, tooltip="Force miscellaneous actions in game.")
    def miscellaneous_actions(self, force=False):
        """
        Miscellaneous actions can be activated here when the generic cooldown is reached.
        """
        if force or timezone.now() > self.props.next_miscellaneous_actions:
            self.logger.info("{force_or_initiate} miscellaneous actions now".format(force_or_initiate="forcing" if force else "beginning"))

            # Running through all generic functions that should only be available once
            # every once in a while, meaning we do not have to check for them at all times.
            self.clan_crate()
            self.daily_rewards()
            self.hatch_eggs()
            self.inbox()

            # Calculate when the next miscellaneous actions process
            # should take place again.
            self.calculate_next_miscellaneous_actions()

    @not_in_transition
    @bot_property(forceable=True, shortcut="shift+b", tooltip="Force a break in game.")
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
                for prop in [prop for prop in self.props.fields if prop.split("_")[0] == "next" and prop not in [
                    "next_break",
                    "next_raid_attack_reset",
                    "next_artifact_upgrade"
                ]]:
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
                        self.logger.info("break has ended... resuming bot now.")
                        self.calculate_next_break()
                        return True

                    if now > break_log_dt:
                        break_log_dt = now + datetime.timedelta(seconds=60)
                        self.logger.info("waiting for break to end... ({break_end})".format(break_end=strfdelta(self.props.resume_from_break - now)))

                    sleep(1)

    @not_in_transition
    @bot_property(forceable=True, shortcut="ctrl+d", tooltip="Force a daily achievement check in game.")
    def daily_achievements(self, force=False):
        """
        Perform a check for any completed daily achievements, collecting them as long as any are present.
        """
        if self.configuration.enable_daily_achievements:
            if force or timezone.now() > self.props.next_daily_achievement_check:
                self.logger.info("{force_or_initiate} daily achievement check now".format(force_or_initiate="forcing" if force else "beginning"))

                if not self.goto_master():
                    return False
                if not self.leave_boss():
                    return False

                # Open the achievements tab in game.
                self.click(
                    point=MASTER_LOCS["achievements"],
                    pause=2
                )

                # Are there any completed daily achievements?
                # Note: The single "ad watch" daily is not completed here
                # unless a user explicitly goes in and watches the ad.
                while self.grabber.search(self.images.daily_collect, bool_only=True):
                    self.find_and_click(
                        image=self.images.daily_collect,
                        log="completed daily achievement found, collecting now."
                    )

                # Additionally, check for the vip collection option
                # for daily achievements.
                self.find_and_click(
                    image=[self.images.vip_daily_collect, self.images.pass_daily_collect],
                    log="vip/season pass daily achievement found, collecting now."
                )

                # Exiting achievements screen now.
                self.calculate_next_daily_achievement_check()
                self.click(
                    point=MASTER_LOCS["screen_top"],
                    clicks=3
                )

    @not_in_transition
    @bot_property(forceable=True, shortcut="ctrl+m", tooltip="Force a milestone check in game.")
    def milestones(self, force=False):
        """
        Perform a check for the collection of a completed milestone reward.
        """
        if self.configuration.enable_milestones:
            if force or timezone.now() > self.props.next_milestone_check:
                self.logger.info("{force_or_initiate} milestone check now".format(force_or_initiate="forcing" if force else "beginning"))

                if not self.goto_master():
                    return False
                if not self.leave_boss():
                    return False

                # Open the milestones tab in game.
                self.click(
                    point=MASTER_LOCS["achievements"],
                    pause=2
                )
                self.click(
                    point=MASTER_LOCS["milestones"]["milestones_header"],
                    pause=1
                )

                # Loop forever until no more milestones can be collected.
                while True:
                    # Is the collect button available and the correct color for collection?
                    if self.grabber.point_is_color(point=MASTER_LOCS["milestones"]["milestones_collect_point"], color=self.colors.COLLECT_GREEN):
                        self.logger.info("a completed milestone is complete, collecting now...")
                        self.click(
                            point=MASTER_LOCS["milestones"]["milestones_collect_point"],
                            pause=1
                        )
                        self.click(
                            point=self.locs.game_middle,
                            clicks=5,
                            interval=0.5
                        )
                        sleep(3)
                    else:
                        self.logger.info("no milestone available for completion...")
                        break

                # Exiting milestones screen now.
                self.calculate_next_milestone_check()
                self.click(
                    point=MASTER_LOCS["screen_top"],
                    clicks=3
                )

    @not_in_transition
    @bot_property(forceable=True, shortcut="ctrl+r", tooltip="Force a raid notifications check in game.")
    def raid_notifications(self, force=False):
        """
        Perform all checks to see if a sms message will be sent to notify a user of an active raid.
        """
        if self.configuration.enable_raid_notifications:
            if force or timezone.now() > self.props.next_raid_notifications_check:
                self.logger.info("{force_or_initiate} raid notifications check now".format(force_or_initiate="forcing" if force else "beginning"))

                # Has an attack reset value already been parsed?
                if self.props.next_raid_attack_reset:
                    if self.props.next_raid_attack_reset > timezone.now():
                        self.logger.info("the next raid attack reset is still in the future, no notification will be sent.")
                        self.calculate_next_raid_notifications_check()
                        return False

                # Opening up the clan raid panel and checking if the fight button is available.
                # This would mean that we can perform some fights, if it is present, we also check to
                # see how much time until the attacks reset, once the current time has surpassed that
                # value, we allow another notification to be sent.
                if not self.goto_clan():
                    return False

                self.click(
                    point=self.locs.clan_raid,
                    pause=4
                )

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
                        to_num=self.configuration.raid_notifications_twilio_to_number,
                        instance=self.instance
                    )

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

    def welcome_screen_check(self):
        """
        Check to see if the welcome panel is currently on the screen, and close it if the global
        configuration currently has welcome screen checks toggled.
        """
        if globals.welcome_screen_checks():
            # Try to find and click the non-vip or vip enabled welcome
            # screen progress report to close the panel.
            self.find_and_click(
                image=[self.images.welcome_collect_no_vip, self.images.welcome_collect_vip]
            )

    def rate_screen_check(self):
        """
        Check to see if the game rate panel is currently on the screen, and close it.
        """
        if globals.rate_screen_checks():
            self.find_and_click(
                image=self.images.rate_icon
            )

    def ad(self):
        """
        Collect ad if one is available on the screen.

        Note: This function does not require a max loop (FUNCTION_LOOP_TIMEOUT) since it only ever loops
              while the collect panel is on screen, this provides only two possible options.

        This is the main ad function. Used in two places:
           - One instance is used by the transition functionality and decorator.
           - The other one allows the function to be called directly without decorators added.
        """
        collected = False
        while self.grabber.search(image=[self.images.collect_ad, self.images.collect_ad_pass, self.images.watch_ad], bool_only=True):
            # VIP/Season Pass Unlocked...
            found = self.find_and_click(
                image=[self.images.collect_ad, self.images.collect_ad_pass],
                pause=1
            )
            if found:
                collected = True
            # No VIP...
            if not found:
                if globals.pihole_ads():
                    self.logger.info("attempting to collect ad with pi hole now...")

                    # When pi hole is enabled, we can wait until a collect button has
                    # shown up on the screen, since the ad will eventually finish on its own.
                    while not self.grabber.search(image=self.images.collect_ad, bool_only=True):
                        # Make sure we don't accidentally mis-click or click on collect while
                        # the game is lagging or some other oddity that would cause this to loop forever.
                        self.find_and_click(
                            image=self.images.watch_ad,
                            log="waiting for pi hole to finish ad..."
                        )

                    # Ad has finished processing at this point, as the collect ad button should
                    # now be present somewhere on the screen.
                    found = self.find_and_click(
                        image=self.images.collect_ad,
                    )
                    if found:
                        collected = True

                # Pi hole functionality is disabled, we should just decline
                # the fairy ad here, user has no way of collecting.
                else:
                    self.find_and_click(
                        image=self.images.no_thanks,
                        log="declining fairy ad now..."
                    )

        # Actual collection of an is handled outside of our while loop. Pi hole or vip enabled ads
        # are tracked through the statistics. Doing this here to avoid our loop updating the stats constantly.
        if collected:
            self.logger.info("ad was successfully collected...")
            self.stats.increment_ads()
            sleep(1)

    @not_in_transition
    @bot_property(queueable=True, tooltip="Collect an ad in game if one is available.")
    def collect_ad(self):
        self.ad()

    def collect_ad_no_transition(self):
        self.ad()

    @not_in_transition
    @bot_property(queueable=True, shortcut="shift+f", tooltip="Attempt to begin the boss fight in game.")
    def fight_boss(self):
        """
        Ensure that the boss is being fought if it isn't already.
        """
        if self.grabber.search(image=self.images.fight_boss, bool_only=True):
            loops = 0
            while loops != BOSS_LOOP_TIMEOUT:
                found = self.find_and_click(
                    image=self.images.fight_boss,
                    pause=0.8,
                    log="initiating boss fight in game now..."
                )
                if found:
                    return True

                # Looping indefinitely until our loops has reached the configured
                # maximum boss loop timeout.
                sleep(0.5)
                loops += 1

            self.logger.warning("unable to enter boss fight, skipping...")
        return True

    @not_in_transition
    @bot_property(queueable=True, shortcut="shift+l", tooltip="Attempt to leave the boss fight in game.")
    def leave_boss(self):
        """
        Ensure that there is no boss being fought (avoids transition).
        """
        if self.grabber.search(image=self.images.leave_boss, bool_only=True):
            loops = 0
            while loops != BOSS_LOOP_TIMEOUT:
                found = self.find_and_click(
                    image=self.images.leave_boss,
                    pause=0.8,
                    log="leaving boss fight in game now..."
                )
                # Flipping our logic slightly here, since leaving the fight would occur when
                # attempting to click on the "fight_boss" image and it not being present.
                if not found:
                    return True

                # Looping indefinitely until our loops has reached the configured
                # maximum boss loop timeout.
                sleep(0.5)
                loops += 1

            self.logger.warning("unable to leave boss fight, skipping...")
        return True

    @not_in_transition
    @bot_property(queueable=True, tooltip="Begin generic tapping process in game.")
    def tap(self):
        """
        Perform simple screen tap over entire game area.
        """
        if self.configuration.enable_tapping:
            self.logger.info("beginning generic tapping process...")

            # Ensure the game screen is currently displaying the titan correctly.
            self.ensure_collapsed_closed()

            # Looping through all of our fairy map locations... Clicking and checking
            # for ads throughout the process.
            self.logger.info("executing tapping process {repeats} time(s)".format(repeats=self.configuration.tapping_repeat))
            for i in range(self.configuration.tapping_repeat):
                for index, point in enumerate(self.locs.fairies_map, start=1):
                    # No need to sleep, some fails are acceptable since
                    # we loop through a good amount fo coords here.
                    self.click(
                        point=point
                    )

                # Check for ads after each routine iteration, check is expensive
                # so no need to run multiple checks.
                self.collect_ad_no_transition()

    @not_in_transition
    @bot_property(queueable=True, tooltip="Begin minigame tapping process in game.")
    def minigames(self):
        if self.configuration.enable_minigames:
            self.logger.info("beginning minigame execution process...")

            # Ensure the game screen is currently displaying the titan correctly.
            self.ensure_collapsed_closed()
            self.logger.info("executing minigames process {repeats} time(s)".format(repeats=self.configuration.minigames_repeat))
            self.logger.info("executing minigames: {minigames}".format(minigames=", ".join(self.minigame_order)))

            for i in range(self.configuration.minigames_repeat):
                for minigame in self.minigame_order:
                    self.logger.info("tapping minigame: {minigame}".format(minigame=minigame))
                    for point in getattr(self.locs, minigame):
                        sleep(0.02)
                        self.click(
                            point=point
                        )

                    # Sleep for an additional amount of time if astral awakening
                    # is currently enabled (allow orb to fly).
                    if minigame == "astral_awakening" and self.configuration.minigames_repeat > 1:
                        self.logger.info("sleeping slightly to allow astral awakening orb to fly...")
                        sleep(0.5)

                self.collect_ad_no_transition()

    @not_in_transition
    def ensure_collapsed_closed(self):
        """
        Ensure that regardless of the current panel that is active, our game screen is present.

        We do this by attempting to collapse (or close) any panel that's open in game.
        """
        self.logger.info("attempting to collapse any panels in game now.")

        if self.grabber.search(image=[self.images.settings, self.images.fight_boss, self.images.leave_boss,
                                      self.images.icon_boss, self.images.clan_raid_ready, self.images.clan_no_raid], bool_only=True):
            # Return early if any images are present that could only be seen when the
            # game is in a collapsed state, regardless of panel.
            return True

        # If we reach this point, it means that none of our expected images are present,
        # (probably un-collapsed panel currently on screen).
        return self.find_and_click(
            image=[self.images.collapse_panel, self.images.exit_panel, self.images.large_exit_panel],
        )

    @not_in_transition
    def goto_panel(self, panel, icon, top_find, bottom_find, collapsed=True, top=True, equipment_tab=None):
        """
        Goto a specific panel, panel represents the key of this panel, also used when determining what panel
        to click on initially.

        Icon represents the image in game that represents a panel being open. This image is searched
        for initially before attempting to move to the top or bottom of the specified panel.

        NOTE: This function will return a boolean to determine if the panel was reached successfully. This can be
              used to exit out of actions or other pieces of bot functionality early if something has gone wrong.

        The equipment tab should only be used when we are travelling to the equipment panel directly, ensuring
        that the specified tab is opened before finishing.
        """
        self.logger.debug("attempting to travel to the {collapse_expand} {top_bot} of {panel} panel".format(
            collapse_expand="collapsed" if collapsed else "expanded", top_bot="top" if top else "bottom", panel=panel))

        loops = 0
        while not self.grabber.search(icon, bool_only=True):
            if loops == FUNCTION_LOOP_TIMEOUT:
                self.logger.warning("error occurred while travelling to {panel} panel, exiting function early.".format(panel=panel))
                return False

            loops += 1
            self.click(
                point=getattr(self.locs, panel),
                pause=1
            )

        # The shop panel may not be expanded/collapsed. Skip when travelling to shop panel.
        if panel != "shop":
            # Ensure the panel is expanded/collapsed appropriately.
            loops = 0
            if collapsed:
                while not self.grabber.search(self.images.expand_panel, bool_only=True):
                    if loops == FUNCTION_LOOP_TIMEOUT:
                        self.logger.warning("unable to collapse panel: {panel}, exiting function early.".format(panel=panel))
                        return False

                    loops += 1
                    self.click(
                        point=self.locs.expand_collapse_top,
                        pause=1,
                        offset=1
                    )
            else:
                while not self.grabber.search(self.images.collapse_panel, bool_only=True):
                    if loops == FUNCTION_LOOP_TIMEOUT:
                        self.logger.warning("unable to expand panel: {panel}, exiting function early.".format(panel=panel))
                        return False

                    loops += 1
                    self.click(
                        point=self.locs.expand_collapse_bottom,
                        pause=1,
                        offset=1
                    )

        # The equipment panel acts slightly different then our other panels, we don't really have a top
        # or bottom find image available, but we can choose between the five different equipment types.
        if panel == "equipment":
            if not equipment_tab:
                return True

            # Let's ensure that the specified tab is opened (ie: sword, headgear, cloak, aura, slash).
            while not self.grabber.point_is_color(point=EQUIPMENT_LOCS["color_checks"][equipment_tab], color=self.colors.EQUIPMENT_CHOSEN):
                self.click(
                    point=EQUIPMENT_LOCS["tabs"][equipment_tab],
                    pause=1
                )

            # Let's also perform a bit of a drag to try and reach the top or bottom of the tab.
            # Ensuring that our tab is at the top.
            if top:
                self.drag(
                    start=EQUIPMENT_LOCS["drag_equipment"]["start"],
                    end=EQUIPMENT_LOCS["drag_equipment"]["end"],
                    pause=0.1
                )
            else:
                self.drag(
                    start=EQUIPMENT_LOCS["drag_equipment"]["end"],
                    end=EQUIPMENT_LOCS["drag_equipment"]["start"],
                    pause=0.1
                )
            return True
        # Any other panel travelling happens here.
        else:
            # At this point, the panel should at least be opened.
            find = top_find if top or bottom_find is None else bottom_find

            # Trying to travel to the top or bottom of the specified panel, trying a set number of times
            # before giving up and breaking out of loop.
            loops = 0
            end_drag = self.locs.scroll_top_end if top else self.locs.scroll_bottom_end

            if not find:
                _last = self.grabber.snapshot(region=PANEL_COORDS["panel_check"])
                _current = _last

                while True:
                    if loops == FUNCTION_LOOP_TIMEOUT:
                        self.logger.warning("error occurred while travelling to {panel} panel, exiting function early.".format(panel=panel))
                        return False

                    loops += 1
                    self.drag(
                        start=self.locs.scroll_start,
                        end=end_drag,
                        pause=1
                    )
                    _last = _current
                    _current = self.grabber.snapshot(region=PANEL_COORDS["panel_check"])

                    # If the images are currently duplicates, it means we can no longer
                    # travel up or down anymore, essentially the top or bottom is hit.
                    if self.stats.images_duplicate(image_one=_last, image_two=_current):
                        break

            else:
                while not self.grabber.search(find, bool_only=True):
                    if loops == FUNCTION_LOOP_TIMEOUT:
                        self.logger.warning("error occurred while travelling to {panel} panel, exiting function early.".format(panel=panel))
                        return False

                    loops += 1
                    self.drag(
                        start=self.locs.scroll_start,
                        end=end_drag,
                        pause=1
                    )

            # Reaching this point represents that the specified panel
            # was successfully reached in the game.
            return True

    def goto_master(self, collapsed=True, top=True):
        """
        Instruct the bot to travel to the sword master panel.
        """
        return self.goto_panel(
            "master",
            self.images.master_active,
            self.images.master,
            self.images.silent_march,
            collapsed=collapsed,
            top=top
        )

    def goto_heroes(self, collapsed=True, top=True):
        """
        Instruct the bot to travel to the heroes panel.
        """
        return self.goto_panel(
            "heroes",
            self.images.heroes_active,
            None,
            None,
            collapsed=collapsed,
            top=top
        )

    def goto_equipment(self, collapsed=True, top=True, tab=None):
        """
        Instruct the bot to travel to the heroes panel.
        """
        return self.goto_panel(
            "equipment",
            self.images.equipment_active,
            None,
            None,
            collapsed=collapsed,
            top=top,
            equipment_tab=tab
        )

    def goto_pets(self, collapsed=True, top=True):
        """
        Instruct the bot to travel to the pets panel.
        """
        return self.goto_panel(
            "pets",
            self.images.pets_active,
            None,
            None,
            collapsed=collapsed,
            top=top
        )

    def goto_artifacts(self, collapsed=True, top=True):
        """
        Instruct the bot to travel to the artifacts panel.
        """
        return self.goto_panel(
            "artifacts",
            self.images.artifacts_active,
            None,
            None,
            collapsed=collapsed,
            top=top
        )

    def goto_shop(self, collapsed=False, top=True):
        """
        Instruct the bot to travel to the shop panel.
        """
        return self.goto_panel(
            "shop",
            self.images.shop_active,
            self.images.shop_keeper,
            None,
            collapsed=collapsed,
            top=top
        )

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

            self.click(
                point=self.locs.clan
            )
            loops += 1
            sleep(3)

        return True

    @not_in_transition
    def ensure_no_panel(self):
        """
        Instruct the bot to make sure no panels are currently open.
        """
        self.logger.info("attempting to close any panels in game.")

        loops = 0
        while self.grabber.search(image=[self.images.exit_panel, self.images.large_exit_panel], bool_only=True):
            if loops == FUNCTION_LOOP_TIMEOUT:
                self.logger.info("unable to close panels, giving up.")
                return False

            found = self.find_and_click(
                image=[self.images.exit_panel, self.images.large_exit_panel]
            )
            # Return true if we've found the exit image and clicked on it.
            if found:
                break

            loops += 1
            sleep(0.5)

        # If no panels are already open, return true now since
        # we can safely assume we're in a proper state if exit panels aren't found.
        return True

    @bot_property(queueable=True, shortcut="p", tooltip="Pause all bot functionality.")
    def pause(self):
        """
        Execute a pause for the current bot session.
        """
        self.PAUSE = True

        self.instance.pause()
        if self.scheduler.state == STATE_RUNNING:
            self.scheduler.pause()

        self.instance.pause()

    @bot_property(queueable=True, shortcut="r", tooltip="Resume all bot functionality.")
    def resume(self):
        """
        Execute a resume for the current bot session.
        """
        self.PAUSE = False

        self.instance.resume()
        if self.scheduler.state == STATE_PAUSED:
            self.scheduler.resume()

        self.instance.resume()

    @bot_property(queueable=True, shortcut="e", tooltip="Terminate all bot functionality.")
    def terminate(self):
        """
        Execute a termination of the current bot session.
        """
        self.TERMINATE = True

    def soft_shutdown(self):
        """
        Perform a soft shutdown of the bot, taking care of any cleanup or related tasks.
        """
        self.logger.info("beginning soft shutdown...")
        self.update_stats(
            force=True
        )

    @bot_property(queueable=True, shortcut="shift+e", tooltip="Perform soft termination of all bot functionality.")
    def soft_terminate(self):
        """
        Execute a soft shutdown/termination of the current bot session.
        """
        self.soft_shutdown()
        self.TERMINATE = True

    def setup_shortcuts(self):
        """
        Setup the keypress shortcut listener.
        """
        self.logger.info("initiating keyboard (shortcut) listener...")
        shortcuts.add_handle(instance=self.instance, logger=self.logger)
        shortcuts.hook()

    def setup_loop_functions(self):
        """
        Generate list of loop functions based on the enabled functions specified in the configuration.
        """
        # Using function.__name__ to ensure that changing our function names causes this to error out,
        # which in turn, requires us to update it.
        lst = [
            k for k, v in {
                self.fight_boss.__name__: True,
                self.miscellaneous_actions.__name__: True,
                self.tap.__name__: self.configuration.enable_tapping,
                self.minigames.__name__: self.configuration.enable_minigames,
                self.level_master.__name__: self.configuration.enable_master,
                self.level_heroes.__name__: self.configuration.enable_heroes,
                self.level_skills.__name__: self.configuration.enable_level_skills,
                self.activate_skills.__name__: self.configuration.enable_activate_skills,
                self.swap_headgear.__name__: self.configuration.enable_headgear_swap,
                self.perks.__name__: self.configuration.enable_perk_usage,
                self.prestige.__name__: self.configuration.enable_auto_prestige,
                self.daily_achievements.__name__: self.configuration.enable_daily_achievements,
                self.milestones.__name__: self.configuration.enable_milestones,
                self.raid_notifications.__name__: self.configuration.enable_raid_notifications,
                self.update_stats.__name__: self.configuration.enable_stats,
                self.breaks.__name__: self.configuration.enable_breaks
            }.items() if v
        ]

        self.logger.info("loop functions have been setup...")
        self.logger.info("{loop_funcs}".format(loop_funcs=", ".join(lst)))

        return lst

    def initialize(self):
        """
        Run any initial functions as soon as a session is started.
        """
        # Boot up the scheduler instance so it begins running all interval/period
        # type functions.
        if self.scheduler.state == STATE_STOPPED:
            self.scheduler.start()

        # Make sure the boss fight is entered if possible before beginning
        # normal bot runtime loop.
        self.fight_boss()

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
            self.daily_achievements(force=True)
        if self.configuration.milestones_check_on_start:
            self.milestones(force=True)
        if self.configuration.raid_notifications_check_on_start:
            self.raid_notifications(force=True)
        if self.configuration.headgear_swap_on_start:
            self.swap_headgear(force=True)
        if self.configuration.use_perks_on_start:
            self.perks(force=True)

    def run(self, start=True):
        """
        A run encapsulates the entire bot runtime process into a single function that conditionally
        checks for different things that are currently happening in the game, then launches different
        automated action within the emulator.
        """
        if start:
            try:
                # Ensure authentication check takes place before
                # running any other functionality.
                self.authenticate()

                # Perform an initial validation check before running
                # any bot functions.
                if self.VALID_AUTHENTICATION is False:
                    raise InvalidAuthenticationError()

                if self.enable_shortcuts:
                    self.setup_shortcuts()

                self.goto_master()
                self.initialize()
                self.get_upgrade_artifacts()

                if self.configuration.enable_artifact_purchase:
                    self.next_artifact_index = 0
                    self.update_next_artifact_upgrade()

                loop_functions = self.setup_loop_functions()
                pause_log_dt = timezone.now() + datetime.timedelta(seconds=10)

                while True:
                    for func in loop_functions:
                        # Any explicit functions can be executed after the main game loop has finished.
                        # The Queue handles the validation to ensure only available functions can be created...
                        for qfunc in Queue.objects.filter(instance=self.instance).order_by("-created"):
                            qfunc.finish()
                            if not bot_property.queueables(function=qfunc.function, forceables=True):
                                self.logger.warning("queued function: {func} encountered but this function does not "
                                                    "exist on the bot... ignoring function...".format(func=qfunc.function))

                            # Valid queueable function has been queued up. Executing normally.
                            else:
                                self.logger.info("queued function: {func} will be executed!".format(func=qfunc.function))
                                wait = wait_afterwards(
                                    function=getattr(self, qfunc.function),
                                    floor=self.configuration.post_action_min_wait_time,
                                    ceiling=self.configuration.post_action_max_wait_time
                                )

                                if bot_property.forceables(function=qfunc.function):
                                    wait(force=True)
                                else:
                                    wait()

                        if self.VALID_AUTHENTICATION is False:
                            raise InvalidAuthenticationError()
                        if self.TERMINATE:
                            raise TerminationEncountered()
                        if self.PAUSE:
                            now = timezone.now()
                            if now > pause_log_dt:
                                pause_log_dt = now + datetime.timedelta(seconds=10)
                                self.logger.info("waiting for resume...")

                            continue

                        wait_afterwards(
                            function=getattr(self, func),
                            floor=self.configuration.post_action_min_wait_time,
                            ceiling=self.configuration.post_action_max_wait_time
                        )()

            except InvalidAuthenticationError:
                self.logger.info("authentication credentials are no longer valid... terminating!")
            except TerminationEncountered:
                self.logger.info("manual termination encountered... terminating!")
            except FailSafeException:
                self.logger.info("failsafe termination encountered: terminating!")
            except Exception as exc:
                self.logger.exception("critical error encountered: {exc}".format(exc=exc))
                self.logger.info("terminating!")
                if self.configuration.soft_shutdown_on_critical_error:
                    self.logger.info("soft shutdown is enabled on critical error... attempting to shutdown softly...")
                    self.soft_shutdown()

            # Cleaning up the BotInstance once a termination has been received.
            finally:
                # Stop the schedulers functionality once the session has been stopped.
                if self.scheduler.state in [STATE_RUNNING, STATE_PAUSED]:
                    self.scheduler.shutdown(wait=False)

                self.stats.session.end = timezone.now()
                self.stats.session.save()
                self.instance.stop()
                Queue.flush()

                # Unhook our now terminated instance from our local shortcut module.
                # Shortcuts are still active at this point, but no logs or queued events are created for this instance.
                if self.enable_shortcuts:
                    shortcuts.unhook(
                        instance=self.instance,
                        logger=self.logger
                    )

                self.logger.info("==========================================================================================")
                self.logger.info("{session}".format(session=self.stats.session))
                self.logger.info("==========================================================================================")
                self.logger.handlers = []

                # Sending the offline signal to our authentication backend.
                # Initialization handles the online state for us, we need to ensure that
                # we go offline when a session is finished.
                AuthWrapper().offline()
