from django.db import models
from django.urls import reverse

from titandash.constants import DATETIME_FMT
from titandash.bot.core.maps import ARTIFACT_TIER_MAP
from titandash.bot.core.utilities import convert

from jsonfield.fields import JSONField

from decimal import Decimal


GAME_STATISTICS_HELP_TEXT = {
    "highest_stage_reached": "Highest stage reached in game overall.",
    "total_pet_level": "Total pet level reached in game overall.",
    "gold_earned": "How much gold has been earned in game overall.",
    "taps": "How many taps have taken place in game overall.",
    "titans_killed": "How many titans have been killed in game overall.",
    "bosses_killed": "How many bosses have been killed in game overall.",
    "critical_hits": "How many critical hits have been scored in game overall.",
    "chestersons_killed": "How many chestersons have been killed in game overall.",
    "prestiges": "How many total prestiges have taken place in game overall.",
    "days_since_install": "How many days since the game has been installed.",
    "play_time": "How much active play time has been accrued in game overall.",
    "relics_earned": "How many relics have been earned game overall.",
    "fairies_tapped": "How many fairies have been tapped on in game overall.",
    "daily_achievements": "How many daily achievements have been completed in game overall.",
    "tournament_points": "How many overall tournaments points have been earned.",
    "instance": "The bot instance associated with these game statistics."
}


class GameStatistics(models.Model):
    """
    GameStatistics Model.

    Represents all in game statistics that can be grabbed by the Bot. An OCR check is performed on the in game stats.
    These values are updated when these stats are pushed from the Bot, to the database.
    """
    class Meta:
        verbose_name = "Game Statistics"
        verbose_name_plural = "Game Statistics"

    highest_stage_reached = models.CharField(verbose_name="Highest Stage Reached", blank=True, null=True, max_length=255, help_text=GAME_STATISTICS_HELP_TEXT["highest_stage_reached"])
    total_pet_level = models.CharField(verbose_name="Total Pet Level", blank=True, null=True, max_length=255, help_text=GAME_STATISTICS_HELP_TEXT["total_pet_level"])
    gold_earned = models.CharField(verbose_name="Gold Earned", blank=True, null=True, max_length=255, help_text=GAME_STATISTICS_HELP_TEXT["gold_earned"])
    taps = models.CharField(verbose_name="Taps", max_length=255, blank=True, null=True, help_text=GAME_STATISTICS_HELP_TEXT["taps"])
    titans_killed = models.CharField(verbose_name="Titans Killed", blank=True, null=True, max_length=255, help_text=GAME_STATISTICS_HELP_TEXT["titans_killed"])
    bosses_killed = models.CharField(verbose_name="Bosses Killed", blank=True, null=True, max_length=255, help_text=GAME_STATISTICS_HELP_TEXT["bosses_killed"])
    critical_hits = models.CharField(verbose_name="Critical Hits", blank=True, null=True, max_length=255, help_text=GAME_STATISTICS_HELP_TEXT["critical_hits"])
    chestersons_killed = models.CharField(verbose_name="Chestersons Killed", blank=True, null=True, max_length=255, help_text=GAME_STATISTICS_HELP_TEXT["chestersons_killed"])
    prestiges = models.CharField(verbose_name="Prestiges", blank=True, null=True, max_length=255, help_text=GAME_STATISTICS_HELP_TEXT["prestiges"])
    days_since_install = models.CharField(verbose_name="Days Since Install", blank=True, null=True, max_length=255, help_text=GAME_STATISTICS_HELP_TEXT["days_since_install"])
    play_time = models.CharField(verbose_name="Play Time", blank=True, null=True, max_length=255, help_text=GAME_STATISTICS_HELP_TEXT["play_time"])
    relics_earned = models.CharField(verbose_name="Relics Earned", blank=True, null=True, max_length=255, help_text=GAME_STATISTICS_HELP_TEXT["relics_earned"])
    fairies_tapped = models.CharField(verbose_name="Fairies Tapped", blank=True, null=True, max_length=255, help_text=GAME_STATISTICS_HELP_TEXT["fairies_tapped"])
    daily_achievements = models.CharField(verbose_name="Daily Achievements", blank=True, null=True, max_length=255, help_text=GAME_STATISTICS_HELP_TEXT["daily_achievements"])
    tournament_points = models.CharField(verbose_name="Tournament Points", blank=True, null=True, max_length=255, help_text=GAME_STATISTICS_HELP_TEXT["tournament_points"])
    instance = models.ForeignKey(verbose_name="Instance", to="BotInstance", null=True, on_delete=models.CASCADE, help_text=GAME_STATISTICS_HELP_TEXT["instance"])

    def __str__(self):
        return "{instance} GameStatistics".format(instance=self.instance.name)

    def highest_stage(self):
        if self.highest_stage_reached is not None and self.highest_stage_reached != "":
            return convert(self.highest_stage_reached) or 1  # Ensure 1 is used if non truthy is converted...
        else:
            return None

    def time_played_average(self):
        """
        Given the days since install, and time played by a user, convert this into
        an average amount of time played per day.
        """
        installed = int(self.days_since_install) if self.days_since_install else 0
        played = self.play_time if self.play_time else None

        if played:
            try:
                if "d" in played:
                    played_hours = int(played.split("d")[0]) * 24
                else:
                    played_hours = int(played.split(":")[0])

            # Malformed time played value can cause this fail...
            # We'll use a base string if we're unable to parse out played hours.
            except Exception:
                return "N/A"
        else:
            return 0

        return round(played_hours / installed, 2)

    @property
    def progress(self):
        """
        Return current max stage progress.
        """
        from settings import STAGE_CAP

        stage = int(convert(self.highest_stage_reached)) if self.highest_stage_reached else 0

        return {
            "stage": stage,
            "max_stage": STAGE_CAP,
            "percent": round(stage / STAGE_CAP * 100, 2)
        }

    @property
    def played(self):
        return {
            "days_since_install": self.days_since_install if self.days_since_install else 0,
            "play_time": self.play_time if self.play_time else "no",
            "average": self.time_played_average
        }

    def json(self):
        return {
            "highest_stage_reached": self.highest_stage_reached,
            "total_pet_level": self.total_pet_level,
            "gold_earned": self.gold_earned,
            "taps": self.taps,
            "titans_killed": self.titans_killed,
            "bosses_killed": self.bosses_killed,
            "critical_hits": self.critical_hits,
            "chestersons_killed": self.chestersons_killed,
            "prestiges": self.prestiges,
            "days_since_install": self.days_since_install,
            "play_time": self.play_time,
            "relics_earned": self.relics_earned,
            "fairies_tapped": self.fairies_tapped,
            "daily_achievements": self.daily_achievements,
            "tournament_points": self.tournament_points
        }


BOT_STATISTICS_HELP_TEXT = {
    "ads": "How many ads have been earned and tracked by the bot.",
    "updates": "How many times has bot statistics been updated.",
    "instance": "The bot instance associated with these game statistics."
}


class BotStatistics(models.Model):
    """
    BotStatistics Model.

    Bot statistics taken from the Bot while running and executing functions.
    """
    class Meta:
        verbose_name = "Bot Statistics"
        verbose_name_plural = "Bot Statistics"

    # Game actions.
    ads = models.PositiveIntegerField(verbose_name="Premium Ads", default=0, help_text=BOT_STATISTICS_HELP_TEXT["ads"])
    updates = models.PositiveIntegerField(verbose_name="Updates", default=0, help_text=BOT_STATISTICS_HELP_TEXT["updates"])

    instance = models.ForeignKey(verbose_name="Instance", to="BotInstance", null=True, on_delete=models.CASCADE, help_text=BOT_STATISTICS_HELP_TEXT["instance"])

    def __str__(self):
        return "{instance} BotStatistics".format(instance=self.instance.name)

    @property
    def prestiges(self):
        """
        Retrieve total amount of prestiges for this set BotStatistics instance.
        """
        return PrestigeStatistics.objects.grab(instance=self.instance).prestiges.all().count()

    @property
    def sessions(self):
        """
        Retrieve the total amount of sessions for this BotStatistics instance.
        """
        return Session.objects.filter(instance=self.instance).count()

    def json(self):
        return {
            "ads": self.ads,
            "updates": self.updates,
            "prestiges": self.prestiges,
            "sessions": self.sessions
        }


ARTIFACT_OWNED_HELP_TEXT = {
    "artifact": "Specify the artifact being used.",
    "owned": "Specify if this artifact is owned or not.",
    "instance": "The bot instance associated with this owned artifact."
}


class ArtifactOwned(models.Model):
    """
    ArtifactOwned Model.

    Artifacts can be associated to a boolean representing whether or not they are currently owned.
    """
    class Meta:
        verbose_name = "Artifact Owned"
        verbose_name_plural = "Artifacts Owned"

    artifact = models.ForeignKey(verbose_name="Artifact", to="Artifact", on_delete=models.CASCADE, help_text=ARTIFACT_OWNED_HELP_TEXT["artifact"])
    owned = models.BooleanField(verbose_name="Owned", default=False, help_text=ARTIFACT_OWNED_HELP_TEXT["owned"])
    instance = models.ForeignKey(verbose_name="Instance", to="BotInstance", null=True, on_delete=models.CASCADE, help_text=ARTIFACT_OWNED_HELP_TEXT["instance"])

    def __str__(self):
        return "{instance} {artifact} ({owned})".format(instance=self.instance.name, artifact=self.artifact, owned=self.owned)

    def json(self):
        """Return ArtifactOwned as JSON Compliant Object."""
        art = self.artifact.json()
        art.update({"owned": self.owned})

        return art


class ArtifactStatisticsManager(models.Manager):
    def grab(self, instance):
        """
        Attempt to grab the current ArtifactStatistics instance. One will be generated with some default values
        if one does not already exist.
        """
        from .artifact import Artifact, Tier
        if self.filter(instance=instance).count() == 0:
            arts = self.create(instance=instance)
        else:
            arts = self.get(instance=instance)

        for tier, dct in ARTIFACT_TIER_MAP.items():
            for key, value in dct.items():
                if key not in arts.artifacts.all().values_list("artifact__name", flat=True):
                    arts.artifacts.add(ArtifactOwned.objects.create(
                        instance=instance,
                        artifact=Artifact.objects.get_or_create(
                            name=key,
                            tier=Tier.objects.get_or_create(tier=tier, name="Tier {tier}".format(tier=tier))[0],
                            key=value[1],
                            image="{name}.png".format(name=key.replace("'", ""))
                        )[0]))

        return arts


ARTIFACT_STATISTICS_HELP_TEXT = {
    "artifacts": "Choose the artifacts associated with this artifact statistics instance.",
    "instance": "The bot instance associated with these artifact statistics."
}


class ArtifactStatistics(models.Model):
    """
    ArtifactStatistics Model.

    Artifact statistics stores the relation between artifacts and whether or not they're owned
    into a single artifact statistics instance.
    """
    class Meta:
        verbose_name = "Artifact Statistics"
        verbose_name_plural = "Artifact Statistics"

    objects = ArtifactStatisticsManager()
    artifacts = models.ManyToManyField(verbose_name="Artifacts", to="ArtifactOwned", help_text=ARTIFACT_STATISTICS_HELP_TEXT["artifacts"])
    instance = models.ForeignKey(verbose_name="Instance", to="BotInstance", null=True, on_delete=models.CASCADE, help_text=ARTIFACT_STATISTICS_HELP_TEXT["instance"])

    def __str__(self):
        return "ArtifactStatistics ({owned}/{all})".format(owned=len(self.owned()), all=len(self.artifacts.all()))

    def owned(self):
        return self.artifacts.filter(owned=True)

    def missing(self):
        return self.artifacts.filter(owned=False)

    def json(self):
        return {
            ao.artifact.key: ao.json() for ao in self.artifacts.all()
        }


SESSION_HELP_TEXT = {
    "uuid": "Specify the unique identifier for this session.",
    "version": "Specify the version of the bot during this session.",
    "start": "Start datetime for this session.",
    "end": "End datetime for this session.",
    "log": "Specify the file path to the log file associated with this session.",
    "game_statistic_differences": "Game statistic differences associated with session.",
    "bot_statistic_differences": "Bot statistic differences associated with session.",
    "configuration": "Config instance associated with this session.",
    "configuration_snapshot": "Config snapshot used when session was started.",
    "instance": "The bot instance associated with the session."
}


class Log(models.Model):
    """
    Log Model.

    Store references to log files generated so that they can be retrieved through the dashboard if needed.
    """
    class Meta:
        verbose_name = "Log"
        verbose_name_plural = "Logs"

    log_file = models.CharField(verbose_name="Log File", max_length=255)

    def exists(self):
        """
        Determine whether or not this log file actually exists.
        """
        try:
            with open(self.log_file):
                return True
        except FileNotFoundError:
            return False

    def json(self, truncate=False):
        ctx = {
            "id": self.pk,
            "filename": self.log_file,
            "data": []
        }

        with open(self.log_file) as file:
            lines = file.readlines()
            for index, line in enumerate(lines, start=1):
                ctx["data"].append({
                    "num": index,
                    "line": line
                })
                if index > 3000:
                    if truncate:
                        break

        ctx["length"] = len(ctx["data"])
        return ctx


class Session(models.Model):
    """
    Session Model.

    Sessions are started each time the Bot is started. A session is identified by it's unique identifier
    that is generated by the Bot when started. It stores information about the differences between stats
    from when the Bot was started, and whenever the last statistic update took place. The configuration used
    is also stored here which can be used for debugging purposes or error auditing.
    """
    class Meta:
        verbose_name = "Session"
        verbose_name_plural = "Sessions"

    uuid = models.CharField(verbose_name="Unique Identifier", blank=True, null=True, max_length=255, help_text=SESSION_HELP_TEXT["uuid"])
    version = models.CharField(verbose_name="Version", blank=True, null=True, max_length=255, help_text=SESSION_HELP_TEXT["version"])
    start = models.DateTimeField(verbose_name="Start Date", blank=True, null=True, help_text=SESSION_HELP_TEXT["start"])
    end = models.DateTimeField(verbose_name="End Date", blank=True, null=True, help_text=SESSION_HELP_TEXT["end"])
    log = models.ForeignKey(verbose_name="Log File", to="Log", on_delete=models.CASCADE, blank=True, null=True, max_length=255, help_text=SESSION_HELP_TEXT["log"])
    configuration = models.ForeignKey(verbose_name="Configuration", to="Configuration", on_delete=models.CASCADE, blank=True, null=True, help_text=SESSION_HELP_TEXT["configuration"])
    configuration_snapshot = JSONField(verbose_name="Configuration Snapshot", blank=True, null=True, help_text=SESSION_HELP_TEXT["configuration_snapshot"])
    instance = models.ForeignKey(verbose_name="Session Instance", to="BotInstance", related_name="session_instance", on_delete=models.CASCADE, blank=True, null=True, help_text=SESSION_HELP_TEXT["instance"])

    def __str__(self):
        return "{instance} [Session [{uuid}] v{version}]".format(instance=self.instance.name, uuid=self.uuid, version=self.version)

    def save(self, *args, **kwargs):
        snapshot = self.configuration.json(condense=True)

        # JSONField will not allow decimal object, coerce to string decimals.
        for group in snapshot:
            for key in snapshot[group]:
                if isinstance(snapshot[group][key], Decimal):
                    snapshot[group][key] = str(snapshot[group][key])

        self.configuration_snapshot = snapshot
        super(Session, self).save(*args, **kwargs)

    def duration(self):
        if not self.start or not self.end:
            return "N/A"

        s = (self.end - self.start).total_seconds()
        hours = s // 3600
        s = s - (hours * 3600)
        minutes = s // 60
        seconds = s - (minutes * 60)

        return "{:02}:{:02}:{:02}".format(int(hours), int(minutes), int(seconds))

    def json(self, prestige_count_only=False):
        """
        Return Session and Associated Models As JSON Compliant Dictionary.
        """
        from titandash.models.prestige import Prestige
        dct = {
            "uuid": self.uuid,
            "instance": self.instance.name,
            "version": self.version,
            "start": {
                "datetime": str(self.start),
                "formatted": self.start.astimezone().strftime(DATETIME_FMT) if self.start else "N/A",
                "epoch": int(self.start.astimezone().timestamp()) if self.start else 0
            },
            "end": {
                "datetime": str(self.end),
                "formatted": self.end.astimezone().strftime(DATETIME_FMT) if self.end else "N/A",
                "epoch": int(self.end.astimezone().timestamp()) if self.end else 0
            },
            "log": reverse('log', kwargs={'pk': self.log.pk}) if self.log else "N/A",
            "configuration": self.configuration_snapshot,
            "duration": str(self.duration()),
        }

        if prestige_count_only:
            prestiges = Prestige.objects.filter(session=self).count()
            count = prestiges
        else:
            prestiges = Prestige.objects.filter(session=self)
            if len(prestiges) > 0:
                prestiges = [p.json() for p in prestiges]
                count = len(prestiges)
            else:
                prestiges = []
                count = 0

        dct["prestiges"] = {
            "prestiges": prestiges,
            "count": count
        }

        return dct


STATS_HELP_TEXT = {
    "game_statistics": "Game Statistics associated with this statistics instance.",
    "bot_statistics": "Bot Statistics associated with this statistics instance.",
    "sessions": "Sessions associated with this statistics instance.",
    "instance": "The bot instance associated with these statistics."
}


class StatisticsManager(models.Manager):
    def grab(self, instance):
        """
        Attempt to grab the current Statistics instance. One will be generated with some default values
        if one does not already exist.
        """
        if self.filter(instance=instance).count() == 0:
            game_statistics, bot_statistics = GameStatistics.objects.create(instance=instance), BotStatistics.objects.create(instance=instance)
            return self.create(
                game_statistics=game_statistics,
                bot_statistics=bot_statistics,
                instance=instance
            )

        # Returning the existing instance.
        return self.get(instance=instance)


class Statistics(models.Model):
    """
    Statistics Model.

    The statistics model is used to contain all statistics in one single location.
    """
    class Meta:
        verbose_name = "Statistics"
        verbose_name_plural = "Statistics"

    objects = StatisticsManager()
    game_statistics = models.ForeignKey(verbose_name="Game Statistics", to="GameStatistics", on_delete=models.CASCADE, blank=True, null=True, help_text=STATS_HELP_TEXT["game_statistics"])
    bot_statistics = models.ForeignKey(verbose_name="Bot Statistics", to="BotStatistics", on_delete=models.CASCADE, blank=True, null=True, help_text=STATS_HELP_TEXT["bot_statistics"])
    sessions = models.ManyToManyField(verbose_name="Sessions", to="Session", blank=True, help_text=STATS_HELP_TEXT["sessions"])
    instance = models.ForeignKey(verbose_name="Instance", to="BotInstance", null=True, on_delete=models.CASCADE, help_text=STATS_HELP_TEXT["instance"])

    def __str__(self):
        return "{instance} Statistics ({key})".format(instance=self.instance.name, key=self.pk)

    def json(self):
        return {
            "GAME_STATISTICS": self.game_statistics.json(),
            "BOT_STATISTICS": self.bot_statistics.json(),
        }


class PrestigeStatisticsManager(models.Manager):
    def grab(self, instance):
        """
        Attempt to grab the current PrestigeStatistics instance. One will be generated with some default values
        if one does not already exist.
        """
        if len(self.filter(instance=instance)) == 0:
            self.create(instance=instance)

        # Returning the existing instance.
        return self.get(instance=instance)


PRESTIGE_STATISTICS_HELP_TEXT = {
    "prestiges": "Choose the prestiges that are associated with this prestige statistics instance.",
    "instance": "The bot instance associated with these prestige statistics."
}


class PrestigeStatistics(models.Model):
    """
    PrestigeStatistics Model.

    Store all statistics related to prestiges that take place in game.
    """
    class Meta:
        verbose_name = "Prestige Statistics"
        verbose_name_plural = "Prestige Statistics"

    objects = PrestigeStatisticsManager()
    prestiges = models.ManyToManyField(verbose_name="Prestiges", to="Prestige", blank=True, help_text=PRESTIGE_STATISTICS_HELP_TEXT["prestiges"])
    instance = models.ForeignKey(verbose_name="Instance", to="BotInstance", null=True, on_delete=models.CASCADE, help_text=PRESTIGE_STATISTICS_HELP_TEXT["instance"])

    def __str__(self):
        return "{instance} PrestigeStatistics [{count} Prestiges]".format(instance=self.instance.name, count=self.prestiges.all().count(), key=self.pk)
