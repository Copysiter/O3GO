window.initToolbar = function() {
    $('#analytics-toolbar').kendoToolBar({
        items: [
            {
                template: "<div class='k-window-title ps-6'>Analytics</div>",
            },
            { type: 'spacer' },
            {
                type: 'button',
                text: 'Refresh',
                click: function () {
                    $('#analytics-grid').data('kendoGrid').dataSource.read();
                },
            },
            {
                type: 'button',
                text: 'Clear Filter',
                click: function () {
                    $('#analytics-grid').data('kendoGrid').dataSource.filter({});
                },
            },
        ],
    });
}
