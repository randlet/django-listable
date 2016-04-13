$(Listable.tableId).addClass(
    Listable.cssTableClass
).dataTable({
    aaSorting:[],
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
    sDom:Listable.DOM,
    oLanguage: {sUrl: Listable.language},
}).columnFilter({
    sPlaceHolder: "head:after",
    aoColumns: Listable.columnFilterDefs,
    iFilteringDelay:250
}).find("input, select").addClass(
    Listable.cssInputClass
);
