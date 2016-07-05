
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '' && name) {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

var table = $(Listable.tableId).addClass(
    Listable.cssTableClass
).dataTable({
    //aaSorting:[],
    bStateSave:Listable.stateSave,
    bPaginate: true,
    sPaginationType:Listable.paginationType,
    iDisplayLength: Listable.displayLength,
    bProcessing: true,
    bServerSide: true,
    sAjaxSource: Listable.url,
    bAutoWidth: Listable.autoWidth,
    aoColumns:Listable.columnDefs,
    aaSorting:Listable.order,
    bFilter:true,
    sDom:Listable.DOM
}).columnFilter({
    sPlaceHolder: "head:after",
    aoColumns: Listable.columnFilterDefs,
    iFilteringDelay:250
});

var cookie_obj = JSON.parse(window.getCookie(Listable.cookie));

if (cookie_obj) {
    for (var i in cookie_obj.aoSearchCols) {
        var searcher = cookie_obj.aoSearchCols[i].sSearch;
        if (searcher.charAt(0) == '^') {
            searcher = searcher.replace('^(', '').replace(')$', '');
            if (searcher != '.*') {
                var c = parseInt(i) + 1;
                var searchers = searcher.split('|');
                var select = $("thead > tr > th:nth-child(" + c + ") select");
                for (var j in searchers) {
                    var option = $(select).children("option[value='" + searchers[j] + "']");
                    $(option).attr('selected', 'selected');
                }
            }
        }
    }
}

$("option.search_init").text('-----');

for (var col in Listable.columnFilterDefs) {
    if (Listable.columnFilterDefs[col]) {
        if (Listable.columnFilterDefs[col].type == 'select') {
            var c = parseInt(col) + 1;
            var select = $("thead > tr > th:nth-child(" + c + ") select");
            if (Listable.columnFilterDefs[col].multiple) {
                $(select)
                    .attr('multiple', 'multiple')
                    .multiselect({
                        includeSelectAllOption: true,
                        buttonWidth: '125px',
                        numberDisplayed: 1,
                        nonSelectedText: '------'
                    });
            } else {
                $(select).attr('multiple', false).multiselect({
                    buttonWidth: '125px'
                });
            }
            $(select).multiselect();

        } else if (Listable.columnFilterDefs[col].type == 'date') {
            var c = parseInt(col) + 1;
            var date = $("thead > tr > th:nth-child(" + c + ") input");

            $(date).datepicker({
                orientation: 'bottom left',
                format: 'dd M yyyy',
                autoclose: true,
                clearBtn: true,
                toggleActive: true,

            }).on('changeDate', function(x) {
                $(this).trigger('keyup');
            });
        }
    }
}

$(table).find("input, select, button").addClass(
    Listable.cssInputClass
);
