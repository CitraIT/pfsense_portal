# Generated by Django 3.2.9 on 2021-11-13 23:48

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('backup', '0003_auto_20211111_2303'),
    ]

    operations = [
        migrations.AlterField(
            model_name='backup',
            name='start_date',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
