from django.contrib import admin
from django.contrib.auth.models import User
from sorl.thumbnail.admin import AdminImageMixin
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
    
    inlines = [
        ServiceInline,
        DeathNoticeOtherServicesInline,
    ]
admin.site.register(Death_notice, Death_noticeAdmin)

class ObituaryAdmin(AdminImageMixin, admin.ModelAdmin):
    list_display = ('death_notice', 'ready_for_print', 'gender', 'date_of_birth', 'service_date', 'obituary_created', 'admin_thumbnail', 'display_photo_file_name', 'obituary_in_system', 'obituary_has_run', 'obituary_publish_date', 'status',)
    list_editable = ('obituary_in_system', 'obituary_has_run', 'obituary_publish_date')
    search_fields = ['death_notice__last_name', 'death_notice__first_name',]
    
    inlines = [
        MarriageInline,
        VisitationInline,
        BEIInline,
        Other_servcesInline,
        ChildrenInline,
        SiblingsInline,
    ]

admin.site.register(Obituary, ObituaryAdmin)

class ServiceAdmin(admin.ModelAdmin):
    list_display = ('service', 'service_date_time',)

admin.site.register(Service, ServiceAdmin)
