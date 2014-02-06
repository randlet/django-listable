$(Listable.tableId).dataTable({
    bSaveState:Listable.saveState,
    bPaginate: true,
    sPaginationType:Listable.paginationType,
    bProcessing: true,
    bServerSide: true,
    sAjaxSource: Listable.url,
    bAutoWidth: Listable.autoWidth,
    fnAdjustColumnSizing:true,
    aoColumnDefs:Listable.columnDefs,
    bFilter:true,
    sDom:Listable.DOM
}).columnFilter({
    sPlaceHolder: "head:after",
    aoColumns: Listable.columnFilterDefs,
    iFilteringDelay:250
});
