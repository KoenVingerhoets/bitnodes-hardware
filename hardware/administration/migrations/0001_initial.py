# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import hardware.administration.models


class Migration(migrations.Migration):

    dependencies = [
        ('sites', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Bandwidth',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('updated_date', models.DateTimeField(auto_now=True)),
                ('max_uplink', models.PositiveIntegerField(default=0)),
                ('site', models.OneToOneField(to='sites.Site', on_delete=django.db.models.deletion.CASCADE)),
            ],
        ),
        migrations.CreateModel(
            name='BitcoinAddress',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('updated_date', models.DateTimeField(auto_now=True)),
                ('bitcoin_address', models.CharField(blank=True, unique=True, max_length=35, validators=[hardware.administration.models.validate_bitcoin_address])),
                ('site', models.OneToOneField(to='sites.Site', on_delete=django.db.models.deletion.CASCADE)),
            ],
        ),
    ]
