import mimetypes
from datetime import datetime
from datetime import timedelta
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.shortcuts import render, redirect

from django.utils import timezone
from django.core.paginator import Paginator
from django.shortcuts import render
from django.http import HttpResponse
from django.db.models import Q

from .forms import AnalystAuditSearchForm, AnalystIntegrationRequestForm
from .models import Audit, AuditProp, IntRequest, IntRequestProp
from django.views.generic import ListView
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required

# Create your views here.
from .models import Endpoint
from .models import MftSchedule
from .models import Route


@login_required
def index(request):
    return render(request, 'OASIS/index.html')


@login_required
def analyst_audit_list_view(request):
    user = request.user
    print(user.is_superuser)
    sform = AnalystAuditSearchForm(request.GET)
    # add the dictionary during initialization 
    days = int(request.GET.get('days', 1))
    time_threshold = timezone.now() - timedelta(days=days)
    # results = Widget.objects.filter(created__lt=time_threshold)

    audit_list = Audit.objects.all().order_by('-proc_time').filter(proc_time__gt=time_threshold)
    if days == -1:
        audit_list = Audit.objects.all().order_by('-proc_time')
    guid = request.GET.get('messageguid')
    if guid is not None:
        days = -1
        audit_list = Audit.objects.all().order_by('-proc_time').filter(messageguid=guid)
    prod_ident = request.GET.get('producer_ident')
    if prod_ident is not None:
        days = -1
        audit_list = Audit.objects.all().order_by('-proc_time').filter(producer_ident=prod_ident)
    con_ident = request.GET.get('consumer_ident')
    if con_ident is not None:
        days = -1
        audit_list = Audit.objects.all().order_by('-proc_time').filter(consumer_ident=con_ident)
    routeid = request.GET.get('route_id')
    if routeid is not None:
        days = -1
        audit_list = Audit.objects.all().order_by('-proc_time').filter(route_id=routeid)

    processstate_hide = request.GET.getlist('processstate_hide')
    # print(processstate_hide)
    if processstate_hide is not None:
        audit_list = Audit.objects.all().order_by('-proc_time').exclude(processstate__in=processstate_hide)
    processstate = request.GET.get('processstate')
    if processstate is not None:
        # days = -1
        audit_list = Audit.objects.all().order_by('-proc_time').filter(processstate=processstate)
    messagecontrolid = request.GET.get('messagecontrolid')
    if messagecontrolid is not None:
        days = -1
        audit_list = Audit.objects.all().order_by('-proc_time').filter(messagecontrolid=messagecontrolid)

    if request.method == 'GET':
        form = AnalystAuditSearchForm(request.GET)
        if form.is_valid():
            print(form.cleaned_data['search_processstates'])
            time_window = None
            search_fields = None
            endpoints = None
            p_states = None
            combined = None
            if len(form.cleaned_data['search_processstates']) > 0:
                # add filtering for process states otherwise infer all instead of none
                for s in form.cleaned_data['search_processstates']:
                    if p_states is None:
                        p_states = Q(processstate__exact=s)
                    else:
                        p_states = p_states | Q(processstate__exact=s)
                if combined is None:
                    combined = p_states
                else:
                    combined = combined & p_states
            days = form.cleaned_data['search_window']
            if len(days) > 0:
                # we have a window for search
                days = int(days)
                today = timezone.now()
                past = today - timedelta(days=days)
                time_window = Q(proc_time__range=(past, today))
                if combined is None:
                    combined = time_window
                else:
                    combined = combined & time_window

            if len(form.cleaned_data['search_term']) > 0:
                search_fields = Q(processstate__icontains=form.cleaned_data['search_term']) | Q(messageguid__icontains=form.cleaned_data['search_term']) | Q(
                    producer_ident__icontains=form.cleaned_data['search_term']) | Q(consumer_ident__icontains=form.cleaned_data['search_term']) | Q(
                    description__icontains=form.cleaned_data['search_term']) | Q(messagereference__icontains=form.cleaned_data['search_term'])
                if combined is None:
                    combined = search_fields
                else:
                    combined = combined & search_fields

            if not user.is_superuser:
                # we are an analyst, get endpoints and do query constraints
                endpoint_list = Endpoint.objects.all().order_by('bw_process_ident').filter(analysts__id=user.id).values_list('id', flat=True)
                endpoints = Q(producer_id__in=endpoint_list) | Q(consumer_id__in=endpoint_list)
                if combined is None:
                    combined = endpoints
                else:
                    combined = combined & endpoints
            print(combined)
            if combined is not None:
                audit_list = Audit.objects.filter(
                    combined
                ).order_by('-proc_time')


    paginator = Paginator(audit_list, 200)  # Show 200 audits per page.
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'OASIS/analyst_audit_list_view.html', {'page_obj': page_obj, 'days': days, 'form': sform})


@login_required
def analyst_endpoint_list_view(request):
    l_user = request.user
    endpoint_list = Endpoint.objects.all().order_by('bw_process_ident').filter(analysts__id=l_user.id)
    # add the dictionary during initialization 
    days = int(request.GET.get('days', 1))
    # results = Widget.objects.filter(created__lt=time_threshold)

    paginator = Paginator(endpoint_list, 200)  # Show 200 audits per page.
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'OASIS/analyst_endpoint_list_view.html', {'page_obj': page_obj, 'days': days})


@login_required
def analyst_download_audit_file(request, pk):
    audit = Audit.objects.get(id=pk)
    properties = audit.auditprop.all()
    fl_path = audit.messagereference
    filename = audit.messagereference.rsplit('/', 1)[-1]
    for prop in properties:
        if prop.name.lower() == 'original_filename':
            filename = prop.value
            break

    fl = open(fl_path, "r")
    mime_type, _ = mimetypes.guess_type(fl_path)
    response = HttpResponse(fl, content_type=mime_type)
    response['Content-Disposition'] = "attachment; filename=%s" % filename
    return response


@login_required
def analyst_audit_detail_view(request, pk):
    audit = Audit.objects.get(id=pk)
    properties = audit.auditprop.all()
    return render(request, 'OASIS/analyst_audit_detail_view.html', {'Audit': audit, 'Properties': properties})


@login_required
def analyst_endpoint_detail_view(request, pk):
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
        r = (i // 3) + 1
        if r not in scheds_by_row:
            scheds_by_row[r] = []
        scheds_by_row[r].append(s)
        i = i + 1
    # print(routes)
    return render(request, 'OASIS/analyst_endpoint_detail_view.html',
                  {'Endpoint': endpoint, 'Properties': properties, 'Routes': routes, 'Schedules': schedules, 'sched_rows': sched_rows, 'scheds_by_row': scheds_by_row})


def analyst_int_request_view(request):
    add_form = AnalystIntegrationRequestForm(request.POST)
    if request.method == "POST":
        if add_form.is_valid():
            intreq_model_fields = [f.name for f in IntRequest._meta.get_fields()]
            #intersection of form fields to main model
            fields_for_main = list(set(intreq_model_fields) & set(add_form.cleaned_data.keys()))
            #the fields that should be properties cause not in main intrequest model
            fields_for_props = list(set(add_form.cleaned_data.keys()) - set(intreq_model_fields))
            print(fields_for_main)
            print(fields_for_props)
            ir = IntRequest()
            # set main table field values
            for f in fields_for_main:
                setattr(ir, f, add_form.cleaned_data[f])
            #save it so we have an id
            ir.save()
            for fp in fields_for_props:
                ip = IntRequestProp(int_request_id=ir.id, name=fp, value=add_form.cleaned_data[fp], env='STG')
                ip.save()

    return render(request, 'OASIS/analyst_int_request.html', {'form': add_form})


def sign_up(request):
    context = {}
    form = UserCreationForm(request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            user = form.save()
            login(request, user)
            return render(request, 'OASIS/index.html')
    context['form'] = form
    return render(request, 'registration/sign_up.html', context)


@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Your password was successfully updated!')
            return redirect('change_password')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'OASIS/analyst_change_password.html', {
        'form': form
    })
