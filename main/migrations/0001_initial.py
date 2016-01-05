# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Teams',
            fields=[
                ('access_token', models.CharField(max_length=1000)),
                ('team_name', models.CharField(max_length=1000)),
                ('team_id', models.CharField(max_length=1000, serialize=False, primary_key=True)),
                ('incoming_webhook_url', models.CharField(max_length=1000)),
                ('incoming_webhook_configuration_url', models.CharField(max_length=1000)),
                ('last_changed', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
