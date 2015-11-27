from django.contrib import admin

from .models import Template, Resource, Env


class TemplateAdmin(admin.ModelAdmin):
    pass


class ResourceAdmin(admin.ModelAdmin):
    pass


class EnvAdmin(admin.ModelAdmin):
    pass


admin.site.register(Template, TemplateAdmin)
admin.site.register(Resource, ResourceAdmin)
admin.site.register(Env, EnvAdmin)
