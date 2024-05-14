window.initToolbar = function() {
    $('#proxies-toolbar').kendoToolBar({
        items: [
            {
                template: "<div class='k-window-title ps-6'>Proxies</div>",
            },
            {
                type: 'spacer',
            },
            {
                type: 'button',
                text: 'Refresh',
                click: function (e) {
                    $('#proxies-grid').data('kendoGrid').dataSource.read();
                },
            },
            {
                type: 'button',
                text: 'Clear Filter',
                click: function (e) {
                    $('#proxies-grid').data('kendoGrid').dataSource.filter({});
                },
            },
            {
                type: 'button',
                text: 'New Proxy',
                icon: 'plus',
                click: function (e) {
                    let grid = $('#proxies-grid').data('kendoGrid');
                    grid.addRow();
                },
            },
        ],
    });
}