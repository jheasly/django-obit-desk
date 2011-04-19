from django.forms import ModelForm
from django.forms.models import inlineformset_factory
from obituary.models import Death_notice, Service, Obituary, Visitation

ServiceFormSet = inlineformset_factory(Death_notice, 
    Service,
    can_delete=True,
    extra=1,)

class Death_noticeForm(ModelForm):
    class Meta:
         model = Death_notice
         exclude = ('funeral_home', 'death_notice_has_run',)

VisitationFormSet = inlineformset_factory(Obituary,
    Visitation,
    can_delete=True,
    extra=1,)

class ObituaryForm(ModelForm):
#     def __init__(self, request, *args, **kwargs):
#         super(ObituaryForm, self).__init__(*args, **kwargs)
#         self.fields['death_notice'].queryset = Death_notice.objects.filter(funeral_home=request.user).order_by('last_name',)
    
    class Meta:
        model = Obituary
        exclude = ('first_name', 'funeral_home', 'death_notice_has_run', 'obituary_has_run',)
