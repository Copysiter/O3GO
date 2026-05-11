window.initGrid = function() {
    let timer = null;
    let resizeColumn = false;
    let showLoader = true;
    let token = window.isAuth;

    try {
        let { access_token, token_type } = token;
        var service_columns = []

        stripFunnyChars = function (value) {
            return (value+'').replace(/[\x09-\x10]/g, '') ? value : '';
        }

        $.ajax({
            type: 'GET',
            url: `${api_base_url}/api/v1/services/?filter[0][field]=is_active&filter[0][operator]=istrue`,
            headers: {
                Authorization: `${token_type} ${access_token}`,
                accept: 'application/json',
            },
        }).done(function (result) {
            const titles = {
                start: 'start',
                number: 'number',
                code: 'code',
                code_pct: 'code, %',
                no_code: 'no code',
                code_cost: 'cost',
                code_total: 'total',
                waiting: 'waiting',
                bad: 'bad',
                error_1: 'error-1',
                error_2: 'error-2',
                account: 'account',
                account_ban: 'ban',
                sent: 'sent',
                sent_avg: 'sent, avg',
                delivered: 'delivered',
                sent_cost: 'cost',
                sent_total: 'total'
            };
            let data = result.data;
            window.servicesData = data;

            data.forEach((obj) => {
                let columns = [];
                Object.keys(titles).forEach(key => {
                    let title = titles[key];
                    if (obj.columns.includes(key)) {
                        columns.push({
                            field: key + '_count_' + obj.id,
                            title: "<span class='rotate'>" + title + "</span>",
                            rowSpan: 2,
                            sortable: ['code_pct', 'msg_avg'].includes(key) ? false : true,
                            filterable: false,
                            attributes: {
                                style: `background:\\${obj.color_bg}44;`,
                            },
                            headerAttributes: {
                                class: 'rotate-cell',
                                style: 'color:' + obj.color_txt + ';background:' + obj.color_bg + ';',
                            },
                            template: function(item) {
                                if (key == 'code_pct') {
                                    if (
                                        item.hasOwnProperty('code_count_' + obj.id) &&
                                        item.hasOwnProperty('number_count_' + obj.id) &&
                                        item['code_count_' + obj.id] > 0 &&
                                        item['number_count_' + obj.id] > 0
                                    ) {
                                        return (item['code_count_' + obj.id]/item['number_count_' + obj.id]*100).toFixed(1);
                                    } else {
                                        return 0;
                                    }
                                }
                                if (key == 'code_cost') {
                                    return obj.cost_1;
                                }
                                if (key == 'code_total') {
                                    if (
                                        item.hasOwnProperty('code_total_' + obj.id)
                                    ) {
                                        return item['code_total_' + obj.id].toFixed(2);
                                    } else {
                                        return 0;
                                    }
                                }
                                if (key == 'sent_avg') {
                                    if (
                                        item.hasOwnProperty('sent_count_' + obj.id) &&
                                        item.hasOwnProperty('account_count_' + obj.id) &&
                                        item['sent_count_' + obj.id] > 0 &&
                                        item['account_count_' + obj.id] > 0
                                    ) {
                                        return (item['sent_count_' + obj.id]/item['account_count_' + obj.id]).toFixed(1);
                                    } else {
                                        return 0;
                                    }
                                }
                                if (key == 'sent_cost') {
                                    return obj.cost_2;
                                }
                                if (key == 'sent_total') {
                                    if (
                                        item.hasOwnProperty('sent_total_' + obj.id)
                                    ) {
                                        return item['sent_total_' + obj.id].toFixed(2);
                                    } else {
                                        return 0;
                                    }
                                }
                                if (item.hasOwnProperty(key + '_count_' + obj.id)) {
                                    return item[key + '_count_' + obj.id];
                                } else {
                                    return 0;
                                }
                            }
                        });
                    }
                });
                if (columns.length > 0) {
                    service_columns.push({
                        service_id: obj.id,
                        title: obj.name,
                        headerTemplate: '<span>' + (obj.name ? obj.name : obj.alias) + '</span>',
                        headerAttributes: {
                            style: 'color:' + obj.color_txt + ';background:' + obj.color_bg + ';',
                        },
                        filterable: {
                            mode: 'menu',
                        },
                        columns: columns
                    });
                }
            });

            var gridColumns = [
                {
                    field: 'alert',
                    title: ' ',
                    filterable: false,
                    sortable: false,
                    template: '# if (timedelta > 300) { #<div class="mdi mdi-alert text-red fs-18 mx-n2 my-n5"></div># } else { ## } #'
                },
                {
                    field: 'api_key',
                    title: 'API Key',
                    filterable: {
                        multi: true,
                        dataSource: new kendo.data.DataSource({
                            transport: {
                                read: {
                                    url: `${api_base_url}/api/v1/options/api_key`,
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
                        itemTemplate: function(e) {
                            console.log(e);
                            if (e.field == "all") {
                                return "";
                            } else {
                                return "<div class=''><label class='d-flex align-items-center py-8 ps-3 border-bottom cursor-pointer'><input type='checkbox' name='" + e.field + "' value='#=value#' class='k-checkbox k-checkbox-md k-rounded-md'/><span class='ms-8'>#=text#</span></label></div>"
                            }
                        }
                    }
                },
                {
                    field: 'device_name',
                    title: 'Device',
                    sortable: false,
                    filterable: {
                        cell: {
                            inputWidth: 0,
                            showOperators: true,
                            operator: 'contains',
                        },
                    },
                    template: '# if (device_name) { ##: device_name ## } else { ## } #'
                },
                {
                    field: 'device_ext_id',
                    title: 'Ext ID',
                    sortable: false,
                    filterable: {
                        cell: {
                            inputWidth: 0,
                            showOperators: true,
                            operator: 'contains',
                        },
                    },
                },
                {
                    field: 'device_root',
                    title: 'Root',
                    sortable: false,
                    template: "<div class='marker block #=device_root == 1 ? 'green' : 'red'#'><i></i></div>",
                    filterable: false,
                },
                {
                    field: 'device_operator',
                    title: 'Operator',
                    sortable: false,
                    filterable: {
                        cell: {
                            inputWidth: 0,
                            showOperators: true,
                            operator: 'contains',
                        },
                    },
                }
            ].concat(service_columns).concat([
                {
                    service_id: 'total_cost',
                    title: "Total Cost",
                    headerTemplate: '<span>Total Cost</span>',
                    headerAttributes: {
                        style: 'background:#cfcfcf;',
                    },
                    filterable: {
                        mode: 'menu',
                    },
                    columns: [{
                        field: 'code_total',
                        title: "<span class='rotate'>code cost</span>",
                        sortable: false,
                        filterable: false,
                        headerAttributes: {
                            class: 'rotate-cell',
                            style: 'background:#cfcfcf;',
                        },
                        template: function(item) {
                            return (item.code_total || 0).toFixed(2);
                        }
                    }, {
                        field: 'sent_total',
                        title: "<span class='rotate'>sent cost</span>",
                        sortable: false,
                        filterable: false,
                        headerAttributes: {
                            class: 'rotate-cell',
                            style: 'background:#cfcfcf;',
                        },
                        template: function(item) {
                            return (item.sent_total || 0).toFixed(2);
                        }
                    }]
                }, {
                    field: 'timestamp',
                    title: 'Last Activity',
                    sortable: true,
                    filterable: false,
                    format: '{0: yyyy-MM-dd HH:mm:ss}',
                },
                {
                    field: 'ts_1',
                    title: 'Last Success Code',
                    filterable: false,
                    format: '{0: yyyy-MM-dd HH:mm:ss}',
                },
                {
                    field: 'info_1',
                    title: 'Info 1',
                    sortable: false,
                    filterable: {
                        cell: {
                            inputWidth: 0,
                            showOperators: true,
                            operator: 'contains',
                        },
                    },
                },
                {
                    field: 'info_2',
                    title: 'Info 2',
                    sortable: false,
                    filterable: {
                        cell: {
                            inputWidth: 0,
                            showOperators: true,
                            operator: 'contains',
                        },
                    },
                },
                {
                    field: 'info_3',
                    title: 'Info 3',
                    sortable: false,
                    filterable: {
                        cell: {
                            inputWidth: 0,
                            showOperators: true,
                            operator: 'contains',
                        },
                    },
                }
            ]);

            var leafColumns = [];
            function collectLeaves(cols, parentTitle) {
                for (var i = 0; i < cols.length; i++) {
                    var col = cols[i];
                    var pTitle = (col.title || '').replace(/<[^>]*>/g, '') || parentTitle || '';
                    if (col.columns) {
                        collectLeaves(col.columns, pTitle);
                    } else if (col.field || col.template) {
                        var title = (col.title || '').replace(/<[^>]*>/g, '') || col.field || '';
                        if (pTitle && title && pTitle !== title) {
                            title = pTitle + ' - ' + title;
                        } else if (pTitle && !title) {
                            title = pTitle;
                        }
                        leafColumns.push({field: col.field, template: col.template, exportTitle: title});
                    }
                }
            }
            collectLeaves(gridColumns, '');

            $('#report-grid').kendoGrid({
                dataSource: {
                    transport: {
                        read: {
                            url: `${api_base_url}/api/v1/report/`,
                            type: 'GET',
                            beforeSend: function (request) {
                                request.setRequestHeader('Authorization', `${token_type} ${access_token}`);
                            },
                            dataType: 'json',
                        },
                        parameterMap: function (data, type) {
                            if (data.hasOwnProperty('take')) {
                                data.limit = data.take;
                                delete data.take;
                            }
                            if (data.hasOwnProperty('page')) {
                                delete data.page;
                            }
                            if (data.hasOwnProperty('pageSize')) {
                                delete data.pageSize;
                            }
                            if (data.hasOwnProperty('filter') && data.filter) {
                                function flattenFilters(filter) {
                                    if (filter.filters) {
                                        var result = [];
                                        filter.filters.forEach(function(f) {
                                            result = result.concat(flattenFilters(f));
                                        });
                                        return result;
                                    }
                                    return [filter];
                                }
                                data.filter = flattenFilters(data.filter);
                            }

                            if (type === 'read') return data;
                            return kendo.stringify(data);
                        },
                    },
                    pageSize: 500,
                    serverPaging: true,
                    serverFiltering: true,
                    serverSorting: true,
                    schema: {
                        data: function (response) {
                            if (response.data !== undefined) return response.data;
                            else return response;
                        },
                        total: 'total',
                        model: {
                            id: 'id',
                            fields: {
                                id: { type: 'number'},
                                api_key: { type: 'string' },
                                device_id: { type: 'number' },
                                device_ext_id: { type: 'string' },
                                device_operator: { type: 'string' },
                                timestamp: { type: 'date' },
                                ts_1: { type: 'date'},
                            },
                        },
                    },
                    filter: { field: 'period', operator: "eq", value: '0d' },
                    requestStart: function (e) {
                        setTimeout(function (e) {
                            if (showLoader) $('.k-loading-mask').show();
                        });
                    },
                },
                height: '100%',
                reorderable: true,
                resizable: false,
                selectable: 'row',
                persistSelection: true,
                sortable: true,
                dataBinding: function (e) {
                    clearTimeout(timer);
                },
                dataBound: function (e) {
                    showLoader = true;
                },
                filterable: {
                    mode: 'menu',
                    extra: false,
                    operators: {
                        string: {
                            eq: 'Equal to',
                            neq: 'Not equal to',
                            startswith: 'Starts with',
                            endswith: 'Ends with',
                            contains: 'Contains',
                            doesnotcontain: 'Does not contain',
                            isnullorempty: 'Has no value',
                            isnotnullorempty: 'Has value',
                        },
                        number: {
                            eq: 'Equal to',
                            neq: 'Not equal to',
                            gt: 'Greater than',
                            gte: 'Greater than or equal to',
                            lt: 'Less than',
                            lte: 'Less than or equal to',
                        },
                    },
                },
                pageable: {
                    refresh: true,
                    pageSizes: [100, 250, 500],
                },
                change: function (e) {},
                excel: {
                    fileName: 'o3go_report.xlsx',
                    allPages: true,
                    filterable: true
                },
                excelExport: function(e) {
                    var rows = [];

                    var headerRow = {cells: [], type: 'header'};
                    for (var ci = 0; ci < leafColumns.length; ci++) {
                        headerRow.cells.push({value: leafColumns[ci].exportTitle});
                    }
                    rows.push(headerRow);

                    var data = e.data;
                    for (var di = 0; di < data.length; di++) {
                        var item = data[di];
                        var row = {cells: []};
                        for (var ci = 0; ci < leafColumns.length; ci++) {
                            var field = leafColumns[ci].field;
                            var tmpl = leafColumns[ci].template;
                            var value = '';
                            if (tmpl) {
                                value = tmpl(item);
                            } else if (field && item.hasOwnProperty(field)) {
                                value = item[field];
                            }
                            if (typeof value === 'string') {
                                value = stripFunnyChars(value);
                                var num = parseFloat(value.replace(',', '.'));
                                if (!isNaN(num) && num.toString() === value.replace(',', '.')) {
                                    value = num;
                                }
                            }
                            row.cells.push({value: value});
                        }
                        rows.push(row);
                    }

                    e.workbook.sheets[0].rows = rows;
                },
                columns: gridColumns,
            });
            window.optimize_grid(['#report-grid']);
        }).fail(function (result) {

        });
        jQuery.fn.selectText = function () {
            var doc = document;
            var element = this[0];
            $('input, textarea, select').blur();
            if (doc.body.createTextRange) {
                var range = document.body.createTextRange();
                range.moveToElementText(element);
                range.select();
            } else if (window.getSelection) {
                var selection = window.getSelection();
                var range = document.createRange();
                range.selectNodeContents(element);
                selection.removeAllRanges();
                selection.addRange(range);
            }
        };

        $('#report-grid').on('dblclick', "td[role='gridcell']", function (e) {
            var text = $(this).find('.text');
            if (text.length) text.selectText();
            else $(this).selectText();
        });

        $(document).keydown(function (e) {
            if (e.key === 'Escape') {
                selectedDataItems = [];
                selectedItemIds = [];
                selectedItemImsi = [];
                $('#report-grid').data('kendoGrid').clearSelection();
            }
        });

    } catch (error) {
        console.warn(error);
    }
}
