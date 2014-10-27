from django.contrib import admin

from . import models


class StaffAdmin(admin.ModelAdmin):

    list_display = ("id", "first_name", "last_name", "department",)
    list_filter = ("department",)

    def queryset(self, request):
        qs = super(StaffAdmin, self).queryset(request)
        return qs.select_related("department")


admin.site.register([models.Staff], StaffAdmin)
admin.site.register([models.Department, models.Position, models.Business, models.GenericModelA, models.GenericModelB], admin.ModelAdmin)
