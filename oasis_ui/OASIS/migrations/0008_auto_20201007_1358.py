# Generated by Django 3.0 on 2020-10-07 20:58

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('OASIS', '0007_auto_20201007_0935'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='appsetting',
            options={'managed': True, 'verbose_name': 'Application Setting', 'verbose_name_plural': 'Application Settings'},
        ),
        migrations.AlterModelOptions(
            name='auditprop',
            options={'managed': True, 'verbose_name': 'Audit Property', 'verbose_name_plural': 'Audit Properties'},
        ),
        migrations.AlterModelOptions(
            name='endpointprop',
            options={'managed': True, 'verbose_name': 'Endpoint Property', 'verbose_name_plural': 'Endpoint Properties'},
        ),
        migrations.AlterModelOptions(
            name='intrequest',
            options={'managed': True, 'verbose_name': 'Integration Request'},
        ),
        migrations.AlterModelOptions(
            name='intrequestprop',
            options={'managed': True, 'verbose_name': 'Integration Request Property', 'verbose_name_plural': 'Integration Request Properties'},
        ),
        migrations.AlterModelOptions(
            name='routeprop',
            options={'managed': True, 'verbose_name': 'Route Property', 'verbose_name_plural': 'Route Properties'},
        ),
        migrations.AddField(
            model_name='intrequest',
            name='name',
            field=models.CharField(default='empty', max_length=255),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='endpointprop',
            name='endpoint',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='Properties', to='OASIS.Endpoint'),
        ),
        migrations.AlterField(
            model_name='routeprop',
            name='route',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='Properties', to='OASIS.Route'),
        ),
    ]
