# Generated by Django 3.1.5 on 2021-07-19 18:44

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('frontend', '0012_auto_20210719_1836'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='clocksystem',
            options={'ordering': ('employee', 'date_in', 'date_out', 'clocked_in_at', 'clocked_out_at', 'location', 'role', 'time_worked', 'in_comment', 'out_comment')},
        ),
    ]
