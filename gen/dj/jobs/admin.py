from django.contrib import admin

from dj.jobs.models import Organisation, Job, APIKey


class OrganisationAdmin(admin.ModelAdmin):
    pass


class JobAdmin(admin.ModelAdmin):
    pass


class APIKeyAdmin(admin.ModelAdmin):
    pass


admin.site.register(Organisation, OrganisationAdmin)
admin.site.register(Job, JobAdmin)
admin.site.register(APIKey, APIKeyAdmin)
