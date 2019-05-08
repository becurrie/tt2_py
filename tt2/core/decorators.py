"""
decorators.py

Any decorators used by the bot should be placed here. Mostly used to store the _not_in_transition decorator
that handles pausing the bot and fixing any issues that may come up when a transition state is detected.

A transition state refers to one of the following states in game:
    - Stage changing over (screen overlay present during).
    - Premium ad available (no way to click out of this other than accepting/declining).

These states are handled through clicking on the top of the screen if required. The ad collection
is handled manually by clicking on either accept or decline based on user settings.
"""
from tt2.core.utilities import in_transition_func, sleep
from random import randint


def not_in_transition(function, max_loops=30):
    """
    Stop functionality until some sort of game object is on the screen that represents the game not being
    in a transition state. If a transition state is detected, click the top of the screen a couple of
    times.

    We will provide a max amount of loops before giving up and attempting to continue with bot functionality.

    Note, this is used as a decorator function, placed above functions to ensure that the in_transition_func is called
    before the actual function is called. in_transition_func can be called directly if needed in specific
    parts of the bot.
    """
    def in_transition(*args, **kwargs):
        """Looping until a transition state is no longer found. Or max loops has been reached."""
        in_transition_func(*args, max_loops=max_loops)
        return function(*args, **kwargs)
    return in_transition


def wait_afterwards(function, floor, ceiling):
    """Delay a function after it's been called for a random amount of seconds between the specified floor and ceiling."""
    def wrapped(*args, **kwargs):
        function(*args, **kwargs)
        sleep(randint(floor, ceiling))
    return wrapped
