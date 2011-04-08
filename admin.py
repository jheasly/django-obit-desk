# TO DO: Add list_editable = 'has_run' if superuser.
# TO DO: Photo renamer ob.last.first.jpg

from django import forms
from django.contrib import admin
from django.contrib.auth.models import User
from django.forms.models import modelform_factory
from django.utils.functional import curry
from django.contrib.admin.util  import flatten_fieldsets
from obituary.models import Death_notice, Obituary, FuneralHomeProfile, \
    Service, Visitation, BEI, Other_services, Children, Siblings

class FuneralHomeProfileAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'city', 'state', 'phone',)
    
    def get_form(self, request, obj=None):
        f = super(FuneralHomeProfileAdmin, self).get_form(request, obj)
        qs = f.base_fields['user'].queryset
        f.base_fields['user'].queryset = qs.order_by('username')
        return f
    
admin.site.register(FuneralHomeProfile, FuneralHomeProfileAdmin)

class ServiceInline(admin.TabularInline):
    model = Service

class VisitationInline(admin.TabularInline):
    model = Visitation

class BEIInline(admin.TabularInline):
    model = BEI

class Other_servcesInline(admin.TabularInline):
    model = Other_services

class ChildrenInline(admin.TabularInline):
    model = Children

class SiblingsInline(admin.TabularInline):
    model = Siblings

class Death_noticeAdmin(admin.ModelAdmin):
    def __init__(self, model, admin_site, *args, **kwargs):
        request = kwargs.pop('request', None)
        if request:
            if request.user.is_superuser:
                self.list_filter = ('has_run',)
        super(Death_noticeAdmin, self).__init__(model, admin_site, *args, **kwargs)
    
    list_display = ('first_name', 'last_name', 'created', 'funeral_home', 'has_run',)
    
    inlines = [
        ServiceInline,
    ]
    
    # overriding get_form for custom 'exclude'
    def get_form(self, request, obj=None, **kwargs):
        """
        Returns a Form class for use in the admin add view. This is used by
        add_view and change_view.
        """
        if self.declared_fieldsets:
            fields = flatten_fieldsets(self.declared_fieldsets)
        else:
            fields = None
        if self.exclude is None:
            exclude = []
        else:
            exclude = list(self.exclude)
        exclude.extend(kwargs.get("exclude", []))
        exclude.extend(self.get_readonly_fields(request, obj))
        # if exclude is an empty list we pass None to be consistant with the
        # default on modelform_factory
        exclude = exclude or None
        defaults = {
            "form": self.form,
            "fields": fields,
            "exclude": exclude,
            "formfield_callback": curry(self.formfield_for_dbfield, request=request),
        }
        defaults.update(kwargs)
#         return modelform_factory(self.model, **defaults)
        '''
        Additional tinkering to the modelform_factory Form class
        i.e., sorting the 'funeral_home' dropdown by 'username'
        '''
        f = modelform_factory(self.model, **defaults)
        qs = f.base_fields['funeral_home'].queryset
        f.base_fields['funeral_home'].queryset = qs.order_by('username')
        return f
    
    def queryset(self, request):
        qs = super(Death_noticeAdmin, self).queryset(request)
        if request.user.is_superuser:
            return qs
        else:
            return qs.filter(funeral_home = request.user)
    
    def save_model(self, request, obj, form, change):
        obj.funeral_home = request.user
        obj.save()
    
    def has_change_permission(self, request, obj=None):
        if not obj:
            return True # So they can see the change list page
        if request.user.is_superuser or obj.funeral_home == request.user:
            return True
        else:
            return False
    
    has_delete_permission = has_change_permission
    
admin.site.register(Death_notice, Death_noticeAdmin)

class ObituaryForm(forms.ModelForm):
    fieldsets = (
        (None, {
            'fields': ('death_notice', 'cause_of_death', 
                'gender', 'date_of_birth', 'place_of_birth', 'parents_names', 
                'married', 'marriage_date', 'marriage_location', 'education',
                'career_work_experience', 'military_service', 
                'life_domestic_partner', 'length_of_relationship',
                'memorial_contributions', 'family_contact', 
                'family_contact_phone', 'photo'),
        }),
        ( 'Survivors', {
            'fields': ('spouse', 'spouse_death', 'parents', 'grandparents', 
                'number_of_grandchildren', 'number_of_great_grandchildren',
                'number_of_great_great_grandchildren', 'preceded_in_death_by',),
            'description': ('''Additional <strong>Survivor</strong> information 
                entered below; in the <strong>Children</strong> and 
                <strong>Siblings</strong> fieldsets.''')
        }),
    )
    
    class Meta:
        model = Obituary
        exclude = ['funeral_home', 'has_run',]

class ObituaryAdminForm(forms.ModelForm):
    fieldsets = (
        (None, {
            'fields': ('funeral_home', 'death_notice', 'cause_of_death', 
                'gender', 'date_of_birth', 'place_of_birth', 'parents_names', 
                'married', 'marriage_date', 'marriage_location', 'education',
                'career_work_experience', 'military_service', 
                'life_domestic_partner', 'length_of_relationship',
                'memorial_contributions', 'family_contact', 
                'family_contact_phone', 'photo'),
        }),
        ( 'Survivors', {
            'fields': ('spouse', 'spouse_death', 'parents', 'grandparents', 
                'number_of_grandchildren', 'number_of_great_grandchildren',
                'number_of_great_great_grandchildren', 'preceded_in_death_by',),
            'description': ('''Additional <strong>Survivor</strong> information 
                entered below; in the <strong>Children</strong> and 
                <strong>Siblings</strong> fieldsets.''')
        }),
        (None, {
             'fields': ('has_run',)
        }),
    )
    
    class Meta:
        model = Obituary

class ObituaryAdmin(admin.ModelAdmin):
    list_display = ('death_notice', 'gender', 'date_of_birth', 'created', 'photo_file_name',)
    
    inlines = [
        VisitationInline,
        BEIInline,
        Other_servcesInline,
        ChildrenInline,
        SiblingsInline,
    ]
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'death_notice':
            if not request.user.is_superuser:
                kwargs['queryset'] = Death_notice.objects.filter(funeral_home=request.user)
            return db_field.formfield(**kwargs)
        return super(ObituaryAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)
    
    # overriding get_form for custom 'exclude'
    def get_form(self, request, obj=None, **kwargs):
        """
        Returns a Form class for use in the admin add view. This is used by
        add_view and change_view.
        """
        if self.declared_fieldsets:
            fields = flatten_fieldsets(self.declared_fieldsets)
        else:
            fields = None
        if self.exclude is None:
            exclude = []
        else:
            exclude = list(self.exclude)
        exclude.extend(kwargs.get("exclude", []))
        exclude.extend(self.get_readonly_fields(request, obj))
        # if exclude is an empty list we pass None to be consistant with the
        # default on modelform_factory
        exclude = exclude or None
        defaults = {
            "form": self.form,
            "fields": fields,
            "exclude": exclude,
            "formfield_callback": curry(self.formfield_for_dbfield, request=request),
        }
        defaults.update(kwargs)
#         return modelform_factory(self.model, **defaults)
        
        '''
        Additional tinkering to the modelform_factory Form class
        i.e., sorting the 'funeral_home' dropdown by 'username'
        '''
#         f = modelform_factory(self.model, **defaults)
        
        if request.user.is_superuser:
            qs = ObituaryAdminForm.base_fields['funeral_home'].queryset
            ObituaryAdminForm.base_fields['funeral_home'].queryset = qs.order_by('username')
            return ObituaryAdminForm
        else:
            return ObituaryForm
    
    def changelist_view(self, request, extra_context=None):
        if request.user.is_superuser:
            self.list_filter=('has_run',)
            self.list_editable = ('has_run',)
            '''
            Check to see if 'has_run' is in list_display and add if  it isn't.
            '''
            if not 'has_run' in self.list_display:
                self.list_display.append('has_run')
        else:
            self.list_filter = None
            self.list_editable = None
            if 'has_run' in  self.list_display:
                '''
                If 'has_run' is already in list_display, and user isn't a
                superuser, then remove it. 
                '''
                self.list_display.remove('has_run')
        return super(ObituaryAdmin, self).changelist_view(request, extra_context=extra_context)
    
    def queryset(self, request):
        qs = super(ObituaryAdmin, self).queryset(request)
        if request.user.is_superuser:
            return qs
        else:
            return qs.filter(funeral_home = request.user)
    
    def save_model(self, request, obj, form, change):
        if not request.user.is_superuser:
            obj.funeral_home = request.user
        obj.save()
    
    def has_change_permission(self, request, obj=None):
        if not obj:
            return True # So they can see the change list page
        if request.user.is_superuser or obj.funeral_home == request.user:
            return True
        else:
            return False
    
    has_delete_permission = has_change_permission

admin.site.register(Obituary, ObituaryAdmin)
