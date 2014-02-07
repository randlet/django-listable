from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import ugettext as _
from django.utils.formats import localize

User = get_user_model()

ACTIVE = 'active'
INACTIVE = 'inactive'
TERMINATED = 'terminated'

ACTIVE_CHOICES = (
    (ACTIVE,"Active"),
    (INACTIVE,"Inactive"),
    (TERMINATED,"Terminated"),
)

ACTIVE_CHOICES_DISPLAY = dict(ACTIVE_CHOICES)


class Business(models.Model):

    name = models.CharField(max_length=255)

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


class Staff(models.Model):

    first_name = models.CharField(max_length=255, help_text=_("Enter the name of the staff being rounded"))
    last_name = models.CharField(max_length=255, help_text=_("Enter the name of the staff being rounded"))
    active = models.CharField(max_length=10, choices = ACTIVE_CHOICES)

    position = models.ForeignKey(Position)
    department = models.ForeignKey(Department)

    class Meta:
        verbose_name_plural = "staff"
        ordering = ("last_name", "first_name",)

    def name(self):
        return "%s, %s" % (self.last_name, self.first_name)

    def status(self):
        return ACTIVE_CHOICES_DISPLAY[self.active]

    def __unicode__(self):
        return self.name()

