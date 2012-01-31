from django.contrib import admin
from django.contrib.auth.models import User
from sorl.thumbnail.admin import AdminImageMixin
from obituary.forms import ObituaryAdminForm
from obituary.models import Death_notice, Obituary, FuneralHomeProfile, \
    Service, Visitation, BEI, Other_services, Children, Siblings, Marriage, \
    DeathNoticeOtherServices

class FuneralHomeProfileAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'city', 'state', 'phone',)
    list_filter = ('user__is_active',)

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

class MarriageInline(admin.TabularInline):
    model = Marriage

class DeathNoticeOtherServicesInline(admin.TabularInline):
    model = DeathNoticeOtherServices

class Death_noticeAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'ready_for_print', 'death_notice_created', 'death_notice_in_system', 'death_notice_has_run',)
    list_editable = ('death_notice_in_system', 'death_notice_has_run',)
    list_filter = ('death_notice_in_system', 'death_notice_has_run',)
    search_fields = ['last_name', 'first_name',]
    
    # To filter out everything but funeral homes in inline dropdown.
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'funeral_home':
            # needs tighter filtering and ordering ... 
            kwargs['queryset'] = User.objects.exclude(is_staff=True)
        return super(Death_noticeAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)
    
    inlines = [
        ServiceInline,
        DeathNoticeOtherServicesInline,
    ]
admin.site.register(Death_notice, Death_noticeAdmin)

class ObituaryAdmin(AdminImageMixin, admin.ModelAdmin):
    list_display = ('death_notice', 'fh', 'ready_for_print', 'obituary_in_system', 'obituary_has_run', 'obituary_publish_date', 'preferred_run_date', 'service_date', 'admin_thumbnail', 'obituary_created', 'status', 'date_of_birth', )
    list_editable = ('obituary_in_system', 'obituary_has_run', 'obituary_publish_date')
    list_filter = ('death_notice__funeral_home',)
    search_fields = ['death_notice__last_name', 'death_notice__first_name',]
    date_hierarchy = 'preferred_run_date'
    ordering = ('-preferred_run_date',)
    
    form = ObituaryAdminForm
    
    inlines = [
        MarriageInline,
        VisitationInline,
        BEIInline,
        Other_servcesInline,
        ChildrenInline,
        SiblingsInline,
    ]
    
    death_notice_fk_filter_related_only=True
    death_notice_fk_filter_name_field='city_of_residence'
    
    def fh(self, obj):
        return obj.death_notice.funeral_home.username
    fh.short_description = u'Funeral home'

admin.site.register(Obituary, ObituaryAdmin)

class ServiceAdmin(admin.ModelAdmin):
    list_display = ('service', 'service_date_time',)

admin.site.register(Service, ServiceAdmin)
