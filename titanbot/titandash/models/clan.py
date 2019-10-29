from django.db import models
from django.db.models import Sum

from titandash.constants import DATETIME_FMT


class UnParsableRaidResultLine(Exception):
    pass


class Clan(models.Model):
    """
    Generic clan model. Simply storing the clan name and code.
    """
    class Meta:
        verbose_name = "Clan"
        verbose_name_plural = "Clans"

    code = models.CharField(max_length=255)
    name = models.CharField(max_length=255)

    def __str__(self):
        return "Clan: {name} ({code})".format(name=self.name, code=self.code)

    def json(self):
        return {
            "code": self.code,
            "name": self.name
        }


class Member(models.Model):
    """
    Clan member model, store the name and code of each member in a clan.
    """
    class Meta:
        verbose_name = "Member"
        verbose_name_plural = "Members"

    code = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    clan = models.ForeignKey(to=Clan, on_delete=models.CASCADE)

    def __str__(self):
        return "Member: {name} ({code})".format(name=self.name, code=self.code)

    def json(self):
        return {
            "code": self.code,
            "name": self.name,
            "clan": self.clan.json()
        }


class RaidResultDamage(models.Model):
    """
    Store instances of damage done during a specific instance of a RaidResult.
    """
    class Meta:
        verbose_name = "Raid Result Damage"
        verbose_name_plural = "Raid Results Damages"

    rank = models.PositiveIntegerField()
    attacks = models.PositiveIntegerField()
    damage = models.PositiveIntegerField()
    member = models.ForeignKey(to=Member, on_delete=models.CASCADE)

    def __str__(self):
        return "{member} - {attacks}: {damage}".format(member=self.member, attacks=self.attacks, damage=self.damage)

    def json(self):
        return {
            "rank": self.rank,
            "attacks": self.attacks,
            "damage": {
                "damage": self.damage,
                "formatted": "{:,}".format(self.damage)
            },
            "member": self.member.json()
        }


class RaidResultManager(models.Manager):
    """
    Custom manager to allow the generation of new RaidResult instances
    when a valid set of clipboard data is available.
    """
    def generate(self, clipboard, clan, instance):
        """
        Generate a new RaidResults instance.

        Creating a digested version of the clipboard content and clan info
        that can be used as a way to determine if the current result being generated
        should be trashed or not based on whether or not the result already exists in the system.

        After the digest is present, we parse the data to generate Clan members if they
        do not already exist, as well as raid attack instances for each user.

        Finally, we generate the RaidResult with all associated data.
        """
        def split_csv(_csv):
            """
            Split the clipboard text result by any newline instances. Some malformed data may
            be present after the proper data when split, so we remove it if it is present.
            """
            data = _csv.split("\n")

            if len(data) > 51:
                return data[1:51]
            else:
                return data[1:]

        def parse_line(line):
            try:
                _rank, _name, _code, _attacks, _damage = line.split(",")
            except ValueError:
                raise UnParsableRaidResultLine

            try:
                _rank = int(_rank)
                _attacks = int(_attacks)
                _damage = int(_damage)
            except ValueError:
                raise UnParsableRaidResultLine

            return _rank, _name, _code, _attacks, _damage

        def generate_digest(csv):
            """
            Generate a simple digested version of the clipboard content. We use this to simply compare
            copied content so we can early exit if one that has already been parsed is parsed again.
            """
            _dmg = 0
            _atks = 0

            for _res in split_csv(csv):
                try:
                    _rank, _name, _code, _attacks, _damage = parse_line(_res)
                except UnParsableRaidResultLine:
                    continue

                _dmg += _damage
                _atks += _attacks

            return str(_atks) + str(_dmg)

        digest = generate_digest(clipboard)
        if self.filter(digest=digest).count() > 0:
            return False

        # This is a unique clan raid result instance, begin parsing the relevant
        # data from the clipboard CSV output.
        members = []
        raid_damage_results = []

        for res in split_csv(clipboard):
            try:
                rank, name, code, attacks, damage = parse_line(res)
            except UnParsableRaidResultLine:
                continue

            # Clan members can easily change their usernames, ensure
            # the name stays up to date in the database if the name changes.
            try:
                member = Member.objects.get(code=code, clan=clan)
            except Member.DoesNotExist:
                member = Member.objects.create(code=code, name=name, clan=clan)

            if member.name != name:
                member.name = name
                member.save()

            result = RaidResultDamage.objects.get_or_create(rank=rank, attacks=attacks, damage=damage, member=member)[0]

            members.append(member)
            raid_damage_results.append(result)

        # The clan members and attack instances are generated, generating the
        # actual RaidResult that will be used.
        result = self.create(digest=digest, clan=clan, instance=instance)
        result.attacks.add(*raid_damage_results)
        result.save()

        return result


class RaidResult(models.Model):
    """
    Main storage for parsed raid results.
    """
    class Meta:
        verbose_name = "Raid Result"
        verbose_name_plural = "Raid Results"

    objects = RaidResultManager()
    digest = models.CharField(max_length=255, unique=True)
    parsed = models.DateTimeField(auto_created=True, auto_now_add=True)
    clan = models.ForeignKey(to=Clan, on_delete=models.CASCADE)
    attacks = models.ManyToManyField(to=RaidResultDamage)
    instance = models.ForeignKey(verbose_name="Instance", to="BotInstance", null=True, on_delete=models.CASCADE)

    def __str__(self):
        return "{instance} RaidResult: {parsed} - {clan}".format(instance=self.instance.name, parsed=self.parsed, clan=self.clan)

    def total_damage(self):
        agg = self.attacks.aggregate(Sum("damage"))

        return {
            "damage": agg["damage__sum"],
            "formatted": "{:,}".format(agg["damage__sum"]) if agg["damage__sum"] else None
        }

    def json(self):
        from django.urls import reverse
        return {
            "digest": self.digest,
            "instance": self.instance.name,
            "parsed": {
                "datetime": str(self.parsed),
                "formatted": self.parsed.astimezone().strftime(DATETIME_FMT),
                "epoch": int(self.parsed.timestamp())
            },
            "clan": self.clan.json(),
            "attacks": [attack.json() for attack in self.attacks.all().order_by("rank")],
            "total_damage": self.total_damage(),
            "url": reverse("raid", kwargs={"digest": self.digest})
        }
