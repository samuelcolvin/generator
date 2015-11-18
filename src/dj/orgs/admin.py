from django.contrib import admin

from .models import Organisation, APIKey


class OrganisationAdmin(admin.ModelAdmin):
    pass


class APIKeyAdmin(admin.ModelAdmin):
    pass


admin.site.register(Organisation, OrganisationAdmin)
admin.site.register(APIKey, APIKeyAdmin)
