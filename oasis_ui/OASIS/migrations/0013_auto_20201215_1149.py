# Generated by Django 3.0 on 2020-12-15 18:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('OASIS', '0012_auto_20201208_0942'),
    ]

    operations = [
        migrations.AlterField(
            model_name='routeprop',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AlterField(
            model_name='routeprop',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
    ]
