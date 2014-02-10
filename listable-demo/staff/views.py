# Create your views here.
from django.views.generic import View
from django.http import Http404
from listable.views  import BaseListableView, Column

from . import models

class StaffList(BaseListableView):

    model = models.Staff

    columns = (
        Column(field="id", ordering=True, filtering=False),
        Column(field="name", ordering="last_name", filtering=True),
        Column(field="department", ordering="department__name", filtering=True),
        Column(field="position", ordering="position__name", filtering=True),
        Column(field="business", ordering="department__business__name", filtering=True),
    )

    def name(self, staff):
        return staff.name()

    def department(self, staff):
        return staff.department.name

    def business(self, staff):
        return staff.department.business.name

