from django.conf import settings

LISTABLE_DOM =  getattr(settings, "LISTABLE_DOM", '<"row"<"col-sm-6"i><"col-sm-6"rp>>rt<"row"<"col-sm-12"lp>>')
LISTABLE_PAGINATION_TYPE = getattr(settings, "LISTABLE_PAGINATION_TYPE", "bootstrap")
LISTABLE_STATE_SAVE = getattr(settings, "LISTABLE_STATE_SAVE", True)
LISTABLE_PAGINATE_BY = getattr(settings, "LISTABLE_PAGINATE_BY", 10)

