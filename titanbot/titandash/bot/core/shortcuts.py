"""
shortcuts.py

Encapsulating the threading functionality that is used by the keyboard shortcuts present
within the Bot. Used to ensure the Thread is stoppable while still using our
while True loop to always be waiting for I/O.
"""
from django.utils import timezone

from titandash.models.queue import Queue
from titandash.bot.core.constants import FUNCTION_SHORTCUTS, SHORTCUT_FUNCTIONS

import keyboard
import operator
import collections
import datetime


SHIFT = "shift"
CTRL = "ctrl"
ALT = "alt"

_HOOKED = False
LOGGERS = []
INSTANCES = []
COOLDOWN = 2

TIMESTAMP = timezone.now()
RESUME = timezone.now()

CURRENT = dict()
INDEX = 0


def add_handle(instance, logger):
    """
    Add a new handler to our shortcuts module.

    Each handler is added to our globally available data sets, and are used when a shortcut
    is activated to send out a log message, as well as queue up the function specified.
    """
    global INSTANCES, LOGGERS

    INSTANCES.append(instance)
    LOGGERS.append(logger)
    logger.info("{instance} added to shortcut module.".format(instance=instance))


def clear_handles():
    """
    Clear all handlers currently present.
    """
    global INSTANCES, LOGGERS

    INSTANCES.clear()
    LOGGERS.clear()


def hook():
    """
    Hook the keyboard modules on_press and on_release functionality with our custom
    shortcuts functionality.

    We only ever hook once, and our loggers/instances present are actually used when
    a callback is executed.
    """
    global _HOOKED

    if not _HOOKED:
        keyboard.on_press(callback=on_press)
        keyboard.on_release(callback=on_release)

        # Flipping our flag now, hook will be called again for each instance
        # being started, but only one hook call is ever successfully called.
        _HOOKED = True


def unhook(instance, logger):
    """
    Unhook the specified instance from the shortcuts module.

    This is done when a session is terminated through some means available to the user, or an error occurs.

    When this happens, we may have other instances still running, in which case, we want to only remove
    the specified instance from our logger/instances list.
    """
    global INSTANCES, LOGGERS

    for index, _instance in enumerate(INSTANCES):
        if instance == _instance:
            del INSTANCES[index]
            break
    for index, _logger in enumerate(LOGGERS):
        if logger == _logger:
            del LOGGERS[index]
            break


def _fix_event(event):
    """
    Fix the event so that any shift, ctrl or alt buttons can be used to initiate a combo.
    """
    split = event.name.split(" ")[-1]
    if split in [SHIFT, CTRL, ALT]:
        return split

    return event.name


def _log(message, level="info"):
    """
    Generate a log message for each available module logger present.
    """
    global LOGGERS

    # Looping through each logger available, sending the specified message to them.
    # We do this so we can have multiple instances using the same keyboard events.
    for logger in LOGGERS:
        getattr(logger, level)(message)


def _queue(function):
    """
    Generate a queue object for the specified function for each available instance.
    """
    global INSTANCES

    # Looping through each instance available, generating a queue object for
    # all of them. Ensuring that multiple instances generate the same functions.
    for instance in INSTANCES:
        Queue.objects.create(function=function, instance=instance)


def on_press(event):
    """
    When a keypress takes place, some checks take place to fixup the event passed and additional checks
    are present to allow a user to use keyboard combinations to activate functionality within a Bot.
    """
    global TIMESTAMP, INDEX, RESUME, INSTANCES

    TIMESTAMP = timezone.now()
    if INDEX < 0:
        INDEX = 0
    if event:
        key = _fix_event(event=event)
        if key in CURRENT:
            return

        # Determine if the key pressed is present in any of the available shortcuts.
        for short in FUNCTION_SHORTCUTS.keys():
            if key in short.split("+"):
                CURRENT[key] = INDEX
                INDEX += 1
                break

        if len(CURRENT) > 0:
            combo = "+".join(collections.OrderedDict(sorted(CURRENT.items(), key=operator.itemgetter(1))).keys())
            if combo in FUNCTION_SHORTCUTS:
                if TIMESTAMP > RESUME:
                    _queue(function=FUNCTION_SHORTCUTS[combo])
                    _log(message="{combo} pressed, adding '{func}' to queued functions...".format(combo=combo, func=FUNCTION_SHORTCUTS[combo]))
                    RESUME = RESUME + datetime.timedelta(seconds=1)


def on_release(event):
    """When a keypress is released, removing that key from the current set of active keys."""
    global CURRENT, INDEX

    try:
        CURRENT.pop(_fix_event(event=event))
        INDEX -= 1
    except KeyError:
        pass
