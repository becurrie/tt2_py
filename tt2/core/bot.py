"""
core.py

Main bot initialization and script startup should take place here. All actions and main bot loops
will be maintained from this location.
"""
from settings import (
    ROOT_DIR, CONFIG_FILE, STATS_FILE, STAGE_CAP, GAME_VERSION, __VERSION__,
)

from tt2.core.maps import *
from tt2.core.constants import STAGE_PARSE_THRESHOLD
from tt2.core.grabber import Grabber
from tt2.core.configure import Config
from tt2.core.stats import Stats
from tt2.core.wrap import Images, Locs, Colors
from tt2.core.utilities import click_on_point, click_on_image, drag_mouse, make_logger, strfdelta, sleep
from tt2.core.decorators import not_in_transition

from pyautogui import easeOutQuad, FailSafeException

import datetime
import keyboard
import git
import random


class BotException(Exception):
    pass


class Bot:
    """
    Main Bot class, generates the Window handler object, generated a configuration object used through
    the main game loop to determine how actions are performed within the game.
    """
    def __init__(self, config=CONFIG_FILE, stats_file=STATS_FILE, logger=None):
        self.TERMINATE = False
        self.config = Config(config)

        if logger:
            self.logger = logger
        else:
            self.logger = make_logger(self.config.LOGGING_LEVEL)

        if not self.config.ENABLE_LOGGING:
            self.logger.disabled = True

        # Bot utilities.
        self.grabber = Grabber(self.config.EMULATOR, self.logger)
        self.stats = Stats(self.grabber, self.config, stats_file, self.logger)

        # Data containers.
        self.images = Images(IMAGES, self.logger)
        self.locs = Locs(GAME_LOCS, self.logger)
        self.colors = Colors(GAME_COLORS, self.logger)

        self._last_stage = None
        self.current_stage = None

        self.next_action_run = None
        self.next_prestige = None
        self.next_stats_update = None

        self.next_heavenly_strike = None
        self.next_deadly_strike = None
        self.next_hand_of_midas = None
        self.next_fire_sword = None
        self.next_war_cry = None
        self.next_shadow_clone = None

        # Clan battle check should control when and if the bot knows that a clan quest is currently on cooldown,
        # if a clan quest is currently active, this can remain None. Only checked every X minutes based on config.
        self.next_clan_battle_check = None

        # Clan battle ready at datetime attribute. This is set when a clan check determines that the clan
        # quest is currently on cooldown, This datetime is checked on each game loop.
        self.clan_battle_ready_at = None

        self.logger.info("Bot (v{version}) (v{game_version}) [{commit}] has been initialized.".format(
            version=__VERSION__, game_version=GAME_VERSION, commit=git.Repo(ROOT_DIR).head.commit.hexsha))
        self.logger.info("SESSION: [{session}]".format(session=self.stats.session))
        self.logger.info("=======================================================")

        # Create a list of the functions called in there proper order
        # when actions are performed by the bot.
        self.action_order = self._order_actions()
        self.skill_order = self._order_skill_intervals()

        # Store information about the artifacts in game.
        self.owned_artifacts = None
        self.next_artifact_index = None
        self.next_artifact_upgrade = None

        # Setup the datetime objects used initially to determine when the bot
        # will perform specific actions in game.
        self.calculate_skill_execution()
        self.calculate_next_prestige()
        self.calculate_next_stats_update()
        self.calculate_next_clan_battle_check()
        self.calculate_next_action_run()

    def get_owned_artifacts(self):
        """Retrieve a list of all discovered/owned artifacts in game."""
        self.logger.info("Retrieving owned artifacts that will be used when upgrading after prestige.")
        lst = []
        for tier, d in self.stats.artifact_statistics["artifacts"].items():
            if self.config.UPGRADE_OWNED_TIER:
                if "," in self.config.UPGRADE_OWNED_TIER:
                    self.config.UPGRADE_OWNED_TIER = self.config.UPGRADE_OWNED_TIER.split(",")

                if tier not in self.config.UPGRADE_OWNED_TIER:
                    continue

            for key, owned in d.items():
                if not owned:
                    continue
                if key in ARTIFACT_WITH_MAX_LEVEL:
                    continue

                if self.config.IGNORE_SPECIFIC_ARTIFACTS:
                    if "," in self.config.IGNORE_SPECIFIC_ARTIFACTS:
                        self.config.IGNORE_SPECIFIC_ARTIFACTS = self.config.IGNORE_SPECIFIC_ARTIFACTS.split(",")

                    if key in self.config.IGNORE_SPECIFIC_ARTIFACTS:
                        continue

                self.logger.info("Artifact: {artifact} will be upgraded.".format(artifact=key))
                lst.append(key)

        if self.config.SHUFFLE_OWNED_ARTIFACTS:
            self.logger.info("Shuffling owned artifacts that will be upgraded.")
            random.shuffle(lst)

        return lst

    def update_next_artifact_upgrade(self):
        """Update the next artifact to be upgraded to the next one in the list."""
        if self.next_artifact_index + 1 == len(self.owned_artifacts):
            self.next_artifact_index = 0
            self.next_artifact_upgrade = self.owned_artifacts[self.next_artifact_index]
        else:
            self.next_artifact_index += 1
            self.next_artifact_upgrade = self.owned_artifacts[self.next_artifact_index]

    def parse_current_stage(self):
        """
        Attempt to update the current stage attribute through an OCR check in game. The current_stage
        attribute is initialized as None, and if the current stage parsed here is unable to be coerced into
        an integer, it will be set back to None.

        When using the attribute, a check should be performed to ensure it isn't None before running
        numeric friendly conditionals.
        """
        stage_parsed = self.stats.stage_ocr()
        try:
            stage = int(stage_parsed)
            self.logger.debug("Stage '{stage_text}' successfully coerced into an integer: {stage}.".format(
                stage_text=stage_parsed, stage=stage))
            if stage > STAGE_CAP:
                self.logger.debug("Stage {stage} is > the STAGE_CAP: {stage_cap}, resetting stage variables.".format(
                    stage=stage, stage_cap=STAGE_CAP))
                self._last_stage, self.current_stage = None, None
                return

            # Is the stage potentially way greater than the last check? Could mean the parse failed.
            if isinstance(self._last_stage, int):
                diff = stage - self._last_stage
                if diff > STAGE_PARSE_THRESHOLD:
                    self.logger.debug(
                        "Difference between current stage and last stage passes the stage change threshold: "
                        "{stage_thresh} ({stage} - {last_stage} = {diff}), resetting stage variables.".format(
                            stage_thresh=STAGE_PARSE_THRESHOLD, stage=stage, last_stage=self._last_stage, diff=diff))
                    self._last_stage, self.current_stage = None, None
                    return

            self.logger.debug("Current stage in game was successfully parsed: {stage}".format(stage=stage))
            self._last_stage = self.current_stage
            self.logger.debug("Last stage has been set to the previous current stage in game: {last_stage}".format(
                last_stage=self._last_stage))
            self.current_stage = stage

        # ValueError when the parsed stage isn't able to be coerced.
        except ValueError:
            self.logger.debug("OCR check could not parse out a proper string from image, resetting stage variables.")
            self._last_stage, self.current_stage = None, None

    def _order_actions(self):
        """Determine order of in game actions. Mapped to their respective functions."""
        sort = sorted([
            (self.config.ORDER_LEVEL_HEROES, self.level_heroes, "level_heroes"),
            (self.config.ORDER_LEVEL_MASTER, self.level_master, "level_master"),
            (self.config.ORDER_LEVEL_SKILLS, self.level_skills, "level_skills"),
        ], key=lambda x: x[0])

        self.logger.debug("Actions in game have been ordered successfully.")
        for action in sort:
            self.logger.debug("{order} : {action_key}.".format(order=action[0], action_key=action[2]))

        return sort

    def _order_skill_intervals(self):
        """Determine order of skills with intervals, first index will be the longest interval."""
        sort = sorted([
            (self.config.INTERVAL_HEAVENLY_STRIKE, "heavenly_strike"),
            (self.config.INTERVAL_DEADLY_STRIKE, "deadly_strike"),
            (self.config.INTERVAL_HAND_OF_MIDAS, "hand_of_midas"),
            (self.config.INTERVAL_FIRE_SWORD, "fire_sword"),
            (self.config.INTERVAL_WAR_CRY, "war_cry"),
            (self.config.INTERVAL_SHADOW_CLONE, "shadow_clone"),
        ], key=lambda x: x[0], reverse=True)

        self.logger.debug("Skill intervals have been ordered successfully.")
        for index, skill in enumerate(sort, start=1):
            self.logger.debug("{index}: {key} ({interval})".format(index=index, key=skill[1], interval=skill[0]))

        return sort

    @not_in_transition
    def _inactive_skills(self):
        """Create a list of all skills that are currently inactive."""
        inactive = []
        for key, region in MASTER_COORDS["skills"].items():
            if self.grabber.search(self.images.cancel_active_skill, region, bool_only=True):
                continue
            inactive.append(key)

        for key in inactive:
            self.logger.debug("{key} is not currently activated.".format(key=key))

        return inactive

    @not_in_transition
    def _not_maxed(self, inactive):
        """Given a list of inactive skill keys, determine which ones are not maxed out of those."""
        not_maxed = []
        for key, region in {k: r for k, r in MASTER_COORDS["skills"].items() if k in inactive}.items():
            if self.grabber.search(self.images.skill_max_level, region, bool_only=True):
                continue
            not_maxed.append(key)

        for key in not_maxed:
            self.logger.debug("{key} is not currently max level.".format(key=key))

        return not_maxed

    def calculate_skill_execution(self):
        """Calculate the datetimes that are attached to each skill in game and when they should be activated."""
        now = datetime.datetime.now()
        for key in SKILLS:
            interval_key = "INTERVAL_{0}".format(key.upper())
            next_key = "next_{0}".format(key)
            interval = getattr(self.config, interval_key, 0)
            if interval != 0:
                dt = now + datetime.timedelta(seconds=interval)
                setattr(self, next_key, dt)
                self.logger.debug("{skill} will be activated in {time}.".format(skill=key, time=strfdelta(dt - now)))
            else:
                self.logger.debug("{skill} has interval set to zero, will not be activated.".format(skill=key))

    def calculate_next_prestige(self):
        """Calculate when the next timed prestige will take place."""
        now = datetime.datetime.now()
        dt = now + datetime.timedelta(seconds=self.config.PRESTIGE_AFTER_X_MINUTES * 60)
        self.next_prestige = dt
        self.logger.debug("The next timed prestige will take place in {time}".format(time=strfdelta(dt - now)))

    def should_prestige(self):
        """
        Determine if prestige will take place. This value is based off of the configuration
        specified by the User.

        - After specified amount of time during run.
        - After a certain stage has been reached.
        - After max stage has been reached.
        - After a percent of max stage has been reached.
        """
        if self.config.PRESTIGE_AFTER_X_MINUTES != 0:
            now = datetime.datetime.now()
            self.logger.debug("Timed prestige is enabled, and should take place in {time}".format(
                time=strfdelta(self.next_prestige - now)))

            # Is the hard time limit set? If it is, perform prestige no matter what,
            # otherwise, look at the current stage conditionals present and prestige
            # off of those instead.
            if now > self.next_prestige:
                self.logger.debug("Timed prestige will happen now.")
                return True

        # Current stage must not be None, using time gate before this check. stage == None is only possible when
        # OCR checks are failing, this can happen when a stage change happens as the check takes place, causing
        # the image recognition to fail. OR if the parsed text doesn't pass the validation checks when parse is
        # malformed.
        if self.current_stage is None:
            self.logger.debug("Current stage is currently None, no stage conditionals can be checked currently.")
            return False

        # Any other conditionals will be using the current stage attribute of the bot.
        elif self.config.PRESTIGE_AT_STAGE != 0:
            self.logger.debug("Prestige at specific stage: {current}/{needed}.".format(
                current=self.current_stage, needed=self.config.PRESTIGE_AT_STAGE))
            if self.current_stage >= self.config.PRESTIGE_AT_STAGE:
                self.logger.debug("Prestige stage has been reached, prestige will happen now.")
                return True
            else:
                return False

        # These conditionals are dependant on the highest stage reached, if one isn't available,
        # (due to parsing error). We skip these until it is available, or the time limit is reached.
        if not self.stats.highest_stage:
            self.logger.debug("The highest stage statistic ({highest_stage}) seems to be set to an invalid value. "
                              "No prestige conditionals that rely on this statistic can currently be checked.")
            return False

        elif self.config.PRESTIGE_AT_MAX_STAGE:
            self.logger.debug("Prestige at max stage: {current}/{needed}.".format(
                current=self.current_stage, needed=self.stats.highest_stage))
            if self.current_stage >= self.stats.highest_stage:
                self.logger.debug("Max stage has been reached, prestige will happen now.")
                return True
            else:
                return False

        elif self.config.PRESTIGE_AT_MAX_STAGE_PERCENT != 0:
            percent = float(self.config.PRESTIGE_AT_MAX_STAGE_PERCENT) / 100
            threshold = int(self.stats.highest_stage * percent)
            self.logger.debug("Prestige at max stage percent ({percent}): {current}/{needed}".format(
                percent=percent, current=self.current_stage, needed=threshold))
            if self.current_stage >= threshold:
                self.logger.debug("Percent of max stage has been reached, prestige will happen now.")
                return True
            else:
                return False

        # Otherwise, only a time limit has been set for a prestige and it wasn't reached.
        return False

    def calculate_next_action_run(self):
        """Calculate when the next set of actions will be ran."""
        now = datetime.datetime.now()
        dt = now + datetime.timedelta(seconds=self.config.RUN_ACTIONS_EVERY_X_SECONDS)
        self.next_action_run = dt
        self.logger.debug("Actions in game will be initiated in {time}".format(time=strfdelta(dt - now)))

    def calculate_next_stats_update(self):
        """Calculate when the next stats update should take place."""
        now = datetime.datetime.now()
        dt = now + datetime.timedelta(seconds=self.config.STATS_UPDATE_INTERVAL_MINUTES * 60)
        self.next_stats_update = dt
        self.logger.debug("Statistics update in game will be initiated in {time}".format(time=strfdelta(dt - now)))

    def calculate_next_clan_battle_check(self):
        """Calculate when the next clan battle check should take place."""
        now = datetime.datetime.now()
        dt = now + datetime.timedelta(seconds=self.config.CLAN_BATTLE_CHECK_INTERVAL_MINUTES * 60)
        self.next_clan_battle_check = dt
        self.logger.debug("Clan battle check in game will be initiated in {time}".format(time=strfdelta(dt - now)))

    @not_in_transition
    def level_heroes(self):
        """Perform all actions related to the levelling of all heroes in game."""
        if self.config.ENABLE_HEROES:
            self.logger.info("Hero levelling process is beginning now.")
            self.goto_heroes(collapsed=False)

            # A quick check can be performed to see if the top of the heroes panel contains
            # a hero that is already max level, if this is the case, it's safe to assume
            # that all heroes below have been maxed out. Instead of scrolling and levelling
            # all heroes, just level the top heroes.
            if self.grabber.search(self.images.max_level, bool_only=True):
                self.logger.debug("A max levelled hero has been found on the top portion of the hero panel.")
                self.logger.debug("Only the first set of heroes will be levelled.")
                for point in HEROES_LOCS["level_heroes"][::-1][1:9]:
                    click_on_point(point, self.config.HERO_LEVEL_INTENSITY, interval=0.07)

                # Early exit as well.
                return

            # Always level the first 5 heroes in the list.
            self.logger.debug("Levelling first five heroes in list.")
            for point in HEROES_LOCS["level_heroes"][::-1][1:6]:
                click_on_point(point, self.config.HERO_LEVEL_INTENSITY, interval=0.07)

            # Travel to the bottom of the panel.
            for i in range(5):
                drag_mouse(self.locs.scroll_start, self.locs.scroll_bottom_end)

            drag_start = HEROES_LOCS["drag_heroes"]["start"]
            drag_end = HEROES_LOCS["drag_heroes"]["end"]

            # Begin level and scrolling process. An assumption is made that all heroes
            # are unlocked, meaning that some un-necessary scrolls may take place.
            self.logger.debug("Scrolling and levelling all heroes.")
            for i in range(4):
                for point in HEROES_LOCS["level_heroes"]:
                    click_on_point(point, clicks=self.config.HERO_LEVEL_INTENSITY, interval=0.07)

                # Skip the last drag since it's un-needed.
                if i != 3:
                    drag_mouse(drag_start, drag_end, duration=1, pause=1, tween=easeOutQuad,
                               quick_stop=self.locs.scroll_quick_stop)

    @not_in_transition
    def level_master(self):
        """Perform all actions related to the levelling of the sword master in game."""
        if self.config.ENABLE_MASTER:
            clicks = self.config.MASTER_LEVEL_INTENSITY
            self.logger.info("Levelling the sword master {clicks} time(s)".format(clicks=clicks))

            # Travel to the sword master panel, and level up specified amount of clicks.
            self.goto_master(collapsed=False)
            click_on_point(MASTER_LOCS["master_level"], clicks=clicks)

    @not_in_transition
    def level_skills(self):
        """Perform all actions related to the levelling of skills in game."""
        if self.config.ENABLE_SKILLS:
            self.logger.info("Levelling up skills in game if they are inactive and not maxed.")
            self.goto_master(collapsed=False)

            # Looping through each skill coord, clicking to level up.
            for skill in self._not_maxed(self._inactive_skills()):
                point = MASTER_LOCS["skills"].get(skill)

                # Should the bot upgrade the max amount of upgrades available for the current skill?
                if self.config.MAX_SKILL_IF_POSSIBLE:
                    # Retrieve the pixel location where the color should be the proper max level
                    # color once a single click takes place.
                    color_point = MASTER_LOCS["skill_level_max"].get(skill)
                    click_on_point(point, pause=1)

                    # Take a snapshot right after, and check for the point being the proper color.
                    self.grabber.snapshot()
                    if self.grabber.current.getpixel(color_point) == self.colors.WHITE:
                        self.logger.debug("Levelling max amount of available upgrades for skill: {skill}.".format(
                            skill=skill))
                        click_on_point(color_point, pause=0.5)

                # Otherwise, just level up the skills normally using the intensity setting.
                else:
                    self.logger.debug("Levelling skill: {skill} {intensity} time(s).".format(
                        skill=skill, intensity=self.config.SKILL_LEVEL_INTENSITY))
                    click_on_point(MASTER_LOCS["skills"].get(skill), clicks=self.config.SKILL_LEVEL_INTENSITY)

    def actions(self, force=False):
        """Perform bot actions in game."""
        now = datetime.datetime.now()
        if force or now > self.next_action_run:
            self.logger.info("{force_or_initiate} in game actions now.".format(
                force_or_initiate="Forcing" if force else "Beginning"))
            self.goto_master(collapsed=False)
            for action in self.action_order:
                action[1]()

                # The end of each action should send the game back to the expanded
                # sword master panel, regardless of the order of actions to ensure
                # normalized instructions each time an action ends.
                self.goto_master(collapsed=False)

            # Recalculate the time for the next set of actions to take place.
            self.calculate_next_action_run()
            self.stats.actions += 1

    @not_in_transition
    def update_stats(self, force=False):
        """Update the bot stats by travelling to the stats page in the heroes panel and performing OCR update."""
        if self.config.ENABLE_STATS:
            now = datetime.datetime.now()
            if force or now > self.next_stats_update:
                self.logger.info("{force_or_initiate} in game statistics update now.".format(
                    force_or_initiate="Forcing" if force else "Beginning"))
                self.goto_heroes()

                # Leaving boss fight here so that a stage transition does not take place
                # in the middle of a stats update.
                self.leave_boss()

                # Opening the stats panel within the heroes panel in game.
                # Scrolling to the bottom of this page, which contains all needed game stats info.
                click_on_point(HEROES_LOCS["stats_collapsed"], pause=0.5)
                for i in range(5):
                    drag_mouse(self.locs.scroll_start, self.locs.scroll_bottom_end)

                self.stats.update_ocr()
                self.stats.updates += 1
                self.stats.write()

                self.calculate_next_stats_update()
                click_on_point(MASTER_LOCS["screen_top"], clicks=3)

    @not_in_transition
    def prestige(self):
        """Perform a prestige in game."""
        if self.config.ENABLE_AUTO_PRESTIGE:
            if self.should_prestige():
                self.logger.info("Beginning prestige in game now.")
                self.check_tournament()
                self.goto_master(collapsed=False, top=False)

                # Click on the prestige button, and check for the prompt confirmation being present. Sleeping
                # slightly here to ensure that connections issues do not cause the prestige to be misfire.
                click_on_point(MASTER_LOCS["prestige"], pause=3)
                prestige_found, prestige_position = self.grabber.search(self.images.confirm_prestige)
                if prestige_found:
                    click_on_point(MASTER_LOCS["prestige_confirm"], pause=1)
                    click_on_point(MASTER_LOCS["prestige_final"], pause=10)

                    # If a timer is used for prestige. Reset this timer to the next timed prestige value.
                    if self.config.PRESTIGE_AFTER_X_MINUTES != 0:
                        self.calculate_next_prestige()

                    # After a prestige, run all actions instantly to ensure that initial levels are gained.
                    # Also attempt to activate skills afterwards so that stage progression is started before
                    # any other actions or logic takes place in game.
                    self.actions(force=True)
                    self.activate_skills(force=True)

                    # If the current stage currently is greater than the current max stage, lets update our stats
                    # to reflect that a new max stage has been reached. This allows for
                    if self.current_stage and self.stats.highest_stage:
                            if self.current_stage > self.stats.highest_stage:
                                self.logger.info(
                                    "Current run stage is greater than your previous max stage {max}, forcing a stats "
                                    "update to reflect these changes.".format(max=self.stats.highest_stage))
                                self.update_stats(force=True)

                    # Additional checks can take place during a prestige.
                    self.artifacts()
                    self.daily_rewards()
                    self.hatch_eggs()

    @not_in_transition
    def artifacts(self):
        """Determine whether or not any artifacts should be purchased, and purchase them."""
        if self.config.ENABLE_ARTIFACT_PURCHASE:
            self.goto_artifacts(collapsed=False)

            if self.config.UPGRADE_OWNED_ARTIFACTS:
                artifact = self.next_artifact_upgrade
                self.update_next_artifact_upgrade()
            elif self.config.UPGRADE_ARTIFACT:
                artifact = self.config.UPGRADE_ARTIFACT

            # Fallback to the users first artifact. This shouldn't happen, better safe than sorry.
            else:
                artifact = self.owned_artifacts[0]

            # Make sure that the proper spend max multiplier is used to fully upgrade an artifact.
            while not self.grabber.search(self.images.spend_max, bool_only=True):
                click_on_point(ARTIFACTS_LOCS["buy_multiplier"], pause=0.5)
                click_on_point(ARTIFACTS_LOCS["buy_max"], pause=0.5)

            # Looking for the artifact to upgrade here, dragging until it is finally found.
            while not self.grabber.search(ARTIFACT_MAP.get(artifact), bool_only=True):
                drag_mouse(self.locs.scroll_start, self.locs.scroll_bottom_end)
                sleep(1)

            # Making it here means the artifact in question has been found.
            found, position = self.grabber.search(ARTIFACT_MAP.get(artifact))
            new_x = position[0] + ARTIFACTS_LOCS["artifact_push"]["x"]
            new_y = position[1] + ARTIFACTS_LOCS["artifact_push"]["y"]

            # Currently just upgrading the artifact to it's max level. Future updates may include the ability
            # to determine how much to upgrade an artifact by.
            click_on_point((new_x, new_y), pause=1)

    @not_in_transition
    def check_tournament(self):
        """Check that a tournament is available/active. Tournament will be joined if a new possible."""
        if self.config.ENABLE_TOURNAMENTS:
            self.logger.info("Checking for tournament ready to join/in progress.")
            self.goto_master()

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
                click_on_point(self.locs.tournament, pause=2)
                found, position = self.grabber.search(self.images.join)
                if found:
                    self.logger.info("Joining new tournament now.")
                    click_on_point(self.locs.join, pause=2)
                    click_on_point(self.locs.tournament_prestige, pause=10)

                # Otherwise, maybe the tournament is over? Or still running.
                else:
                    collect_found, collect_position = self.grabber.search(self.images.collect_prize)
                    if collect_found:
                        self.logger.info("Tournament is over, attempting to collect reward now.")
                        click_on_point(self.locs.collect_prize, pause=2)
                        click_on_point(self.locs.game_middle, clicks=10, interval=0.5)

    @not_in_transition
    def daily_rewards(self):
        """Collect any daily gifts if they're available."""
        self.logger.info("Checking if any daily rewards are currently available to collect.")
        self.goto_master()
        reward_found = self.grabber.search(self.images.daily_reward, bool_only=True)
        if reward_found:
            self.logger.info("Daily rewards are available, collecting now.")
            click_on_point(self.locs.open_rewards, pause=1)
            click_on_point(self.locs.collect_rewards, pause=1)
            click_on_point(self.locs.game_middle, 5, interval=0.5, pause=1)
            click_on_point(MASTER_LOCS["screen_top"], pause=1)

    @not_in_transition
    def hatch_eggs(self):
        """Hatch any eggs if they're available."""
        if self.config.ENABLE_EGG_COLLECT:
            self.logger.info("Checking if any eggs are available to be hatched in game.")
            self.goto_master()
            egg_found = self.grabber.search(self.images.hatch_egg, bool_only=True)
            if egg_found:
                self.logger.info("Egg(s) are available, collecting now.")
                click_on_point(self.locs.hatch_egg, pause=1)
                click_on_point(self.locs.game_middle, 5, interval=0.5, pause=1)

    @not_in_transition
    def clan_battle(self, force_ready=False, force_check=False):
        """
        Perform all clan quest related functionality here. The clan battle should function and encapsulate
        the two following use cases.

        1. Every x amount of minutes, a check will occur that checks to see if a clan battle is on cooldown, if it is,
           the time remaining until that battle starts is parsed and the date is set to a instance attribute that is
           also checked here. If during this check, a fight is already in progress, a fight will take place right away
           using the normal clan quest fight logic.

        2. Every game loop also comes into here, and checks that the current datetime is greater than the new instance
           attribute that controls when the clan quest should be available. If the attribute isn't set (likely meaning
           that the bot has been initialized and no check has occurred yet), then the fight is skipped until it is set.
           If the current datetime is greater, normal clan quest fight logic should take place.
        """
        def fight(seconds=40):
            """
            Main quest fight logic, deals with clicking for X amount of seconds.

            Some overkill is specified as a default for the fight, fights only last thirty seconds,
            but we want to click longer so that we click while the fight is active, and ensure that
            the fight finished ui is clicked on to bring us back to the clan quest panel.
            """
            stop_at = datetime.datetime.now() + datetime.timedelta(seconds=seconds)
            self.logger.info("Starting clan quest fight, clicking will stop in {time}".format(
                time=strfdelta(stop_at - datetime.datetime.now())))

            # Clicking continuously until stop_at date is reached with now().
            while datetime.datetime.now() < stop_at:
                click_on_point(self.locs.game_middle, pause=0.07)

        # Are clan quests enabled at all?
        if self.config.ENABLE_CLAN_QUEST:
            # Firstly, determine if the bot knows whether or not a clan quest is currently pending
            # start based on a cooldown that has been previously recorded.
            now = datetime.datetime.now()
            if force_ready or self.clan_battle_ready_at:
                # We now know that there's a datetime available to determine when the clan quest will be ready.
                if force_ready or now > self.clan_battle_ready_at:
                    self.logger.info("{force_or_initiate} clan quest fight process now.".format(
                        force_or_initiate="Forcing" if force_ready else "Beginning"))

                    # Clan battle should be ready now. Let's begin the clan battle logic here.
                    # First, ensure we start with no panels open.
                    self.no_panel()

                    # Open the clan quest panel.
                    click_on_point(self.locs.clan, pause=5)
                    click_on_point(self.locs.clan_quest, pause=5)

                    # Determine whether or not the initial fight we go into will cost diamonds or not, this may
                    # happen due to configuration changes and restarting bot. Although rare, still worth dealing with.
                    if self.config.ENABLE_EXTRA_FIGHT:
                        if self.grabber.search(self.images.diamond, bool_only=True):
                            if self.grabber.search(self.images.deal_110_next_attack, precision=0.95, bool_only=True):
                                # Only ever fighting an additional fight if it costs five diamonds.
                                # Spending more is un-realistic and unsupported at the moment.
                                click_on_point(self.locs.clan_fight, pause=2)
                                click_on_point(self.locs.diamond_okay, pause=5)

                                fight()
                                self.stats.clan_ship_battles += 1
                                sleep(8)

                                # Leave the clan quest and default page.
                                click_on_point(self.locs.clan_quest_exit, pause=2)
                                click_on_point(self.locs.clan_leave_screen, clicks=3, pause=2)

                    # If the initial fight is a normal clan quest (no diamond cost), start by fighting like normal
                    # and performing the check to determine if diamonds will be spent during the second fight.
                    if self.grabber.search(self.images.fight, bool_only=True):
                        self.logger.info("Clan quest is available to participate in.")
                        # A diamond costing fight could potentially come up here, the check happens later on,
                        # which means we should return early if one comes up at this point.
                        if self.grabber.search(self.images.diamond, bool_only=True):
                            self.logger.info("Diamonds are required to participate, exiting now.")
                            self.calculate_next_clan_battle_check()
                            click_on_point(self.locs.clan_quest_exit, pause=2)
                            click_on_point(self.locs.clan_leave_screen, clicks=3, pause=2)
                            return

                        # Otherwise, a normal clan quest is available to participate in.
                        self.logger.info("Attempting to participate in clan quest now.")
                        click_on_point(self.locs.clan_fight, pause=5)

                        fight()
                        self.stats.clan_ship_battles += 1
                        sleep(8)

                        if self.config.ENABLE_EXTRA_FIGHT:
                            if self.grabber.search(self.images.diamond, bool_only=True):
                                if self.grabber.search(self.images.deal_110_next_attack, bool_only=True):
                                    self.logger.info("Extra clan quest fight has been enabled, and entry cost is five "
                                                     "diamonds, spending diamonds and entering fight again.")

                                    # Begin an additional fight by spending diamonds.
                                    click_on_point(self.locs.clan_fight, pause=2)
                                    click_on_point(self.locs.diamond_okay, pause=5)

                                    fight()
                                    self.stats.clan_ship_battles += 1
                                    sleep(8)

                        # All clan quest fights have been completed now, leave the clan quest pages.
                        self.logger.info("Exiting the clan panel now.")
                        click_on_point(self.locs.clan_quest_exit, pause=2)
                        click_on_point(self.locs.clan_leave_screen, clicks=3, pause=2)

                    # Additionally, the clan battle ready at attribute should be set back to None, so that
                    # only once the clan battle check takes place again to determine if a quest is active,
                    # or on cooldown, will a fight take place.
                    self.clan_battle_ready_at = None

            # If the clan_battle_ready_at attribute isn't set, perform a check to set the value.
            else:
                if force_check or now > self.next_clan_battle_check:
                    self.logger.info("{force_or_initiate} clan battle play again check now.".format(
                        force_or_initiate="Forcing" if force_check else "Beginning"))

                    # Travel to the clan quest page, checking to see if a clan quest is currently in progress.
                    # OR, that a clan quest is on cooldown, using this information to determine when the next
                    # fight should take place.
                    self.no_panel()
                    click_on_point(self.locs.clan, pause=5)
                    click_on_point(self.locs.clan_quest, pause=5)

                    # Is the clan quest currently active, or on cooldown?
                    if self.grabber.search(self.images.goal_complete, bool_only=True):
                        self.logger.info("Clan quest is currently on cooldown, attempting to parse out the next fight "
                                         "date in game now.")

                        # Perform an OCR check on the clan quest page, this will determine the datetime
                        # at which the clan quest will be ready to participate in.
                        self.clan_battle_ready_at = self.stats.play_again_ocr()
                        self.logger.info("Clan quest will be ready in {time}".format(
                            time=strfdelta(self.clan_battle_ready_at - now)))

                    # Clan quest in progress, lets set the clan battle ready at to the current datetime.
                    # Next game loop will then begin a clan quest.
                    else:
                        self.logger.info("A clan quest is already in progress, setting the ready date to now.")
                        self.clan_battle_ready_at = now

                    # Exit out of the clan quest screen.
                    self.logger.info("Exiting the clan panel now.")
                    click_on_point(self.locs.clan_quest_exit, pause=2)
                    click_on_point(self.locs.clan_leave_screen, clicks=3, pause=2)

                    # Calculate the next clan battle check.
                    self.calculate_next_clan_battle_check()

    @not_in_transition
    def clan_crate(self):
        """Check if a clan crate is currently available and collect it if one is."""
        self.goto_master()
        click_on_point(self.locs.clan_crate, pause=0.5)
        found, pos = self.grabber.search(self.images.okay)
        if found:
            self.logger.info("Clan crate was found, collecting now.")
            click_on_image(self.images.okay, pos, pause=1)

    @not_in_transition
    def collect_ad(self):
        """Collect ad if one is available on the screen."""
        while self.grabber.search(self.images.collect_ad, bool_only=True):
            if self.config.ENABLE_PREMIUM_AD_COLLECT:
                self.stats.premium_ads += 1
                self.logger.info("Collecting premium ad now.")
                click_on_point(self.locs.collect_ad, pause=1, offset=1)
            else:
                self.logger.info("Declining premium ad now.")
                click_on_point(self.locs.no_thanks, pause=1, offset=1)

    def collect_ad_no_transition(self):
        """Collect ad if one is available on the screen. No transition wrapper is included though."""
        while self.grabber.search(self.images.collect_ad, bool_only=True):
            if self.config.ENABLE_PREMIUM_AD_COLLECT:
                self.stats.premium_ads += 1
                self.logger.info("Collecting premium ad now.")
                click_on_point(self.locs.collect_ad, pause=1, offset=1)
            else:
                self.logger.info("Declining premium ad now.")
                click_on_point(self.locs.no_thanks, pause=1, offset=1)

    @not_in_transition
    def fight_boss(self):
        """Ensure that the boss is being fought if it isn't already."""
        if self.grabber.search(self.images.fight_boss, bool_only=True):
            self.logger.info("Initiating boss fight in game now.")
            click_on_point(self.locs.fight_boss, pause=0.5)

    @not_in_transition
    def leave_boss(self):
        """Ensure that there is no boss being fought (avoids transition)."""
        while not self.grabber.search(self.images.fight_boss, bool_only=True):
            click_on_point(self.locs.fight_boss, pause=0.2)

        sleep(3)

    @not_in_transition
    def tap(self):
        """Perform simple screen tap over entire game area."""
        if self.config.ENABLE_TAPPING:
            self.logger.info("Tapping...")
            taps = 0
            for point in self.locs.fairies_map:
                taps += 1
                if taps == 5:
                    # Check for an ad as the tapping process occurs. Click and return early if one is available.
                    if self.grabber.search(self.images.collect_ad, bool_only=True):
                        self.collect_ad_no_transition()
                        return

                    # Reset taps counter.
                    taps = 0
                click_on_point(point)

            # If no transition state was found during clicks, wait a couple of seconds in case a fairy was
            # clicked just as the tapping ended.
            sleep(2)

    @not_in_transition
    def activate_skills(self, force=False):
        """Activate any skills off of cooldown, and determine if waiting for longest cd to be done."""
        if self.config.ENABLE_SKILLS:
            self.logger.debug("Activating skills in game now.")
            self.goto_master()

            # Datetime to determine skill intervals.
            now = datetime.datetime.now()
            skills = [s for s in self.skill_order if s[0] != 0]
            next_key = "next_"

            if self.config.FORCE_ENABLED_SKILLS_WAIT and not force:
                attr = getattr(self, next_key + skills[0][1])
                if not now > attr:
                    self.logger.debug("Skills will only be activated once {key} is ready.".format(key=skills[0][1]))
                    self.logger.debug("{key} will be ready in {time}.".format(
                        key=skills[0][1], time=strfdelta(attr - now)))
                    return

            # If this point is reached, ensure no panel is currently active, and begin skill activation.
            self.no_panel()
            for skill in skills:
                self.logger.info("Activating {skill} now.".format(skill=skill[1]))
                click_on_point(getattr(self.locs, skill[1]), pause=0.2)

            # Recalculate all skill execution times.
            self.calculate_skill_execution()

    @not_in_transition
    def _goto_panel(self, panel, icon, top_find, bottom_find, collapsed=True, top=True, max_tries=25):
        """
        Goto a specific panel, panel represents the key of this panel, also used when determining what panel
        to click on initially.

        Icon represents the image in game that represents a panel being open. This image is searched
        for initially before attempting to move to the top or bottom of the specified panel.
        """
        self.logger.debug("attempting to travel to the {collapse_expand} {top_bot} of {panel} panel".format(
            collapse_expand="collapsed" if collapsed else "expanded", top_bot="top" if top else "bottom", panel=panel)
        )

        while not self.grabber.search(icon, bool_only=True):
            click_on_point(getattr(self.locs, panel), pause=1)

        # At this point, the panel should at least be opened.
        find = top_find if top or bottom_find is None else bottom_find

        # Trying to travel to the top or bottom of the specified panel, trying a set number of times
        # before giving up and breaking out of loop.
        loops = 0
        end_drag = self.locs.scroll_top_end if top else self.locs.scroll_bottom_end
        while not self.grabber.search(find, bool_only=True):
            if loops == max_tries:
                break

            # Manually wrap drag_mouse function in the not_in_transition call, ensure that
            # un-necessary mouse drags are not performed.
            drag_mouse(self.locs.scroll_start, end_drag, pause=1)
            loops += 1

        # The shop panel may not be expanded/collapsed. Skip when travelling to shop panel.
        if panel != "shop":
            # Ensure the panel is expanded/collapsed appropriately.
            if collapsed:
                while not self.grabber.search(self.images.expand_panel, bool_only=True):
                    click_on_point(self.locs.expand_collapse_top, pause=1, offset=1)
            else:
                while not self.grabber.search(self.images.collapse_panel, bool_only=True):
                    click_on_point(self.locs.expand_collapse_bottom, pause=1, offset=1)

    def goto_master(self, collapsed=True, top=True):
        """Instruct the bot to travel to the sword master panel."""
        self._goto_panel(
            "master", self.images.master_active, self.images.account, self.images.prestige,
            collapsed=collapsed, top=top
        )

    def goto_heroes(self, collapsed=True, top=True):
        """Instruct the bot to travel to the heroes panel."""
        self._goto_panel(
            "heroes", self.images.heroes_active, self.images.upgrades, self.images.maya_muerta,
            collapsed=collapsed, top=top
        )

    def goto_equipment(self, collapsed=True, top=True):
        """Instruct the bot to travel to the heroes panel."""
        self._goto_panel(
            "equipment", self.images.equipment_active, self.images.crafting, None,
            collapsed=collapsed, top=top
        )

    def goto_pets(self, collapsed=True, top=True):
        """Instruct the bot to travel to the pets panel."""
        self._goto_panel(
            "pets", self.images.pets_active, self.images.next_egg, None,
            collapsed=collapsed, top=top
        )

    def goto_artifacts(self, collapsed=True, top=True):
        """Instruct the bot to travel to the artifacts panel."""
        self._goto_panel(
            "artifacts", self.images.artifacts_active, self.images.salvaged, None,
            collapsed=collapsed, top=top
        )

    def goto_shop(self, collapsed=False, top=True):
        """Instruct the bot to travel to the shop panel."""
        self._goto_panel(
            "shop", self.images.shop_active, self.images.shop_keeper, None,
            collapsed=collapsed, top=top
        )

    @not_in_transition
    def no_panel(self):
        """Instruct the bot to make sure no panels are currently open."""
        while self.grabber.search(self.images.exit_panel, bool_only=True):
            click_on_point(self.locs.close_bottom, offset=2)
            if not self.grabber.search(self.images.exit_panel, bool_only=True):
                break

            click_on_point(self.locs.close_top, offset=2)
            if not self.grabber.search(self.images.exit_panel, bool_only=True):
                break

    def soft_shutdown(self):
        """Perform a soft shutdown of the bot, taking care of any cleanup or related tasks."""
        self.logger.info("Beginning soft shutdown now.")
        self.update_stats(force=True)

    def restart_game(self):
        """
        Attempt to restart the game within the emulator. Currently supported emulators include:

        - Nox
        """
        from pyautogui import moveTo
        self.logger.info("Attempting to restart the game within {emulator} emulator".format(
            emulator=self.config.EMULATOR
        ))
        click_on_point(EMULATOR_LOCS[self.config.EMULATOR]["opened_apps"], pause=3)
        moveTo(EMULATOR_LOCS[self.config.EMULATOR]["close_game"][0],
               EMULATOR_LOCS[self.config.EMULATOR]["close_game"][1], pause=5)
        click_on_point(EMULATOR_LOCS[self.config.EMULATOR]["close_game"], pause=3)

        # Opening the game, waiting at least twenty seconds before continuing.
        click_on_point(EMULATOR_LOCS[self.config.EMULATOR]["launch_game"], pause=20)

    def run(self):
        """
        A run encapsulates the entire bot runtime process into a single function that conditionally
        checks for different things that are currently happening in the game, then launches different
        automated action within the emulator.
        """
        try:
            self.goto_master()
            if self.config.RUN_ACTIONS_ON_START:
                self.actions(force=True)
            if self.config.ACTIVATE_SKILLS_ON_START:
                self.activate_skills(force=True)
            if self.config.UPDATE_STATS_ON_START:
                self.update_stats(force=True)
            if self.config.CLAN_BATTLE_CHECK_ON_START:
                self.clan_battle(force_check=True)

            # Update the initial bots artifacts information that is used when upgrading
            # artifacts in game. This is handled after stats have been updated.
            self.owned_artifacts = self.get_owned_artifacts()
            self.next_artifact_index = 0
            self.next_artifact_upgrade = self.owned_artifacts[self.next_artifact_index]

            # Main game loop.
            while True:
                if self.TERMINATE:
                    self.logger.info("TERMINATE SIGNAL, EXITING.")
                    break

                self.goto_master()
                self.fight_boss()
                self.clan_crate()
                self.tap()
                self.collect_ad()
                self.parse_current_stage()
                self.prestige()
                self.clan_battle()
                self.actions()
                self.activate_skills()
                self.update_stats()

        # Making use of the PyAutoGUI FailSafeException to allow some cleanup to take place
        # before totally exiting. Only if the CTRL key is held down when exception is thrown.
        except FailSafeException:
            self.logger.info(
                "Bot SHUTDOWN SIGNAL RETRIEVED. Press the {key} key to perform a soft shutdown in {seconds} "
                "second(s).".format(key=self.config.SOFT_SHUTDOWN_KEY, seconds=self.config.SHUTDOWN_SECONDS))

            # Create datetime objects to specify how long until the bot shutdowns.
            now = datetime.datetime.now()
            shutdown_at = now + datetime.timedelta(seconds=self.config.SHUTDOWN_SECONDS)

            soft = False
            while now < shutdown_at:
                now = datetime.datetime.now()
                if keyboard.is_pressed(self.config.SOFT_SHUTDOWN_KEY) and not soft:
                    soft = True
                    self.logger.info("Soft SHUTDOWN will take place in {time}".format(
                        time=strfdelta(shutdown_at - now)))
            if soft:
                self.soft_shutdown()
            else:
                return None

        # Any other exception, perform soft shutdown before termination if specified by configuration.
        except BotException as exc:
            self.logger.critical("CRITICAL ERROR ENCOUNTERED: {exc}".format(exc=exc))
            if self.config.SOFT_SHUTDOWN_ON_CRITICAL_ERROR:
                self.logger.info("Soft SHUTDOWN will take place now due to critical error.")
                self.soft_shutdown()
