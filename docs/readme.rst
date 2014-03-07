=============================
django-listable Readme
=============================

Listable is a Django package to make the integration of your Django
models with `Datatables.js <https://datatables.net/>`_ easy.

Django-listable was motivated by my repeated need to generate sortable
and filterable tables from my Django models for CRUD apps.

The idea is that you should easily be able to go from a model like this::

    class Staff(models.Model):

        first_name = models.CharField(max_length=255, help_text=_("Enter the name of the staff being rounded"))
        last_name = models.CharField(max_length=255, help_text=_("Enter the name of the staff being rounded"))
        active = models.CharField(max_length=10, choices = ACTIVE_CHOICES)

        position = models.ForeignKey(Position)
        department = models.ForeignKey(Department)

        limit = models.Q(app_label='staff', model='genericmodela') | models.Q(app_label='staff', model='genericmodelb')
        content_type = models.ForeignKey(ContentType, limit_choices_to=limit)
        object_id = models.PositiveIntegerField()
        generic_object = generic.GenericForeignKey("content_type", "object_id")

to a filterable/orderable table in a template like this with as little code as possible:

.. image:: _static/staff_table.png

There are a couple of other similar projects worth checking out to see if they fit your
needs better:

- `django-datatables-view <https://pypi.python.org/pypi/django-datatables-view>`_
- `django-datatables <https://pypi.python.org/pypi/django-datatables>`_
- `django-eztables <https://github.com/noirbizarre/django-eztables>`_



.. image:: https://badge.fury.io/py/djangoeasytables.png
    :target: http://badge.fury.io/py/djangolistable

.. https://travis-ci.org/randlet/djangolistable.png?branch=master
        :target: https://travis-ci.org/randlet/django-listable

.. image:: https://pypip.in/d/djangoeasytables/badge.png
        :target: https://crate.io/packages/django-listable?version=latest


.. A reusable Django app to make integrations with the DataTables javascript library easy.

.. Documentation
.. -------------
..
.. The full documentation is at http://djangolistable.rtfd.org.
..
.. Quickstart
.. ----------
..
.. Install django-listable::
..
..     pip install django-listable
..
.. Then use it in a project::
..
.. 	import listable
..
.. Features
.. --------
..
.. * TODO
