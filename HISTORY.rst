.. :changelog:

=======
History
=======

0.9.0 (2025-03-28)
------------------

* Django 5 compatability

0.8.10 (2024-09-20)
-------------------

* Fixed XSS issues and filtering items with quotes

0.8.8 (2024-09-11)
------------------

* Improved page performance by reducing `queryset.count()` calls.

* Added ``get_{field}_choices`` to allow for custom select and multi-select dropdown choices.

0.8.7 (2024-09-06)
------------------

* Allow specifying ``nulls_first`` and ``nulls_last`` behaviour in the ``order_fields`` options. For
  example:

  .. code-block:: python

    class SomeListableView(BaseListableView):
        order_fields = {
            "some_field":  {
                "desc": {"nulls_last": True},
                "asc": {"nulls_fist": True},
            }
        }

0.8.6 (2024-08-22)
------------------

* Fix issue with filters containing Unicode characters that contain surrogate pairs

0.8.5 (2024-07-03)
------------------

* Fix issue with filters containing Unicode characters

0.8.3 (2024-07-03)
------------------

* Add support for "Live Filters".

0.8.2 (2023-12-22)
------------------

* Django 4.x compatibility


0.8.1 (2023-05-25)
------------------

* In order to allow ``|`` characters in searches, the search term separator for
  multi selects has been updated to use ```|``` which is a 3 character sequence
  unlikely to apply in normal searches.

0.8.0 (2023-04-18)
------------------

* Added a loose_text_search setting to views.  Set ``loose_text_search = True``
  on your view to enable partial matching in your text searches. For example
  "Fo Ba" will match "Foo Bar".

0.7.0 (2023-02-24)
------------------

* Listable for Django 3.2

0.6.0 (2021-10-07)
------------------

* Add field names to column headers as data attributes
* Add columnSearch to Listable context object

0.5.2 (2021-08-20)
------------------

* Fix issue with encoding of search filters

0.5.1 (2021-06-15)
------------------

* wrap datatables css/scripts in function so static is not called at import



0.5.0 (2021-02-03)
------------------
* Fixed a same site cookie issue
* Fixed a bug where select dropdowns were being truncated by bottom of page
* Added a get_fields method to set fields dynamically
* Fix an issue with incorrect timezones
* Add support for Django 2-


0.4.3 (2017-05-11)
------------------
Fix values_to_dt to allow unicode

0.4.1 (2016-10-14)
------------------
Add fix for when using FORCE_SCRIPT_NAME setting

0.4.0 (2016-10-02)
------------------
Update to support Django 1.8-1.10 and Python 2.7-3.5

0.3.10 (2016-11-08)
-------------------
Cast search term to lower case if case insensitive search requested to allow
easier filtering with extra queries.

0.3.9 (2016-09-27)
------------------
Fix formatting bug introduced by 0.3.8

0.3.8 (2016-09-27)
------------------
Fix unicode encoding error

0.3.7 (2016-08-25)
------------------
Add date range picker

0.3.6 (2016-06-29)
------------------
Add multi select and date select widgets (thanks to @ryanbottema)

0.3.5 (2016-06-22)
------------------
Fix filtering and count queries for django-mssql

0.3.3 (2015-04-12)
------------------
* Fix filtering of None values for SELECT fields

0.3.1 (2015-02-25)
------------------
* Fix issue with boolean field filtering

0.2.10 (2014-12-16)
-------------------
* Fix issue with pagination type

0.2.9 (2014-12-15)
------------------
* Fix issue with namespaced urls

0.2.6 (2014-10-30)
------------------
* add view args & kwargs to context to allow full reverse

0.2.5 (2014-10-30)
------------------
* fix order_by

0.2.0 (2014-10-29)
------------------
* Complete overhaul of api

0.1.2 (2014-07-09)
------------------
* Fix saveState bug

0.1.0 (2013-08-15)
------------------

* First release on PyPI.
