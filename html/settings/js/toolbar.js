window.initToolbar = function() {
    let token = window.isAuth;
    try {
        let { access_token, token_type } = token;

        $('#settings-toolbar').kendoToolBar({
            items: [
                {
                    template: "<div class='k-window-title ps-6'>Variables</div>",
                },
                {
                    type: 'spacer',
                },
                {
                    type: 'button',
                    text: 'Refresh',
                    click: function (e) {
                        $('#settings-grid').data('kendoGrid').dataSource.read();
                    },
                },
                {
                    type: 'button',
                    text: 'Clear Filter',
                    click: function (e) {
                        $('#settings-grid').data('kendoGrid').dataSource.filter({});
                    },
                },
                {
                    type: 'button',
                    text: 'New Variable',
                    icon: 'plus',
                    click: function (e) {
                        let grid = $('#settings-grid').data('kendoGrid');
                        grid.addRow();
                    },
                },
            ],
        });

        $('#setting-groups-toolbar').kendoToolBar({
            items: [
                {
                    template: "<div class='k-window-title ps-6'>Setting Groups</div>",
                },
                {
                    type: 'spacer',
                },
                {
                    type: 'button',
                    id: 'enable',
                    text: 'Enable',
                    icon: 'checkbox-checked',
                    hidden: true,
                    attributes: { 'class': 'k-button-solid-success' },
                    click: function (e) {
                        // $('#setting-groups-grid').data('kendoGrid').dataSource.read();
                        let grid = $('#setting-groups-grid').data('kendoGrid');
                        let rows = grid.select();
                        let ids = []
                        for (let i = 0; i < rows.length; i++) {
                            let dataItem = grid.dataItem($(rows[i]));
                            dataItem.is_activae = true;
                            ids.push(dataItem.id);
                        }
                        kendo.confirm("<div style='padding:5px 10px 0 10px;'>Are you sure you want to enable setting groups?</div>").done(function() {
                            $.ajax({
                                url: `http://${api_base_url}/api/v1/setting_groups/status`,
                                type: "PUT",
                                data: JSON.stringify({ ids: ids, is_active: true}),
                                processData: false,
                                ContentType: 'application/json',
                                headers: {
                                    'Content-Type': 'application/json; odata=verbose',
                                    'Authorization': `${token_type} ${access_token}`
                                },
                                success: function(data) {

                                },
                                error: function(jqXHR, textStatus, ex) {

                                }
                            }).then(function(data) {
                                if (!data.error) {
                                    grid.dataSource.read();
                                    grid.clearSelection();
                                    e.sender.hide($('#delete'));
                                }
                            });
                        }).fail(function() {

                        });
                    },
                },
                {
                    type: 'button',
                    id: 'disable',
                    text: 'Disable',
                    icon: 'checkbox-null',
                    hidden: true,
                    attributes: { 'class': 'k-button-solid-warning' },
                    click: function (e) {
                        // $('#setting-groups-grid').data('kendoGrid').dataSource.read();
                        let grid = $('#setting-groups-grid').data('kendoGrid');
                        let rows = grid.select();
                        let ids = []
                        for (let i = 0; i < rows.length; i++) {
                            let dataItem = grid.dataItem($(rows[i]));
                            dataItem.is_activae = false;
                            ids.push(dataItem.id);
                        }
                        kendo.confirm("<div style='padding:5px 10px 0 10px;'>Are you sure you want to disable setting groups</div>").done(function() {
                            $.ajax({
                                url: `http://${api_base_url}/api/v1/setting_groups/status`,
                                type: "PUT",
                                data: JSON.stringify({ ids: ids, is_active: false }),
                                processData: false,
                                ContentType: 'application/json',
                                headers: {
                                    'Content-Type': 'application/json; odata=verbose',
                                    'Authorization': `${token_type} ${access_token}`
                                },
                                success: function(data) {

                                },
                                error: function(jqXHR, textStatus, ex) {

                                }
                            }).then(function(data) {
                                if (!data.error) {
                                    grid.dataSource.read();
                                }
                            });
                        }).fail(function() {

                        });
                    },
                },
                {
                    type: 'button',
                    id: 'delete',
                    text: 'Delete',
                    icon: 'cancel',
                    hidden: true,
                    attributes: { 'class': 'k-button-solid-error' },
                    click: function (e) {
                        let grid = $('#setting-groups-grid').data('kendoGrid');
                        let rows = grid.select();
                        let ids = []
                        for (let i = 0; i < rows.length; i++) {
                            let dataItem = grid.dataItem($(rows[i]));
                            ids.push(dataItem.id);
                        }
                        kendo.confirm("<div style='padding:5px 10px 0 10px;'>Are you sure you want to delete setting groups?</div>").done(function() {
                            $.ajax({
                                url: `http://${api_base_url}/api/v1/setting_groups/delete`,
                                type: "POST",
                                data: JSON.stringify({ ids: ids }),
                                processData: false,
                                ContentType: 'application/json',
                                headers: {
                                    'Content-Type': 'application/json; odata=verbose'
                                },
                                success: function(data) {

                                },
                                error: function(jqXHR, textStatus, ex) {

                                }
                            }).then(function(data) {
                                if (!data.error) {
                                    grid.dataSource.read();
                                    grid.clearSelection();
                                    e.sender.hide($('#delete'));
                                }
                            });
                        }).fail(function() {

                        });
                    },
                },
                {
                    type: 'button',
                    text: 'Refresh',
                    click: function (e) {
                        $('#setting-groups-grid').data('kendoGrid').dataSource.read();
                    },
                },
                {
                    type: 'button',
                    text: 'Clear Filter',
                    click: function (e) {
                        $('#setting-groups-grid').data('kendoGrid').dataSource.filter({});
                    },
                },
                {
                    type: 'button',
                    text: 'New Setting Group',
                    icon: 'plus',
                    click: function (e) {
                        let grid = $('#setting-groups-grid').data('kendoGrid');
                        grid.addRow();
                    },
                },
            ],
        });

    } catch (error) {
        console.warn(error);
    }
}