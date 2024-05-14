window.initToolbar = function() {
    $('#report-toolbar').kendoToolBar({
        items: [
            {
                template: "<div class='k-window-title ps-6'>Report</div>",
            },
            {
                type: 'spacer',
            },
            {
                type: 'button',
                text: 'Refresh',
                click: function (e) {
                    $('#report-grid').data('kendoGrid').dataSource.read();
                },
            },
            {
                type: 'button',
                text: 'Clear Filter',
                click: function (e) {
                    $('#report-grid').data('kendoGrid').dataSource.filter({});
                },
            },
        ],
    });
}