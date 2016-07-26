import random

from django.db import models
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext as _


ACTIVE = 'active'
INACTIVE = 'inactive'
TERMINATED = 'terminated'

ACTIVE_CHOICES = (
    (ACTIVE, "Active"),
    (INACTIVE, "Inactive"),
    (TERMINATED, "Terminated"),
)

ACTIVE_CHOICES_DISPLAY = dict(ACTIVE_CHOICES)


class Business(models.Model):

    name = models.CharField(max_length=255)
    business_type = models.IntegerField(choices=zip(range(5), range(5)), default=1)

    class Meta:
        verbose_name_plural = "Businesses"

    def __unicode__(self):
        return self.name


class Department(models.Model):

    name = models.CharField(max_length=255)
    business = models.ForeignKey(Business)

    def __unicode__(self):
        return self.name


class Position(models.Model):

    name = models.CharField(max_length=255)

    def __unicode__(self):
        return self.name


class ContractType(models.Model):

    name = models.CharField(max_length=32)

    def __unicode__(self):
        return self.name


class AbstractGeneric(models.Model):

    name = models.CharField(max_length=255)
    description = models.TextField()

    staff = generic.GenericRelation(
        "Staff",
        content_type_field="content_type",
        object_id_field="object_id",
    )

    class Meta:
        abstract = True


class GenericModelA(AbstractGeneric):

    class Meta:
        verbose_name_plural = "Generic Model A's"

    def __unicode__(self):
        return self.name


class GenericModelB(AbstractGeneric):

    class Meta:
        verbose_name_plural = "Generic Model B's"

    def __unicode__(self):
        return self.name


years = [str(i) for i in range(2000, 2015)]
incident_years = [str(i) for i in range(2014, 2017)]


def add_a_datetime():

    return random.choice(years) + '-' + str(random.choice(range(1, 13))) + '-' + str(random.choice(range(1, 29))) + ' ' + str(random.choice(range(0, 24))) + ':' + str(random.choice(range(0, 60))) + ':' + str(random.choice(range(0, 60)))


def add_a_date():

    return random.choice(incident_years) + '-' + str(random.choice(range(1, 13))) + '-' + str(random.choice(range(1, 29)))


class Staff(models.Model):

    first_name = models.CharField(max_length=255, help_text=_("Enter the name of the staff being rounded"))
    last_name = models.CharField(max_length=255, help_text=_("Enter the name of the staff being rounded"))
    active = models.CharField(max_length=10, choices=ACTIVE_CHOICES)

    is_manager = models.BooleanField(default=False)

    position = models.ForeignKey(Position)
    department = models.ForeignKey(Department)
    contract_type = models.ForeignKey(ContractType)

    date_hired = models.DateTimeField(default=add_a_datetime)
    last_incident = models.DateField(default=add_a_date)

    limit = models.Q(app_label='staff', model='genericmodela') | models.Q(app_label='staff', model='genericmodelb')
    content_type = models.ForeignKey(ContentType, limit_choices_to=limit)
    object_id = models.PositiveIntegerField()
    generic_object = generic.GenericForeignKey("content_type", "object_id")

    class Meta:
        verbose_name_plural = "staff"
        ordering = ("last_name", "first_name",)

    def name(self):
        return "%s, %s" % (self.last_name, self.first_name)

    def status(self):
        return ACTIVE_CHOICES_DISPLAY[self.active]

    def __unicode__(self):
        return self.name()
