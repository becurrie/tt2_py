from django.contrib.auth.models import User

from .constants import *

from titandash.models.queue import Queue
from titandash.bot.core.window import WindowHandler
from titandash.bot.core.bot import Bot

from threading import Thread

import time
import string


def title(value):
    """Remove underscored and replace with spaces. Apply 'title' modification to value."""
    capped = [char for char in string.capwords(value.replace("_", " "))]

    # If a string also contains some letters after an apostrophe, we should capitalize that
    # letter... (ie: O'ryan's Charm -> O'Ryan's Charm).
    for index, char in enumerate(capped):
        if char is "'":
            if index + 1 <= len(capped):
                if capped[index + 2] != ' ':
                    capped[index + 1] = capped[index + 1].upper()

    return "".join(capped)


def start(config, window, shortcuts, instance):
    """
    Start a new Bot Process if one does not already exist. We can check for an existing one by looking at the
    current Bot model and the data present. If one does exist, we can send a termination signal to ensure that
    the old bot has stopped and that a new Bot Session can be initialized.
    """
    from titandash.models.configuration import Configuration

    if instance.state == RUNNING:
        Queue.objects.add(function="terminate", instance=instance)
    if instance.state == PAUSED:
        Queue.objects.add(function="resume", instance=instance)

    while instance.state != STOPPED:
        time.sleep(0.2)
        instance = instance.refresh_from_db()
        continue

    # At this point. The bot is no longer running, and a new instance can be started up
    # in a new thread.
    # Bot initialization will handle the creation of a new BotInstance.
    if instance.state == STOPPED:
        win = WindowHandler().grab(hwnd=window)
        configuration = Configuration.objects.get(pk=config)
        Thread(target=Bot, kwargs={
            'configuration': configuration,
            'window': win,
            'enable_shortcuts': shortcuts,
            'instance': instance,
            'start': True
        }).start()


def pause(instance):
    """Attempt to pause the current BotInstance if it is currently running."""
    if instance.state == STOPPED:
        return

    Queue.objects.add(function="pause", instance=instance)


def stop(instance):
    """Attempt to stop the current BotInstance if it is currently running."""
    if instance.state == STOPPED:
        return

    Queue.objects.add(function="terminate", instance=instance)


def resume(instance):
    """Attempt to resume the current BotInstance if it is currently running."""
    if instance.state == STOPPED:
        return

    Queue.objects.add(function="resume", instance=instance)


# Import/Export Functionality.
def import_model_kwargs(export_string, compression_keys=None):
    """
    Import a given export string back into the current model that the mixin is present on.
    """
    kwargs = {}
    # Let's begin parsing out the export string provided...
    # Fixup leading/trailing whitespace issues.
    export_string = export_string.lstrip().rstrip()
    export_attrs = export_string.split(ATTR_SEPARATOR)

    for attribute in export_attrs:
        key, value = attribute.split(VALUE_SEPARATOR)
        key_found = False

        # Initially, we must check if a compression key was used to shorten the key of this value.
        # If so, we'll convert back to the correct value name.
        if compression_keys:
            for c_key, c_val in compression_keys.items():
                if key == str(c_val):
                    key = c_key
                    key_found = True
                    break

        # Break if the key wasn't found in our compression keys list.
        # Since this means the configuration must be old and removed now.
        if not key_found:
            continue

        # At this point, "key" should be the name of a value available on the model.
        # We now need to parse the value itself...
        # Is a boolean value being used (BOOL SEP + "T" Or "F")/
        if len(value) == 3 and BOOLEAN_PREFIX in value:
            if value[2] == "T":
                value = True
            elif value[2] == "F":
                value = False

            kwargs[key] = value
            continue

        # Is a foreign key value specified?
        if FK_PREFIX in value:
            kwargs[key] = [value.replace(FK_PREFIX, "")]
            if kwargs[key][0] == "None":
                kwargs[key][0] = None
            continue

        # Is a many to many value specified?
        if M2M_PREFIX in value:
            value = value.replace(M2M_PREFIX, "")
            kwargs[key] = [val for val in value.split(M2M_SEPARATOR)]
            for index, v in enumerate(kwargs[key]):
                if v == "None":
                    kwargs[key][index] = None
            continue

        # This case means we reached some sort of char field of plain
        # text input field.
        try:
            kwargs[key] = int(value)
        except ValueError:
            if value == "None":
                kwargs[key] = None
            else:
                kwargs[key] = value

    # We now have the kwargs associated with this exported model.
    return kwargs


def get_titan_user():
    """
    Retrieve the titan user, if it already exists, we use the existing one, otherwise
    a new one with proper defaults is created.
    """
    try:
        return User.objects.get(username="titan")
    except User.DoesNotExist:
        return User.objects.create_superuser(
            username="titan",
            password="titan",
            first_name="Titan",
            last_name="Dash",
            email="titan@dash.com"
        )
