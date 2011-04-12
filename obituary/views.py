from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
# from django.forms.models import modelformset_factory, inlineformset_factory
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.generic.list_detail import object_list
from obituary.models import Death_notice, Service, Obituary, Visitation
from obituary.forms import Death_noticeForm, ServiceFormSet, ObituaryForm, \
    VisitationFormSet

# Create your views here.

def deaths(request, model=None):
    if request.META['HTTP_USER_AGENT'].count('Macintosh'):
        request_machine = 'MAC'
        template_name = 'obituary/obituary_list_mac.html'    # saved in UTF-8 format
    else:
        request_machine = 'WIN'
        template_name = 'obituary/obituary_list_win.html'    # saved in DOS format

    model = eval(model)
    if model == Death_notice:
        queryset = model.objects.filter(has_run=False).order_by('last_name')
    else:
        queryset = model.objects.filter(has_run=False).order_by('death_notice__last_name')

    return object_list(
        request,
        queryset = queryset,
        mimetype = 'text/plain',
        template_name = template_name,
        extra_context = {
            'request_machine': request_machine,
        },
    )

@login_required
def fh_index(request):
    death_notices = Death_notice.objects.filter(funeral_home__username=request.user.username)
    obituaries = Obituary.objects.filter(funeral_home__username=request.user.username)
    return render_to_response('obituary/fh_index.html', {
        'death_notices': death_notices,
        'obituaries': obituaries,
        'user': request.user,
    })

def manage_death_notice(request, death_notice_id=None):
    if request.POST:
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
            return HttpResponseRedirect(reverse('death_notice_index'))
    else:
        if death_notice_id:
            death_notice = Death_notice.objects.get(pk=death_notice_id)
            form = Death_noticeForm(instance=death_notice)
            formset =ServiceFormSet(instance=death_notice)
        else:
            form = Death_noticeForm()
            formset = ServiceFormSet(instance=Death_notice())
    
    return render_to_response('obituary/manage_death_notice.html', {
        'form': form,
        'formset': formset,
    }, context_instance=RequestContext(request))

def manage_obituary(request, obituary_id=None):
    if request.POST:
        if obituary_id:
            obituary = Obituary.objects.get(pk=obituary_id)
            form = ObituaryForm(request.POST, request.FILES, instance=obituary)
        else:
            form = ObituaryForm(request.POST, request.FILES)
    else:
        form = ObituaryForm(request)
        formset = VisitationFormSet(instance=Obituary())
    
    return render_to_response('obituary/manage_obituary.html', {
        'form': form,
        'formset': formset,
    }, context_instance=RequestContext(request))

# def manage_death_notice(request, death_notice_id=None):
#     if death_notice_id is not None:
#         death_notice = Death_notice.objects.get(pk=death_notice_id)
#         formset = ServiceInlineFormset(instance=death_notice)
#     
#     if request.method == 'POST':
#         form = Death_noticeForm(request.POST, request.FILES, instance=death_notice)
#         if form.is_valid():
#             form.save()
#             return HttpResponseRedirect(reverse('death_notice_index'))
#     else:
#         form = Death_noticeForm()
#         formset = ServiceInlineFormset(instance=death_notice)
#     return render_to_response('obituary/manage_death_notice.html', {
#         'form': form,
#         'formset': formset,
#     })

# def manage_death_notice(request, death_notice_id=None):
#     if death_notice_id is not None:
#         death_notice = Death_notice.objects.get(pk=death_notice_id)
#     ServiceInlineFormSet = inlineformset_factory(Death_notice, Service)
#     if request.method == 'POST':
#         formset = ServiceInlineFormSet(request.POST, request.FILES, instance=death_notice)
#         if formset.is_valid():
#             formset.save()
#     else:
#         formset = ServiceInlineFormSet(instance=death_notice)
#     return render_to_response('obituary/manage_death_notice.html', {
#         'formset': formset,
#     })

def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse('death_notice_index'))
