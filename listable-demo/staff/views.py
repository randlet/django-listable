from django.utils.translation import ugettext as _
from django.contrib.contenttypes.models import ContentType
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
        "is_manager",
    )

    widgets = {
        "department__business__name": SELECT,
        "department__business__business_type": SELECT,
        "position__name": SELECT,
        "choices": SELECT,
        "active": SELECT,
        "is_manager": SELECT
    }

    search_fields = {
        "name": ("first_name", "last_name",),
        "last_name": "last_name__exact",
        "genericname": "genericname",
        "department__name": "department__name",
    }

    order_fields = {
        "name": ("last_name", "first_name",),
    }

    headers = {
        "position__name": _("Position"),
        "department__business__name": _("Business"),
        "department__business__business_type": _("Business Type"),
    }

    order_by = ("-name",)

    select_related = ("department", "position", "department__business",)

    def generic(self, obj):
        return obj.generic_object.name

    def name(self, staff):
        return staff.name()

    def get_extra(self):
        cta = ContentType.objects.get_for_model(models.GenericModelA)
        ctb = ContentType.objects.get_for_model(models.GenericModelB)

        extraq = """
         CASE
            WHEN content_type_id = {0}
                THEN (SELECT name AS genericname from staff_genericmodela WHERE object_id = staff_genericmodela.id)
            WHEN content_type_id = {1}
                THEN (SELECT name AS genericname from staff_genericmodelb WHERE object_id = staff_genericmodelb.id)
         END
         """.format(cta.pk, ctb.pk)

        return {"select": {'genericname': extraq}}
