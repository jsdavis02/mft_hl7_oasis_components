# Generated by Django 3.0 on 2020-12-16 16:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('OASIS', '0014_auto_20201215_1315'),
    ]

    operations = [
        migrations.AlterField(
            model_name='endpointprop',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AlterField(
            model_name='endpointprop',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
    ]
