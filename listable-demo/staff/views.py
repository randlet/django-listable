# Create your views here.
from django.views.generic import View
from django.http import Http404
from listable.views  import BaseListableView, Column, SELECT

from . import models

class StaffList(BaseListableView):

    model = models.Staff

    columns = (
        Column(
            field="id",
            ordering=False,
            filtering=False
        ),
        Column(
            field="first_name",
            ordering="first_name",
            filtering="first_name",
        ),
        Column(
            field="name",
            ordering="last_name",
            filtering="last_name",
            widget=SELECT,
        ),
        Column(
            field="department",
            ordering="department__name",
            filtering="department__name",
            widget=SELECT,
        ),
        Column(
            header="Position Name",
            field="position",
            ordering="position__name",
            filtering="position__name",
        ),
        Column(
            header="Business Name",
            field="business",
            ordering="department__business__name",
            filtering=True
        ),
    )

    def name(self, staff):
        return staff.name()

    def department(self, staff):
        return staff.department.name

    def business(self, staff):
        return staff.department.business.name

