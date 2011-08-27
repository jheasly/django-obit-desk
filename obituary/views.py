import codecs, datetime
from django import forms
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.db import IntegrityError
from django.db.models.loading import get_models, get_app, get_apps
from django.forms.models import modelform_factory
from django.http import HttpResponseRedirect, HttpResponseNotFound, HttpResponse
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext, loader
from django.utils.html import escape
from django.utils.translation import ugettext
from django.views.generic.list_detail import object_list
from obituary.models import Death_notice, Obituary
from obituary.forms import Death_noticeForm, \
    ServiceFormSet, ObituaryForm, VisitationFormSet, BEI_FormSet, \
    Other_servicesFormSet, ChildrenFormSet, SiblingsFormSet, MarriageFormSet, \
    DeathNoticeOtherServicesFormSet

from obituary_settings import DISPLAY_DAYS_BACK

# Create your views here.

def deaths(request, model=None):
    # Set the right template
    if request.META['HTTP_USER_AGENT'].count('Macintosh') and model == 'Death_notice':
        template_name = 'death_list_unix_line_endings.html'
    elif request.META['HTTP_USER_AGENT'].count('Macintosh') and model == 'Obituary':
        template_name = 'obituary_list_unix_line_endings.html'
    elif model == 'Death_notice':
        template_name = 'death_list_windows_line_endings.html'
    else:
        template_name = 'obituary_list_windows_line_endings.html'
        
    model = eval(model)
    if model == Death_notice:
        queryset = model.objects.filter(death_notice_in_system=False, obituary__isnull=True).order_by('last_name')
    else:
        queryset = model.objects.filter(obituary_in_system=False, status='live').order_by('death_notice__last_name')
    
#     return object_list(
#         request,
#         queryset = queryset,
#         mimetype = 'text/plain;charset=utf-8',
#         template_name = template_name,
#     )

    t = loader.get_template(template_name)
    c = RequestContext(request, {'object_list': queryset })
    data = t.render(c).replace('  ', ' ')
    data = data.replace('; ; ', '; ')
    data = data.replace('> ', '>')
    r = HttpResponse(data, mimetype='text/plain;charset=utf-8')

#     r = object_list(
#         request,
#         queryset = queryset,
#         mimetype = 'text/plain;charset=utf-8',
#         template_name = template_name,
#     )
    r['Content-Disposition'] = 'attachment; filename=%s-[%s].txt;' % (model._meta.verbose_name_plural.lower().replace(' ', '-'), datetime.datetime.now().strftime('%Y-%m-%d-%I-%M-%S-%p'))
    return r

@login_required
def fh_index(request):
    
    days_ago = datetime.timedelta(days=DISPLAY_DAYS_BACK)
    
    death_notices = Death_notice.objects.filter(death_notice_created__gte=( datetime.datetime.now() - days_ago ), funeral_home__username=request.user.username)
    obituaries = Obituary.objects.filter(obituary_created__gte=( datetime.datetime.now() - days_ago ), death_notice__funeral_home__username=request.user.username)
    ObituaryFactoryFormSet = modelform_factory(Obituary)
    
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
            messages.success(request, msg, fail_silently=True)
            return HttpResponseRedirect(reverse('death_notice_index'))
        
        if death_notice_id:
            death_notice = Death_notice.objects.get(pk=death_notice_id)
            form = Death_noticeForm(request.POST, request.FILES, instance=death_notice)
            formset = ServiceFormSet(request.POST, instance=death_notice)
            dn_os_formset = DeathNoticeOtherServicesFormSet(request.POST, instance=death_notice)
        else:
            form = Death_noticeForm(request.POST, request.FILES)
            formset = ServiceFormSet(request.POST)
            dn_os_formset = DeathNoticeOtherServicesFormSet(request.POST)
        
        if form.is_valid() and formset.is_valid() and dn_os_formset.is_valid():
            death_notice = form.save(commit=False)
            death_notice.funeral_home = request.user
            death_notice.save()
            formset = ServiceFormSet(request.POST, instance=death_notice)
            formset.save()
            dn_os_formset = DeathNoticeOtherServicesFormSet(request.POST, instance=death_notice)
            msg = ugettext('Death notice for %s %s saved.' % (death_notice.first_name, death_notice.last_name))
            messages.success(request, msg, fail_silently=True)
            dn_os_formset.save()
            if request.POST.has_key('add_another'):
                return HttpResponseRedirect(reverse('add_death_notice'))
            else:
                return HttpResponseRedirect(reverse('death_notice_index'))
    else:
        if death_notice_id:
            death_notice = Death_notice.objects.get(pk=death_notice_id)
            form = Death_noticeForm(instance=death_notice)
            formset = ServiceFormSet(instance=death_notice)
            dn_os_formset = DeathNoticeOtherServicesFormSet(instance=death_notice)
        else:
            form = Death_noticeForm()
            formset = ServiceFormSet(instance=Death_notice())
            dn_os_formset = DeathNoticeOtherServicesFormSet(instance=Death_notice())
    
    return render_to_response('manage_death_notice.html', {
        'form': form,
        'formset': formset,
        'other_services_formset': dn_os_formset,
        'death_notice_id': death_notice_id,
    }, context_instance=RequestContext(request))

# http://docs.djangoproject.com/en/1.3/topics/forms/modelforms/
def manage_obituary(request, obituary_id=None):
    if obituary_id:
        # Editing existing record ... 
        obituary = get_object_or_404(Obituary, pk=obituary_id)
    else:
        # Creating new record ... 
        obituary = Obituary()
    
    if request.method == 'POST':
        if request.POST.has_key('delete') and obituary_id:
            current_obit = Obituary.objects.filter(death_notice__funeral_home__username=request.user.username).get(pk=obituary_id)
            current_obit.delete()
            msg = ugettext('The %(verbose_name)s for %(first)s %(last)s was deleted.') % \
                {
                    'verbose_name': Obituary._meta.verbose_name,
                    'first': current_obit.death_notice,
                    'last': current_obit.death_notice.last_name,
                }
            messages.success(request, msg, fail_silently=False)
            return HttpResponseRedirect(reverse('death_notice_index'))
        
        form = ObituaryForm(request, request.POST, request.FILES, instance=obituary)
        formset = VisitationFormSet(request.POST, instance=obituary)
        bei_formset = BEI_FormSet(request.POST, instance=obituary)
        os_formset = Other_servicesFormSet(request.POST, instance=obituary)
        child_formset = ChildrenFormSet(request.POST, instance=obituary)
        sib_formset = SiblingsFormSet(request.POST, instance=obituary)
        wed_formset = MarriageFormSet(request.POST, instance=obituary)
        
        if form.is_valid() and formset.is_valid() and bei_formset.is_valid() and \
            os_formset.is_valid() and child_formset.is_valid() and \
            sib_formset.is_valid() and wed_formset.is_valid():
            
            msg = ugettext('The %(verbose_name)s for %(first)s %(last)s was updated.') % \
                {
                    'verbose_name': Obituary._meta.verbose_name,
                    'first': obituary.death_notice.first_name,
                    'last': obituary.death_notice.last_name,
                }
            messages.success(request, msg, fail_silently=False)
            
            obituary = form.save()
            formset.save()
            bei_formset.save()
            os_formset.save()
            child_formset.save()
            sib_formset.save()
            wed_formset.save()
            if request.POST.has_key('submit'):
                return HttpResponseRedirect(reverse('death_notice_index'))
            elif request.POST.has_key('submit_add'):
                return HttpResponseRedirect(reverse('add_obituary'))
            else:
                return HttpResponseRedirect(reverse('obituary.views.manage_obituary', args=(obituary.pk,)))
    else:
        if obituary_id:
            form = ObituaryForm(request, instance=obituary)
            formset = VisitationFormSet(instance=obituary)
            bei_formset = BEI_FormSet(instance=obituary)
            os_formset = Other_servicesFormSet(instance=obituary)
            child_formset = ChildrenFormSet(instance=obituary)
            sib_formset = SiblingsFormSet(instance=obituary)
            wed_formset = MarriageFormSet(instance=obituary)
        else:
            form = ObituaryForm(request)
            formset = VisitationFormSet(instance=Obituary())
            bei_formset = BEI_FormSet(instance=Obituary())
            os_formset = Other_servicesFormSet(instance=Obituary())
            child_formset = ChildrenFormSet(instance=Obituary())
            sib_formset = SiblingsFormSet(instance=Obituary())
            wed_formset = MarriageFormSet(instance=Obituary())
    
    return render_to_response('manage_obituary.html', {
        'form': form,
        'formset_name': formset.model._meta.verbose_name,
        'formset': formset,
        'bei_formset_name': bei_formset.model._meta.verbose_name,
        'bei_formset': bei_formset,
        'os_formset_name': os_formset.model._meta.verbose_name,
        'os_formset': os_formset,
        'child_formset_name': child_formset.model._meta.verbose_name,
        'child_formset': child_formset,
        'sib_formset_name': sib_formset.model._meta.verbose_name,
        'sib_formset': sib_formset,
        'wed_formset': wed_formset,
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
                    dn_name = model._meta.verbose_name
                    form = Death_noticeForm
                    service_form = ServiceFormSet
                    dn_os_formset = DeathNoticeOtherServicesFormSet
                
                if request.method == 'POST':
                    form = form(request.POST)
                    service_form = service_form(request.POST)
                    dn_os_formset = DeathNoticeOtherServicesFormSet(request.POST)
                    if form.is_valid() and service_form.is_valid() and dn_os_formset.is_valid():
                        try:
                            if normal_model_name == 'Death_notice':
                                new_obj = form.save(commit=False)
                                new_obj.funeral_home = request.user
                                new_obj.save()
                                service_form = ServiceFormSet(request.POST, instance=new_obj)
                                service_form.save()
                                dn_os_formset = DeathNoticeOtherServicesFormSet(request.POST, instance=new_obj)
                                dn_os_formset.save()
                            else:
                                new_obj = form.save()
                        except forms.ValidationError, error:
                            new_obj = None
                        
                        if new_obj:
                             return HttpResponse('<script type="text/javascript">opener.dismissAddAnotherPopup(window, "%s", "%s");</script>' % \
                                    (escape(new_obj._get_pk_val()), escape(new_obj)))
                else:
                   form = form()
                
                page_context = {'form': form, 'service_form': service_form, 'other_services_formset': dn_os_formset, 'field': normal_model_name, 'dn_verbose_name': dn_name }
                return render_to_response('dn_popup.html', page_context, context_instance=RequestContext(request))
