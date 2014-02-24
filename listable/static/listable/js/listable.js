$(Listable.tableId).addClass(
    Listable.cssTableClass
).dataTable({
    bStateSave:Listable.stateSave,
    bPaginate: true,
    sPaginationType:Listable.paginationType,
    bProcessing: true,
    bServerSide: true,
    bStateSave: Listable.saveState,
    sAjaxSource: Listable.url,
    bAutoWidth: Listable.autoWidth,
    fnAdjustColumnSizing:true,
    aoColumns:Listable.columnDefs,
    bFilter:true,
    sDom:Listable.DOM
}).columnFilter({
    sPlaceHolder: "head:after",
    aoColumns: Listable.columnFilterDefs,
    iFilteringDelay:250
}).find("input, select").addClass(
    Listable.cssInputClass
);
