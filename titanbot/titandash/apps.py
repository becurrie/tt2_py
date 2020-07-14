from django.apps import AppConfig
from django.db.models.signals import post_migrate


class TitandashConfig(AppConfig):
    name = "titandash"
    verbose_name = "TitanDash"

    def ready(self):
        post_migrate.connect(migrate_callback, sender=self)

        # Importing checks.
        import titandash.checks


def migrate_callback(sender, **kwargs):
    """
    When TitanDash is migrated. Some additional data should be generated in regards to the artifacts available
    in the Bot's artifact maps. As new artifacts are released and added, this callback should handle adding
    them to the database.
    """
    from django.contrib.auth.models import User
    from titandash.models.artifact import Artifact, Tier
    from titandash.models.configuration import Configuration
    from titandash.bot.core.maps import ARTIFACT_TIER_MAP

    try:
        for tier, dct in ARTIFACT_TIER_MAP.items():
            if tier not in Tier.objects.all().values_list("tier", flat=True):
                Tier.objects.create(tier=tier, name="Tier {tier}".format(tier=tier))

            artifacts = Artifact.objects.all()
            for name, value in dct.items():
                if name not in artifacts.values_list("name", flat=True):
                    Artifact.objects.create(
                        name=name,
                        tier=Tier.objects.get(tier=tier),
                        key=value[1],
                        image="{name}.png".format(name=name.replace("'", ""))
                    )

        # Generating a default configuration if none exist yet.
        if Configuration.objects.all().count() == 0:
            cfg = Configuration.objects.create(name="DEFAULT")
            cfg.upgrade_owned_tier.add(Tier.objects.get(tier="S"))
            cfg.save()

    # TypeError may occur when migrating to 'zero' or if migration does not include
    # the needed models (Artifact, Tier, etc)... Pass in this case and ignore safely.
    except TypeError:
        pass
