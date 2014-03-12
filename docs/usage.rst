========
Usage
========

There's four steps to using django-listable

[*] Including `listable` in your settings.INSTALLED_APPS
[*] Create a view by subclassing listable.views.BaseListableView
[*] Connect the view to a url pattern in your apps urls.py
[*] Include the `listable` template tag in a template

These steps will demonstrated below assuming we have
a Django application called staff and we want to create a page on our
site with a list of staff and the department and business they belong to.

with the following models defined::

    class Business(models.Model):

        name = models.CharField(max_length=255)


    class Department(models.Model):

        name = models.CharField(max_length=255)
        business = models.ForeignKey(Business)


    class Staff(models.Model):

        first_name = models.CharField(max_length=255, help_text=_("Enter the name of the staff being rounded"))
        last_name = models.CharField(max_length=255, help_text=_("Enter the name of the staff being rounded"))
        active = models.CharField(max_length=10, choices = ACTIVE_CHOICES)

        department = models.ForeignKey(Department)

        def name(self):
            return "%s, %s" % (self.last_name, self.first_name)

        def status(self):
            return self.get_active_display()



Adding `listable` to settings.INSTALLED_APPS
--------------------------------------------

To start using django-listable add `listable` to your INSTALLED_APPS::

    INSTALLED_APPS = (
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.sites',
        'django.contrib.messages',
        'django.contrib.staticfiles',
        'django.contrib.admin',
        'staff',
        'listable',
        ...
    )

Defining a Listable view
------------------------

To define a `listable` view, sublcass `listable.views.BaseListableView`
and set the model that is to be used as the source of data::

    from listable.views import BaseListableView, Column
    from models import Staff


    class StaffList(BaseListableView):

        model = models.Staff

        ...

Defining Columns for your view
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Every `listable` view must define one or more columns to be displayed in the table.
A `listable` column is defined using the `listable.views.Column` data structure.
A `Column` is essentially a namedtuple with the following fields (detailed descriptions below):

*field*
  The model field name for the column(this can also be a `virtual` field name described below)
*filtering*
  Defines whether the column should be filterable and how the ordering should be done
*widget*
  For filterable columns you have the option of using a text input or an html select input
*ordering*
  Defines whether the column should be orderable and how the ordering should be done
*header*
  Defines the column header to be displayed in the table

Each of these fields is defined in more detail below.

Column.field
............

A full example of a `listable` view is shown below::

    class StaffList(BaseListableView):

        model = models.Staff


        columns = (
            Column(
                field="id",
                ordering=False,
                filtering=False
            ),
            Column(field="first_name"),
            Column(field="name", ordering="last_name", widget=SELECT),
            Column(
                field="department",
                ordering="department__name",
                filtering="department__name",
                widget=SELECT,
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

Adding your view to your apps urls.py
-------------------------------------

stuff

Including the `listable` template tag in a template
---------------------------------------------------

more stuff

