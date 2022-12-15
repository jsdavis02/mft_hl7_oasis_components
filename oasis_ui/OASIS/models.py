import configparser
import os
from base64 import b64decode
from base64 import b64encode

import nacl
import nacl.secret
import nacl.utils
from django.db import models
from django.conf import settings
from django.utils.datetime_safe import datetime


class AppSetting(models.Model):
    name = models.TextField()
    value = models.TextField()
    env = models.CharField(max_length=25)

    class Meta:
        managed = True
        verbose_name = 'Application Setting'
        verbose_name_plural = 'Application Settings'

    def __str__(self):
        return self.name+' : '+self.value+' : '+self.env


class AuditProp(models.Model):
    audit = models.ForeignKey('Audit', on_delete=models.CASCADE, related_name='auditprop')
    name = models.TextField()
    value = models.TextField(blank=True, null=True)
    id = models.BigAutoField(primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)

    class Meta:
        managed = True
        verbose_name = 'Audit Property'
        verbose_name_plural = 'Audit Properties'

    def __str__(self):
        return str(self.name)+'='+str(self.value)


class Audit(models.Model):
    id = models.BigAutoField(primary_key=True)
    processstate = models.CharField(db_column='ProcessState', max_length=50)  # Field name made lowercase.
    messageguid = models.BigIntegerField(db_column='MessageGUID')  # Field name made lowercase.
    messagecontrolid = models.TextField(db_column='MessageControlID', blank=True, null=True)  # Field name made lowercase.
    datetimeofmessage = models.DateTimeField(db_column='DateTimeofMessage', blank=True, null=True)  # Field name made lowercase.
    created_at = models.DateTimeField(auto_now=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True)
    proc_time = models.DateTimeField(blank=True, null=True)
    messagepayload = models.TextField(db_column='MessagePayload', blank=True, null=True)  # Field name made lowercase.
    producer_ident = models.CharField(max_length=50, blank=True, null=True)
    consumer_ident = models.CharField(max_length=50, blank=True, null=True)
    route_id = models.BigIntegerField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    producer_id = models.BigIntegerField(blank=True, null=True)
    consumer_id = models.BigIntegerField(blank=True, null=True)
    type = models.CharField(max_length=25, blank=True, null=True)
    messagereference = models.TextField(db_column='MessageReference', blank=True, null=True)  # Field name made lowercase.
    data_format = models.CharField(max_length=100, blank=True, null=True)

    @property
    def short_description(self):
        return self.description if len(self.description) < 100 else (self.description[:99] + '..')

    class Meta:
        managed = True



class MftSchedule(models.Model):
    endpoint = models.ForeignKey('Endpoint', on_delete=models.CASCADE, related_name='mftschedule')
    name = models.TextField()
    active = models.BooleanField()
    freq_type = models.CharField(max_length=100, choices=[
        ('Daily', 'Daily'),
        ('Hours', 'Hours'),
        ('Minutes', 'Minutes'),
        ('Monthly', 'Monthly'),
        ('Monthly_Weekly', 'Monthly Weekly'),
        ('Specific_Date_and_Time', 'Specific Date and Time'),
        ('Specific_Time_Daily', 'Specific Time Daily'),
        ('Trigger', 'Trigger'),
        ('Weekly', 'Weekly'),
        ('Yearly', 'Yearly')
    ])
    freq_interval = models.IntegerField(blank=True, null=True)
    spec_date = models.DateField(blank=True, null=True)
    spec_time = models.TimeField(blank=True, null=True)
    last_run = models.DateTimeField()
    id = models.BigAutoField(primary_key=True)
    sub_day_freq_type = models.CharField(max_length=100, blank=True, null=True)
    sub_day_freq_interval = models.IntegerField(blank=True, null=True)
    sub_day_stop_schedule = models.BooleanField(blank=True, null=True)
    sub_day_start_time = models.TimeField(blank=True, null=True)
    sub_day_end_time = models.TimeField(blank=True, null=True)
    last_files_found = models.DateTimeField(blank=True, null=True)
    sub_day_last_run = models.DateField(blank=True, null=True)
    pause_start = models.DateTimeField(blank=True, null=True)
    pause_end = models.DateTimeField(blank=True, null=True)
    sub_freq_interval = models.IntegerField(blank=True, null=True)
    first_run = models.DateTimeField(blank=True, null=True)
    first_files_found = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now=True, blank=True, null=True)  # Field name made lowercase. This field type is a guess.
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)  # Field name made lowercase. This field type is a guess.

    class Meta:
        managed = True

    def __str__(self):
        return str(self.name)+' - '+str(self.freq_type)

    @classmethod
    def get_row_display(cls, sched_count=0):
        if sched_count == 0:
            return 0
        # print(sched_count)
        whole_num = sched_count // 3
        # print(whole_num)
        if whole_num <= 0:
            return 1
        remainder = sched_count % whole_num
        if remainder > 0:
            return whole_num+1
        return whole_num
    # def friendly_value(self, field_name=None):
    #     friendlies = []
    #     if field_name in friendlies:
    #         for pair in friendlies[field_name]:
    #             if pair[self[field_name]] == self[field_name]:
    #                 return pair[self[field_name]]
    #     return self[field_name]





class EndpointProp(models.Model):
    id = models.BigAutoField(primary_key=True)
    endpoint = models.ForeignKey('Endpoint', on_delete=models.CASCADE, related_name='endpointprop')
    name = models.CharField(max_length=75)
    value = models.TextField(blank=True, null=True)
    env = models.CharField(max_length=25, choices=[('DEV', 'DEV'), ('TST', 'TST'), ('PPRD', 'PPRD'), ('PRD', 'PRD'), ('STG', 'STG')])
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)  # Field name made lowercase. This field type is a guess.
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)  # Field name made lowercase. This field type is a guess.

    class Meta:
        managed = True
        verbose_name = 'Endpoint Property'
        verbose_name_plural = 'Endpoint Properties'

    def __str__(self):
        return str(self.name)+'='+str(self.value)+'-'+str(self.env)

    @property
    def do_decrypt(self):
        # lets just return on all conditions we can think of where decrypting makes no sense
        if 'password' not in self.name:
            return self.value
        if self.value is None:
            return self.value
        if ':' not in self.value:
            return self.value
        config = configparser.ConfigParser(interpolation=None)
        config.read(os.path.join(os.path.abspath(os.path.dirname(__file__)),"config.ini"))
        env = config.get("CURRENT", "env")
        secret_key = config.get(env, 'secret_key')
        encrypted = str(self.value)
        
        encrypted = encrypted.split(':')
        if len(encrypted) != 2:
            raise Exception('String given does not look encrypted')
        # We decode the two bits independently
        nonce = b64decode(encrypted[0])
        encrypted = b64decode(encrypted[1])
        # We create a SecretBox, making sure that out secret_key is in bytes
        box = nacl.secret.SecretBox(bytes(secret_key, encoding='utf8'))
        decrypted = box.decrypt(encrypted, nonce).decode('utf-8')
        return decrypted

    @property
    def do_encrypt(self):
        
        # lets just return on all conditions we can think of where decrypting makes no sense
        if 'password' not in str(self.name):
            return self.value
        if self.value is None:
            return self.value
        if ':' in str(self.value):
            return self.value
        config = configparser.ConfigParser(interpolation=None)
        config.read(os.path.join(os.path.abspath(os.path.dirname(__file__)),"config.ini"))
        env = config.get("CURRENT", "env")
        secret_key = config.get(env, 'secret_key')
        seed = nacl.utils.random(nacl.secret.SecretBox.NONCE_SIZE)

        box = nacl.secret.SecretBox(bytes(secret_key, encoding='utf8'))
        encrypted = box.encrypt(bytes(str(self.value), encoding='utf8'), seed)
        b64_seed = b64encode(seed)
        b64_enc = b64encode(encrypted.ciphertext)
        b_sep = bytes(":", encoding='utf8')

        return (b64_seed+b_sep+b64_enc).decode('utf-8')

class Endpoint(models.Model):
    objects = None
    id = models.BigAutoField(primary_key=True)
    organization = models.CharField(max_length=100, blank=True, null=True)
    software = models.CharField(max_length=50, blank=True, null=True)
    doclink = models.TextField(blank=True, null=True)
    subsystem = models.TextField(blank=True, null=True)
    active = models.BooleanField(default=False)
    alert_level = models.IntegerField(default=4)
    description = models.TextField(blank=True, null=True)  # This field type is a guess.
    direction = models.CharField(max_length=25, blank=True, null=True, choices=[('consumer', 'Consumer'), ('producer', 'Producer')])
    bw_process_ident = models.CharField(max_length=75, blank=True, null=True)
    receiving_app = models.CharField(max_length=25, blank=True, null=True)
    receiving_facility = models.CharField(max_length=25, blank=True, null=True)
    name = models.TextField(blank=True, null=True)
    type = models.CharField(max_length=25)
    portmon_host = models.CharField(max_length=25, blank=True, null=True)
    portmon_time = models.DateTimeField(blank=True, null=True)
    bw_app_ident = models.CharField(max_length=75, blank=True, null=True)
    analysts = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name='analyst_endpoint')
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)  # Field name made lowercase. This field type is a guess.
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)  # Field name made lowercase. This field type is a guess.

    class Meta:
        managed = True

    def get_fields(self):
        return [(field.name, field.value_to_string(self)) for field in Endpoint._meta.fields]

    def __str__(self):
        return str(self.id)+' - '+str(self.bw_process_ident)+' - '+str(self.name)+' - '+self.direction


class IntRequestProp(models.Model):
    id = models.BigAutoField(primary_key=True)
    int_request = models.ForeignKey('IntRequest', on_delete=models.CASCADE, related_name='intrequestprop')
    name = models.CharField(max_length=255)
    value = models.CharField(max_length=255, blank=True, null=True)
    env = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)  # Field name made lowercase. This field type is a guess.
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)  # Field name made lowercase. This field type is a guess.

    class Meta:
        managed = True
        verbose_name = 'Integration Request Property'
        verbose_name_plural = 'Integration Request Properties'

    def __str__(self):
        return str(self.name)+'='+str(self.value)+'-'+str(self.env)


class IntRequest(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)
    contact_name = models.CharField(max_length=255)
    contact_email = models.CharField(max_length=255)
    contact_phone = models.CharField(max_length=255, blank=True, null=True)
    description = models.CharField(max_length=255, blank=True, null=True)
    producer_description = models.CharField(max_length=255, blank=True, null=True)
    consumer_description = models.CharField(max_length=255, blank=True, null=True)
    producer_type = models.CharField(max_length=255)
    consumer_type = models.CharField(max_length=255)
    data_transfer_req = models.CharField(max_length=255, blank=True, null=True)
    data_manipulation_req = models.CharField(max_length=255, blank=True, null=True)
    doclink = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now=True, blank=True)  # Field name made lowercase. This field type is a guess.
    updated_at = models.DateTimeField(auto_now=True, blank=True)  # Field name made lowercase. This field type is a guess.
    status = models.CharField(max_length=255)

    class Meta:
        managed = True
        verbose_name = 'Integration Request'

    def __str__(self):
        return str(self.name)+' - '+str(self.contact_name)


class RouteProp(models.Model):
    id = models.BigAutoField(primary_key=True)
    route = models.ForeignKey('Route', on_delete=models.CASCADE, related_name='routeprop')
    name = models.CharField(max_length=50)
    value = models.TextField(blank=True, null=True)
    env = models.CharField(max_length=25)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)  # Field name made lowercase. This field type is a guess.
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)  # Field name made lowercase. This field type is a guess.

    class Meta:
        managed = True
        verbose_name = 'Route Property'
        verbose_name_plural = 'Route Properties'

    def __str__(self):
        return str(self.name)+'='+str(self.value)+'-'+str(self.env)


class Route(models.Model):
    objects = None
    id = models.BigAutoField(primary_key=True)
    producer = models.ForeignKey('Endpoint', models.DO_NOTHING, related_name='producer', blank=True, null=True)
    consumer = models.ForeignKey('Endpoint', models.DO_NOTHING, related_name='consumer', blank=True, null=True)
    producer_messagetypemessagecode = models.CharField(max_length=50)
    producer_messagetypetriggerevent = models.CharField(max_length=50)
    consumer_messagetypemessagecode = models.CharField(max_length=50)
    consumer_messagetypetriggerevent = models.CharField(max_length=50)
    hascriteria = models.BooleanField(db_column='hasCriteria')  # Field name made lowercase.
    active = models.BooleanField()
    hassplit = models.BooleanField(db_column='hasSplit')  # Field name made lowercase.
    hastranslation = models.BooleanField(db_column='hasTranslation')  # Field name made lowercase.
    type = models.CharField(max_length=25)
    name = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)  # Field name made lowercase. This field type is a guess.
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)  # Field name made lowercase. This field type is a guess.

    class Meta:
        managed = True

    def __str__(self):
        return str(self.name)


class Import(models.Model):
    id = models.BigAutoField(primary_key=True)
    import_file = models.FileField(upload_to='import_files')
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)  # Field name made lowercase. This field type is a guess.
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)  # Field name made lowercase. This field type is a guess.

    def __str__(self):
        return str(self.import_file) + str(self.created_at)
