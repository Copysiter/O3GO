window.initToolbar = function() {
    function showReportNotification(message, type) {
        let notification = $('#report-notification').data('kendoNotification');
        if (!notification) {
            $('#report-notification').kendoNotification({
                position: {
                    top: 54,
                    right: 12,
                },
                stacking: 'down',
                autoHideAfter: 5000,
                width: 'auto',
            });
            notification = $('#report-notification').data('kendoNotification');
        }
        notification.show(message, type || 'info');
    }

    function currentReportFilters() {
        const grid = $('#report-grid').data('kendoGrid');
        const filter = grid.dataSource.filter();
        if (!filter) return [];
        if (filter.filters) return filter.filters.slice();
        return [filter];
    }

    function currentReportPeriod(filters) {
        const periodFilter = filters.find((item) => item.field === 'period');
        if (periodFilter) {
            const ddl = $('#period-ddl').data('kendoDropDownList');
            const text = ddl ? ddl.text() : '';
            return text && text !== 'Select Period' ? text : periodFilter.value;
        }
        const from = filters.find((item) => item.field === 'date' && item.operator === 'gte');
        const to = filters.find((item) => item.field === 'date' && item.operator === 'lte');
        if (from && to) return `${from.value} — ${to.value}`;
        return 'Current selection';
    }

    $('#report-toolbar').kendoToolBar({
        items: [
            {
                template: "<div class='k-window-title ps-6'>Report</div>",
            },
            { type: 'spacer'},
            {
                template: "<select id='services' />",
            },
            { type: "separator" },
            {
                template: "<input id='period-ddl' class='datepicker' />",
            },
            { type: "separator" },
            {
                template: "<div id='wrapper-drp'><div id='daterangepicker'></div></div>",
            },
            { type: "separator" },
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
                    let grid = $("#report-grid").data("kendoGrid")
                    let filters = grid.dataSource.filter().filters
                    filters = filters.filter(obj => ['service_id', 'period', 'date'].includes(obj.field));
                    grid.dataSource.filter(filters);
                },
            },
            {
                type: 'button',
                text: 'Export to Excel',
                icon: 'excel',
                click: function (e) {
                    const grid = $('#report-grid').data('kendoGrid');
                    const filter = grid.dataSource.filter();
                    const params = new URLSearchParams();
                    if (filter != undefined) {
                        filter.filters.forEach((filter, index) => {
                            for (const [key, value] of Object.entries(filter)) {
                                params.append(`filters[${index}][${key}]`, value);
                            }
                        });
                    }
                    const exportURL = `${api_base_url}/api/v1/export/report?${params.toString()}`;
                    exportToExcel(exportURL)
                },
            },
            {
                type: 'button',
                text: 'Create Analytics',
                icon: 'chart-column-clustered',
                click: function (e) {
                    const filters = currentReportFilters();
                    const period = currentReportPeriod(filters);
                    const token = window.isAuth;
                    const { access_token, token_type } = token;
                    kendo.ui.progress($('#content'), true);
                    $.ajax({
                        url: `${api_base_url}/api/v1/analytics/run`,
                        type: 'POST',
                        data: JSON.stringify({ period: period, filters: filters }),
                        processData: false,
                        contentType: 'application/json',
                        headers: {
                            Authorization: `${token_type} ${access_token}`,
                            accept: 'application/json',
                        },
                    }).done(function (data) {
                        showReportNotification(
                            `Analytics generation started. ID: ${data.id}`,
                            'success'
                        );
                    }).fail(function (xhr) {
                        const detail = xhr.responseJSON && xhr.responseJSON.detail
                            ? xhr.responseJSON.detail
                            : 'Failed to start analytics generation';
                        showReportNotification(detail, 'error');
                    }).always(function () {
                        kendo.ui.progress($('#content'), false);
                    });
                },
            },
        ],
    });

    $("#services").kendoMultiSelect({
        placeholder: 'Select services',
        dataSource: new kendo.data.DataSource({
            transport: {
                read: {
                    url: `${api_base_url}/api/v1/options/service`,
                    type: 'GET',
                    beforeSend: function (request) {
                        request.setRequestHeader(
                            'Authorization',
                            `${token_type} ${access_token}`
                        );
                    },
                },
            },
        }),
        autoWidth: true,
        tagMode: 'single',
        dataTextField: 'text',
        dataValueField: 'value',
        valuePrimitive: true,
        downArrow: true,
        animation: false,
        autoClose: false,
        messages: {
            singleTag: "service(s) selected!",
        },
        change: function (e) {
            let grid = $("#report-grid").data("kendoGrid")
            let filters = grid.dataSource.filter().filters
            const index = filters.findIndex(obj => obj.field == 'service_id');
            const values = e.sender.value()
            const value = JSON.stringify(values)
            if (index !== -1) {
                if (values.length > 0) {
                    filters[index].value = value;
                } else {
                    filters.splice(index, 1);
                }
            } else {
                if (values.length > 0) {
                    filters.push({
                        field: 'service_id',
                        operator: 'overlaps',
                        value: value
                    });
                }
            }
            grid.dataSource.filter(filters);
            for (let i = 0; i < grid.columns.length; i++) {
                const column = grid.columns[i]
                if ('service_id' in column) {
                    if (values.length < 1 || values.includes(column.service_id)) {
                        grid.showColumn(i);
                    } else {
                        grid.hideColumn(i);
                    }
                }
            }
        },
    });

    $("#period-ddl").kendoDropDownList({
        dataSource: [{"value": "0d", "text": "Current Day"},
                     {"value": "1d", "text": "Yesterday"},
                     {"value": "3d", "text": "Last 3 Days"},
                     {"value": "7d", "text": "Last 7 Days"},
                     {"value": "30d", "text": "Last 30 Days"}],
        optionLabel: "Select Period",
        dataTextField: 'text',
        dataValueField: 'value',
        valuePrimitive: true,
        downArrow: true,
        animation: false,
        autoClose: true,
        value: "0d",
        select: function (e) {
            window.selectedPeriod = e.dataItem;
            /*
            let chart = $("#chart").data("kendoChart");
            chart.setOptions({
                title: {
                    text: `Selected Period: ${window.selectedPeriod ? window.selectedPeriod : "None"}, Selected Name: ${window.row_name}`,
                },
            });
            chart.refresh();
            */
            if (!e.dataItem.value.length) {
                let daterangepicker = $("#daterangepicker").data("kendoDateRangePicker");
                daterangepicker.enable(true);
            } else {
                let grid = $("#report-grid").data("kendoGrid")
                const service_filter = grid.dataSource.filter().filters.find(obj => obj.field == 'service_id');
                let filters = [{
                    field: 'period',
                    operator: 'eq',
                    value: e.dataItem.value,
                }]
                if (service_filter != undefined) {
                    filters.push(service_filter)
                }
                daterangepicker.enable(false);
                $("#report-grid").data("kendoGrid").clearSelection();
                $("#report-grid").data("kendoGrid").dataSource.filter(filters);
            }
        },
    });
    $("#daterangepicker").kendoDateRangePicker({
        format: "yyyy-MM-dd",
        labels: false,
        startField: "startField",
        enable: false,
        change: function () {
            let range = this.range();
            if (range.start && range.end) {
                let begin_dt = kendo.parseDate(range.start, "yyyy-MM-dd h:mm:ss tt");
                let end_dt = kendo.parseDate(range.end, "yyyy-MM-dd h:mm:ss tt");
                let begin = kendo.toString(begin_dt, "yyyy-MM-dd 00:00:00");
                let end = kendo.toString(end_dt, "yyyy-MM-dd 23:59:59");
                let grid = $("#report-grid").data("kendoGrid")
                const service_filter = grid.dataSource.filter().filters.find(obj => obj.field == 'service_id');
                let filters = [{
                    field: 'date',
                    operator: 'gte',
                    value: begin,
                }, {
                    field: 'date',
                    operator: 'lte',
                    value: end,
                }]
                if (service_filter != undefined) {
                    filters.push(service_filter)
                }
                $("#report-grid").data("kendoGrid").dataSource.filter(filters);
            }
        }
    });
    let daterangepicker = $("#daterangepicker").data("kendoDateRangePicker");
    daterangepicker.enable(false);
    let rangePicker = document.getElementById("daterangepicker");
    rangePicker.children[1].innerHTML = "&mdash;";
    rangePicker.children[1].style.marginTop = "5px";

    $('#services').triggerHandler('change');
}
