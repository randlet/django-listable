import datetime
from functools import reduce
import json
from urllib.parse import unquote

from django.db.models import Q
import django.db.models.fields
from django.http import Http404, HttpResponse
from django.template.loader import get_template
from django.urls import resolve
from django.utils import formats, timezone
from django.utils.translation import ugettext as _
from django.views.generic import ListView
import six

from . import settings as li_settings
from . import utils

d_version = django.get_version().split('.')
d_version_old = d_version[0] == '1' and int(d_version[1]) < 8
if d_version_old:
    from django.template import Context

basestring = (str, bytes)


TEXT = "text"
SELECT = "select"
SELECT_MULTI = "selectmulti"
DATE = "date"
DATE_RANGE = "daterange"
SELECT_MULTI_FROM_MULTI = "selectmultifrommulti"

TODAY = "Today"
YESTERDAY = "Yesterday"
TOMORROW = "Tomorrow"
LAST_7_DAYS = "Last 7 Days"
LAST_14_DAYS = "Last 14 Days"
LAST_30_DAYS = "Last 30 Days"
LAST_365_DAYS = "Last 365 Days"
THIS_WEEK = "This Week"
THIS_MONTH = "This Month"
THIS_QUARTER = "This Quarter"
THIS_YEAR = "This Year"
LAST_WEEK = "Last Week"
LAST_MONTH = "Last Month"
LAST_QUARTER = "Last Quarter"
LAST_YEAR = "Last Year"
WEEK_TO_DATE = "Week To Date"
MONTH_TO_DATE = "Month To Date"
QUARTER_TO_DATE = "Quarter To Date"
YEAR_TO_DATE = "Year To Date"
NEXT_WEEK = "Next Week"
NEXT_MONTH = "Next Month"
NEXT_QUARTER = "Next Quarter"
NEXT_YEAR = "Next Year"

NONEORNULL = 'noneornull'


class BaseListableView(ListView):

    fields = ()
    widgets = {}
    order_fields = {}
    search_fields = {}
    headers = {}

    multi_separator = ', '

    paginate_by = li_settings.LISTABLE_PAGINATE_BY
    filter_delay = li_settings.LISTABLE_FILTER_DELAY

    select_related = ()
    prefetch_related = ()

    order_by = ()

    defer = True

    def __init__(self, *args, **kwargs):

        super(BaseListableView, self).__init__(**kwargs)

    def get(self, request, *args, **kwargs):
        """
        return regular list view on page load and then json data on
        datatables ajax request.
        """

        for field in self.get_fields(request=request):
            if field not in self.widgets:
                if field in self.search_fields and not self.search_fields[field]:
                    self.widgets[field] = None
                else:
                    self.widgets[field] = TEXT

        self.search_filters = {}

        # below adapted from Django list view code
        self.object_list = self.get_queryset()

        if not self.request.is_ajax():
            return super(BaseListableView, self).get(request, *args, **kwargs)

        self.set_query_params()

        self.extra = self.get_extra()
        if self.extra:
            self.object_list = self.object_list.extra(**self.extra)

        self.object_list = self.filter_queryset(self.object_list)
        self.object_list = self.order_queryset(self.object_list)

        if self.select_related:
            self.object_list = self.object_list.select_related(*self.select_related)

        if self.prefetch_related:
            self.object_list = self.object_list.prefetch_related(*self.prefetch_related)

        # Some Django backends can choke when paginating a query
        # that has an extra clause on it (the count() call fails)
        # so we can patch on our own count function that first tries the
        # native count method and then falls back on a query that uses a single
        # db call and if all else fails just iterate the queryset and count it.
        # Not ideal but it seems to work.
        if self.extra:
            orig_count = self.object_list.count

            def count():
                try:
                    # works ok on mssql
                    return orig_count()
                except:
                    try:
                        from django.db import connection
                        cursor = connection.cursor()
                        sql, params = self.object_list.query.sql_with_params()
                        count_sql = "SELECT COUNT(*) FROM ({0})".format(sql)
                        cursor.execute(count_sql, params)
                        return cursor.fetchone()[0]
                    except:
                        # fall back to iterating and counting :(
                        return len(_ for x in self.object_list.values_list("pk"))
            self.object_list.count = count

        allow_empty = self.get_allow_empty()

        if not allow_empty:
            # When pagination is enabled and object_list is a queryset,
            # it's better to do a cheap query than to load the unpaginated
            # queryset in memory.
            if (self.get_paginate_by(self.object_list) is not None and
                    hasattr(self.object_list, 'exists')):
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
            "iTotalRecords": self.get_queryset().count(),
            "iTotalDisplayRecords": self.object_list.count(),
            "sEcho": secho,
        }
        return context

    def get_table_id(self):

        # every table needs a unique ID to play well with sticky cookies
        resolve_match = resolve(self.request.path_info)
        current_url = resolve_match.url_name
        if resolve_match.namespace:
            current_url = "{0}_{1}".format(resolve_match.namespace, current_url)

        table_id = ("listable-table-" + current_url)

        return table_id

    def get_context_data(self, *args, **kwargs):
        """ Context data for full page request """
        context = super(BaseListableView, self).get_context_data(*args, **kwargs)
        template = get_template("listable/_table.html")

        headers = [self.get_header_for_field(f) for f in self.get_fields(request=self.request)]
        table_context = {
            'headers': headers,
            'table_id': self.get_table_id().replace(":", "_").replace(".", "_"),
            'request': self.request,
        }
        if d_version_old:
            table_context = Context(table_context)

        context['listable_table'] = template.render(table_context)
        context['args'] = self.args
        context['kwargs'] = self.kwargs

        return context

    def get_fields(self, request=None):
        return self.fields

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

    qs_count = 0

    # def get_queryset(self):
    #     """ filter and order queryset based on DataTables parameters """
    #
    #     # wer're not displaying anything on page load
    #     # if self.defer and not self.request.is_ajax():
    #     #     return self.model.objects.none()
    #     self.qs_count += 1
    #     print self.qs_count
    #
    #     qs = super(BaseListableView, self).get_queryset()
    #
    #     return qs

    def get_filters(self, field, queryset=None):
        """Populates options for SELECT and SELECT_MULTI filters based on values in the initial queryset"""

        if not queryset or len(queryset) == 0:
            queryset = self.get_queryset()

        if self.get_extra() and 'select' in self.get_extra() and field in self.get_extra()['select']:
            queryset = queryset.extra(select=self.get_extra()['select'])

        ordering = self.order_fields.get(field, field)
        if ordering in (False, True, None):
            ordering = field
        filters = [
            f if f != (None, None) else (NONEORNULL, 'None')
            for f in queryset.values_list(field, field).order_by(ordering)
        ]

        return filters

    def filter_queryset(self, qs):
        """ filter the input queryset according to column definitions.

        This method is awful :(
        """

        cur_tz = timezone.get_current_timezone()

        for col_num, field in enumerate(self.get_fields(request=self.request)):

            search_term = self.search_filters.get("sSearch_%d" % col_num, None)
            filtering = self.search_fields.get(field, True)
            widget = self.widgets[field]

            # would like to use __regex here, but mssql doesn't come standard with __regex functionaliy
            # instead of installing regex_clr, some logic is used
            if widget is None:
                continue

            if search_term:
                if widget == SELECT:
                    search_term = [unquote(search_term).replace('\\', '')]

                elif widget in [SELECT_MULTI, SELECT_MULTI_FROM_MULTI]:
                    if search_term in ['^(.*)$', '^()$']:
                        search_term = ''
                    else:
                        search_term = unquote(search_term[2:-2]).replace('\\', '').split('|')

                elif widget == DATE_RANGE:
                    start = datetime.datetime.strptime(search_term.split(' - ')[0], '%d %b %Y').replace(hour=0, minute=0, second=0)
                    end = datetime.datetime.strptime(search_term.split(' - ')[1], '%d %b %Y').replace(hour=23, minute=59, second=59)
                    start = cur_tz.localize(start)
                    end = cur_tz.localize(end)
                    search_term = (start, end)

                elif widget == DATE:
                    try:
                        start = datetime.datetime.strptime(search_term.split('-')[0], '%a %b %d %Y %H:%M:%S %Z').replace(hour=0, minute=0, second=0)
                        end = datetime.datetime.strptime(search_term.split('-')[0], '%a %b %d %Y %H:%M:%S %Z').replace(hour=23, minute=59, second=59)
                        start = cur_tz.localize(start)
                        end = cur_tz.localize(end)
                        search_term = (start, end)
                    except ValueError:
                        start = datetime.datetime.strptime(search_term, '%d %b %Y').replace(hour=0, minute=0, second=0)
                        end = datetime.datetime.strptime(search_term, '%d %b %Y').replace(hour=23, minute=59, second=59)
                        start = cur_tz.localize(start)
                        end = cur_tz.localize(end)
                        search_term = (start, end)

            has_none = False

            if filtering and search_term:

                if isinstance(filtering, bool):
                    filtering = field

                if isinstance(filtering, basestring):

                    if '__icontains' in filtering:
                        search_term = search_term.lower()

                    if self.get_extra() and 'select' in self.get_extra() and field in self.get_extra()['select']:

                        if widget in [DATE, DATE_RANGE, SELECT_MULTI_FROM_MULTI]:
                            raise ValueError('%s widget not configurable with extra query' % widget)

                        if widget == TEXT:
                            qs = qs.extra(where=["{0} LIKE %s".format(self.extra['select'][field])], params=["%{0}%".format(search_term)])

                        elif widget in [SELECT, SELECT_MULTI]:

                            search_term_string = "("
                            for st in search_term:
                                search_term_string = search_term_string + "'" + st + "',"
                            search_term_string = search_term_string[:-1] + ")"

                            qs = qs.extra(where=["{0} IN {1}".format(self.extra['select'][field], search_term_string)])

                    else:

                        if widget in [SELECT, SELECT_MULTI, SELECT_MULTI_FROM_MULTI]:
                            has_none = True if NONEORNULL in search_term else False
                            filtering = '{0}__in'.format(filtering)

                        elif widget == TEXT:
                            filtering = '{0}__icontains'.format(filtering)

                        elif widget in [DATE, DATE_RANGE]:
                            filtering = '{0}__range'.format(filtering)

                        if has_none:
                            qs = qs.filter(Q(**{"{0}__isnull".format(field): True}) | Q(**{filtering: search_term})).distinct()
                        else:
                            qs = qs.filter(**{filtering: search_term}).distinct()

                else:

                    if self.get_extra() and 'select' in self.get_extra() and field in self.get_extra()['select']:
                        raise ValueError('Multiple filters on field not configurable with extra.')

                    if widget in [SELECT, SELECT_MULTI]:
                        filterings = ()
                        for i in range(len(filtering)):
                            filterings = filterings + ('{0}__in'.format(filtering[i]),)
                        queries = reduce(lambda q, f: q | Q(**{f: search_term}), filterings, Q())
                        qs = qs.filter(queries)

                    elif widget == TEXT:
                        queries = reduce(lambda q, f: q | Q(**{f: search_term}), filtering, Q())
                        qs = qs.filter(queries)

                    elif widget in [DATE, DATE_RANGE, SELECT_MULTI_FROM_MULTI]:
                        raise ValueError('%s widget not configurable for multiple filters.' % widget)

        return qs

    def get_extra(self):
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
        fields = self.get_fields(request=self.request)
        for colnum, direction in order_cols:
            field = fields[colnum]
            ordering = self.order_fields.get(field, field)

            if ordering:

                if isinstance(ordering, basestring):
                    # eg ordering= 'first_name' or ordering = 'business__name'
                    orderings.append("%s%s" % (direction, ordering))
                else:
                    try:
                        # eg ordering=("last_name","first_name", )
                        for o in ordering:
                            orderings.append("%s%s" % (direction, o))
                    except TypeError:
                        # eg ordering = True
                        orderings.append("%s%s" % (direction, field))

        return qs.order_by(*orderings)

    def get_rows(self, objects):
        rows = []
        fields = self.get_fields(request=self.request)
        for obj in objects:
            rows.append([self.format_col(field, obj) for field in fields])
        return rows

    def format_col(self, field, obj):

        is_multi = self.widgets[field] == SELECT_MULTI_FROM_MULTI

        # first see if view subclass has a formatter defined
        formatter = getattr(self, field, None)
        if formatter:
            return formatter(obj) if callable(formatter) else formatter

        # fk property
        if "__" in field:
            if is_multi:
                return self.multi_separator.join(utils.lookup_dunder_prop(obj, field, multi=True))
            return utils.lookup_dunder_prop(obj, field)
        elif is_multi:
            raise AttributeError("Must specify field to display for many to many field (ie: %s__id)" % field)

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
        elif isinstance(attr, six.string_types):
            attr.encode("UTF-8")
        elif attr is None:
            return ""

        return "%s" % attr

    def set_query_params(self):
        """
        Create a search and order context, overridng any cookie values
        with request values.  This is required when "Sticky" DataTables filters
        are used.
        """

        self.search_filters.update(self.cookie_params())

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

        for idx, (col, dir_, __) in enumerate(dt_cookie_params["aaSorting"]):
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
        cookie_name = li_settings.cookie_name(self.request, current_url)
        for k, v in self.request.COOKIES.items():
            if k == cookie_name and v:
                cookie_dt_params = json.loads(unquote(v))

        return cookie_dt_params
