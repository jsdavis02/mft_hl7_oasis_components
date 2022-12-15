import configparser
import os
import socket
from django.contrib import admin
from django.contrib.admin import AdminSite
from django.core import serializers
from django.core.mail import EmailMessage
from django.core.mail import send_mail
from django.forms import model_to_dict
from django.http import HttpResponse
from django.template.response import TemplateResponse
from django.urls import path
from django.urls import reverse
from django.utils.html import format_html
from django.utils.http import urlencode
from django.utils.safestring import mark_safe
from import_export.admin import ImportExportActionModelAdmin
from import_export import fields, resources
from import_export.widgets import ForeignKeyWidget, ManyToManyWidget
from import_export.admin import ImportExportModelAdmin
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponseRedirect
from .models import AppSetting, Import, Audit, AuditProp, Endpoint, EndpointProp, Route, RouteProp, MftSchedule, IntRequest, IntRequestProp
from django.contrib.auth.models import Permission
from import_export import resources
import json
from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
# Register your models here.
# 1. export/import config
# 2. Endpoint view/edits
# 3. Reverse relationship and delete confirm aware of properties and sub items
# 4. Routes view with props
# 5. Route list make Endpoints links and ordering by them?


class UserAdmin(BaseUserAdmin):
    
    def send_invite_email(modeladmin, request, queryset):
        config = configparser.ConfigParser(interpolation=None)
        config.read(os.path.join(os.path.abspath(os.path.dirname(__file__)),"config.ini"))
        env = config.get("CURRENT", "env")
        hostname = socket.gethostname()
        subject = f"User Invitation for Oasis {env}"
        user_invite_from = AppSetting.objects.filter(name='user_invite_from').filter(env=env).first()
        user_invite_bcc_obj = AppSetting.objects.filter(name='user_invite_bcc').filter(env=env)
        user_invite_bcc_list = [a.value for a in user_invite_bcc_obj]
        for e in queryset:
            message = f"Below is information to access the Oasis Application Integration Platform:\n"
            message += f"Please save and bookmark the below url, this is where you can view data moves associated with you and access archives of those transfers.\n\n"
            message += f"Web URL: http://{hostname}:9000/\n"
            message += f"Username: {e.username}\n"
            message += f"Password: changeme\n"
            message += f"!! After login click the upper left person icon and change your password, this interface gives access to archive data !!\n"
            message += f"*** username and password are case sensitive and are NOT tied to your single sign on user id, so remember what you set!!!\n"
            email = EmailMessage(subject=subject, body=message, from_email=user_invite_from.value, to=[e.email], bcc=user_invite_bcc_list)
            email.send()
            # auto reset password for user to match invite email
            e.set_password('changeme')
        return HttpResponseRedirect("../user")

    actions = ['send_invite_email']
    send_invite_email.short_description = "Send Email Invites"

class AppSettingResource(resources.ModelResource):
    class Meta:
        model = AppSetting


class AppSettingAdmin(ImportExportActionModelAdmin):
    resource_class = AppSettingResource
    list_display = ('name', 'value', 'env')
    list_filter = ['env']
    search_fields = ['name', 'value', 'env']


class ImportAdmin(admin.ModelAdmin):
    list_display = ('id', 'import_file', 'created_at', 'updated_at')
    search_fields = ['import_file', 'created_at']
    #list_filter = ['processstate', 'type', 'producer_ident', 'consumer_ident']
    list_per_page = 200
    date_hierarchy = 'created_at'

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('admin_import_store/', self.admin_import_store),
        ]
        return custom_urls + urls

    def admin_import_store(self, request):
        print('in admin_import_store')
        print(request.POST)
        # [{"i_id": i_data},{...}]
        i_data = {}
        i_ids = []
        e_ids = {}
        r_ids = {}

        for k, v in request.POST.dict().items():
            print(k)
            print(v)
            # we will only migrate properties selected or schedules
            # if the corresponding endpoint and/or routes are selected
            # so we initially look for just that.
            if k.startswith('endpoint_'):
                print('we have an endpoint with old pk of: '+str(v))
                #all form names have the import file id and we need it
                epname = k.split('_')
                e_id = epname[2]
                i_file_id = epname[1]
                e_ids[e_id] = {'i_file_id': i_file_id, 'properties': [], 'schedules': []}
                print('we have an endpoint with old id of: '+e_id+' in import file id: '+i_file_id)
                # everything with import/export is in relation to endpoints or routes, so lets load up
                # import files referenced here, and on routes below
                if i_file_id not in i_ids:
                    i_ids.append(i_file_id)
                    i_file = Import.objects.get(pk=i_file_id)
                    i_data[i_file_id] = json.load(i_file.import_file)
                # load and save new endpoint
            if k.startswith('endpointprop_'):
                ename = k.split('_')
                i_file_id = ename[1]
                e_id = ename[2]
                ep_id = ename[3]
                if e_id not in e_ids.keys():
                    # nothing created yet for parent endpoint
                    e_ids[e_id] = {'i_file_id': '', 'properties': [], 'schedules': []}
                e_ids[e_id]['properties'].append(ep_id)
                print('we have an endpoint property for endpoint: '+e_id+' with old id of: '+ep_id+' in import file id: '+i_file_id)
            if k.startswith('route_'):
                rname = k.split('_')
                i_file_id = rname[1]
                r_id = rname[2]
                r_ids[r_id] = {
                    'i_file_id': i_file_id,
                    'properties': [],
                    'producer': {},  # could be {'type': 'existing', 'id': ''},
                    'consumer': {}  # could be {'type': 'existing', 'id': ''}
                }
                print('we have a route with old pk of: '+str(v)+' in import file id: '+i_file_id)
                print(r_ids)
                if i_file_id not in i_ids:
                    i_ids.append(i_file_id)
                    i_file = Import.objects.get(pk=i_file_id)
                    i_data[i_file_id] = json.load(i_file.import_file)
            if k.startswith('rt_producer_') and 'None' not in v:
                vval = v.split('_')
                r_link = "existing"
                e_id = vval[1]
                rpname = k.split('_')
                r_id = rpname[2]
                i_file_id = None
                if vval[0] == "i":
                    r_link = "importing"
                    i_file_id = vval[1]
                    e_id = vval[2]
                if r_id not in r_ids.keys():
                    r_ids[r_id] = {
                        'i_file_id': i_file_id,
                        'properties': [],
                        'producer': {},  # could be {'type': 'existing', 'id': ''},
                        'consumer': {}  # could be {'type': 'existing', 'id': ''}
                    }
                r_ids[r_id]['producer'] = {'type': r_link, 'id': e_id, 'i_file_id': i_file_id}
                print('we have route producer for old route id: '+r_id+' with '+r_link+' endpoint id: '+e_id)
            if k.startswith('rt_consumer_') and 'None' not in v:
                vval = v.split('_')
                r_link = "existing"
                e_id = vval[1]
                rpname = k.split('_')
                r_id = rpname[2]
                i_file_id = None
                if vval[0] == "i":
                    r_link = "importing"
                    i_file_id = vval[1]
                    e_id = vval[2]
                if r_id not in r_ids.keys():
                    r_ids[r_id] = {
                        'i_file_id': i_file_id,
                        'properties': [],
                        'producer': {},  # could be {'type': 'existing', 'id': ''},
                        'consumer': {}  # could be {'type': 'existing', 'id': ''}
                    }
                r_ids[r_id]['consumer'] = {'type': r_link, 'id': e_id, 'i_file_id': i_file_id}
                print('we have route consumer for old route id: '+r_id+' with '+r_link+' endpoint id: '+vval[1])
            if k.startswith('routeprop_'):
                rname = k.split('_')
                i_file_id = rname[1]
                r_id = rname[2]
                rp_id = rname[3]
                r_ids[r_id]['properties'].append(rp_id)
                print('we have a route property for route: '+r_id+' with old id of: '+rp_id)
            if k.startswith('schedule_'):
                sname = k.split('_')
                i_file_id = sname[1]
                e_id = sname[2]
                es_id = sname[3]
                e_ids[e_id]['schedules'].append(es_id)
                print('we have a schedule for importing endpoint with old id: '+e_id+' and old schedule id: '+es_id)
        saved_endpoint_data = {}
        saved_route_data = {}
        # print(i_data)
        for ki, i in i_data.items():
            # print(ki)
            # print(i)
            for er_data in i:
                print(er_data['endpoint']['id'])
                print(e_ids.keys())
                if str(er_data['endpoint']['id']) in e_ids.keys():
                    print('we have an endpoint to save')
                    old_e_id = er_data['endpoint']['id']
                    # this endpoint should be imported
                    # print(er_data['endpoint'])
                    del er_data['endpoint']['analysts']
                    del er_data['endpoint']['id']
                    new_endpoint = Endpoint(**er_data['endpoint'])
                    print(new_endpoint.id)
                    new_endpoint.save()
                    print(new_endpoint.id)
                    saved_endpoint_data[old_e_id] = new_endpoint
                    for p in er_data['endpointprops']:
                        # print(old_e_id)
                        # print(e_ids)
                        # print(p)
                        for np in e_ids[str(old_e_id)]['properties']:
                            print(np)
                            print(p['pk'])
                            print(type(np))
                            print(type(p['pk']))
                            if str(p['pk']) == np:
                                #trim p create instance, add endpoint reference and save
                                print('in saving new endpoint property')
                                del p['fields']['endpoint']
                                new_e_p = EndpointProp(**p['fields'])
                                new_e_p.endpoint = new_endpoint
                                new_e_p.save()
                                print(new_e_p.id)
                    for s in er_data['mftschedules']:
                        for ns in e_ids[str(old_e_id)]['schedules']:
                            if str(s['pk']) == ns:
                                #trim p create instance, add endpoint reference and save
                                del s['fields']['endpoint']
                                new_e_s = MftSchedule(**s['fields'])
                                new_e_s.endpoint = new_endpoint
                                new_e_s.save()
                for r in er_data['routes']:
                    print('197'+str(r))
                    print(r['route']['id'])
                    print(r_ids.keys())
                    if str(r['route']['id']) in r_ids.keys():
                        # remove id, producer, consumer
                        # set producer, consumer if existing, if importing we
                        # cannot set till we have saved the endpoint
                        old_r_id = str(r['route']['id'])
                        del r['route']['producer']
                        del r['route']['consumer']
                        new_route = Route(**r['route'])
                        print('new route:'+str(new_route))
                        print(r_ids[old_r_id])
                        if len(r_ids[old_r_id]['producer']) > 0:
                            # we have a producer
                            print('we have a producer to associate')
                            if r_ids[old_r_id]['producer']['type'] == 'existing':
                                # we are associating with existing so pull and do that
                                # not sure if I associate object or just set id
                                pe = Endpoint.objects.get(pk=r_ids[old_r_id]['producer']['id'])
                                print(pe)
                                new_route.producer = pe
                            # we will have to associate imports later
                        if len(r_ids[old_r_id]['consumer']) > 0:
                            # we have a consumer
                            print('we have consumer')
                            if r_ids[old_r_id]['consumer']['type'] == 'existing':
                                # we are associating with existing so pull and do that
                                # not sure if I associate object or just set id
                                ce = Endpoint.objects.get(pk=r_ids[old_r_id]['consumer']['id'])
                                print(ce)
                                new_route.consumer = ce
                            # we will have to associate imports later
                        # put new route object in list for loop after all endpoints
                        saved_route_data[old_r_id] = {'route': new_route, 'properties': []}
                        print(r)
                        for rp in r['routeprops']:
                            print(rp)
                            print(rp['pk'])
                            print(type(rp['pk']))
                            print(r_ids[old_r_id]['properties'])
                            if str(rp['pk']) in r_ids[old_r_id]['properties']:
                                # we import this property
                                del rp['fields']['route']
                                new_route_prop = RouteProp(**rp['fields'])
                                saved_route_data[old_r_id]['properties'].append(new_route_prop)
        for k, r in saved_route_data.items():
            print('230'+str(r))
            print(r['route'])
            print(r_ids[k])
            if len(r_ids[k]['producer']) > 0:
                # we have a producer
                print('we have a producer')
                print(r_ids[k]['producer']['type'])
                if r_ids[k]['producer']['type'] == 'importing':
                    old_ep_id = r_ids[k]['producer']['id']
                    print(old_ep_id)
                    print(type(old_ep_id))
                    print(saved_endpoint_data.keys())
                    if int(old_ep_id) in saved_endpoint_data.keys():
                        print('in setting producer to endpoint for importing')
                        r['route'].producer = saved_endpoint_data[int(old_ep_id)]
            if len(r_ids[k]['consumer']) > 0:
                # we have a consumer
                print('we have a consumer')
                print(r_ids[k]['consumer']['type'])
                if r_ids[k]['consumer']['type'] == 'importing':
                    old_ep_id = r_ids[k]['consumer']['id']
                    if int(old_ep_id) in saved_endpoint_data.keys():
                        r['route'].consumer = saved_endpoint_data[int(old_ep_id)]
            print(r['route'].__dict__)
            r['route'].id = None
            print(r['route'].__dict__)
            r['route'].save()
            print(r['route'].__dict__)
            print(r.keys())
            if 'properties' in r.keys():
                for rp in r['properties']:
                    rp.route = r['route']
                    rp.save()
        return HttpResponseRedirect("../")

    def admin_import_detail_view(self, request, ifilequeryset):
        print('in importadmin class')
        endpoints = []
        i_producers = []
        i_consumers = []
        producers = Endpoint.objects.filter(direction='producer')
        consumers = Endpoint.objects.filter(direction='consumer')
        routes = []
        schedules = []
        for i_file in ifilequeryset:
            import_file_data = json.load(i_file.import_file)
            for e_and_related in import_file_data:
                analysts = e_and_related['endpoint']['analysts']
                del e_and_related['endpoint']['analysts']
                endpoint = Endpoint(**e_and_related['endpoint'])
                endpoint.i_file_id = i_file.id
                if endpoint.direction == 'producer':
                    i_producers.append(endpoint)
                else:
                    i_consumers.append(endpoint)
                to_import = {"endpoint": endpoint, "properties": [], "routes": [], "schedules": []}
                for prop in e_and_related['endpointprops']:
                    endpoint_id = prop['fields']['endpoint']
                    del prop['fields']['endpoint']
                    p = EndpointProp(**prop['fields'])
                    p.i_file_id = i_file.id
                    p.pk = prop['pk']
                    p.endpoint_id = endpoint_id
                    to_import['properties'].append(p)
                for r in e_and_related['routes']:
                    del r['route']['producer']
                    del r['route']['consumer']
                    route = Route(**r['route'])
                    route.i_file_id = i_file.id
                    rdata = {"route": route, "properties": []}
                    for rp in r['routeprops']:
                        del rp['fields']['route']
                        route_prop = RouteProp(**rp['fields'])
                        route_prop.i_file_id = i_file.id
                        route_prop.route_id = route.id
                        route_prop.pk = rp['pk']
                        rdata['properties'].append(route_prop)
                    to_import['routes'].append(rdata)
                for s in e_and_related['mftschedules']:
                    # need to carry endpoint id but not have 
                    # django model try and instantiate endpoint object
                    eid = s['fields']['endpoint']
                    del s['fields']['endpoint']
                    ms = MftSchedule(**s['fields'])
                    ms.i_file_id = i_file.id
                    ms.endpoint_id = eid
                    ms.pk = s['pk']
                    to_import['schedules'].append(ms)
                endpoints.append(to_import)
        print(endpoints)
        return TemplateResponse(request, 'admin/admin_import_view.html', {"endpoints": endpoints, "producers": producers, "consumers": consumers, "i_producers": i_producers, "i_consumers": i_consumers})

    actions = ['admin_import_detail_view']
    admin_import_detail_view.short_description = "Import Resources from File"


class AuditPropInline(admin.TabularInline):
    model = AuditProp


class AuditAdmin(admin.ModelAdmin):
    list_display = ('type', 'proc_time', 'messageguid', 'messagecontrolid', 'processstate', 'short_description','producer_ident', 'consumer_ident', 'route_id')
    search_fields = ['messageguid', 'processstate', 'description']
    list_filter = ['processstate', 'type', 'producer_ident', 'consumer_ident']
    list_per_page = 200
    date_hierarchy = 'proc_time'
    inlines = [
        AuditPropInline,
    ]


class AuditPropAdmin(admin.ModelAdmin):
    list_display = ('id', 'audit_id', 'name', 'value')
    search_fields = ['name', 'value']

class EndpointResource(resources.ModelResource):
    properties = fields.Field(
        widget=ForeignKeyWidget('endpointprop')
    )

    class Meta:
        model = Endpoint
        fields = ('name', 'properties')


class EndpointPropInline(admin.TabularInline):
    model = EndpointProp


class EndpointAdmin(ImportExportActionModelAdmin):
    resource_class = EndpointResource

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('detail/<int:pk>/', self.admin_endpoint_detail_view, name='admin-endpoint-detail-view'),
        ]
        return my_urls + urls

    def export_selected_objects(modeladmin, request, queryset):
        selected = queryset.values_list('pk', flat=True)
        ct = ContentType.objects.get_for_model(queryset.model)
        export_data = []
        
        for e in queryset:
            e_dict = model_to_dict(e)
            routes = None
            if e.direction == 'producer':
                routes = Route.objects.filter(producer_id=e.id)
            else:
                routes = Route.objects.filter(consumer_id=e.id)
            e_data = {
                'endpoint': e_dict,
                'endpointprops': json.loads(serializers.serialize('json', e.endpointprop.all())),
                'routes': [],
                'mftschedules': json.loads(serializers.serialize('json', e.mftschedule.all()))
            }
            routes_list = []
            for r in routes:
                r_dict = model_to_dict(r)
                r_data = {
                    'route': r_dict,
                    'routeprops': json.loads(serializers.serialize('json', r.routeprop.all()))
                }
                routes_list.append(r_data)
            e_data['routes'] = routes_list
            export_data.append(e_data)
        export_data = json.dumps(export_data)
        # print(queryset)
        # print(export_data)
        # print(ct)
        response = HttpResponse(export_data, content_type="text/json-comment-filtered")
        response['Content-Disposition'] = 'attachment; filename="export.json"'
        return response


    def admin_endpoint_detail_view(self, request, pk):
        endpoint = Endpoint.objects.get(id=pk)
        properties = endpoint.endpointprop.all()
        schedules = endpoint.mftschedule.all()
        if endpoint.direction == 'consumer':
            routes = Route.objects.all().filter(consumer_id=endpoint.id)
        else:
            routes = Route.objects.all().filter(producer_id=endpoint.id)
        sched_rows = range(MftSchedule.get_row_display(sched_count=schedules.count()))
        scheds_by_row = {}
        i = 1
        for s in schedules:
            r = (i // 3)+1
            if r not in scheds_by_row:
                scheds_by_row[r] = []
            scheds_by_row[r].append(s)
            i = i+1
        # print(routes)
        return TemplateResponse(request, 'admin/admin_endpoint_detail_view.html', {'Endpoint': endpoint, 'Properties': properties, 'Routes': routes, 'Schedules': schedules, 'sched_rows': sched_rows, 'scheds_by_row': scheds_by_row})

    def view_properties_link(self, obj):
        # count = obj.endpointprop.count()
        url = (
                reverse("admin:{}_{}_changelist".format(obj._meta.app_label, 'endpointprop'))
                + "?"
                + urlencode({"endpoint__id": f"{obj.id}"})
        )
        return format_html('<a href="{}">View Props</a>', url)
    view_properties_link.short_description = 'Properties'

    def view_schedules_link(self, obj):
        # count = obj.mftschedule.count()
        url = (
                reverse("admin:{}_{}_changelist".format(obj._meta.app_label, 'mftschedule'))
                + "?"
                + urlencode({"endpoint__id": f"{obj.id}"})
        )
        return format_html('<a href="{}">View Schedules</a>', url)


    def view_detail_link(self, obj):
        return format_html('<a href="/admin/OASIS/endpoint/detail/'+str(obj.id)+'">View</a>')

    view_detail_link.short_description = 'Details'
    view_schedules_link.short_description = 'Schedules'
    list_display = ('id', 'view_detail_link', 'active', 'type', 'direction', 'bw_process_ident', 'name', 'description', 'created_at')
    search_fields = ['id', 'type', 'bw_process_ident', 'name', 'description']
    list_filter = ['active', 'type', 'direction']
    list_per_page = 50
    inlines = [
        EndpointPropInline,
    ]
    actions = ['export_selected_objects']
    export_selected_objects.short_description = "Export Selected"


class EndpointPropResource(resources.ModelResource):

    class Meta:
        model = EndpointProp
        fields = ('id', 'name', 'value', 'endpoint__bw_process_ident')



class EndpointPropAdmin(ImportExportActionModelAdmin):
    resource_class = EndpointPropResource

    def save_model(self, request, obj, form, change):
        if 'password' in form.cleaned_data['name']:
            obj.refresh_from_db()
            if form.cleaned_data['value'] != obj.value:
                obj.value = form.cleaned_data['value']
                obj.value = obj.do_encrypt
        super().save_model(request, obj, form, change)

    # def endpoint_display(self, obj):
    #     display_text = "<a href={}>{}</a>".format(
    #         reverse('admin:{}_{}_change'.format(obj._meta.app_label, 'endpoint'),
    #                 args=(obj.endpoint.pk,)),
    #         obj.endpoint.bw_process_ident)
    #     if display_text:
    #         return mark_safe(display_text)
    #     return "-"
    e_names = Endpoint.objects.values('id', 'bw_process_ident')


    def endpoint_display(self, obj):
        for e_name in self.e_names:
            if e_name['id'] == obj.endpoint_id:
                return e_name['bw_process_ident']

    endpoint_display.short_description = 'Endpoint'
    list_display = ('id', 'endpoint_id','endpoint_display', 'name', 'value', 'env', 'created_at', 'updated_at')
    search_fields = ['id', 'endpoint__bw_process_ident', 'name', 'value', 'env']
    list_filter = ['env']

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "endpoint":
            kwargs["queryset"] = Endpoint.objects.all().order_by('bw_process_ident')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class MftscheduleResource(resources.ModelResource):
    class Meta:
        model = MftSchedule


class MftscheduleAdmin(ImportExportActionModelAdmin):
    resource_class = MftscheduleResource
    list_display = ('id', 'active', 'endpoint_id', 'name', 'freq_type', 'freq_interval', 'spec_date', 'spec_time', 'pause_start', 'pause_end', 'sub_day_freq_type', 'sub_day_freq_interval', 'sub_day_start_time', 'sub_day_end_time', 'last_run', 'last_files_found', 'first_run', 'first_files_found', 'created_at')
    search_fields = ['id', 'endpoint_id', 'name', 'freq_type']
    list_filter = ['freq_type']


    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "endpoint":
            kwargs["queryset"] = Endpoint.objects.filter(direction='producer').order_by('bw_process_ident')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class RouteResource(resources.ModelResource):
    class Meta:
        model = Route


class RoutePropInline(admin.TabularInline):
    model = RouteProp


class RouteAdmin(ImportExportActionModelAdmin):
    resource_class = RouteResource

    def view_properties_link(self, obj):
        # count = obj.routeprop.count()
        url = (
                reverse("admin:{}_{}_changelist".format(obj._meta.app_label, 'routeprop'))
                + "?"
                + urlencode({"route__id": f"{obj.id}"})
        )
        return format_html('<a href="{}">Properties</a>', url)

    def producer_display(self, obj):
        display_text = "<a href={}>{}</a>".format(
                reverse('admin:{}_{}_change'.format(obj._meta.app_label, 'endpoint'),
                        args=(obj.producer.pk,)),
                obj.producer.bw_process_ident)
        if display_text:
            return mark_safe(display_text)
        return "-"

    def consumer_display(self, obj):
        display_text = "<a href={}>{}</a>".format(
            reverse('admin:{}_{}_change'.format(obj._meta.app_label, 'endpoint'),
                    args=(obj.consumer.pk,)),
            obj.consumer.bw_process_ident)
        if display_text:
            return mark_safe(display_text)
        return "-"


    producer_display.short_description = 'Producer'
    consumer_display.short_description = 'Consumer'
    view_properties_link.short_description = 'Properties'
    list_display = ('id', 'view_properties_link', 'active', 'type', 'name', 'description', 'created_at', 'updated_at')
    search_fields = ['id', 'name', 'description']
    list_per_page = 50
    inlines = [
        RoutePropInline,
    ]


class RoutePropResource(resources.ModelResource):
    class Meta:
        model = RouteProp


class RoutePropAdmin(ImportExportActionModelAdmin):
    resource_class = RoutePropResource

    def route_display(self, obj):
        display_text = "<a href={}>{}</a>".format(
            reverse('admin:{}_{}_change'.format(obj._meta.app_label, 'route'),
                    args=(obj.route.pk,)),
            obj.route.name)
        if display_text:
            return mark_safe(display_text)
        return "-"
    route_display.short_description = 'Route'
    list_display = ('id', 'route_id', 'name', 'value', 'env', 'created_at')
    search_fields = ('id', 'route_id', 'name', 'value', 'env')
    list_filter = ['env']

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "route":
            kwargs["queryset"] = Route.objects.all().order_by('name')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)



class IntResource(resources.ModelResource):
    class Meta:
        model = IntRequest


class IntRequestPropInline(admin.TabularInline):
    model = IntRequestProp


class IntRequestAdmin(ImportExportActionModelAdmin):
    resource_class = IntResource
    list_display = ('id', 'status', 'name', 'contact_name', 'contact_email', 'description', 'producer_type', 'consumer_type', 'created_at', 'updated_at')
    search_fields = ['id', 'status', 'name', 'contact_name', 'contact_email', 'description', 'producer_type', 'consumer_type']
    inlines = [
        IntRequestPropInline,
    ]

class IntRequestPropResource(resources.ModelResource):
    class Meta:
        model = IntRequestProp


class IntRequestPropAdmin(ImportExportActionModelAdmin):
    resource_class = IntRequestPropResource
    list_display = ('id', 'int_request_id', 'name', 'value', 'env', 'created_at', 'updated_at')
    search_fields = ['id', 'int_request_id', 'name', 'value', 'env']

admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(AppSetting, AppSettingAdmin)
admin.site.register(Import, ImportAdmin)
admin.site.register(Audit, AuditAdmin)
admin.site.register(AuditProp, AuditPropAdmin)
admin.site.register(Endpoint, EndpointAdmin)
admin.site.register(EndpointProp, EndpointPropAdmin)
admin.site.register(MftSchedule, MftscheduleAdmin)
admin.site.register(Route, RouteAdmin)
admin.site.register(RouteProp, RoutePropAdmin)
admin.site.register(IntRequest, IntRequestAdmin)
admin.site.register(IntRequestProp, IntRequestPropAdmin)

admin.site.register(Permission)

