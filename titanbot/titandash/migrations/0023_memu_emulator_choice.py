# Generated by Django 2.2.5 on 2019-10-12 14:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('titandash', '0022_configuration_help_texts'),
    ]

    operations = [
        migrations.AlterField(
            model_name='configuration',
            name='emulator',
            field=models.CharField(choices=[('nox', 'Nox Emulator'), ('memu', 'MEmu Emulator')], default='nox', help_text='Which emulator service is being used?', max_length=255, verbose_name='Emulator'),
        ),
    ]