from django.core.cache import cache

from settings import LOG_DIR

from titandash.bot.external.imagesearch import *
from titandash.models.globals import GlobalSettings

from .maps import MASTER_LOCS
from .constants import (
    STATS_LOOKUP_MULTIPLIER, STATS_TIMEDELTA_STR,
    LOGGER_NAME, LOGGER_FORMAT, LOGGER_FILE_NAME, LOGGER_FILE_NAME_STRFMT,
    RAID_NOTIFICATION_MESSAGE
)

from pyautogui import _failSafeCheck

from channels.generic.websocket import async_to_sync
from channels.layers import get_channel_layer

from twilio.rest import Client

from string import Template, Formatter
from pyautogui import *

import datetime
import logging
import time

logger = logging.getLogger(LOGGER_NAME)


class GlobalsChecker:
    """
    Using a pseudo lazy failsafe checking mechanism to avoid making multiple queries to our database
    constantly to check if failsafe functionality is setup.
    """
    def __init__(self):
        self.cache_key = "globals_cache"

    def _get_cache(self):
        """
        Retrieve the cached instance of our global settings instance.

        Resetting the cache every five seconds so that we retain a good amount of cached
        information, but still allow changes made to the instance to propagate into checks.
        """
        return cache.get_or_set(
            key=self.cache_key,
            default=self.__instance,
            timeout=3
        )

    @staticmethod
    def __instance():
        """
        Static method used to retrieve the global settings instance object from the database.
        """
        return GlobalSettings.objects.grab()

    def _failsafe_enabled(self):
        """
        Determine if our cached globals currently have failsafe functionality enabled.
        """
        return self._get_cache().failsafe_enabled

    def _events_enabled(self):
        """
        Determine if our cached globals currently have event functionality enabled.
        """
        return self._get_cache().events_enabled

    def _pihole_ads_enabled(self):
        """
        Determine if our cached globals currently have pihole ad functionality enabled.
        """
        return self._get_cache().pihole_ads_enabled

    def _welcome_screen_checks_enabled(self):
        """
        Determine if our cached globals currently have welcome screen checks enabled.
        """
        return self._get_cache().welcome_screen_checks_enabled

    def _rate_screen_checks_enabled(self):
        """
        Determine if our cached globals currently have rate screen checks enabled.
        """
        return self._get_cache().rate_screen_checks_enabled

    def _logging_level(self):
        return self._get_cache().logging_level

    def failsafe(self):
        """
        Perform a failsafe check if it's currently enabled.
        """
        if self._failsafe_enabled():
            _failSafeCheck()

    def events(self):
        """
        Return a boolean to represent if events are enabled.
        """
        return self._events_enabled()

    def pihole_ads(self):
        """
        Return a boolean to represent if pihole ads are enabled.
        """
        return self._pihole_ads_enabled()

    def welcome_screen_checks(self):
        """
        Return a boolean to represent if welcome screen checks are enabled.
        """
        return self._welcome_screen_checks_enabled()

    def rate_screen_checks(self):
        """
        Return a boolean to represent if rate screen checks are enabled.
        """
        return self._rate_screen_checks_enabled()

    def logging_level(self):
        return self._logging_level()


globals = GlobalsChecker()


def sleep(seconds):
    """
    Wrap the time.sleep method to allow for logging the time to sleep for.
    """
    logger.debug("sleeping for {seconds} second(s)".format(seconds=seconds))
    time.sleep(seconds)


class DeltaTemplate(Template):
    delimiter = "%"


def strfdelta(timedelta, fmt=STATS_TIMEDELTA_STR):
    """
    Format a timedelta object in the given format.
    """
    f = Formatter()
    d = {}
    lst = {"D": 86400, "H": 3600, "M": 60, "S": 1}
    k = map(lambda x: x[1], list(f.parse(fmt)))
    remainder = int(timedelta.total_seconds())

    for i in ("D", "H", "M", "S"):
        if i in k and i in lst.keys():
            d[i], remainder = divmod(remainder, lst[i])

    for key, value in d.items():
        if value < 10 and "D" not in key:
            d[key] = "0" + str(value)

    return f.format(fmt, **d)


def strfnumber(number):
    """
    Return a number with properly formatted thousand separators.

    ie: 43123 -> "43,123"
    """
    if number:
        return "{:,}".format(int(number))
    else:
        return None


def convert(value):
    """
    Attempt to convert a given value into its appropriate integer value.
    """
    try:
        return float(value)
    except ValueError:
        pass
    except TypeError:
        return value

    unit = value[-1]
    try:
        number = float(value[:-1])
    except ValueError:
        number = None

    if not number:
        return value

    if unit in STATS_LOOKUP_MULTIPLIER:
        return STATS_LOOKUP_MULTIPLIER[unit] * number
    return number


def delta_from_values(values):
    """
    Generate a delta from the given values. The values expected here should contain the number and
    letter associated with the value being parsed (ie: ["1d", "4h", "32m"])
    """
    kwargs = {
        "days": 0,
        "hours": 0,
        "minutes": 0
    }

    try:
        for value in values:
            # DAYS.
            if value.endswith("d"):
                kwargs["days"] = int(value[:-1])
            # HOURS.
            if value.endswith("h"):
                kwargs["hours"] = int(value[:-1])
            # MINUTES.
            if value.endswith("m"):
                kwargs["minutes"] = int(value[:-1])

    except ValueError:
        return None

    delta = datetime.timedelta(**kwargs)
    if delta.total_seconds() == 0:
        return None

    return delta


def send_raid_notification(sid, token, from_num, to_num, instance=None):
    """
    Using the Twilio Rest Client, send a sms message to the specified phone number.
    """
    if instance:
        msg = "{instance}: {body}".format(
            instance=instance,
            body=RAID_NOTIFICATION_MESSAGE
        )
    else:
        msg = RAID_NOTIFICATION_MESSAGE

    return Client(sid, token).messages.create(
        to=to_num,
        from_=from_num,
        body=msg
    )


def gen_offset(point, amount):
    """
    Add some offset to a given point.
    """
    if amount == 0:
        return point

    rand_x = random.randint(-amount, amount)
    rand_y = random.randint(-amount, amount)

    return point[0] + rand_x, point[1] + rand_y


def click_on_point(point, window, clicks=1, interval=0.0, button="left", pause=0.0, offset=5):
    """
    Click on the specified X, Y value based on the point passed along as a parameter.
    """
    if offset != 0:
        point = gen_offset(point, offset)

    logger.debug("{button} clicking {point} on screen {clicks} time(s) with {interval} interval and {pause} pause".format(button=button, point=point, clicks=clicks, interval=interval, pause=pause))
    window.click(
        point=(point[0], point[1]),
        clicks=clicks,
        interval=interval,
        button=button,
        pause=pause
    )


def click_on_image(window, image=None, pos=None, button="left", pause=0.0):
    """
    Click on the specified image on the screen.
    """
    logger.debug("{button} clicking on {image} located at {pos} with {pause}s pause".format(button=button, image=image, pos=pos, pause=pause))
    click_image(
        window=window,
        image=image,
        pos=pos,
        action=button,
        timestamp=0,
        pause=pause
    )


def drag_mouse(start, end, window, button="left", pause=0.5):
    """
    Drag the mouse from the starting position, to the end position.
    """
    logger.debug("{button} clicking and dragging mouse from {start} to {end}".format(button=button, start=start, end=end))
    window.drag_mouse(
        start=start,
        end=end,
        button=button,
        pause=pause
    )


class UnrecoverableTransitionState(Exception):
    pass


def in_transition_func(*args, max_loops, **kwargs):
    """
    Directly call this function to perform the transition state check.
    """
    _self = args[0]
    loops = 0

    while True:
        # Check for the early game/non vip game prompts that may pop up
        # while playing the game.
        _self.welcome_screen_check()
        _self.rate_screen_check()

        # Is a panel open that should be closed? This large exit panel will close any in game
        # panels that may of been opened on accident.
        _self.find_and_click(
            image=_self.images.large_exit_panel,
        )

        # Is an ad panel open that should be accepted/declined?
        _self.collect_ad_no_transition()

        # Check the screen for any images that would represent a non active transition state.
        # If any of these are found, it's safe to say that we are NOT in a transition.
        if _self.grabber.search(
                image=[
                    _self.images.exit_panel, _self.images.clan_raid_ready, _self.images.clan_no_raid, _self.images.daily_reward, _self.images.icon_boss,
                    _self.images.fight_boss, _self.images.hatch_egg, _self.images.leave_boss, _self.images.settings, _self.images.tournament,
                    _self.images.pet_damage, _self.images.master_damage
                ],
                bool_only=True
        ):
            break

        # Clicking the top of the screen in case of a transition taking place due to something being
        # present on the screen that requires clicking.
        _self.click(
            point=MASTER_LOCS["screen_top"],
            clicks=3,
            pause=0.5
        )
        _self.logger.info("in a transition? waiting briefly and trying again...")
        sleep(0.25)

        loops += 1
        if loops == max_loops:
            # In this case, the game may of broke? A crash may of occurred. It's safe to attempt to restart the
            # game at this point.
            _self.logger.error("unable to resolve transition state of game, exiting...")

            # Raising our termination error manually. Since our main loop that is accessing this function
            # could contain a while loop, we want to ensure we terminate here.
            raise UnrecoverableTransitionState()


class TitanBotLoggingHandler(logging.StreamHandler):
    def __init__(self, instance, stream=None):
        super(TitanBotLoggingHandler, self).__init__()

        self.instance = instance
        self.channel_layer = get_channel_layer()
        self.group_name = 'titan_log'

    def format_record(self, record):
        return "[{asctime}] {levelname} [{instance}] [{filename} - {funcName} ] {message}".format(
            asctime=record.asctime,
            levelname=record.levelname,
            instance=self.instance.name,
            filename=record.filename,
            funcName=record.funcName,
            message=record.message
        )

    def emit(self, record):
        async_to_sync(self.channel_layer.group_send)(
            self.group_name, {
                'type': 'emitted',
                'instance_id': self.instance.pk,
                'record': {
                    "message": self.format_record(record)
                }
            }
        )


def generate_log_file_name(instance):
    """
    Generate a log file name with the current date.
    """
    init_date_fmt = datetime.datetime.strftime(datetime.datetime.now(), LOGGER_FILE_NAME_STRFMT)
    init_date_fmt = instance.name.replace(" ", "_").lower() + "_" + init_date_fmt
    return "{log_dir}/{name}.log".format(log_dir=LOG_DIR, name=init_date_fmt)


def make_logger(instance, log_level="INFO", log_format=LOGGER_FORMAT, log_name=LOGGER_NAME, log_file=LOGGER_FILE_NAME):
    """
    Grab the logging instance that will be used throughout bot runtime.
    """
    log_formatter = logging.Formatter(log_format.format(instance=instance.name))

    # Grab the current timestamp.
    # We use this to ensure out getLogger call always gets a new logger.
    # Since we can create and kill instances in the same memory space.
    # We always want a unique instance to add handlers too.
    _current = str(datetime.datetime.now().timestamp()).replace(".", "-")
    _logger = logging.getLogger("{log_name}.{instance}.{current}".format(log_name=log_name, instance=instance.pk, current=_current))

    if not log_file:
        log_file = generate_log_file_name(instance=instance)

    fh = logging.FileHandler(log_file)              # File Handler. (log_dir/log_name.log).
    ch = logging.StreamHandler()                    # Stream/Console Handler.
    sh = TitanBotLoggingHandler(instance=instance)  # Custom Websocket-Compat Handler.

    # Iter through handles for readability.
    for _handle in [fh, ch, sh]:
        # We need to also include the proper formatter
        # and handler onto each handle and ensure they're added
        # to our logger correctly.
        _handle.setFormatter(log_formatter)
        _logger.addHandler(hdlr=_handle)

    _logger.setLevel(level=log_level)

    # Return our logger for use once it's been initialized and setup
    # with all of the proper handlers we expect.
    return _logger


def timeit(method):
    """
    Timeit decorator used to measure the execution time of functions.
    """
    def timed(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()
        if 'log_time' in kw:
            name = kw.get('log_name', method.__name__.upper())
            kw['log_time'][name] = int((te - ts) * 1000)
        else:
            print('%r  %2.2f ms' % (method.__name__, (te - ts) * 1000))
        return result
    return timed
