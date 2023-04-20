
import radar
import datetime

from django.db import models
from django.contrib.contenttypes.fields import GenericRelation, GenericForeignKey
from django.contrib.contenttypes.models import ContentType
# from django.utils import timezone

from django.utils.translation import gettext as _


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

    def __str__(self):
        return self.name


class Department(models.Model):

    name = models.CharField(max_length=255)
    business = models.ForeignKey(Business, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Position(models.Model):

    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


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


class GenericModelA(AbstractGeneric):

    class Meta:
        verbose_name_plural = "Generic Model A's"

    def __str__(self):
        return self.name


class GenericModelB(AbstractGeneric):

    class Meta:
        verbose_name_plural = "Generic Model B's"

    def __str__(self):
        return self.name


years = [str(i) for i in range(2000, 2015)]
incident_years = [str(i) for i in range(2014, 2017)]


def add_a_datetime():
    start = datetime.datetime(year=2000, month=1, day=1, tzinfo=datetime.timezone.utc)
    stop = datetime.datetime(year=2016, month=12, day=31, tzinfo=datetime.timezone.utc)
    dt = radar.random_datetime(start=start, stop=stop)
    return dt


def add_a_date():
    return add_a_datetime().date()


class Staff(models.Model):

    first_name = models.CharField(max_length=255, help_text=_("Enter the name of the staff being rounded"))
    last_name = models.CharField(max_length=255, help_text=_("Enter the name of the staff being rounded"))
    active = models.CharField(max_length=10, choices=ACTIVE_CHOICES)

    is_manager = models.BooleanField(default=False)

    position = models.ForeignKey(Position, on_delete=models.CASCADE)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    contract_type = models.ForeignKey(ContractType, on_delete=models.CASCADE)

    date_hired = models.DateTimeField(default=add_a_datetime)
    last_incident = models.DateField(default=add_a_date)

    limit = models.Q(app_label='staff', model='genericmodela') | models.Q(app_label='staff', model='genericmodelb')
    content_type = models.ForeignKey(ContentType, limit_choices_to=limit, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    generic_object = GenericForeignKey("content_type", "object_id")
    generic_object_multi = models.ManyToManyField(
        GenericModelB, blank=True,
        related_name='generic_object_multi'
    )

    class Meta:
        verbose_name_plural = "staff"
        ordering = ("last_name", "first_name",)

    def name(self):
        return "%s, %s" % (self.last_name, self.first_name)

    def status(self):
        return ACTIVE_CHOICES_DISPLAY[self.active]

    def __str__(self):
        return self.name()
