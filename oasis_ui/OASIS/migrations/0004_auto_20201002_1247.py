# Generated by Django 3.0 on 2020-10-02 19:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('OASIS', '0003_auto_20200930_1147'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mftschedule',
            name='freq_type',
            field=models.CharField(choices=[('Daily', 'Daily'), ('Hours', 'Hours'), ('Minutes', 'Minutes'), ('Monthly', 'Monthly'), ('Monthly_Weekly', 'Monthly Weekly'), ('Specific_Date_and_Time', 'Specific Date and Time'), ('Specific_Time_Daily', 'Specific Time Daily'), ('Trigger', 'Trigger'), ('Weekly', 'Weekly'), ('Yearly', 'Yearly')], max_length=100),
        ),
    ]
