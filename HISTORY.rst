.. :changelog:

=======
History
=======


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
