# TO DO: Add list_editable = 'has_run' if superuser.
# TO DO: Photo renamer ob.last.first.jpg

from django.contrib import admin
from django.contrib.auth.models import User
from obituary.models import Death_notice, Obituary, FuneralHomeProfile, \
    Service, Visitation, BEI, Other_services, Children, Siblings, Marriage

class FuneralHomeProfileAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'city', 'state', 'phone',)

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

class Death_noticeAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'death_notice_created', 'death_notice_in_system', 'death_notice_has_run',)
    list_editable = ('death_notice_in_system', 'death_notice_has_run',)
    list_filter = ('death_notice_in_system', 'death_notice_has_run',)
    
    inlines = [
        ServiceInline,
    ]
admin.site.register(Death_notice, Death_noticeAdmin)

class ObituaryAdmin(admin.ModelAdmin):
    list_display = ('death_notice', 'gender', 'date_of_birth', 'service_date', 'obituary_created', 'photo_file_name', 'obituary_in_system', 'obituary_has_run', 'status',)
    list_editable = ('obituary_in_system', 'obituary_has_run')
    
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
