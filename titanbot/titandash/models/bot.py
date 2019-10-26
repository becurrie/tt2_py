from django.db import models
from django.utils import timezone
from django.conf import settings

from channels.generic.websocket import async_to_sync
from channels.layers import get_channel_layer

from titandash.constants import RUNNING, PAUSED, STOPPED, DATETIME_FMT
from titandash.models.statistics import Statistics, Log
from titandash.models.prestige import Prestige
from titandash.models.queue import Queue

import jsonfield


BOT_STATE_CHOICES = (
    ("running", "RUNNING"),
    ("paused", "PAUSED"),
    ("stopped", "STOPPED")
)

BOT_HELP_TEXT = {
    "name": "Name of the bot instance.",
    "state": "Current state of the bot.",
    "uuid": "Unique identifier for this bot instance.",
    "session": "Session associated with the current bot instance.",
    "started": "The date that the bot was started.",
    "current_function": "The current function being executed by the bot."
}


class BotInstanceManager(models.Manager):
    def grab(self):
        """
        Attempt to grab the current Bot instance. We only ever want one single instance. If one does not exist,
        we generate a new one with some default values.
        """
        if len(self.all()) == 0:
            self.create()

        # Returning the existing instance.
        return self.all().first()


class BotInstance(models.Model):
    """
    Bot Model.

    This model is only used to store and check that the bot is currently running or not.

    The state of the bot will be updated by the Bot instance itself when one is started. Additionally,
    if the bot is stopped or shutdown manually (no crash). The bot instance in the database will be updated.

    If the bot hard crashes somehow, we also do a check to see if the PID running the bot that was present
    last is still present and running on the local machine running the bot.
    """
    class Meta:
        verbose_name = "Bot Instance"
        verbose_name_plural = "Bot Instances"

    objects = BotInstanceManager()
    name = models.CharField(verbose_name="Name", max_length=255, blank=True, null=True, help_text=BOT_HELP_TEXT["name"])
    state = models.CharField(verbose_name="State", choices=BOT_STATE_CHOICES, default=STOPPED, max_length=255, help_text=BOT_HELP_TEXT["state"])
    session = models.ForeignKey(verbose_name="Session", blank=True, null=True, to="Session", on_delete=models.CASCADE, help_text=BOT_HELP_TEXT["session"])
    started = models.DateTimeField(verbose_name="Started", blank=True, null=True, help_text=BOT_HELP_TEXT["started"])
    current_function = models.CharField(verbose_name="Current Function", max_length=255, blank=True, null=True, help_text=BOT_HELP_TEXT["current_function"])

    # Last Prestige...
    last_prestige = models.ForeignKey(verbose_name="Last Prestige", to=Prestige, blank=True, null=True, on_delete=models.CASCADE)

    # Raid Attack Reset...
    # --------------------
    # This field is treated quite differently than any other field on the
    # BotInstance currently. This field persists throughout session start/stop.
    # Since a raid attack reset uses a DateTime to determine when it resets,
    # We can leave it as is throughout bot sessions to ensure a notification is
    # not sent every single time a session is started.
    next_raid_attack_reset = models.DateTimeField(verbose_name="Next Raid Attacks Reset", blank=True, null=True)

    # Breaks.
    next_break = models.DateTimeField(verbose_name="Next Break", blank=True, null=True)
    resume_from_break = models.DateTimeField(verbose_name="Resume From Break", blank=True, null=True)

    # Bot Variables...
    configuration = models.ForeignKey(verbose_name="Current Configuration", to="Configuration", blank=True, null=True, on_delete=models.CASCADE)
    window = jsonfield.JSONField(verbose_name="Current Window", blank=True, null=True)
    log = models.ForeignKey(verbose_name="Current Log", to=Log, on_delete=models.CASCADE, blank=True, null=True)
    current_stage = models.PositiveIntegerField(verbose_name="Current Stage", blank=True, null=True)
    next_action_run = models.DateTimeField(verbose_name="Next Action Run", blank=True, null=True)
    next_master_level = models.DateTimeField(verbose_name="Next Master Level", blank=True, null=True)
    next_heroes_level = models.DateTimeField(verbose_name="Next Heroes Level", blank=True, null=True)
    next_skills_level = models.DateTimeField(verbose_name="Next Skills Level", blank=True, null=True)
    next_skills_activation = models.DateTimeField(verbose_name="Next Skills Activation", blank=True, null=True)
    next_miscellaneous_actions = models.DateTimeField(verbose_name="Next Miscellaneous Actions", blank=True, null=True)
    next_prestige = models.DateTimeField(verbose_name="Next Timed Prestige", blank=True, null=True)
    next_randomized_prestige = models.DateTimeField(verbose_name="Next Randomized Prestige", blank=True, null=True)
    next_stats_update = models.DateTimeField(verbose_name="Next Stats Update", blank=True, null=True)
    next_daily_achievement_check = models.DateTimeField(verbose_name="Next Daily Achievement Check", blank=True, null=True)
    next_milestone_check = models.DateTimeField(verbose_name="Next Milestone Check", blank=True, null=True)
    next_raid_notifications_check = models.DateTimeField(verbose_name="Next Raid Notifications Check", blank=True, null=True)
    next_clan_results_parse = models.DateTimeField(verbose_name="Next Clan Results Parse", blank=True, null=True)
    next_heavenly_strike = models.DateTimeField(verbose_name="Next Heavenly Strike", blank=True, null=True)
    next_deadly_strike = models.DateTimeField(verbose_name="Next Deadly Strike", blank=True, null=True)
    next_hand_of_midas = models.DateTimeField(verbose_name="Next Hand Of Midas", blank=True, null=True)
    next_fire_sword = models.DateTimeField(verbose_name="Next Fire Sword", blank=True, null=True)
    next_war_cry = models.DateTimeField(verbose_name="Next War Cry", blank=True, null=True)
    next_shadow_clone = models.DateTimeField(verbose_name="Next Shadow Clone", blank=True, null=True)
    next_artifact_upgrade = models.CharField(verbose_name="Next Artifact Upgrade", max_length=255, blank=True, null=True)

    def __str__(self):
        return "{name} [{state}]".format(name=self.name, state=self.state.upper())

    def key(self):
        return "{name} [{uuid}] v{version}".format(name=self.name, uuid=self.session.uuid, version=self.session.version)

    def save(self, *args, **kwargs):
        if not self.name:
            try:
                max_id = max([int(n.split(" ")[-1]) for n in BotInstance.objects.all().values_list("name", flat=True)])
            except ValueError:
                max_id = 0

            self.name = "Titandash Instance {id}".format(id=max_id + 1)

        super(BotInstance, self).save(*args, **kwargs)

        # Channels send websocket message.
        channel_layer = get_channel_layer()
        group_name = 'titan_instance'
        instance = self.json()

        # Send message to group.
        async_to_sync(channel_layer.group_send)(
            group_name, {
                'type': 'saved',
                'instance_id': instance["id"],
                'instance': instance
            }
        )

    def get_diff_from_max_stage(self, percent=False):
        if self.current_stage is None or self.current_stage == "":
            return None

        stats = Statistics.objects.grab(instance=self)
        try:
            stage = int(self.current_stage)
        except ValueError:
            return None

        max_stage = stats.game_statistics.highest_stage()
        if max_stage is None:
            return None

        if not percent:
            return int(max_stage - stage)

        if max_stage == stage:
            return "100%"

        return "{:.2%}".format(float(stage) / max_stage)

    def json(self):
        """
        Convert the BotInstance into a JSON compliant dictionary.
        """
        from django.urls import reverse
        from titandash.utils import title
        from titandash.models.artifact import Artifact
        dct = {
            "id": self.pk,
            "name": self.name,
            "state": self.state.upper(),
            "started": {
                "datetime": str(self.started) if self.started else None,
                "formatted": self.started.astimezone().strftime(DATETIME_FMT) if self.started else None
            },
            "current_function": {
                "function": self.current_function,
                "title": title(self.current_function) if self.current_function else None,
            },
            "last_prestige": self.last_prestige.json() if self.last_prestige else "N/A",
            "log_file": reverse('log', kwargs={'pk': self.log.pk}) if self.log else "N/A",
            "current_stage": {
                "stage": self.current_stage,
                "diff_from_max": self.get_diff_from_max_stage(),
                "percent_from_max": self.get_diff_from_max_stage(percent=True)
            },
            "next_artifact_upgrade": {
                "title": title(self.next_artifact_upgrade) if self.next_artifact_upgrade else None,
                "image": "{dir}{path}".format(dir=settings.STATIC_URL, path=Artifact.objects.get(name=self.next_artifact_upgrade).image) if self.next_artifact_upgrade else None
            },
            "next_master_level": {
                "datetime": str(self.next_master_level) if self.next_master_level else None,
                "formatted": self.next_master_level.astimezone().strftime(DATETIME_FMT) if self.next_master_level else None
            },
            "next_heroes_level": {
                "datetime": str(self.next_heroes_level) if self.next_heroes_level else None,
                "formatted": self.next_heroes_level.astimezone().strftime(DATETIME_FMT) if self.next_heroes_level else None
            },
            "next_skills_level": {
                "datetime": str(self.next_skills_level) if self.next_skills_level else None,
                "formatted": self.next_skills_level.astimezone().strftime(DATETIME_FMT) if self.next_skills_level else None
            },
            "next_skills_activation": {
                "datetime": str(self.next_skills_activation) if self.next_skills_activation else None,
                "formatted": self.next_skills_activation.astimezone().strftime(DATETIME_FMT) if self.next_skills_activation else None
            },
            "next_miscellaneous_actions": {
                "datetime": str(self.next_miscellaneous_actions) if self.next_miscellaneous_actions else None,
                "formatted": self.next_miscellaneous_actions.astimezone().strftime(DATETIME_FMT) if self.next_miscellaneous_actions else None
            },
            "next_prestige": {
                "datetime": str(self.next_prestige) if self.next_prestige else None,
                "formatted": self.next_prestige.astimezone().strftime(DATETIME_FMT) if self.next_prestige else None
            },
            "next_randomized_prestige": {
                "datetime": str(self.next_randomized_prestige) if self.next_randomized_prestige else None,
                "formatted": self.next_randomized_prestige.astimezone().strftime(DATETIME_FMT) if self.next_randomized_prestige else None
            },
            "next_stats_update": {
                "datetime": str(self.next_stats_update) if self.next_stats_update else None,
                "formatted": self.next_stats_update.astimezone().strftime(DATETIME_FMT) if self.next_stats_update else None
            },
            "next_daily_achievement_check": {
                "datetime": str(self.next_daily_achievement_check) if self.next_daily_achievement_check else None,
                "formatted": self.next_daily_achievement_check.astimezone().strftime(DATETIME_FMT) if self.next_daily_achievement_check else None
            },
            "next_milestone_check": {
                "datetime": str(self.next_milestone_check) if self.next_milestone_check else None,
                "formatted": self.next_milestone_check.astimezone().strftime(DATETIME_FMT) if self.next_milestone_check else None
            },
            "next_raid_notifications_check": {
                "datetime": str(self.next_raid_notifications_check) if self.next_raid_notifications_check else None,
                "formatted": self.next_raid_notifications_check.astimezone().strftime(DATETIME_FMT) if self.next_raid_notifications_check else None
            },
            "next_raid_attack_reset": {
                "datetime": str(self.next_raid_attack_reset) if self.next_raid_attack_reset else None,
                "formatted": self.next_raid_attack_reset.astimezone().strftime(DATETIME_FMT) if self.next_raid_attack_reset else None
            },
            "next_clan_results_parse": {
                "datetime": str(self.next_clan_results_parse) if self.next_clan_results_parse else None,
                "formatted": self.next_clan_results_parse.astimezone().strftime(DATETIME_FMT) if self.next_clan_results_parse else None
            },
            "next_heavenly_strike": {
                "datetime": str(self.next_heavenly_strike) if self.next_heavenly_strike else None,
                "formatted": self.next_heavenly_strike.astimezone().strftime(DATETIME_FMT) if self.next_heavenly_strike else None
            },
            "next_deadly_strike": {
                "datetime": str(self.next_deadly_strike) if self.next_deadly_strike else None,
                "formatted": self.next_deadly_strike.astimezone().strftime(DATETIME_FMT) if self.next_deadly_strike else None
            },
            "next_hand_of_midas": {
                "datetime": str(self.next_hand_of_midas) if self.next_hand_of_midas else None,
                "formatted": self.next_hand_of_midas.astimezone().strftime(DATETIME_FMT) if self.next_hand_of_midas else None
            },
            "next_fire_sword": {
                "datetime": str(self.next_fire_sword) if self.next_fire_sword else None,
                "formatted": self.next_fire_sword.astimezone().strftime(DATETIME_FMT) if self.next_fire_sword else None
            },
            "next_war_cry": {
                "datetime": str(self.next_war_cry) if self.next_war_cry else None,
                "formatted": self.next_war_cry.astimezone().strftime(DATETIME_FMT) if self.next_war_cry else None
            },
            "next_shadow_clone": {
                "datetime": str(self.next_shadow_clone) if self.next_shadow_clone else None,
                "formatted": self.next_shadow_clone.astimezone().strftime(DATETIME_FMT) if self.next_shadow_clone else None
            },
            "next_break": {
                "datetime": str(self.next_break) if self.next_break else None,
                "formatted": self.next_break.astimezone().strftime(DATETIME_FMT) if self.next_break else None
            },
            "resume_from_break": {
                "datetime": str(self.resume_from_break) if self.resume_from_break else None,
                "formatted": self.resume_from_break.astimezone().strftime(DATETIME_FMT) if self.resume_from_break else None
            },
        }

        if self.session:
            dct["session"] = {
                "url": reverse('session', kwargs={"uuid": self.session.uuid}),
                "uuid": self.session.uuid
            }
        if self.configuration:
            dct["configuration"] = {
                "id": self.configuration.pk,
                "url": reverse("admin:titandash_configuration_change", kwargs={"object_id": self.configuration.pk}),
                "name": self.configuration.name
            }
        if self.window:
            dct["window"] = self.window

        return dct

    def reset_vars(self):
        self.current_function = None
        self.last_prestige = None
        self.next_break = None
        self.resume_from_break = None
        self.configuration = None
        self.window = None
        self.log_file = None
        self.current_stage = None
        self.next_master_level = None
        self.next_heroes_level = None
        self.next_skills_level = None
        self.next_skills_activation = None
        self.next_miscellaneous_actions = None
        self.next_prestige = None
        self.next_randomized_prestige = None
        self.next_stats_update = None
        self.next_daily_achievement_check = None
        self.next_milestone_check = None
        self.next_raid_notifications_check = None
        self.next_clan_results_parse = None
        self.next_deadly_strike = None
        self.next_hand_of_midas = None
        self.next_fire_sword = None
        self.next_war_cry = None
        self.next_shadow_clone = None
        self.upgrade_artifacts = None
        self.next_artifact_upgrade = None

    def start(self, session):
        """
        Start the BotInstance. Should be called when the Bot is first initialized.
        """
        self.state = RUNNING
        self.session = session
        self.started = timezone.now()
        self.save()

    def pause(self):
        """
        Pause the BotInstance. Called when signal is sent from user.
        """
        self.state = PAUSED
        self.save()

    def stop(self):
        """
        Stop and kill the BotInstance. Called when exception is raised or manual termination by user.
        """
        self.state = STOPPED
        self.session = None
        self.started = None
        self.current_function = None
        self.reset_vars()
        self.save()

        # Additionally, flush the QueuedFunctions list just to be sure.
        Queue.flush()

    def resume(self):
        """
        Resume the BotInstance. Called when resumed from a paused state.
        """
        self.state = RUNNING
        self.save()
