from __future__ import unicode_literals


from django.utils.encoding import python_2_unicode_compatible
from django.db import models
try:
    from django.contrib.contenttypes.generic import GenericRelation, GenericForeignKey
except:

    from django.contrib.contenttypes.fields import GenericRelation, GenericForeignKey


from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from django.utils.translation import ugettext as _
import radar


ACTIVE = 'active'
INACTIVE = 'inactive'
TERMINATED = 'terminated'

ACTIVE_CHOICES = (
    (ACTIVE, "Active"),
    (INACTIVE, "Inactive"),
    (TERMINATED, "Terminated"),
)

ACTIVE_CHOICES_DISPLAY = dict(ACTIVE_CHOICES)


@python_2_unicode_compatible
class Business(models.Model):

    name = models.CharField(max_length=255)
    business_type = models.IntegerField(choices=zip(range(5), range(5)), default=1)

    class Meta:
        verbose_name_plural = "Businesses"

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class Department(models.Model):

    name = models.CharField(max_length=255)
    business = models.ForeignKey(Business)

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class Position(models.Model):

    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class ContractType(models.Model):

    name = models.CharField(max_length=32)

    def __str__(self):
        return self.name


class AbstractGeneric(models.Model):

    name = models.CharField(max_length=255)
    description = models.TextField()

    staff = GenericRelation(
        "Staff",
        content_type_field="content_type",
        object_id_field="object_id",
    )

    class Meta:
        abstract = True


@python_2_unicode_compatible
class GenericModelA(AbstractGeneric):

    class Meta:
        verbose_name_plural = "Generic Model A's"

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class GenericModelB(AbstractGeneric):

    class Meta:
        verbose_name_plural = "Generic Model B's"

    def __str__(self):
        return self.name


years = [str(i) for i in range(2000, 2015)]
incident_years = [str(i) for i in range(2014, 2017)]


def add_a_datetime():
    start = timezone.datetime(year=2000, month=1, day=1, tzinfo=timezone.utc)
    stop = timezone.datetime(year=2016, month=12, day=31, tzinfo=timezone.utc)
    dt = radar.random_datetime(start=start, stop=stop)
    return dt


def add_a_date():
    return add_a_datetime().date()


@python_2_unicode_compatible
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
    generic_object = GenericForeignKey("content_type", "object_id")

    class Meta:
        verbose_name_plural = "staff"
        ordering = ("last_name", "first_name",)

    def name(self):
        return "%s, %s" % (self.last_name, self.first_name)

    def status(self):
        return ACTIVE_CHOICES_DISPLAY[self.active]

    def __str__(self):
        return self.name()
