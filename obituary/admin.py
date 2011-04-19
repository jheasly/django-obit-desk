# TO DO: Add list_editable = 'has_run' if superuser.
# TO DO: Photo renamer ob.last.first.jpg

from django.contrib import admin
from django.contrib.auth.models import User
from obituary.models import Death_notice, Obituary, FuneralHomeProfile, \
    Service, Visitation, BEI, Other_services, Children, Siblings

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

class Death_noticeAdmin(admin.ModelAdmin):
    pass
admin.site.register(Death_notice, Death_noticeAdmin)

class ObituaryAdmin(admin.ModelAdmin):
    pass
#     list_display = ('death_notice', 'gender', 'date_of_birth', 'obituary_created', 'photo_file_name',)
#     
    inlines = [
        VisitationInline,
        BEIInline,
        Other_servcesInline,
        ChildrenInline,
        SiblingsInline,
    ]

admin.site.register(Obituary, ObituaryAdmin)
