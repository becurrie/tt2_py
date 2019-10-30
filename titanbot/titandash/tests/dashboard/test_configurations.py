"""
test_configuration.py

Test functionality related to the configuration model.
"""
from django.test import TestCase

from titandash.models.configuration import Configuration
from titandash.models.artifact import Artifact, Tier


class ConfigurationTests(TestCase):
    """
    Configuration Tests used to test any functionality performed by the configuration model.
    """
    @classmethod
    def setUpTestData(cls):
        super(ConfigurationTests, cls).setUpTestData()

        # Creating some base configuration models for use with our tests.
        cls.config_1 = Configuration.objects.create(
            name="Test Config 1",
            soft_shutdown_on_critical_error=True,
            enable_egg_collection=False,
            enable_breaks=False,
            enable_heroes=False,
            enable_logging=False,
            logging_level="DEBUG"
        )
        # Modify the artifact upgrade settings so that
        # we can also test our relational fields.
        cls.config_2 = Configuration.objects.create(name="Test Config 2")

        cls.export_strings = {
            1: "0:Test Config 1&1:+BT&2:+BT&3:0&4:1&5:nox&9:+BT&96:1&79:+BT&80:+BT&8:+BF&10:+BT&74:+BF&97:1&75:+BF&76:+BF&77:+BF&78:+BF&11:+BF&12:40&13:180&14:60&15:20&16:+BT&17:+BF&18:1&19:+BT&20:+BF&21:1&22:+BF&23:+BF&24:30&34:+BT&81:60&92:+BT&70:+BF&35:5&36:+BF&82:60&93:+BT&37:3&83:+BT&84:120&94:+BT&85:max&86:max&87:max&88:max&89:max&90:max&91:+BT&95:30&39:+BT&40:0&41:20&42:30&43:40&44:50&45:60&49:+BT&71:+BT&72:2&73:8&50:45&51:0&52:+BF&53:0&55:+BT&54:+BT&57:+BT&60:+BT&61:+BF&62:60&63:+BT&64:+BF&65:300&68:+BF&69:DEBUG&56:+MNone&58:+MNone&59:+MNone",
            2: "0:Test Config 2&1:+BF&2:+BT&3:0&4:1&5:nox&9:+BT&96:1&79:+BT&80:+BT&8:+BT&10:+BT&74:+BF&97:1&75:+BF&76:+BF&77:+BF&78:+BF&11:+BT&12:40&13:180&14:60&15:20&16:+BT&17:+BF&18:1&19:+BT&20:+BF&21:1&22:+BF&23:+BF&24:30&34:+BT&81:60&92:+BT&70:+BF&35:5&36:+BT&82:60&93:+BT&37:3&83:+BT&84:120&94:+BT&85:max&86:max&87:max&88:max&89:max&90:max&91:+BT&95:30&39:+BT&40:0&41:20&42:30&43:40&44:50&45:60&49:+BT&71:+BT&72:2&73:8&50:45&51:0&52:+BF&53:0&55:+BT&54:+BT&57:+BT&60:+BT&61:+BF&62:60&63:+BT&64:+BF&65:300&68:+BT&69:INFO&56:+MS&58:+M95|20|66|82|94|26|31|29|51|59|83|35|32|33|34|61|62|64|53|67|56|75|76|77|25|17|23|73|28|87|86|88|89|90|9|10|7|74|69|71|91|92|93|80|81|85&59:+M22"
        }

        cls.upgrade_tier = Tier.objects.get(tier="S")
        cls.ignore_arts = Artifact.objects.filter(tier__tier="A")
        cls.upgrade_art = Artifact.objects.get(name="book_of_shadows")

        cls.config_2.upgrade_owned_tier.add(cls.upgrade_tier)
        cls.config_2.ignore_artifacts.add(*cls.ignore_arts)
        cls.config_2.upgrade_artifacts.add(cls.upgrade_art)

    def test_configuration_export(self):
        """
        Test the configuration export functionality.
        """
        self.assertEqual(first=self.config_1.export_model(), second=self.export_strings[1])
        self.assertEqual(first=self.config_2.export_model(), second=self.export_strings[2])

    def test_configuration_import(self):
        """
        Test the configuration import functionality.
        """
        imported_1 = Configuration.import_model(export_kwargs=Configuration.import_model_kwargs(export_string=self.export_strings[1]))
        imported_2 = Configuration.import_model(export_kwargs=Configuration.import_model_kwargs(export_string=self.export_strings[2]))

        # Verify that the first imported configuration contains proper values.
        self.assertEqual(first=imported_1.name, second="Imported " + self.config_1.name)
        self.assertEqual(first=imported_1.soft_shutdown_on_critical_error, second=self.config_1.soft_shutdown_on_critical_error)
        self.assertEqual(first=imported_1.enable_egg_collection, second=self.config_1.enable_egg_collection)
        self.assertEqual(first=imported_1.enable_breaks, second=self.config_1.enable_breaks)
        self.assertEqual(first=imported_1.enable_heroes, second=self.config_1.enable_heroes)
        self.assertEqual(first=imported_1.enable_logging, second=self.config_1.enable_logging)
        self.assertEqual(first=imported_1.logging_level, second=self.config_1.logging_level)

        # Artifact assertions.
        self.assertEqual(first=list(imported_1.upgrade_owned_tier.all()), second=list(self.config_1.upgrade_owned_tier.all()))
        self.assertEqual(first=list(imported_1.ignore_artifacts.all()), second=list(self.config_1.ignore_artifacts.all()))
        self.assertEqual(first=list(imported_1.upgrade_artifacts.all()), second=list(self.config_1.upgrade_artifacts.all()))

        # Verify that the second imported configuration contains proper values.
        self.assertEqual(first=imported_2.name, second="Imported " + self.config_2.name)

        # Artifact assertions.
        self.assertEqual(first=list(imported_2.upgrade_owned_tier.all()), second=list(self.config_2.upgrade_owned_tier.all()))
        self.assertEqual(first=list(imported_2.ignore_artifacts.all()), second=list(self.config_2.ignore_artifacts.all()))
        self.assertEqual(first=list(imported_2.upgrade_artifacts.all()), second=list(self.config_2.upgrade_artifacts.all()))
