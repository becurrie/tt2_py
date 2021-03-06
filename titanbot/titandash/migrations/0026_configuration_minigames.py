# Generated by Django 2.2.5 on 2019-10-20 14:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('titandash', '0025_configuration_prestige_randomization'),
    ]

    operations = [
        migrations.AddField(
            model_name='configuration',
            name='enable_astral_awakening',
            field=models.BooleanField(default=False, help_text='Enable astral awakening tapping skill minigame.', verbose_name='Enable Astral Awakening'),
        ),
        migrations.AddField(
            model_name='configuration',
            name='enable_coordinated_offensive',
            field=models.BooleanField(default=False, help_text='Enable coordinated offensive tapping skill minigame.', verbose_name='Enable Coordinated Offensive'),
        ),
        migrations.AddField(
            model_name='configuration',
            name='enable_flash_zip',
            field=models.BooleanField(default=False, help_text='Enable flash zip tapping skill minigame.', verbose_name='Enable Flash Zip'),
        ),
        migrations.AddField(
            model_name='configuration',
            name='enable_heart_of_midas',
            field=models.BooleanField(default=False, help_text='Enable heart of midas tapping skill minigame.', verbose_name='Enable Heart Of Midas'),
        ),
        migrations.AddField(
            model_name='configuration',
            name='enable_minigames',
            field=models.BooleanField(default=False, help_text='Enable the ability to enable/disable different skill minigames that can be executed.', verbose_name='Enable Skill Minigames'),
        ),
    ]
