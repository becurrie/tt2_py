from django.db import models

from titandash.constants import LOGGING_LEVEL_CHOICES, INFO


HELP_TEXT = {
    "failsafe_settings": "Enable or disable the failsafe functionality when a bot session is running. Note that turning this setting off may make it difficult to kill a bot session if an unrecoverable failure occurs. You can always force quit the application if needed though.",
    "event_settings": "Enable or disable the different functionality depending on whether or not an event is currently running in game that modifies in game locations.",
    "pihole_ads_settings": "Enable or disable the ability to watch and collect ads without vip while using pihole to prevent ads from running within tap titans 2. This allows users to basically get the benefits of VIP, without a VIP enabled account. <strong>Note:</strong> This setting will only work if you have properly installed and setup a <a href='https://pi-hole.net/'>pihole</a> server. Titandash does <strong>not</strong> handle this process for you.",
    "welcome_screen_checks_settings": "Enable or disable the option to check for the welcome screen while a bot is running (turning this off may improve performance if you have disabled the welcome screen in your settings).",
    "rate_screen_checks_settings": "Enable or disable the option to check for the rate screen while a bot is running (turning this off may improve performance if you no longer get prompted to rate the game anymore).",
    "logging_level": "Choose a logging level that will be used by bot sessions when they are running.",
}


ON = "on"
OFF = "off"

FAILSAFE_CHOICES = (
    (ON, "On"),
    (OFF, "Off")
)

EVENT_CHOICES = (
    (ON, "On"),
    (OFF, "Off")
)

PIHOLE_ADS_CHOICES = (
    (ON, "On"),
    (OFF, "Off")
)

WELCOME_SCREEN_CHOICES = (
    (ON, "On"),
    (OFF, "Off")
)

RATE_SCREEN_CHOICES = (
    (ON, "On"),
    (OFF, "Off")
)


class GlobalSettingsManager(models.Manager):
    def grab(self, qs=False):
        """
        Attempt to grab the global settings manager instance. We only ever want a single instance. If one does not
        exist yet, we generate a new ne with sme default values.
        """
        if len(self.all()) == 0:
            self.create()

        # Return the explicit queryset if specified.
        # This may prove useful if we wish to perform an update.
        if qs:
            return self.all()

        return self.first()


class GlobalSettings(models.Model):
    """
    GlobalSettings Model.

    Store references to defaults and overridable settings that a user can modify to their liking.
    """
    class Meta:
        verbose_name = "Global Settings"
        verbose_name_plural = "Global Settings"

    objects = GlobalSettingsManager()
    failsafe_settings = models.CharField(verbose_name="Failsafe Settings", max_length=255, choices=FAILSAFE_CHOICES, default=ON, help_text=HELP_TEXT["failsafe_settings"])
    event_settings = models.CharField(verbose_name="In Game Event Settings", max_length=255, choices=EVENT_CHOICES, default=OFF, help_text=HELP_TEXT["event_settings"])
    pihole_ads_settings = models.CharField(verbose_name="Enable PI-Hole Ads", max_length=255, choices=PIHOLE_ADS_CHOICES, default=OFF, help_text=HELP_TEXT["pihole_ads_settings"])
    welcome_screen_checks_settings = models.CharField(verbose_name="Enable Welcome Screen Checks", max_length=255, choices=WELCOME_SCREEN_CHOICES, default=ON, help_text=HELP_TEXT["welcome_screen_checks_settings"])
    rate_screen_checks_settings = models.CharField(verbose_name="Enable Rate Screen Checks", max_length=255, choices=RATE_SCREEN_CHOICES, default=ON, help_text=HELP_TEXT["rate_screen_checks_settings"])
    logging_level = models.CharField(verbose_name="Logging Level", max_length=255, choices=LOGGING_LEVEL_CHOICES, default=INFO, help_text=HELP_TEXT["logging_level"])

    def __str__(self):
        return "GlobalSettings {id}".format(id=self.pk)

    def json(self):
        """
        Convert the GlobalSettings into a JSON compliant dictionary.
        """
        return {
            "id": self.pk,
            "failsafe_settings": self.failsafe_settings,
            "event_settings": self.event_settings,
            "pihole_settings": self.pihole_ads_settings,
            "welcome_screen_checks_settings": self.welcome_screen_checks_settings,
            "rate_screen_checks_settings": self.rate_screen_checks_settings,
            "logging_level": self.logging_level,
        }

    def form_dict(self):
        """
        Return a contextual dictionary with information used to create global settings forms.
        """
        return {
            "global_settings": self,
            "help": HELP_TEXT,
            "choices": {
                "failsafe_settings": FAILSAFE_CHOICES,
                "event_settings": EVENT_CHOICES,
                "pihole_settings": PIHOLE_ADS_CHOICES,
                "welcome_screen_checks_settings": WELCOME_SCREEN_CHOICES,
                "rate_screen_checks_settings": RATE_SCREEN_CHOICES,
                "logging_level": LOGGING_LEVEL_CHOICES
            }
        }

    @property
    def failsafe_enabled(self):
        return self.failsafe_settings == ON

    @property
    def events_enabled(self):
        return self.event_settings == ON

    @property
    def pihole_ads_enabled(self):
        return self.pihole_ads_settings == ON

    @property
    def welcome_screen_checks_enabled(self):
        return self.welcome_screen_checks_settings == ON

    @property
    def rate_screen_checks_enabled(self):
        return self.rate_screen_checks_settings == ON
