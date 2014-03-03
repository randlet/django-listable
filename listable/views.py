import datetime
import json
import urllib

from collections import namedtuple

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from django.db.models.loading import get_model
from django.http import HttpResponse
from django.template import Context
from django.template.loader import get_template
from django.utils import formats
from django.views.generic import ListView

from . import utils
from . import settings as li_settings


DT_COOKIE_NAME = "SpryMedia_DataTables"
TEXT = "text"
SELECT = "select"

class Column(namedtuple('Column', ['field', 'filtering','widget', 'ordering', 'header'])):
    """ Named tuple with default args. See http://stackoverflow.com/a/16721002/79802 """

    def __new__(cls, field, filtering=None, widget=TEXT, ordering=True, header=None):
        return super(Column, cls).__new__(cls, field, filtering, widget, ordering, header)


class BaseListableView(ListView):

    columns = ()
    paginate_by = li_settings.LISTABLE_PAGINATE_BY

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
                raise Http404(_("Empty list and '%(class_name)s.allow_empty' is False.")
                        % {'class_name': self.__class__.__name__})

        context = self.get_table_context_data()
        return HttpResponse(json.dumps(context), content_type='application/json')


    def get_table_context_data(self):
        """ Context data for datatables ajax request """
        self.set_page()

        context = super(BaseListableView, self).get_context_data()

        object_list = context["object_list"]

        context = {
            "aaData": self.get_rows(object_list),
            "iTotalRecords": super(BaseListableView, self).get_queryset().count(),
            "iTotalDisplayRecords": self.object_list.count(),
            "sEcho": int(self.search_filters.get("sEcho")),
        }
        return context

    def get_context_data(self, *args, **kwargs):
        """ Context data for full page request """
        context = super(BaseListableView, self).get_context_data(*args, **kwargs)
        template = get_template("listable/_table.html")
        context['listable_table'] = template.render(Context({'columns':self.columns,}))
        context['columns'] = self.columns
        return context

    def set_page(self):
        """ Set page requested by DataTables """
        offset = int(self.search_filters.get("iDisplayStart", 0))
        page_size = self.get_paginate_by(self.object_list)
        self.kwargs[self.page_kwarg] = offset/page_size + 1

    def get_paginate_by(self, queryset):
        """ Get page size requested by DataTables if available else default value"""
        return int(self.search_filters.get("iDisplayLength", self.paginate_by))

    def get_queryset(self):
        """ filter and order queryset based on DataTables parameters """
        qs = super(BaseListableView, self).get_queryset()
        self.set_query_params()
        qs = self.filter_queryset(qs)
        qs = self.order_queryset(qs)
        return qs

    def filter_queryset(self, qs):
        """ filter the input queryset according to column definitions.  """

        filter_queries = []

        for col_num, column in enumerate(self.columns):

            search_term = self.search_filters.get("sSearch_%d" % col_num, None)

            if column.filtering and search_term:

                if isinstance(column.filtering, basestring) and column.widget == SELECT:
                    if "__" in column.filtering:
                        # foreign key select widget (select by pk)
                        model = utils.column_filter_model(column)
                        qs = qs.filter(Q(**{model: search_term}))
                    else:
                        # local field select widget
                        qs = qs.filter(Q(**{column.filtering: search_term}))

                elif isinstance(column.filtering, basestring):
                    filtering = "%s__icontains" % (column.filtering,)
                    qs = qs.filter(Q(**{filtering: search_term}))
                else:
                    try:
                        #handle case where we are filtering on a Generic Foreign Key field
                        f = Q()
                        for ct, s in column.filtering:
                            model = get_model(*ct.split('.'))
                            ctype = ContentType.objects.get_for_model(model)
                            f |= Q(**{"%s__%s__icontains"%(ctype.model,s):search_term, "content_type": ct})
                        qs = qs.filter(f)
                    except TypeError:
                        filtering = "%s__icontains" % (column.field,)
                        qs = qs.filter(Q(**{filtering: search_term}))

        return qs

    def order_queryset(self, qs):
        """
        Order the input queryset according to column definitions.

        Column ordering definitions can either be a truthy/falsy value, a
        single string or an iterable of strings.  Orderings are in the
        same form as Django model orderings.

        For example:
            Column(field="id", ordering=True/False, ...) <-- Set to False to disable ordering
            Column(field="name", ordering=("last_name", "first_name", ), ...)
            Column(field="last_name", ordering="last_name", ...)
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
            col = self.columns[colnum]

            if col.ordering:

                if isinstance(col.ordering, basestring):
                    #eg Column(field="id", ordering="last_name",, ...)
                    orderings.append("%s%s" % (direction, col.ordering))
                else:
                    try:
                        #eg Column(field="id", ordering=("last_name","first_name", ), ...)
                        for o in col.ordering:
                            orderings.append("%s%s" % (direction, o))
                    except:
                        if col.ordering:
                            #eg Column(field="id", ordering=True, ...)
                            orderings.append("%s%s" % (direction, col.field))

        return qs.order_by(*orderings)

    def get_rows(self, objects):
        rows = []
        for obj in objects:
            rows.append([self.format_col(col.field, obj) for col in self.columns])
        return rows

    def format_col(self, field, obj):

        # first see if subclass has a formatter defined
        formatter = getattr(self,field, None)
        if formatter:
            return formatter(obj) if callable(formatter) else formatter


        # then look on object itself
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
        params["iSortingCols"] = 0  #  tally of number of colums to sort on

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

        for k, v in self.request.COOKIES.items():
            if k.startswith(DT_COOKIE_NAME):
                cookie_dt_params = json.loads(urllib.unquote(v))

        return cookie_dt_params


