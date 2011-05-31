from django import forms
from django.forms import ModelForm
from django.forms.models import inlineformset_factory
from obituary.widgets import SelectWithPopUp
from obituary.models import Death_notice, Service, Obituary, Visitation

class ObitsCalendarDateTimeWidget(forms.DateTimeInput):
    class Media:
        css = {'all':('http://ajax.googleapis.com/ajax/libs/jqueryui/1/themes/overcast/jquery-ui.css',)}
        js = (
            'http://static.registerguard.com/timepicker/jquery.timepicker.addon.js',
        )

class ServiceForm(ModelForm):
    
    class Meta:
        model = Service
        widgets = {
            'service_date_time': ObitsCalendarDateTimeWidget(),
        }

#     def __init__(self, *args, **kwargs):
#         super(ServiceForm, self).__init__(*args, **kwargs)
#         
#         self.fields['service_date_time'].widget = MyCalendarDateTimeWidget()

ServiceFormSet = inlineformset_factory(Death_notice, 
    Service,
    form = ServiceForm,
    can_delete=True,
    extra=1,)

class CalendarWidget(forms.DateInput):
    class Media:
        css = {'all':('http://ajax.googleapis.com/ajax/libs/jqueryui/1/themes/overcast/jquery-ui.css',)}
        js = (
            'http://ajax.googleapis.com/ajax/libs/jquery/1/jquery.min.js',
            'http://ajax.googleapis.com/ajax/libs/jqueryui/1/jquery-ui.min.js',
        )

class Death_noticeForm(ModelForm):
    death_date = forms.DateField(widget=CalendarWidget())
    
    class Meta:
         model = Death_notice
         exclude = ('funeral_home', 'death_notice_in_system', 'death_notice_has_run',)

VisitationFormSet = inlineformset_factory(Obituary,
    Visitation,
    can_delete=True,
    extra=1,)

class ObituaryForm(ModelForm):
    def __init__(self, request, *args, **kwargs):
        super(ObituaryForm, self).__init__(*args, **kwargs)
        self.fields['death_notice'].queryset = Death_notice.objects.filter(funeral_home=request.user).order_by('last_name',)
    
    death_notice = forms.ModelChoiceField(Death_notice.objects, widget = SelectWithPopUp)
    date_of_birth = forms.DateField(widget=CalendarWidget())
    marriage_date = forms.DateField(widget=CalendarWidget())
    
    class Meta:
        model = Obituary
        exclude = ('funeral_home', 'obituary_has_run',)
