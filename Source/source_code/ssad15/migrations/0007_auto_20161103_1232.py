# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2016-11-03 12:32
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('ssad15', '0006_auto_20161103_1231'),
    ]

    operations = [
        migrations.AlterField(
            model_name='running_slots',
            name='start_time',
            field=models.DateTimeField(default=datetime.datetime(2016, 11, 3, 12, 32, 51, 279205, tzinfo=utc), verbose_name='Starting week of the advertisement'),
        ),
    ]
