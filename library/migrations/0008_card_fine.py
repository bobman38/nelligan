# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2018-04-07 01:31
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('library', '0007_book_renewed'),
    ]

    operations = [
        migrations.AddField(
            model_name='card',
            name='fine',
            field=models.CharField(max_length=200, null=True),
        ),
    ]
