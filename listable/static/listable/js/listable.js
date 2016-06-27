
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
}).find("input, select").addClass(
    Listable.cssInputClass
);

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
                        buttonWidth: '100px',
                        numberDisplayed: 1,
                        nonSelectedText: '------'
                    });
            } else {
                $(select).attr('multiple', false).multiselect({
                    buttonWidth: '100px'
                });
            }
            $(select).multiselect();
        } else if (Listable.columnFilterDefs[col].type == 'date') {
            var c = parseInt(col) + 1;
            var date = $("thead > tr > th:nth-child(" + c + ") input");
            $(date).hide().val('').trigger('keyup');
            var dateGroup = $("<div id=date-group-" + col + " class='btn-group' style='width: 70px;'></div>").insertAfter(date);
            var fromGroup = $('<span id="from-' + col + '" class="input-group from"><input type="text" class="form-control from" style="display:none;"><span class="input-group-addon btn btn-sm" style="font-size: 12px; padding: 4px 6px;">From</span> </span>');
            var toGroup = $('<span id="to-' + col + '" class="input-group to"><input type="text" class="form-control to" style="display:none;"><span class="input-group-addon btn btn-sm" style="font-size: 12px; padding: 4px 6px;">To</span> </span>');

            //var from = $("<input type='text' class='datepicker from'>");
            //var to = $("<input type='text' class='datepicker to'>");
            $(fromGroup).appendTo(dateGroup).datepicker({
                showOn: 'button',
                orientation: 'bottom left',
                format: 'yyyy-mm-dd',
                autoclose: true,
                endDate: '0d'
            }).on('changeDate', function(x) {
                var date = $(this).parent().parent().children('input:not(".from"):not(".to")');
                console.log($(date));
                var currDate = $(date).val();
                var newFrom = x.format();
                $(this).children("span.btn").html("<i class='icon-check'></i>");
                if (currDate != '' && currDate.charAt(0) == '*') {
                    var sub = currDate.substring(0, 4);
                    var currTo = '';
                    if (sub == '*f-*') {
                        currDate = '*f-*' + newFrom;
                    } else if (sub == '*ft*') {
                        currTo = currDate.substring(15, 25);
                        currDate = '*ft*' + newFrom + '|' + currTo;
                    } else if (sub == '*-t*') {
                        currTo = currDate.substring(5, 15);
                        currDate = '*ft*' + newFrom + '|' + currTo;
                    } else {
                        console.log('ErRor');
                    }
                } else {
                    currDate = '*f-*' + newFrom;
                }
                $(date).val(currDate).trigger('keyup');
                $(this).parent().children(".input-group.to").data('datepicker').setStartDate(newFrom);
            });
            $(toGroup).appendTo(dateGroup).datepicker({
                showOn: 'button',
                orientation: 'bottom left',
                format: 'yyyy-mm-dd',
                autoclose: true,
                endDate: '0d'
            }).on('changeDate', function(x) {
                var date = $(this).parent().parent().children('input:not(".from"):not(".to")');
                var currDate = $(date).val();
                var newTo = x.format();
                $(this).children("span.btn").html("<i class='icon-check'></i>");
                if (currDate != '' && currDate.charAt(0) == '*') {
                    var sub = currDate.substring(0, 4);
                    var currFrom = '';
                    if (sub == '*f-*') {
                        currFrom = currDate.substring(4, 14);
                        currDate = '*ft*' + currFrom + '|' + newTo;
                    } else if (sub == '*ft*') {
                        currFrom = currDate.substring(4, 14);
                        currDate = '*ft*' + currFrom + '|' + newTo;
                    } else if (sub == '*-t*') {
                        currDate = '*-t*|' + newTo;
                    } else {
                        console.log('ErRor');
                    }
                } else {
                    currDate = '*-t*|' + newTo;
                }
                $(date).val(currDate).trigger('keyup');
                $(this).parent().children(".input-group.from").data('datepicker').setEndDate(newTo);
            });
        }
    }
}
