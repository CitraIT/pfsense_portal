# Generated by Django 3.2.9 on 2021-11-12 01:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backup', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='backuppolicy',
            name='name',
            field=models.CharField(default='default policy', max_length=40),
        ),
    ]