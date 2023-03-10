# Generated by Django 3.0 on 2020-09-25 20:54

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AppSetting',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField()),
                ('value', models.TextField()),
                ('env', models.CharField(max_length=25)),
            ],
            options={
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Audit',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('processstate', models.CharField(db_column='ProcessState', max_length=50)),
                ('messageguid', models.BigIntegerField(db_column='MessageGUID')),
                ('messagecontrolid', models.TextField(blank=True, db_column='MessageControlID', null=True)),
                ('datetimeofmessage', models.DateTimeField(blank=True, db_column='DateTimeofMessage', null=True)),
                ('created_at', models.DateTimeField(blank=True, null=True)),
                ('modified_at', models.DateTimeField(blank=True, null=True)),
                ('proc_time', models.DateTimeField(blank=True, null=True)),
                ('messagepayload', models.TextField(blank=True, db_column='MessagePayload', null=True)),
                ('producer_ident', models.CharField(blank=True, max_length=50, null=True)),
                ('consumer_ident', models.CharField(blank=True, max_length=50, null=True)),
                ('route_id', models.BigIntegerField(blank=True, null=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('producer_id', models.BigIntegerField(blank=True, null=True)),
                ('consumer_id', models.BigIntegerField(blank=True, null=True)),
                ('type', models.CharField(blank=True, max_length=25, null=True)),
                ('messagereference', models.TextField(blank=True, db_column='MessageReference', null=True)),
                ('data_format', models.CharField(blank=True, max_length=100, null=True)),
            ],
            options={
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Endpoint',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('organization', models.CharField(max_length=100)),
                ('software', models.CharField(blank=True, max_length=50, null=True)),
                ('doclink', models.TextField(blank=True, null=True)),
                ('subsystem', models.TextField(blank=True, null=True)),
                ('active', models.BooleanField()),
                ('alert_level', models.IntegerField()),
                ('description', models.TextField(blank=True, null=True)),
                ('direction', models.CharField(blank=True, max_length=25, null=True)),
                ('bw_process_ident', models.CharField(blank=True, max_length=75, null=True)),
                ('receiving_app', models.CharField(blank=True, max_length=25, null=True)),
                ('receiving_facility', models.CharField(blank=True, max_length=25, null=True)),
                ('name', models.TextField(blank=True, null=True)),
                ('type', models.CharField(max_length=25)),
                ('portmon_host', models.CharField(blank=True, max_length=25, null=True)),
                ('portmon_time', models.DateTimeField(blank=True, null=True)),
                ('bw_app_ident', models.CharField(blank=True, max_length=75, null=True)),
            ],
            options={
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='IntRequest',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('contact_name', models.CharField(max_length=255)),
                ('contact_email', models.CharField(max_length=255)),
                ('contact_phone', models.CharField(blank=True, max_length=255, null=True)),
                ('description', models.CharField(blank=True, max_length=255, null=True)),
                ('producer_description', models.CharField(blank=True, max_length=255, null=True)),
                ('consumer_description', models.CharField(blank=True, max_length=255, null=True)),
                ('producer_type', models.CharField(max_length=255)),
                ('consumer_type', models.CharField(max_length=255)),
                ('data_transfer_req', models.CharField(blank=True, max_length=255, null=True)),
                ('data_manipulation_req', models.CharField(blank=True, max_length=255, null=True)),
                ('doclink', models.CharField(blank=True, max_length=255, null=True)),
                ('createdat', models.TextField(db_column='createdAt')),
                ('updatedat', models.TextField(db_column='updatedAt')),
                ('status', models.CharField(max_length=255)),
            ],
            options={
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Route',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('producer_id', models.BigIntegerField()),
                ('consumer_id', models.BigIntegerField()),
                ('producer_messagetypemessagecode', models.CharField(max_length=50)),
                ('producer_messagetypetriggerevent', models.CharField(max_length=50)),
                ('consumer_messagetypemessagecode', models.CharField(max_length=50)),
                ('consumer_messagetypetriggerevent', models.CharField(max_length=50)),
                ('hascriteria', models.BooleanField(db_column='hasCriteria')),
                ('active', models.BooleanField()),
                ('hassplit', models.BooleanField(db_column='hasSplit')),
                ('hastranslation', models.BooleanField(db_column='hasTranslation')),
                ('type', models.CharField(max_length=25)),
                ('name', models.CharField(blank=True, max_length=255, null=True)),
                ('description', models.TextField(blank=True, null=True)),
            ],
            options={
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='RouteProp',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=50)),
                ('value', models.TextField(blank=True, null=True)),
                ('env', models.CharField(max_length=25)),
                ('route', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='OASIS.Route')),
            ],
            options={
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='MftSchedule',
            fields=[
                ('name', models.TextField()),
                ('active', models.BooleanField()),
                ('freq_type', models.CharField(max_length=100)),
                ('freq_interval', models.IntegerField(blank=True, null=True)),
                ('spec_date', models.DateField(blank=True, null=True)),
                ('spec_time', models.TimeField(blank=True, null=True)),
                ('last_run', models.DateTimeField()),
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('sub_day_freq_type', models.CharField(blank=True, max_length=100, null=True)),
                ('sub_day_freq_interval', models.IntegerField(blank=True, null=True)),
                ('sub_day_stop_schedule', models.BooleanField(blank=True, null=True)),
                ('sub_day_start_time', models.TimeField(blank=True, null=True)),
                ('sub_day_end_time', models.TimeField(blank=True, null=True)),
                ('last_files_found', models.DateTimeField(blank=True, null=True)),
                ('sub_day_last_run', models.DateField(blank=True, null=True)),
                ('pause_start', models.DateTimeField(blank=True, null=True)),
                ('pause_end', models.DateTimeField(blank=True, null=True)),
                ('sub_freq_interval', models.IntegerField(blank=True, null=True)),
                ('endpoint', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='OASIS.Endpoint')),
            ],
            options={
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='IntRequestProp',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('value', models.CharField(blank=True, max_length=255, null=True)),
                ('env', models.CharField(max_length=255)),
                ('int_request', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='OASIS.IntRequest')),
            ],
            options={
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='EndpointProp',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=75)),
                ('value', models.TextField(blank=True, null=True)),
                ('env', models.CharField(max_length=25)),
                ('endpoint', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='OASIS.Endpoint')),
            ],
            options={
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='AuditProp',
            fields=[
                ('name', models.TextField()),
                ('value', models.TextField(blank=True, null=True)),
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('audit', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='OASIS.Audit')),
            ],
            options={
                'managed': True,
            },
        ),
    ]
