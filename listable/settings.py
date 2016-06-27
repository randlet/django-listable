from django.conf import settings

# bootstrap 2
# LISTABLE_DOM = getattr(settings, "LISTABLE_DOM", '<"row-fluid"<"span6"ir><"span6"p>>rt<"row-fluid"<"span12"lp>>')

#boostrap 3
LISTABLE_DOM = getattr(settings, "LISTABLE_DOM", '<"row"<"col-sm-6"i><"col-sm-6"rp>>rt<"row"<"col-sm-12"lp>>')

# pagination types -> bootstrap2, bootstrap3, two_button, full_numbers
LISTABLE_PAGINATION_TYPE = getattr(settings, "LISTABLE_PAGINATION_TYPE", "full_numbers")
LISTABLE_STATE_SAVE = getattr(settings, "LISTABLE_STATE_SAVE", True)
LISTABLE_PAGINATE_BY = getattr(settings, "LISTABLE_PAGINATE_BY", 10)
LISTABLE_LANGUAGE = getattr(settings, "LISTABLE_LANGUAGE", False)

DT_COOKIE_NAME = "SpryMedia_DataTables"

