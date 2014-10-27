from django.utils.translation import ugettext as _
from listable.views import BaseListableView, SELECT

from . import models


class StaffList(BaseListableView):

    model = models.Staff

    fields = (
        "id",
        "name",
        "active",
        "department__name",
        "position__name",
        "department__business__name",
        "department__business__business_type",
        "genericname",
    )

    widgets = {
        "department__business__name": SELECT,
        "department__business__business_type": SELECT,
        "position__name": SELECT,
        "choices": SELECT,
        "active": SELECT,
    }

    search_fields = {
        "name": ("first_name__icontains", "last_name__icontains",),
        "last_name": "last_name__exact",
        "genericname": "genericname__icontains",
    }

    order_fields = {
        "name": ("last_name", "first_name",),
    }

    headers = {
        "position__name": _("Position"),
        "department__business__name": _("Business"),
        "department__business__business_type": _("Business Type"),
    }

    select_related = ("department", "position", "department__business",)

    def generic(self, obj):
        return obj.generic_object.name

    def name(self, staff):
        return staff.name()

    def get_extra(self):
        extraq = """
         CASE
            WHEN content_type_id =11
                THEN (SELECT name from staff_genericmodela WHERE object_id = staff_genericmodela.id)
            WHEN content_type_id = 12
                THEN (SELECT name from staff_genericmodelb WHERE object_id = staff_genericmodelb.id)
         END
         """
        return {"select": {'genericname': extraq}}
