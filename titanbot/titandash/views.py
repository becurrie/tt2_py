from django.shortcuts import render
from django.http.response import JsonResponse
from django.core.cache import cache
from django.conf import settings

from django.db.models import Avg
from django.urls import reverse

from titanauth.authentication.wrapper import AuthWrapper
from titanauth.models.release_info import ReleaseInfo

from titandash.utils import start, pause, stop, resume, title
from titandash.constants import RUNNING, PAUSED, STOPPED, CACHE_TIMEOUT
from titandash.models.bot import BotInstance
from titandash.models.statistics import Session, Statistics, Log, ArtifactStatistics
from titandash.models.clan import RaidResult
from titandash.models.artifact import Artifact, Tier
from titandash.models.configuration import Configuration, ThemeConfig
from titandash.models.prestige import Prestige
from titandash.models.queue import Queue
from titandash.bot.core.window import WindowHandler
from titandash.bot.core.constants import QUEUEABLE_FUNCTIONS, QUEUEABLE_TOOLTIPS, SHORTCUT_FUNCTIONS

from io import BytesIO

import os
import datetime
import base64
import json


def dashboard(request):
    """Main dashboard view."""
    ctx = {
        "configurations": [],
        "windows": [],
        "queueable": []
    }

    # Grab all configurations present to send to the dashboard.
    for config in Configuration.objects.all():
        ctx["configurations"].append({"id": config.pk, "name": config.name})

    wh = WindowHandler()
    wh.enum()
    for hwnd, window in wh.filter().items():
        ctx["windows"].append(window.json())

    ctx["windows"].reverse()

    # Grab all queueable functions.
    for queue in QUEUEABLE_FUNCTIONS:
        ctx["queueable"].append({
            "name": title(queue),
            "func": queue,
            "tooltip": QUEUEABLE_TOOLTIPS[queue]
        })

    return render(request, "dashboard.html", context=ctx)


def release(request):
    """
    Perform a request to determine if the current release has had it's information shown to the user.

    Once information is shown once, it does not ever happen again.
    """
    rel = ReleaseInfo.objects.grab(
        version=settings.BOT_VERSION
    )

    # Check if the information has already been displayed to the user, if it has, we
    # can simply return early with a successful request and our flag specifying the state.
    if rel.grabbed:
        return JsonResponse(data={
            "status": "success",
            "state": "shown",
        })

    # Otherwise, let's grab our required information, and return a response with that information.
    try:
        response = {
            "status": "success",
            "state": "not_shown",
            "release": AuthWrapper().release_information(
                version=rel.version
            )
        }

        if response["release"]["status"] == "success":
            rel.grabbed = True
            rel.save()

        return JsonResponse(data=response)

    # Catch any exceptions that occur, we can display a simple alert on the users page
    # Letting them know that this failed. They can report this issue if needed now.
    except Exception as exc:
        return JsonResponse(data={
            "status": "error",
            "error": str(exc)
        })


def configurations(request):
    """
    Render a list of all available configurations. The option to export existing configurations should also be available.

    Additionally, this is our list view, so after a add/save, a message should be available to include
    in our contextual data.
    """
    ctx = {"configurations": []}
    for config in Configuration.objects.all():
        ctx["configurations"].append({"config": config, "export": config.export_model()})

    if request.session.get("message"):
        ctx["message"] = request.session.pop("message")

    return render(request, "configurations/configurations.html", context=ctx)


def configuration(request, pk):
    """
    Render a specific configuration for modification.
    """
    config = Configuration.objects.get(pk=pk)
    ctx = config.form_dict()

    return render(request, "configurations/edit_configuration.html", context=ctx)


def add_configuration(request):
    """
    Render a page with default configuration settings to create a new one.

    Visiting this url generates a brand new configuration temporarily to retrieve an instance
    with all its default values set, it is then deleted and only re added once the users has
    audited the options and chosen to save.
    """
    temp = Configuration()
    ctx = temp.form_dict()
    temp.delete()

    return render(request, "configurations/add_configuration.html", context=ctx)


def delete_configuration(request):
    """
    Delete the specified configuration present in the requests GET.
    """
    config = Configuration.objects.get(pk=request.GET.get("id"))
    config.delete()

    return JsonResponse(data={
        "status": "success",
        "message": "Configuration successfully deleted."
    })


def save_configuration(request):
    """
    Save the configuration information specified in the requests POST.
    """
    configuration_kwargs = dict(request.POST)
    existing = configuration_kwargs.get("key", None)[0]

    # Strip out any un-necessary information.
    del configuration_kwargs["csrfmiddlewaretoken"]
    del configuration_kwargs["key"]

    # Fixup values to be compliant with configuration model.
    try:
        for kwarg, value in configuration_kwargs.items():
            if isinstance(value, list):
                if len(value) == 1:
                    if value[0] in ["true", "false"]:
                        if value[0] == "true":
                            configuration_kwargs[kwarg] = True
                        else:
                            configuration_kwargs[kwarg] = False

                        continue

                # Specific values may need to be coerced into a float.
                if kwarg in ["prestige_at_max_stage_percent"]:
                    configuration_kwargs[kwarg] = float(value[0])
                # M2M Fields should just use their base value.
                elif kwarg in ["upgrade_owned_tier", "upgrade_artifacts", "ignore_artifacts"]:
                    configuration_kwargs[kwarg] = value[0]
                else:
                    # Check for an integer type value...
                    try:
                        configuration_kwargs[kwarg] = int(value[0])
                    # Can not be an int... Use first value present.
                    except ValueError:
                        configuration_kwargs[kwarg] = value[0]
    except Exception as exc:
        return JsonResponse(data={
            "status": "error",
            "message": "An error occurred while parsing configuration data. {exc}".format(exc=exc)
        })

    try:
        # Ensure any un needed keys are removed from kwargs.
        fields = [f.name for f in Configuration._meta.get_fields()]
        configuration_kwargs = {k: v for k, v in configuration_kwargs.items() if k in fields}

        # Before saving/creating the configuration, we have to pop out our
        # m2m fields and update them afterwards...
        upgrade_owned_tier = Tier.objects.filter(pk__in=[t for t in configuration_kwargs.pop("upgrade_owned_tier").split(",") if t != ""])
        upgrade_artifacts = Artifact.objects.filter(key__in=[a for a in configuration_kwargs.pop("upgrade_artifacts").split(",") if a != ""])
        ignore_artifacts = Artifact.objects.filter(key__in=[a for a in configuration_kwargs.pop("ignore_artifacts").split(",") if a != ""])

        if existing:
            config = Configuration.objects.filter(pk=existing)
            config.update(**configuration_kwargs)
            config = config.first()
        else:
            config = Configuration.objects.create(**configuration_kwargs)

        config.upgrade_owned_tier.clear()
        config.upgrade_artifacts.clear()
        config.ignore_artifacts.clear()

        config.upgrade_owned_tier.add(*upgrade_owned_tier)
        config.upgrade_artifacts.add(*upgrade_artifacts)
        config.ignore_artifacts.add(*ignore_artifacts)

        config.save()

        # Return a helpful message for use on list view.
        if existing:
            request.session["message"] = "Configuration {name} was saved successfully.".format(name=config.name)
        else:
            request.session["message"] = "Configuration {name} was added successfully.".format(name=config.name)

        return JsonResponse(data={
            "status": "success",
            "message": "Configuration saved."
        })
    except Exception as exc:
        return JsonResponse(data={
            "status": "error",
            "message": "An error occurred while saving the configuration. {exc}".format(exc=exc)
        })


def import_configuration(request):
    """
    Import a configuration with the specified import string.
    """
    import_string = request.GET.get("importString", None)

    if not import_string:
        return JsonResponse(data={
            "status": "error",
            "message": "A configuration string must be specified before attempting to import a configuration."
        })

    # Configuration string exists! Let's attempt the creation of our
    # configuration model now.
    try:
        config = Configuration.import_model(
            export_kwargs=Configuration.import_model_kwargs(
                export_string=import_string
            )
        )
    except Exception as exc:
        return JsonResponse(data={
            "status": "error",
            "message": "An error occurred while importing the specified configuration: {exc}".format(exc=exc)
        })

    return JsonResponse(data={
        "status": "success",
        "message": "Successfully imported configuration.",
        "config": {
            "name": config.name,
            "export": config.export_model(),
            "pk": config.pk,
            "url": reverse("configuration", kwargs={"pk": config.pk}),
            "created": {
                "timestamp": config.created_at.timestamp(),
                "formatted": config.created
            },
            "updated": {
                "timestamp": config.updated_at.timestamp(),
                "formatted": config.updated
            }
        }
    })


def theme_change(request):
    selected = request.GET.get("theme")
    if not selected:
        selected = "default"

    theme = ThemeConfig.objects.grab()
    theme.theme = selected
    theme.save()

    return JsonResponse(data={"status": "success", "message": "Theme was successfully changed to {theme}".format(theme=theme.theme)})


def log(request, pk):
    """Retrieve a particular log file for viewing."""
    ctx = {
        "exists": False,
        "log": None
    }
    _log = Log.objects.get(pk=pk)

    if _log.exists():
        exists = True
        ctx["log"] = _log.json(truncate=True)
    else:
        exists = False

    ctx["exists"] = exists
    ctx["name"] = _log.log_file.split("\\")[-1]

    return render(request, "log.html", context=ctx)


def session(request, uuid):
    """Retrieve a particular session."""
    ctx = {"session": Session.objects.get(uuid=uuid).json()}
    ctx["SESSION_JSON"] = json.dumps(ctx)

    return render(request, "sessions/session.html", context=ctx)


def sessions(request):
    """Retrieve all sessions."""
    ctx = {"sessions": []}
    if request.GET.get("instance"):
        _sessions = Session.objects.filter(instance=BotInstance.objects.get(pk=request.GET.get("instance")))
    else:
        _sessions = Session.objects.filter(instance=BotInstance.objects.grab())

    ctx["sessions"] = [s.json(prestige_count_only=True) for s in _sessions]
    ctx["SESSIONS_JSON"] = json.dumps(ctx)

    # Return only json context instead of rendered template.
    if request.GET.get("context"):
        return JsonResponse(data={
            "table": render(request, "sessions/sessionsTable.html", context=ctx).content.decode()
        })

    return render(request, 'sessions/sessions.html', context=ctx)


def statistics(request):
    if request.GET.get("instance"):
        stats = Statistics.objects.grab(instance=BotInstance.objects.get(pk=request.GET.get("instance")))
    else:
        stats = Statistics.objects.grab(instance=BotInstance.objects.grab())

    ctx = {
        "game_statistics": {title(key): value for key, value in stats.game_statistics.json().items()},
        "bot_statistics": {title(key): value for key, value in stats.bot_statistics.json().items()},
        "progress": stats.game_statistics.progress,
        "played": stats.game_statistics.played,
        "STATISTICS_JSON": json.dumps({
            "game_statistics": stats.game_statistics.json(),
            "bot_statistics": stats.bot_statistics.json()
        })
    }

    if request.GET.get("context"):
        return JsonResponse(data={
            "allStatistics": render(request, "statistics/statisticsTable.html", context=ctx).content.decode(),
            "progress": render(request, "statistics/statisticsProgress.html", context=ctx).content.decode(),
            "played": render(request, "statistics/statisticsPlayed.html", context=ctx).content.decode()
        })

    return render(request, "statistics/allStatistics.html", context=ctx)


def project_settings(request):
    """Main project settings view."""
    return render(request, "projectSettings.html")


def shortcuts(request):
    """View all shortcuts available for use with the bot."""
    ctx = {"shortcuts": {title(k): v.split("+") for k, v in SHORTCUT_FUNCTIONS.items()}}
    return render(request, "shortcuts.html", context=ctx)


def artifacts(request):
    """Retrieve all artifacts owned."""
    ctx = {"artifacts": []}

    if request.GET.get("instance"):
        _artifacts = ArtifactStatistics.objects.grab(instance=BotInstance.objects.get(pk=request.GET.get("instance"))).artifacts.all()
    else:
        _artifacts = ArtifactStatistics.objects.grab(instance=BotInstance.objects.grab()).artifacts.all()

    for artifact_owned in _artifacts:
        ctx["artifacts"].append(artifact_owned.json())

    ctx["artifactsTotalValue"] = Artifact.objects.all().count()
    ctx["artifactsOwnedValue"] = _artifacts.filter(owned=True).count()
    ctx["ARTIFACTS_JSON"] = json.dumps(ctx)

    if request.GET.get("context"):
        return JsonResponse(data={
            "table": render(request, "artifacts/artifactsTable.html", context=ctx).content.decode()
        })

    return render(request, "artifacts/allArtifacts.html", context=ctx)


def all_prestiges(request):
    """Retrieve all prestiges present."""
    # ctx = {"prestiges": [], "avgPrestigeDuration": None, "avgPrestigeStage": None, "totalPrestiges": None}

    # Grab the instance being specified, if none is set, grabbing the base
    # bot instance (default) throughout the grab method below.
    _instance = request.GET.get("instance")

    def __values(qs):
        ctx = {
            "prestiges": [
                cache.get_or_set(
                    key="prestige.{pk}".format(pk=prestige.pk),
                    default=prestige.json,
                    timeout=CACHE_TIMEOUT
                ) for prestige in qs
            ],
            "totalPrestiges": qs.count(),
            "avgPrestigeStage":  qs.aggregate(average_stage=Avg("stage"))["average_stage"],
            "avgPrestigeDuration": qs.aggregate(average_time=Avg("time"))["average_time"],
        }

        if qs.count() == 0:
            ctx["avgPrestigeDuration"] = "00:00:00"
            ctx["avgPrestigeStage"] = 0
        else:
            ctx["avgPrestigeDuration"] = str(ctx["avgPrestigeDuration"]).split(".")[0]
            ctx["avgPrestigeStage"] = int(ctx["avgPrestigeStage"])

        ctx["PRESTIGES_JSON"] = json.dumps(ctx)
        return ctx

    def __prestige_instance():
        """
        Callable used when caching to grab prestiges with a specific instance.
        """
        return __values(qs=Prestige.objects.filter(instance=BotInstance.objects.get(pk=_instance)).order_by("-timestamp"))

    def __prestige_no_instance():
        """
        Callable used when caching to grab prestiges without a specific instance.
        """
        return __values(qs=Prestige.objects.filter(instance=BotInstance.objects.grab()).order_by("-timestamp"))

    if _instance:
        count = Prestige.objects.filter(instance=BotInstance.objects.get(pk=_instance)).count()
        _prestiges = cache.get_or_set(
            key="titan_instance_prestiges.{instance}.{count}".format(instance=instance, count=count),
            default=__prestige_instance,
            timeout=CACHE_TIMEOUT
        )
    else:
        count = Prestige.objects.filter(instance=BotInstance.objects.grab()).count()
        _prestiges = cache.get_or_set(
            key="titan_no_instance_prestiges.{count}".format(count=count),
            default=__prestige_no_instance,
            timeout=CACHE_TIMEOUT
        )

    if request.GET.get("context"):
        return JsonResponse(data={
            "table": render(request, "prestiges/prestigeTable.html", context=_prestiges).content.decode()
        })

    return render(request, "prestiges/allPrestiges.html", context=_prestiges)


def instance(request):
    return JsonResponse(data=BotInstance.objects.get(pk=request.GET.get("instance")).json())


def kill_instance(request):
    bot = BotInstance.objects.get(pk=request.GET.get("instance"))
    if bot.state == RUNNING or bot.state == PAUSED:
        stop(instance=bot)
        bot.stop()

        # Instance is being killed (or attempted). Whether or not it works, we should explicitly
        # set the authentication reference to an offline state.
        AuthWrapper().offline()
        return JsonResponse(data={"killed": True, "status": "success", "message": "BotInstance has been stopped..."})

    return JsonResponse(data={"killed": False, "status": "success", "message": "No BotInstance is active to be stopped..."})


def signal(request):
    bot = BotInstance.objects.get(pk=request.GET.get("instance"))
    sig = request.GET.get("signal")
    cfg = request.GET.get("config")
    win = request.GET.get("window")
    shrt = True if request.GET.get("shortcuts") == "true" else False

    if sig == "PLAY":
        if bot.state == RUNNING:
            return JsonResponse(data={"status": "warning", "message": "BotInstance is already running..."})
        if bot.state == STOPPED:
            start(config=cfg, window=win, shortcuts=shrt, instance=bot)
            return JsonResponse(data={"status": "success", "message": "BotInstance has been started..."})
        if bot.state == PAUSED:
            resume(instance=bot)
            return JsonResponse(data={"status": "success", "message": "BotInstance has been resumed..."})

    if sig == "PAUSE":
        if bot.state == RUNNING:
            pause(instance=bot)
            return JsonResponse(data={"status": "success", "message": "PAUSE Signal has been received by the bot..."})
        if bot.state == STOPPED or bot.state == PAUSED:
            return JsonResponse(data={"status": "warning", "message": "BotInstance is not currently running..."})

    if sig == "STOP":
        if bot.state == RUNNING:
            stop(instance=bot)
            return JsonResponse(data={"status": "success", "message": "STOP Signal has been received by the bot..."})
        if bot.state == STOPPED or bot.state == PAUSED:
            return JsonResponse(data={"status": "warning", "message": "BotInstance is not currently running..."})


def prestiges(request):
    """Grab any prestige instances that are associated with the specified session."""
    # GET.
    typ = request.GET.get("type")
    if typ == "PRESTIGES":
        _instance = BotInstance.objects.get(pk=request.GET.get("instance"))
        _session = _instance.session

        if _session:
            p = Prestige.objects.filter(session__uuid=_session.uuid)
        else:
            p = []

        # Parse out filtered data...
        # Prestige data as well as averaged out data (average stage prestige, average time per prestige).
        dct = {
            "prestiges": [],
            "avgPrestigeTime": None,
            "avgPrestigeStage": None,
            "lastArtifact": None,
            "totalPrestiges": len(p)
        }

        lst = []
        if len(p) > 0:
            total_times = 0
            total_stages = 0
            for prestige in p.order_by("-timestamp"):
                total_times += prestige.time.total_seconds() if prestige.time else 0
                total_stages += prestige.stage if prestige.stage else 0
                lst.append(prestige.json())

            # Assign all prestiges to data dictionary.
            dct["avgPrestigeTime"] = str(datetime.timedelta(seconds=int(total_times / len(p))))
            dct["avgPrestigeStage"] = int(total_stages / len(p))
            dct["prestiges"] = lst

            if p.last().artifact:
                dct["lastArtifact"] = p.last().artifact.json()
            else:
                dct["lastArtifact"] = None

        return JsonResponse(data=dct)

    if typ == "AVG":
        seconds = int(request.GET.get("totalSeconds"))
        valid_seconds = int(request.GET.get("validSeconds"))
        stages = int(request.GET.get("totalStages"))
        valid_stages = int(request.GET.get("validStages"))

        if valid_seconds == 0:
            valid_seconds = 1
        if valid_stages == 0:
            valid_stages = 1

        return JsonResponse(data={
            "avgPrestigeTime": str(datetime.timedelta(seconds=int(seconds / valid_seconds))),
            "avgPrestigeStage": int(stages / valid_stages)
        })


def screen(request):
    """Grab a screen shot of the current bot in game... Returning it as Base64 Image."""
    # Note: Nox Emulator is the only supported emulator... We can use
    # the expected values for that emulator for our screenshots...
    from titandash.bot.external.imagesearch import region_grabber
    from PIL.Image import ANTIALIAS

    inst = BotInstance.objects.get(pk=request.GET.get("instance"))
    window = inst.window

    grab = region_grabber((
        window["x"], window["y"],
        window["x"] + window["width"],
        window["y"] + window["height"]
    ))
    grab = grab.resize((360, 600), ANTIALIAS)

    buffered = BytesIO()
    grab.save(buffered, format="JPEG", quality=30)

    b = base64.b64encode(buffered.getvalue())
    image_str = "data:image/jpeg;base64, {b64}".format(b64=b.decode("utf-8"))
    return JsonResponse(data={"src": image_str})


def generate_queued(request):
    """Generate a queued function representing the function specified by the user."""
    func = request.GET.get("function")
    inst = BotInstance.objects.get(pk=request.GET.get("instance"))
    Queue.objects.add(function=func, instance=inst)

    return JsonResponse(data={"status": "success", "function": title(func)})


def raids(request):
    ctx = {"raids": []}

    if request.GET.get("instance"):
        _raids = RaidResult.objects.filter(instance=BotInstance.objects.get(pk=request.GET.get("instance")))
    else:
        _raids = RaidResult.objects.filter(instance=BotInstance.objects.grab())

    for raid_result in _raids.order_by("parsed"):
        ctx["raids"].append(raid_result.json())

    ctx["RAIDS_JSON"] = json.dumps(ctx)

    if request.GET.get("context"):
        return JsonResponse(data={
            "table": render(request, "raids/raidsTable.html", context=ctx).content.decode()
        })

    return render(request, "raids/raids.html", context=ctx)


def raid(request, digest):
    ctx = {
        "raid": RaidResult.objects.get(digest=digest).json()
    }

    ctx["RAID_JSON"] = json.dumps(ctx)

    return render(request, "raids/raid.html", context=ctx)


def create_instance(request):
    return JsonResponse(data=BotInstance.objects.create().json())


def remove_instance(request):
    BotInstance.objects.filter(pk=request.GET.get("id")).delete()

    return JsonResponse(data={"status": "success"})


def open_log(request):
    log_name = request.GET.get("log")

    # Open the log through the os module.
    os.startfile(log_name)

    return JsonResponse(data={
        "status": "success"
    })
