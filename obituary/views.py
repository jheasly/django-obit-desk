from django import forms
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.db.models.loading import get_models, get_app, get_apps
from django.forms.models import modelform_factory
# from django.forms.models import modelformset_factory, inlineformset_factory
from django.http import HttpResponseRedirect, HttpResponseNotFound, HttpResponse
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.utils.html import escape
from django.utils.translation import ugettext
from django.views.generic.list_detail import object_list
from obituary.models import Death_notice, Service, Obituary, Visitation
from obituary.forms import Death_noticeForm, \
    ServiceFormSet, ObituaryForm, VisitationFormSet, BEI_FormSet, \
    Other_servicesFormSet

# Create your views here.

def deaths(request, model=None):
    if request.META['HTTP_USER_AGENT'].count('Macintosh'):
        request_machine = 'MAC'
        template_name = 'obituary_list_mac.html'    # saved in UTF-8 format
    else:
        request_machine = 'WIN'
        template_name = 'obituary_list_win.html'    # saved in DOS format
    model = eval(model)
    if model == Death_notice:
        queryset = model.objects.filter(death_notice_has_run=False).order_by('last_name')
    else:
        queryset = model.objects.filter(has_run=False).order_by('death_notice__last_name')

    return object_list(
        request,
        queryset = queryset,
        mimetype = 'text/plain;charset=UTF-8',
        template_name = template_name,
        extra_context = {
            'request_machine': request_machine,
        },
    )

@login_required
def fh_index(request):
    death_notices = Death_notice.objects.filter(funeral_home__username=request.user.username)
    obituaries = Obituary.objects.filter(death_notice__funeral_home__username=request.user.username)
    return render_to_response('fh_index.html', {
        'death_notices': death_notices,
        'obituaries': obituaries,
        'user': request.user,
    }, context_instance=RequestContext(request))

@login_required
def manage_death_notice(request, death_notice_id=None):
    if request.method == 'POST':
        if request.POST.has_key('delete_death_notice'):
            Death_notice.objects.filter(funeral_home__username=request.user.username).get(pk=death_notice_id).delete()
            msg = ugettext('The %(verbose_name)s was deleted.') %\
                { 'verbose_name': Death_notice._meta.verbose_name }
#             messages.success(request, msg, fail_silently=True)
            messages.success(request, msg, fail_silently=False)
            return HttpResponseRedirect(reverse('death_notice_index'))
        
        if death_notice_id:
            death_notice = Death_notice.objects.get(pk=death_notice_id)
            form = Death_noticeForm(request.POST, request.FILES, instance=death_notice)
            formset = ServiceFormSet(request.POST, instance=death_notice)
        else:
            form = Death_noticeForm(request.POST, request.FILES)
            formset = ServiceFormSet(request.POST)
        
        if form.is_valid() and formset.is_valid():
            death_notice = form.save(commit=False)
            death_notice.funeral_home = request.user
            death_notice.save()
            formset = ServiceFormSet(request.POST, instance=death_notice)
            formset.save()
            if request.POST.has_key('add_another'):
                return HttpResponseRedirect(reverse('add_death_notice'))
            else:
                return HttpResponseRedirect(reverse('death_notice_index'))
    else:
        if death_notice_id:
            death_notice = Death_notice.objects.get(pk=death_notice_id)
            form = Death_noticeForm(instance=death_notice)
            formset =ServiceFormSet(instance=death_notice)
        else:
            form = Death_noticeForm()
            formset = ServiceFormSet(instance=Death_notice())
    
    return render_to_response('manage_death_notice.html', {
        'form': form,
        'formset': formset,
        'death_notice_id': death_notice_id,
    }, context_instance=RequestContext(request))

# http://docs.djangoproject.com/en/1.3/topics/forms/modelforms/
def manage_obituary(request, obituary_id=None):
    if obituary_id:
        obituary = Obituary.objects.get(pk=obituary_id)
    else:
        obituary = None
    
    if request.method == 'POST':
        form = ObituaryForm(request, request.POST, request.FILES, instance=obituary)
        formset = VisitationFormSet(request.POST, instance=obituary)
        bei_formset = BEI_FormSet(request.POST, instance=obituary)
        os_formset = Other_servicesFormSet(request.POST, instance=obituary)
        if form.is_valid() and formset.is_valid() and bei_formset.is_valid() and \
            os_formset.is_valid():
            
            form.save()
            formset.save()
            bei_formset.save()
            os_formset.save()
            return HttpResponseRedirect(reverse('obituary.views.manage_obituary', args=(obituary.pk,)))
    else:
        if obituary_id:
            form = ObituaryForm(request, instance=obituary)
            formset = VisitationFormSet(instance=obituary)
            bei_formset = BEI_FormSet(instance=obituary)
            os_formset = Other_servicesFormSet(instance=obituary)
        else:
            form = ObituaryForm(request)
            formset = VisitationFormSet(instance=Obituary())
            bei_formset = BEI_FormSet(instance=Obituary())
            os_formset = Other_servicesFormSet(instance=Obituary())
    
    return render_to_response('manage_obituary.html', {
        'form': form,
        'formset': formset,
        'bei_formset': bei_formset,
        'os_formset': os_formset,
    }, context_instance=RequestContext(request))

def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse('death_notice_index'))

@login_required
def add_new_model(request, model_name):
    if (model_name.lower() == model_name):
        normal_model_name = model_name.capitalize()
    else:
        normal_model_name = model_name
    
    app_list = get_apps()
    for app in app_list:
        for model in get_models(app):
            if model.__name__ == normal_model_name:
                form = modelform_factory(model)
                
                if normal_model_name == 'Death_notice':
                    form = Death_noticeForm
                
                if request.method == 'POST':
                    form = form(request.POST)
                    if form.is_valid():
                        try:
                            if normal_model_name == 'Death_notice':
                                new_obj = form.save(commit=False)
                                new_obj.funeral_home = request.user
                                new_obj.save()
                            else:
                                new_obj = form.save()
                        except forms.ValidationError, error:
                            new_obj = None
                        
                        if new_obj:
                             return HttpResponse('<script type="text/javascript">opener.dismissAddAnotherPopup(window, "%s", "%s");</script>' % \
                                    (escape(new_obj._get_pk_val()), escape(new_obj)))
                else:
                   form = form()
                
                page_context = {'form': form, 'field': normal_model_name}
                return render_to_response('popup.html', page_context, context_instance=RequestContext(request))