import datetime
import json
import urllib

from django.core.exceptions import FieldError
from django.core.urlresolvers import resolve
from django.db.models import Q
from django.http import HttpResponse, Http404
from django.template import Context
from django.template.loader import get_template
from django.utils import formats
from django.utils.translation import ugettext as _
from django.views.generic import ListView

from . import utils
from . import settings as li_settings


DT_COOKIE_NAME = "SpryMedia_DataTables"
TEXT = "text"
SELECT = "select"


class BaseListableView(ListView):

    fields = ()
    widgets = {}
    order_fields = {}
    search_fields = {}
    headers = {}

    paginate_by = li_settings.LISTABLE_PAGINATE_BY

    select_related = ()
    prefetch_related = ()

    def get(self, request, *args, **kwargs):
        """
        return regular list view on page load and then json data on
        datatables ajax request.
        """

        if not self.request.is_ajax():
            return super(BaseListableView, self).get(request, *args, **kwargs)

        # below taken from Django list view code
        self.object_list = self.get_queryset()

        allow_empty = self.get_allow_empty()

        if not allow_empty:
            # When pagination is enabled and object_list is a queryset,
            # it's better to do a cheap query than to load the unpaginated
            # queryset in memory.
            if (self.get_paginate_by(self.object_list) is not None
                    and hasattr(self.object_list, 'exists')):
                is_empty = not self.object_list.exists()
            else:
                is_empty = len(self.object_list) == 0
            if is_empty:
                raise Http404(_("Empty list and '%(class_name)s.allow_empty' is False.").format(class_name=self.__class__.__name__))

        context = self.get_table_context_data(object_list=self.object_list)
        return HttpResponse(json.dumps(context), content_type='application/json')

    def get_table_context_data(self, **kwargs):
        """ Context data for datatables ajax request """
        self.set_page()

        context = super(BaseListableView, self).get_context_data(**kwargs)

        object_list = context["object_list"]

        try:
            secho = int(self.search_filters.get("sEcho"))
        except (TypeError, ValueError):
            secho = None

        context = {
            "aaData": self.get_rows(object_list),
            "iTotalRecords": super(BaseListableView, self).get_queryset().count(),
            "iTotalDisplayRecords": self.object_list.count(),
            "sEcho": secho,
        }
        return context

    def get_context_data(self, *args, **kwargs):
        """ Context data for full page request """
        context = super(BaseListableView, self).get_context_data(*args, **kwargs)
        template = get_template("listable/_table.html")

        # every table needs a unique ID to play well with sticky cookies
        current_url = resolve(self.request.path_info).url_name
        table_id = "listable-table-" + current_url

        headers = [self.get_header_for_field(f) for f in self.fields]
        context['listable_table'] = template.render(Context({'headers': headers, 'table_id': table_id}))

        return context

    def get_header_for_field(self, field):
        try:
            return self.headers[field]
        except KeyError:
            return field.replace("__", " ").replace("_", " ").title()

    def set_page(self):
        """ Set page requested by DataTables """
        offset = int(self.search_filters.get("iDisplayStart", 0))
        page_size = self.get_paginate_by(self.object_list)
        page_kwarg = getattr(self, "page_kwarg", "page")
        self.kwargs[page_kwarg] = offset / page_size + 1

    def get_paginate_by(self, queryset):
        """ Get page size requested by DataTables if available else default value"""
        return int(self.search_filters.get("iDisplayLength", self.paginate_by))

    def get_queryset(self):
        """ filter and order queryset based on DataTables parameters """
        qs = super(BaseListableView, self).get_queryset()
        self.extra = self.get_extra()
        if self.extra:
            qs = qs.extra(**self.extra)

        self.set_query_params()
        qs = self.filter_queryset(qs)
        qs = self.order_queryset(qs)

        if self.select_related:
            qs = qs.select_related(*self.select_related)

        if self.prefetch_related:
            qs = qs.prefetch_related(*self.prefetch_related)

        # FIXME: For some reason Django can choke when paginating a query
        # that has an extra clause on it (the count() call fails)
        # forcing evaluation of the  queryset with len(qs) here avoids that
        # but loads the whole dataset in memory :(
        if self.extra:
            len(qs)

        return qs

    def filter_queryset(self, qs):
        """ filter the input queryset according to column definitions.  """

        for col_num, field in enumerate(self.fields):

            search_term = self.search_filters.get("sSearch_%d" % col_num, None)
            filtering = self.search_fields.get(field, True)

            if filtering and search_term:
                if isinstance(filtering, basestring):
                    if 'select' in self.extra and field in self.extra['select']:
                        qs = qs.extra(where=["{0} LIKE %s".format(field)], params=["%{0}%".format(search_term)])
                    else:
                        qs = qs.filter(**{filtering: search_term})
                else:
                    try:
                        # iterable of search fields e.g. order_fields = {"name": ("first_name", "last_name",)}
                        queries = reduce(lambda q, f: q | Q(**{f: search_term}), filtering, Q())
                        qs = qs.filter(queries)

                    except TypeError:
                        # fall back to default search (e.g order_fields ={"first_name": True})
                        filtering = "{0}__icontains".format(field)
                        try:
                            qs = qs.filter(**{filtering: search_term})
                        except FieldError:
                            raise TypeError("You can not filter on the '{field}' field. Filtering on"
                                " GenericForeignKey's and callables must be explicitly disabled in `search_fields`".format(field=field))

        return qs

    def get_extra(self, qs):
        return None

    def order_queryset(self, qs):
        """
        Order the input queryset according to column ordering definitions.
        """

        n_orderings = int(self.search_filters.get("iSortingCols", 0))

        if n_orderings == 0:
            return qs

        # determine fields and direction to sort
        order_cols = []
        for x in range(n_orderings):
            col = int(self.search_filters.get("iSortCol_%d" % x))
            direction = "" if self.search_filters.get("sSortDir_%d" % x, "asc") == "asc" else "-"
            order_cols.append((col, direction))

        orderings = []
        for colnum, direction in order_cols:
            field = self.fields[colnum]
            ordering = self.order_fields.get(field, field)

            if ordering:

                if isinstance(ordering, basestring):
                    # eg ordering= 'first_name' or ordering = 'business__name'
                    orderings.append("%s%s" % (direction, ordering))
                else:
                    try:
                        #eg ordering=("last_name","first_name", )
                        for o in ordering:
                            orderings.append("%s%s" % (direction, o))
                    except TypeError:
                        # eg ordering = True
                        orderings.append("%s%s" % (direction, field))

        return qs.order_by(*orderings)

    def get_rows(self, objects):
        rows = []
        for obj in objects:
            rows.append([self.format_col(field, obj) for field in self.fields])
        return rows

    def format_col(self, field, obj):

        # first see if view subclass has a formatter defined
        formatter = getattr(self, field, None)
        if formatter:
            return formatter(obj) if callable(formatter) else formatter

        # fk property
        if "__" in field:
            return utils.lookup_dunder_prop(obj, field)

        try:
            return getattr(obj, 'get_{0}_display'.format(field))()
        except AttributeError:
            pass

        try:
            attr = getattr(obj, field)
        except AttributeError:
            raise AttributeError("'%s' is not a valid format specifier" % (field))

        if callable(attr):
            return attr()
        elif isinstance(attr, datetime.datetime):
            return formats.date_format(attr, "SHORT_DATETIME_FORMAT")
        elif isinstance(attr, datetime.date):
            return formats.date_format(attr, "SHORT_DATE_FORMAT")
        elif attr is None:
            return ""

        return str(attr)

    def set_query_params(self):
        """
        Create a search and order context, overridng any cookie values
        with request values.  This is required when "Sticky" DataTables filters
        are used.
        """

        self.search_filters = self.cookie_params()

        # overide any cookie parameters with GET parameters
        self.search_filters.update(self.request.GET.dict())

    def cookie_params(self):
        """return search and ordering parameters from DataTables cookie """

        params = {}

        dt_cookie_params = self.dt_cookie()
        if dt_cookie_params is None:
            return params

        # add search queries
        for idx, search in enumerate(dt_cookie_params["aoSearchCols"]):
            for k, v in search.items():
                params["%s_%d" % (k, idx)] = v

        # columns to sort on
        params["iSortingCols"] = 0  # tally of number of colums to sort on

        for idx, (col, dir_, _) in enumerate(dt_cookie_params["aaSorting"]):
            params["iSortCol_%d" % (idx)] = col
            params["sSortDir_%d" % (idx)] = dir_
            params["iSortingCols"] += 1

        params["iDisplayLength"] = dt_cookie_params["iLength"]
        params["iDisplayStart"] = dt_cookie_params["iStart"]
        params["iDisplayEnd"] = dt_cookie_params["iEnd"]

        return params

    def dt_cookie(self):
        """return raw data tables cookie as dict"""

        cookie_dt_params = None

        current_url = resolve(self.request.path_info).url_name
        cookie_name = "{0}_listable-table-{1}_".format(DT_COOKIE_NAME, current_url)
        for k, v in self.request.COOKIES.items():
            if k == cookie_name:
                cookie_dt_params = json.loads(urllib.unquote(v))

        return cookie_dt_params
