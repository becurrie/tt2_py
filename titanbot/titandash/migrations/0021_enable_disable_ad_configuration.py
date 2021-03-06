# Generated by Django 2.2.5 on 2019-10-06 19:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('titandash', '0020_milestone_help_texts'),
    ]

    operations = [
        migrations.AddField(
            model_name='configuration',
            name='enable_ad_collection',
            field=models.BooleanField(default=True, help_text='Enable to ability to collect ads in game.', verbose_name='Enable Ad Collection'),
        ),
        migrations.AlterField(
            model_name='configuration',
            name='enable_premium_ad_collect',
            field=models.BooleanField(default=False, help_text='Enable the premium ad collection, Note: This will only work if you have unlocked the ability to skip ads, watching ads is not supported.', verbose_name='Enable Premium Ad Collection'),
        ),
    ]
