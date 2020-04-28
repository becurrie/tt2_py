from django.contrib import admin
from django.contrib.admin.decorators import register

from django_paranoid.admin import ParanoidAdmin

from .models.artifact import Artifact, Tier
from .models.configuration import Configuration, ThemeConfig
from .models.bot import BotInstance
from .models.prestige import Prestige
from .models.queue import Queue
from .models.statistics import (
    Statistics, GameStatistics, BotStatistics, ArtifactOwned, ArtifactStatistics,
    PrestigeStatistics, Session
)
from .models.globals import GlobalSettings


@register(BotInstance)
class BotInstanceAdmin(admin.ModelAdmin):
    list_display = ["__str__", "name", "state", "started", "session"]


@register(Prestige)
class PrestigeAdmin(admin.ModelAdmin):
    list_display = ["__str__", "instance", "timestamp", "stage", "time"]


@register(Queue)
class QueueAdmin(admin.ModelAdmin):
    list_display = ["__str__", "instance", "created"]


@register(Tier)
class TierAdmin(admin.ModelAdmin):
    pass


@register(Artifact)
class ArtifactAdmin(admin.ModelAdmin):
    list_display = ["__str__", "name", "tier", "key", "image"]


@register(ThemeConfig)
class ThemeConfigAdmin(admin.ModelAdmin):
    list_display = ["theme"]


@register(Configuration)
class ConfigurationAdmin(ParanoidAdmin):
    list_display = ["__str__"]
    save_as = True


@register(Statistics)
class StatisticsAdmin(admin.ModelAdmin):
    filter_horizontal = ["sessions"]
    list_display = ["__str__", "instance"]


@register(GameStatistics)
class GameStatisticsAdmin(admin.ModelAdmin):
    list_display = ["__str__", "instance"]


@register(BotStatistics)
class BotStatisticsAdmin(admin.ModelAdmin):
    list_display = ["__str__", "instance"]


@register(ArtifactStatistics)
class ArtifactStatisticsAdmin(admin.ModelAdmin):
    list_display = ["__str__", "instance"]
    filter_horizontal = ["artifacts"]


@register(ArtifactOwned)
class ArtifactOwnedAdmin(admin.ModelAdmin):
    list_display = ["__str__", "instance", "owned"]


@register(PrestigeStatistics)
class PrestigeStatisticsAdmin(admin.ModelAdmin):
    list_display = ["__str__", "instance"]


@register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ["__str__", "instance", "uuid", "version", "start"]


@register(GlobalSettings)
class GlobalSettingsAdmin(admin.ModelAdmin):
    list_display = ["pk", "failsafe_settings", "event_settings", "pihole_ads_settings"]
