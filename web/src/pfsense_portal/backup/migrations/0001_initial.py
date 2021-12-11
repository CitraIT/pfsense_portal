# Generated by Django 3.2.9 on 2021-11-12 01:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('firewall', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='BackupFile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('path', models.CharField(max_length=255)),
                ('is_encrypted', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='BackupPolicy',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('run_hour', models.IntegerField()),
                ('run_minutes', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Backup',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_date', models.DateTimeField()),
                ('finish_date', models.DateTimeField()),
                ('file', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='backup.backupfile')),
                ('firewall', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='firewall.firewall')),
            ],
        ),
    ]
