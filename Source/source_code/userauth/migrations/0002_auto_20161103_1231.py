# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2016-11-03 12:31
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('userauth', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='uploadadvetisement',
            name='start_week',
            field=models.DateTimeField(default=datetime.datetime(2016, 11, 3, 12, 31, 38, 821694, tzinfo=utc), verbose_name='Starting week of the advertisement'),
        ),
    ]
