from django import forms

from .models import Audit

class AnalystAuditSearchForm(forms.Form):
    search_term = forms.CharField(label='Search Audits', max_length=100, required=False)
    search_window = forms.ChoiceField(label='Time Window', required=False, choices=[('', 'All'), ('1', 'Last 24 Hours'), ('7', 'Last 7 Days'), ('15', 'Last 15 Days'), ('30', 'Last 30 Days'), ('90', 'Last 90 Days')])
    search_processstates = forms.MultipleChoiceField(label='Process States', required=False)
    
    def __init__(self, *args, **kwargs):
        super(AnalystAuditSearchForm, self).__init__(*args, **kwargs)
        p_states = Audit.objects.all().order_by('processstate').values_list("processstate","processstate").distinct()
        self.fields['search_processstates'].choices = p_states
        

class AnalystIntegrationRequestForm(forms.Form):
    request_types = [
        ('', 'Select One'),
        ('MFT-FS', 'In Hospital Network File Location'),
        ('MFT-SMB', 'In Hospital Network Windows Location'),
        ('MFT-SFTP-Client', 'In or Out of Hospital SFTP Location'),
        ('unknown', 'Do Not Know')
    ]
    yes_no = [('yes', 'YES'), ('no', 'NO')]
    description = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control'}), required=False)
    contact_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), required=False)
    contact_email = forms.EmailField(widget=forms.TextInput(attrs={'class': 'form-control'}), required=False)
    contact_phone = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), required=False)
    producer_description = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control'}), required=False)
    producer_type = forms.ChoiceField(choices=request_types, widget=forms.Select(attrs={'class': 'form-control'}), required=False)
    producer_host = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), required=False)
    producer_port = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), required=False)
    producer_path = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), required=False)
    producer_file_scheme = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), required=False)
    producer_username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), required=False)
    producer_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}), required=False)
    schedule = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control'}), required=False)
    producer_delete_source = forms.ChoiceField(choices=yes_no, widget=forms.Select(attrs={'class': 'form-control'}), required=False)

    consumer_description = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control'}), required=False)
    consumer_type = forms.ChoiceField(choices=request_types, widget=forms.Select(attrs={'class': 'form-control'}), required=False)
    consumer_host = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), required=False)
    consumer_port = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), required=False)
    consumer_path = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), required=False)
    consumer_file_scheme = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), required=False)
    consumer_username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), required=False)
    consumer_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}), required=False)
    
    data_transfer_req = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control'}), required=False)
    data_manipulation_req = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control'}), required=False)
    audit_persist = forms.ChoiceField(choices=yes_no, widget=forms.Select(attrs={'class': 'form-control'}), required=False)
    alert_level = forms.ChoiceField(choices=[
        ('1', 'High'),
        ('2', 'Medium'),
        ('3', 'Low'),
        ('4', 'Very Low'),
        ('100', 'None')
    ], widget=forms.Select(attrs={'class': 'form-control'}), required=False)
    error_email = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), required=False)
    confirm_email = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), required=False)
    no_files_email = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), required=False)
    doclink = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), required=False)


class ProcessStateFilterForm(forms.Form):
    process_state_list = Audit.objects.values('processstate').distinct()
    #print(process_state_list)
    flist = []
    for ps in process_state_list:
        flist.append((ps['processstate'], ps['processstate']))
    ProcessStates = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple, choices=flist)
