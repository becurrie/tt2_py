"""
core.py

Main bot initialization and script startup should take place here. All actions and main bot loops
will be maintained from this location.
"""
from settings import CONFIG_FILE, STATS_FILE, STAGE_CAP

from tt2.core.maps import *
from tt2.core.constants import STAGE_PARSE_THRESHOLD
from tt2.core.grabber import Grabber
from tt2.core.configure import Config
from tt2.core.stats import Stats
from tt2.core.images import Images
from tt2.core.locs import Locs
from tt2.core.utilities import click_on_point, drag_mouse, make_logger, strfdelta, sleep
from tt2.core.decorators import not_in_transition

from pyautogui import easeOutQuad, FailSafeException

import datetime
import keyboard


class BotException(Exception):
    pass


class Bot:
    """
    Main Bot class, generates the Window handler object, generated a configuration object used through
    the main game loop to determine how actions are performed within the game.
    """
    def __init__(self, config=CONFIG_FILE, stats_file=STATS_FILE, logger=None):
        self.config = Config(config)

        if logger:
            self.logger = logger
        else:
            self.logger = make_logger(self.config.LOGGING_LEVEL)

        if not self.config.ENABLE_LOGGING:
            self.logger.disabled = True

        # Initialize miscellaneous classes here.
        self.grabber = Grabber(self.config.EMULATOR, self.config.HEIGHT, self.config.WIDTH, self.logger)
        self.stats = Stats(self.grabber, self.config, stats_file, self.logger)
        self.images = Images(IMAGES)
        self.locs = Locs(GAME_LOCS[self.stats.key])

        # Debug some information about this bot instantiation.
        self.logger.debug("config instance has been initialized: {0}".format(vars(self.config)))
        self.logger.debug("grabber instance has been initialized: {0}".format(vars(self.grabber)))
        self.logger.debug("stats instance has been initialized: {0}".format(self.stats.as_json()))
        self.logger.debug("images instance has been initialized: {0}".format(vars(self.images)))
        self.logger.debug("locs instance has been initialized: {0}".format(vars(self.locs)))

        # Additional locations and coords can be set here.
        self.master_locs = MASTER_LOCS[self.stats.key]
        self.master_coords = MASTER_COORDS[self.stats.key]
        self.heroes_locs = HEROES_LOCS[self.stats.key]
        self.artifacts_locs = ARTIFACTS_LOCS[self.stats.key]
        self.emulator_locs = EMULATOR_LOCS[self.stats.key][self.config.EMULATOR]

        self.logger.debug("master locations have been initialized: {0}".format(self.master_locs))
        self.logger.debug("master coordinates have been initialized: {0}".format(self.master_coords))
        self.logger.debug("heroes locations have been initialized: {0}".format(self.heroes_locs))
        self.logger.debug("artifacts locations have been initialized: {0}".format(self.artifacts_locs))
        self.logger.debug("emulator locations have been initialized: {0}".format(self.emulator_locs))

        # Additional image maps can be set here.
        self.artifacts_images = ARTIFACT_MAP

        self.logger.info("bot instance has been initialized successfully")
        self.logger.info("uuid: {0}".format(self.stats.session))

        # Bot termination flag. run() should exit if True.
        self.TERMINATE = False

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

        # Additional in game intervals.
        self.next_clan_battle_check = None

        # Create a list of the functions called in there proper order
        # when actions are performed by the bot.
        self.action_order = self._order_actions()
        self.skill_order = self._order_skill_intervals()

        # Setup the datetime objects used initially to determine when the bot
        # will perform specific actions in game.
        self.calculate_skill_execution()
        self.calculate_next_prestige()
        self.calculate_next_stats_update()
        self.calculate_next_clan_battle_check()

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
            self.logger.info("attempting to coerce value: {stage} into a integer".format(stage=stage_parsed))
            stage = int(stage_parsed)
            if stage > STAGE_CAP:
                self.logger.warn("parsed stage is greater than highest possible stage, skipping this parse")
                self._last_stage = None
                self.current_stage = None
                return

            # Is the stage potentially way greater than the last check? Could mean the parse failed.
            if isinstance(self._last_stage, int):
                if stage - self._last_stage > STAGE_PARSE_THRESHOLD:
                    self.logger.warn("parsed stage minus last parsed stage is greater than the threshold ({thresh}), "
                                     "skipping this parse".format(thresh=STAGE_PARSE_THRESHOLD))
                    self._last_stage = None
                    self.current_stage = None
                    return

            self._last_stage = self.current_stage
            self.current_stage = stage
            self.logger.info("current stage was successfully parsed: {stage}".format(stage=stage))

        # ValueError when the parsed stage isn't able to be coerced.
        except ValueError:
            self.logger.warn("unable to coerce text, setting current stage to None instead")
            self._last_stage = None
            self.current_stage = None

    def _order_actions(self):
        """Determine order of in game actions. Mapped to their respective functions."""
        sort = sorted([
            (self.config.ORDER_LEVEL_HEROES, self.level_heroes, "level_heroes"),
            (self.config.ORDER_LEVEL_MASTER, self.level_master, "level_master"),
            (self.config.ORDER_LEVEL_SKILLS, self.level_skills, "level_skills"),
        ], key=lambda x: x[0])

        self.logger.info("actions in game will run in the following order")
        for i, action in enumerate(sort, start=1):
            self.logger.info("{index}: {func_name}".format(index=i, func_name=action[2]))

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

        self.logger.info("skills have been ordered successfully")
        for i, skill in enumerate(sort, start=1):
            if skill[1] is not None:
                self.logger.info("{index}: {key} - {interval}".format(index=i, key=skill[1], interval=skill[0]))

        return sort

    @not_in_transition
    def _inactive_skills(self):
        """Create a list of all skills that are currently inactive."""
        inactive = []
        for key, region in self.master_coords["skills"].items():
            if self.grabber.search(self.images.cancel_active_skill, region, bool_only=True):
                continue

            # Skill is not currently active, add it to the list.
            inactive.append(key)

        for i in inactive:
            self.logger.info("{skill} is currently inactive".format(skill=i))

        return inactive

    @not_in_transition
    def _not_maxed(self, inactive):
        """Given a list of inactive skill keys, determine which ones are not maxed out of those."""
        not_maxed = []

        for key, region in {k: r for k, r in self.master_coords["skills"].items() if k in inactive}.items():
            if self.grabber.search(self.images.skill_max_level, region, bool_only=True):
                continue

            # Skills is not currently maxed, add it to the list.
            not_maxed.append(key)

        for n in not_maxed:
            self.logger.info("{skill} is not currently maxed".format(skill=n))

        return not_maxed

    def calculate_skill_execution(self):
        """Calculate the datetimes that are attached to each skill in game and when they should be activated."""
        now = datetime.datetime.now()
        self.logger.info("attempting to calculate next skill execution times")

        for key in SKILLS:
            interval_key = "INTERVAL_{0}".format(key.upper())
            next_key = "next_{0}".format(key)
            interval = getattr(self.config, interval_key, 0)
            if interval != 0:
                dt = now + datetime.timedelta(seconds=interval)
                setattr(self, next_key, dt)
                self.logger.info("next {key} will be activated at: {date} ({time})".format(
                    key=key, date=str(dt), time=strfdelta(dt - now))
                )
            else:
                self.logger.debug("{key} will not be activated".format(key=key))

    def calculate_next_prestige(self):
        """Calculate when the next prestige will take place."""
        now = datetime.datetime.now()
        dt = now + datetime.timedelta(seconds=self.config.PRESTIGE_AFTER_X_MINUTES * 60)
        self.next_prestige = dt
        self.logger.info("next prestige will take place at: {date} ({time})".format(
            date=str(dt), time=strfdelta(dt - now))
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
        if self.config.PRESTIGE_AFTER_X_MINUTES != 0:
            now = datetime.datetime.now()

            # Is the hard time limit set? If it is, perform prestige no matter what,
            # otherwise, look at the current stage conditionals present and prestige
            # off of those instead.
            if now > self.next_prestige:
                return True

            self.logger.info("timed prestige will occur at {date} ({time})".format(
                date=str(now), time=strfdelta(self.next_prestige - now)
            ))

        # Current stage must not be None, using time gate before this check.
        # stage == None is only possible when OCR checks are failing, this can
        # happen when a stage change happens as the check takes place, causing
        # the image recognition to fail.
        if self.current_stage is None:
            return False

        # Any other conditionals will be using the current stage attribute of the bot.
        elif self.config.PRESTIGE_AT_STAGE != 0:
            if self.current_stage >= self.config.PRESTIGE_AT_STAGE:
                self.logger.info("stage: {stage} has been reached, beginning prestige now".format(
                    stage=self.config.PRESTIGE_AT_STAGE
                ))
                return True
            else:
                return False

        # These conditionals are dependant on the highest stage reached, if one isn't available,
        # (due to parsing error). We skip these until it is available, or the time limit is reached.
        if not self.stats.highest_stage:
            self.logger.info("it looks like your highest stage is being used as a prestige requirement but "
                             "no highest stage is available, skipping for now")
            return False

        elif self.config.PRESTIGE_AT_MAX_STAGE:
            if self.current_stage >= self.stats.highest_stage:
                self.logger.info("max stage: {max_stage} has been reached, beginning prestige now".format(
                    max_stage=self.stats.highest_stage
                ))
                return True
            else:
                return False

        elif self.config.PRESTIGE_AT_MAX_STAGE_PERCENT != 0:
            percent = self.config.PRESTIGE_AT_MAX_STAGE_PERCENT / 100
            threshold = int(self.stats.highest_stage * percent)
            if self.current_stage >= threshold:
                self.logger.info("{percent}% of max stage: {max_stage} has been reached, beginning prestige now".format(
                    percent=self.config.PRESTIGE_AT_MAX_STAGE_PERCENT, max_stage=self.stats.highest_stage
                ))
                return True
            else:
                return False

        # Otherwise, only a time limit has been set for a prestige and it wasn't reached.
        self.logger.info("no prestige requirements were met, prestige will not happen right now")
        return False

    def calculate_next_action_run(self):
        """Calculate when the next set of actions will be ran."""
        now = datetime.datetime.now()
        dt = now + datetime.timedelta(seconds=self.config.RUN_ACTIONS_EVERY_X_SECONDS)
        self.next_action_run = dt
        self.logger.info("next action run will take place at: {date} ({time})".format(
            date=str(dt), time=strfdelta(dt - now))
        )

    def calculate_next_stats_update(self):
        """Calculate when the next stats update should take place."""
        now = datetime.datetime.now()
        dt = now + datetime.timedelta(seconds=self.config.STATS_UPDATE_INTERVAL_MINUTES * 60)
        self.next_stats_update = dt
        self.logger.info("next stats update run will take place at: {date} ({time})".format(
            date=str(dt), time=strfdelta(dt - now))
        )

    def calculate_next_clan_battle_check(self):
        """Calculate when the next clan battle check should take place."""
        now = datetime.datetime.now()
        dt = now + datetime.timedelta(seconds=self.config.CLAN_BATTLE_CHECK_INTERVAL_MINUTES * 60)
        self.next_clan_battle_check = dt
        self.logger.info("next clan battle check will take place at: {date} ({time})".format(
            date=str(dt), time=strfdelta(dt - now)
        ))

    @not_in_transition
    def level_heroes(self):
        """Perform all actions related to the levelling of all heroes in game."""
        if self.config.ENABLE_HEROES:
            self.logger.info("beginning hero levelling process")
            self.goto_heroes(collapsed=False)

            # A quick check can be performed to see if the top of the heroes panel contains
            # a hero that is already max level, if this is the case, it's safe to assume
            # that all heroes below have been maxed out. Instead of scrolling and levelling
            # all heroes, just level the top heroes.
            if self.grabber.search(self.images.max_level, bool_only=True):
                self.logger.info("max level hero found at top of panel, skipping normal hero level process")
                self.logger.info("levelling top heroes only")
                for point in self.heroes_locs["level_heroes"][::-1][1:9]:
                    click_on_point(point, self.config.HERO_LEVEL_INTENSITY, interval=0.07)

                # Early exit as well.
                return

            # Always level the first 5 heroes in the list.
            for point in self.heroes_locs["level_heroes"][::-1][1:6]:
                click_on_point(point, self.config.HERO_LEVEL_INTENSITY, interval=0.07)

            # Travel to the bottom of the panel.
            for i in range(5):
                drag_mouse(self.locs.scroll_start, self.locs.scroll_bottom_end)

            drag_start = self.heroes_locs["drag_heroes"]["start"]
            drag_end = self.heroes_locs["drag_heroes"]["end"]

            # Begin level and scrolling process. An assumption is made that all heroes
            # are unlocked, meaning that some un-necessary scrolls may take place.
            for i in range(4):
                for point in self.heroes_locs["level_heroes"]:
                    click_on_point(point, clicks=self.config.HERO_LEVEL_INTENSITY, interval=0.07)

                # Skip the last drag since it's un-needed.
                if i != 3:
                    drag_mouse(
                        drag_start, drag_end, duration=1, pause=1, tween=easeOutQuad,
                        quick_stop=self.locs.scroll_quick_stop
                    )

    @not_in_transition
    def level_master(self):
        """Perform all actions related to the levelling of the sword master in game."""
        if self.config.ENABLE_MASTER:
            self.logger.info("beginning master levelling process")
            self.goto_master(collapsed=False)
            click_on_point(self.master_locs["master_level"], clicks=self.config.MASTER_LEVEL_INTENSITY)

    @not_in_transition
    def level_skills(self):
        """Perform all actions related to the levelling of skills in game."""
        if self.config.ENABLE_SKILLS:
            self.logger.info("beginning skills levelling process")
            self.goto_master(collapsed=False)

            # Looping through each skill coord, clicking to level up.
            for skill in self._not_maxed(self._inactive_skills()):
                self.logger.info("levelling up {skill} {clicks} time(s) now".format(
                    skill=skill, clicks=self.config.SKILL_LEVEL_INTENSITY)
                )
                click_on_point(self.master_locs["skills"].get(skill), clicks=self.config.SKILL_LEVEL_INTENSITY)

    def actions(self, force=False):
        """Perform bot actions in game."""
        now = datetime.datetime.now()

        # Force will ensure that the next_action_run is less than the now datetime.
        # Causing all actions to be ran no matter what.
        if force:
            self.logger.info("forcing actions to run now instead of later")
            self.next_action_run = now - datetime.timedelta(seconds=1)

        if now > self.next_action_run:
            self.logger.info("beginning in game actions now")
            # Ensure that the game is currently on the sword master panel (expanded).
            self.goto_master(collapsed=False)

            # Looping through ordered actions and executing callable attached.
            for action in self.action_order:
                action[1]()

                # The end of each action should send the game back to the expanded
                # sword master panel, regardless of the order of actions.
                self.goto_master(collapsed=False)

            # Recalculate the time for the next set of actions to take place.
            self.calculate_next_action_run()
            self.stats.actions += 1

        # How much time left until actions will take place?
        self.logger.debug("actions will take place in {date} ({time})".format(
            date=self.next_action_run, time=strfdelta(self.next_action_run - now)
        ))

    @not_in_transition
    def update_stats(self, force=False):
        """Update the bot stats by travelling to the stats page in the heroes panel and performing OCR update."""
        if self.config.ENABLE_STATS:
            now = datetime.datetime.now()

            # Allow the ability to force a stats update by modifying the
            if force:
                now = self.next_stats_update + datetime.timedelta(seconds=1)

            if now > self.next_stats_update:
                self.logger.info("performing{force_no_force} stats update now".format(
                    force_no_force=" a forced" if force else ""
                ))
                self.stats.updates += 1
                self.goto_heroes()

                click_on_point(self.heroes_locs["stats_collapsed"], pause=0.5)

                # Scroll to the bottom of the heroes stats popup.
                for i in range(3):
                    drag_mouse(self.locs.scroll_start, self.locs.scroll_bottom_end)

                # Update stats instance through OCR update.
                self.stats.update_ocr()
                self.stats.write()
                self.calculate_next_stats_update()

                click_on_point(self.master_locs["screen_top"], clicks=3)

    @not_in_transition
    def prestige(self):
        """Perform a prestige in game."""
        if self.config.ENABLE_AUTO_PRESTIGE:
            if self.should_prestige():
                self.logger.info("beginning prestige process now.")
                self.check_tournament()
                self.goto_master(collapsed=False, top=False)

                # Click on the prestige button, and check for the prompt confirmation being present. Sleeping
                # slightly here to ensure that connections issues do not cause the prestige to be misfire.
                click_on_point(self.master_locs["prestige"], pause=1)

                prestige_found, prestige_position = self.grabber.search(self.images.confirm_prestige)
                if prestige_found:
                    click_on_point(self.master_locs["prestige_confirm"], pause=1)
                    click_on_point(self.master_locs["prestige_final"], pause=10)
                else:
                    # In case of an error during prompt confirmations, click out of any potential
                    # prompts before attempting to continue running.
                    click_on_point(self.master_locs["screen_top"], pause=1)
                    self.goto_master()

                    # Returning here, next prestige hasn't been modified, next loop will
                    # attempt to prestige again.
                    return

                # Additional checks can take place during a prestige.
                self.artifacts()
                self.daily_rewards()
                self.hatch_eggs()

                # Ensure that next action run values are set properly after prestige.
                # Always want to run through actions after a prestige, unlock skills/heroes as soon as possible.
                now = datetime.datetime.now()
                self.next_action_run = now - datetime.timedelta(seconds=1)

                # If a timer is used for prestige.
                if self.config.PRESTIGE_AFTER_X_MINUTES != 0:
                    self.calculate_next_prestige()

    @not_in_transition
    def artifacts(self):
        """Determine whether or not any artifacts should be purchased, and purchase them."""
        if self.config.ENABLE_ARTIFACT_PURCHASE:
            self.logger.info("checking if any artifacts should be upgraded")
            # for now, just click where it likely is.
            self.goto_artifacts(collapsed=False)

            while not self.grabber.search(self.images.spend_max, bool_only=True):
                self.logger.info("changing buy multiplier to spend max")
                click_on_point(self.artifacts_locs["buy_multiplier"], pause=0.5)
                click_on_point(self.artifacts_locs["buy_max"], pause=0.5)

            self.logger.info("searching for {artifact} on screen".format(artifact=self.config.UPGRADE_ARTIFACT))
            while not self.grabber.search(self.artifacts_images.get(self.config.UPGRADE_ARTIFACT), bool_only=True):
                drag_mouse(self.locs.scroll_start, self.locs.scroll_bottom_end)

            self.logger.info("{artifact} has been found, upgrading now".format(artifact=self.config.UPGRADE_ARTIFACT))

            # Making it here means the artifact in question has been found.
            found, position = self.grabber.search(getattr(self.images, self.config.UPGRADE_ARTIFACT))
            new_x = position[0] + self.artifacts_locs["artifact_push"]["x"]
            new_y = position[1] + self.artifacts_locs["artifact_push"]["y"]

            # Currently just upgrading the artifact to it's max level. Future updates may include the ability
            # to determine how much to upgrade an artifact by.
            click_on_point((new_x, new_y), pause=0.5)

    @not_in_transition
    def check_tournament(self):
        """Check that a tournament is available/active. Tournament will be joined if a new possible."""
        if self.config.ENABLE_TOURNAMENTS:
            self.logger.info("beginning tournament check now")
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
                self.logger.info("tournament is available, checking status")
                click_on_point(self.locs.tournament, pause=2)
                found, position = self.grabber.search(self.images.join)
                if found:
                    self.logger.info("joining new tournament and performing prestige now")
                    click_on_point(self.locs.join, pause=2)
                    click_on_point(self.locs.tournament_prestige, pause=10)

                # Otherwise, maybe the tournament is over? Or still running.
                else:
                    collect_found, collect_position = self.grabber.search(self.images.collect_prize)
                    if collect_found:
                        self.logger.info("tournament has ended, collecting prize")
                        click_on_point(self.locs.collect_prize, pause=2)
                        click_on_point(self.locs.game_middle, clicks=10, interval=0.5)

                    # Exit tournament screen, and ensure master panel is open.
                    else:
                        self.logger.info("tournament is still in process, exiting now")
                        click_on_point(self.master_locs["screen_top"], pause=1)
                        self.goto_master()

    @not_in_transition
    def daily_rewards(self):
        """Collect any daily gifts if they're available."""
        self.logger.info("checking if any daily rewards are available")
        self.goto_master()

        reward_found = self.grabber.search(self.images.daily_reward, bool_only=True)
        if reward_found:
            self.logger.info("rewards are available, collecting now")
            click_on_point(self.locs.open_rewards, pause=1)
            click_on_point(self.locs.collect_rewards, pause=1)
            click_on_point(self.locs.game_middle, 5, interval=0.5, pause=1)
            click_on_point(self.master_locs["screen_top"], pause=1)

    @not_in_transition
    def hatch_eggs(self):
        """Hatch any eggs if they're available."""
        if self.config.ENABLE_EGG_COLLECT:
            self.logger.info("checking if any eggs are ready to hatch")
            self.goto_master()

            egg_found = self.grabber.search(self.images.hatch_egg, bool_only=True)
            if egg_found:
                self.logger.info("eggs are available, hatching now")
                click_on_point(self.locs.hatch_egg, pause=1)
                click_on_point(self.locs.game_middle, 5, interval=0.5, pause=1)

    @not_in_transition
    def clan_battle(self):
        """
        Participant in a clan battle if one is available. Based on the amount of clan quests configured in the
        users config file, this will potentially spend diamonds.
        """
        if self.config.ENABLE_CLAN_QUEST:
            now = datetime.datetime.now()
            if now > self.next_clan_battle_check:
                self.logger.info("checking if a clan battle is ready")
                self.goto_master()

                # Clicking into the main clan page in game. Slight pause is also initiated in case
                # any server lag is present and may cause the clan load to be longer.
                click_on_point(self.locs.clan, pause=5)

                # Click into the clan quest.
                click_on_point(self.locs.clan_quest, pause=2)

                # Is a clan quest battle available for us to participate in?
                if self.grabber.search(self.images.fight, bool_only=True):
                    # If the entry fee into the first clan quest is diamond blocked, it means the last
                    # clan quest probably hasn't reset since we last participated. Exit here to ensure
                    # diamonds are not spent on accident. This conditional is unlikely due to the image
                    # check performed above, but worth having.
                    if self.grabber.search(self.images.diamond, bool_only=True):
                        self.logger.info("diamonds are required to begin battle, exiting clan quest")
                        self.calculate_next_clan_battle_check()
                        return

                    self.logger.info("clan battle is ready and available, participating now")

                    # Begin first clan quest, using a datetime to determine when to stop clicking. Datetime is
                    # slightly above the normal time for a clan quest, just to provide enough of a threshold to
                    # account for lag or a buggy clan fight.
                    click_on_point(self.locs.clan_fight, pause=2)
                    end = datetime.datetime.now() + datetime.timedelta(seconds=40)
                    while datetime.datetime.now() < end:
                        click_on_point(self.locs.game_middle, pause=0.07)

                    self.stats.clan_ship_battles += 1
                    # Additional sleep in case post fight is lagging.
                    sleep(8)

                    # Perform check to determine if an additional fight should take place (5 diamonds).
                    if self.config.ENABLE_EXTRA_FIGHT:
                        if self.grabber.search(self.images.deal_110_next_attack, bool_only=True):
                            self.logger.info("spending five diamonds to participate in clan battle again.")
                            click_on_point(self.locs.clan_fight, pause=1)
                            click_on_point(self.locs.diamond_okay, pause=5)

                            end = datetime.datetime.now() + datetime.timedelta(seconds=40)
                            while datetime.datetime.now() < end:
                                click_on_point(self.locs.game_middle, pause=0.07)

                            self.stats.clan_ship_battles += 1
                            # Additional sleep in case post fight is lagging again.
                            sleep(5)
                        else:
                            self.logger.info("first fight was successful, the next one costs more than five diamonds, "
                                             "exiting instead of fighting again")

                # All clan quests should be finished now, safe to exit the panel and resume bot.
                click_on_point(self.locs.clan_quest_exit, pause=2)
                click_on_point(self.locs.clan_leave_screen, clicks=5, pause=1)

                self.calculate_next_clan_battle_check()

    @not_in_transition
    def collect_ad(self):
        """Collect ad if one is available on the screen."""
        self.logger.info("collecting any ads available on the screen")
        if self.grabber.search(self.images.collect_ad, bool_only=True):
            if self.config.ENABLE_PREMIUM_AD_COLLECT:
                self.logger.info("accepting premium ad")
                self.stats.premium_ads += 1
                click_on_point(self.locs.collect_ad, pause=1)
            else:
                self.logger.info("declining premium ad")
                click_on_point(self.locs.no_thanks, pause=1)

    @not_in_transition
    def fight_boss(self):
        """Ensure that the boss is being fought if it isn't already."""
        self.logger.info("checking if the boss is not currently being fought")
        if self.grabber.search(self.images.fight_boss, bool_only=True):
            self.logger.info("attempting to fight boss")
            click_on_point(self.locs.fight_boss, pause=0.5)

    @not_in_transition
    def tap(self):
        """Perform simple screen tap over entire game area."""
        if self.config.ENABLE_TAPPING:
            self.logger.info("beginning tapping process in game")

            taps = 0
            for point in self.locs.fairies_map:
                taps += 1

                # Check for an ad as the tapping process occurs. Click and return early if one is available.
                if taps == 5:
                    if self.grabber.search(self.images.collect_ad, bool_only=True):
                        self.collect_ad()
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
            self.logger.info("beginning process to activate skills")
            self.goto_master()

            # Datetime to determine skill intervals.
            now = datetime.datetime.now()
            skills = [s for s in self.skill_order if s[0] != 0]
            next_key = "next_"

            if self.config.FORCE_ENABLED_SKILLS_WAIT and not force:
                attr = getattr(self, next_key + skills[0][1])
                if not now > attr:
                    self.logger.info("skills will only be activated when {key} is ready.".format(key=skills[0][1]))
                    self.logger.info("{key} will be ready to activate in: {time}".format(
                        key=skills[0][1], time=strfdelta(attr - now))
                    )
                    return

            # If this point is reached, ensure no panel is currently active, and begin skill activation.
            self.no_panel()

            if force:
                self.logger.info("forcing skill activation instead of waiting")

            for skill in skills:
                self.logger.info("activating {skill} now".format(skill=skill[1]))
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
        self.logger.debug("using {top_find} as top_find image".format(top_find=top_find))
        self.logger.debug("using {bot_find} as bottom_find image".format(bot_find=bottom_find))

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
            "artifacts", self.images.artifacts_active, self.images.artifacts_discovered, None,
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
        self.logger.info("attempting to close any open panels in game")
        while self.grabber.search(self.images.exit_panel, bool_only=True):
            click_on_point(self.locs.close_bottom, offset=2)
            if not self.grabber.search(self.images.exit_panel, bool_only=True):
                break

            click_on_point(self.locs.close_top, offset=2)
            if not self.grabber.search(self.images.exit_panel, bool_only=True):
                break

    def soft_shutdown(self):
        """Perform a soft shutdown of the bot, taking care of any cleanup or related tasks."""
        self.logger.info("attempting to run soft shutdown before bot execution is terminated")

        # Update bot statistics before shutdown.
        self.update_stats(force=True)

    def restart_game(self):
        """
        Attempt to restart the game within the emulator. Currently supported emulators include:

        - Nox
        """
        from pyautogui import moveTo
        self.logger.info("attempting to restart the game within {emulator} emulator".format(
            emulator=self.config.EMULATOR
        ))
        click_on_point(self.emulator_locs["opened_apps"], pause=1)
        moveTo(self.emulator_locs["close_game"][0], self.emulator_locs["close_game"][1], pause=3)

        click_on_point(self.emulator_locs["close_game"], pause=2)

        # Opening the game, waiting at least twenty seconds before continuing.
        click_on_point(self.emulator_locs["launch_game"], pause=20)

    def run(self):
        """
        A run encapsulates the entire bot runtime process into a single function that conditionally
        checks for different things that are currently happening in the game, then launches different
        automated action within the emulator.
        """
        try:
            self.logger.info("running bot now...")
            self.goto_master()

            if self.config.ACTIVATE_SKILLS_ON_START:
                self.level_master()
                self.level_skills()
                self.activate_skills(force=True)

            if self.config.RUN_ACTIONS_ON_START:
                self.actions(force=True)
            else:
                self.calculate_next_action_run()

            # Main game loop.
            while True:
                if self.TERMINATE:
                    self.logger.info("bot termination flag has been set, exiting")
                    break

                # Main bot game loop process / actions.
                self.goto_master()
                self.fight_boss()
                self.tap()
                self.collect_ad()
                self.parse_current_stage()
                self.prestige()
                self.clan_battle()
                self.actions()
                self.activate_skills()
                self.update_stats()

        except FailSafeException:
            # Making use of the PyAutoGUI FailSafeException to allow some cleanup to take place
            # before totally exiting. Only if the CTRL key is held down when exception is thrown.
            self.logger.info(
                "bot is shutting down now, please press the {key} key to perform a soft shutdown in {seconds} "
                "second(s).".format(
                    key=self.config.SOFT_SHUTDOWN_KEY, seconds=self.config.SHUTDOWN_SECONDS)
            )

            # Create datetime objects to specify how long until the bot shutdowns.
            now = datetime.datetime.now()

            # Give a user five seconds before going through with normal shutdown.
            shutdown_at = now + datetime.timedelta(seconds=self.config.SHUTDOWN_SECONDS)

            # Flag to determine soft shutdown status.
            soft = False

            while now < shutdown_at:
                now = datetime.datetime.now()
                if keyboard.is_pressed(self.config.SOFT_SHUTDOWN_KEY) and not soft:
                    soft = True
                    self.logger.info("soft shutdown will now take place in {time}".format(
                        time=strfdelta(shutdown_at - now))
                    )

            if soft:
                self.logger.info("{key} was activated during shutdown, soft shutdown will execute now".format(
                    key=self.config.SOFT_SHUTDOWN_KEY)
                )
                self.soft_shutdown()

        # Any other exception, perform soft shutdown before termination.
        except BotException as exc:
            self.logger.critical("bot has encountered critical error: {exc}".format(exc=exc))
            if self.config.SOFT_SHUTDOWN_ON_CRITICAL_ERROR:
                self.soft_shutdown()
