# Generated by Django 3.2.9 on 2022-06-03 03:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('firewall', '0002_firewall_api_key'),
    ]

    operations = [
        migrations.AddField(
            model_name='firewall',
            name='is_online',
            field=models.BooleanField(default=False),
        ),
    ]
