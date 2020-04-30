from settings import LOCAL_DATA_SCREENSHOTS_DIR

from django.db import models
from django.urls import reverse

from titandash.constants import DATETIME_FMT

import os


class Participant(models.Model):
    """
    Participant Model.

    Store all participants within the tournament they are a part of.

    We can include some additional information about each one as well to
    derive their placement in a tournament as well as the stage they reached.
    """
    rank = models.CharField(verbose_name="Rank", blank=True, max_length=255)
    username = models.CharField(verbose_name="Username", blank=True, max_length=255)
    stage = models.CharField(verbose_name="Stage", blank=True, max_length=255)
    is_user = models.BooleanField(verbose_name="Is User")

    def __str__(self):
        return "<{username}> - Rank: {rank} - Stage: {stage}".format(
            username=self.username,
            rank=self.rank,
            stage=self.stage
        )

    def json(self):
        """
        Return Participant As JSON.
        """
        return {
            "pk": self.pk,
            "rank": self.rank or "N/A",
            "username": self.username or "N/A",
            "stage": self.stage or "N/A",
            "is_user": self.is_user
        }


class Tournament(models.Model):
    """
    Tournament Model.

    Store all tournaments in the database with the participants for each included as well as some additional information.
    """
    class Meta:
        verbose_name = "Tournament"
        verbose_name_plural = "Tournaments"

    instance = models.ForeignKey(verbose_name="Bot Instance", to="BotInstance", on_delete=models.CASCADE)
    identifier = models.CharField(verbose_name="Identifier", unique=True, max_length=255)
    finished = models.DateTimeField(verbose_name="Finished", auto_now_add=True)
    participants = models.ManyToManyField(verbose_name="Participants", to="Participant")

    def __str__(self):
        return "Tournament <{identifier}>".format(
            identifier=self.identifier
        )

    def delete(self, using=None, keep_parents=False):
        """
        When a tournament is deleted, we should also attempt to remove the screenshot associated with it.
        """
        try:
            os.remove(os.path.join(LOCAL_DATA_SCREENSHOTS_DIR, self.screenshot))
        except FileNotFoundError:
            pass

        super(Tournament, self).delete(using=using, keep_parents=keep_parents)

    @property
    def screenshot(self):
        """
        Return the name of the screenshot associated with this tournament.
        """
        return "{identifier}.png".format(identifier=self.identifier)

    def json(self):
        """
        Return Tournament As JSON.
        """
        return {
            "pk": self.pk,
            "instance": self.instance.pk,
            "screenshot": self.screenshot,
            "identifier": self.identifier,
            "url": reverse("tournament", kwargs={"identifier": self.identifier}),
            "finished": {
                "datetime": str(self.finished),
                "formatted": self.finished.astimezone().strftime(DATETIME_FMT),
                "epoch": int(self.finished.timestamp())
            },
            "participants": [p.json() for p in self.participants.all()],
            "participants_count": self.participants.count(),
            "user_rank": self.user_rank,
            "user_stage": self.user_stage,
        }

    @property
    def user_rank(self):
        """
        Return the users rank from all available participants.
        """
        try:
            return self.participants.filter(is_user=True).first().rank
        except models.ObjectDoesNotExist:
            return "N/A"

    @property
    def user_stage(self):
        """
        Return the users stage from all available participants.
        """
        try:
            return self.participants.filter(is_user=True).first().stage
        except models.ObjectDoesNotExist:
            return "N/A"
