window.initGrid = function() {
    let timer = null;
    let resizeColumn = false;
    let showLoader = true;
    // let { access_token, token_type } =
    //     window.storageToken.options.offlineStorage.getItem();
    let token = window.isAuth;

    try {
        let { access_token, token_type } = token;
        var service_columns = []

        stripFunnyChars = function (value) {
            return (value+'').replace(/[\x09-\x10]/g, '') ? value : '';
        }

        $.ajax({
            type: 'GET',
            url: `${api_base_url}/api/v1/services/?filters[0][field]=is_active&filters[0][operator]=istrue`,
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
                waiting: 'waiting',
                bad: 'bad',
                error_1: 'error-1',
                error_2: 'error-2',
                account: 'account',
                account_ban: 'ban',
                sent: 'sent',
                sent_avg: 'sent, avg',
                delivered: 'delivered'
            };
            let data = result.data;

            console.log(data);

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
                        // parameterMap: function (options, type) {
                        //     return kendo.stringify(options);
                        // },
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
                                data.filter = data.filter.filters;
                            }

                            if (type === 'read') return data;
                            return kendo.stringify(data);
                        },
                    },
                    // data: fakedata,
                    pageSize: 100,
                    serverPaging: true, // true
                    serverFiltering: true, // true
                    serverSorting: true, // true
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
                    // if (!resizeColumn) {
                    //     autoFitColumn(e.sender);
                    //     resizeColumn = true;
                    // }

                    // timer = setTimeout(function () {
                    //     showLoader = false;
                    //     e.sender.dataSource.read();
                    // }, 30000);
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
                excelExport: function(e){
                    var sheet = e.workbook.sheets[0];
                    for (var i = 0; i < sheet.rows.length; i++) {
                        for (var ci = 0; ci < sheet.rows[i].cells.length; ci++) {
                            sheet.rows[i].cells[ci].value = stripFunnyChars(sheet.rows[i].cells[ci].value)
                        }
                    }
                },
                columns: [
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
                            cell: {
                                inputWidth: 0,
                                showOperators: true,
                                operator: 'contains',
                            },
                        },
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
                        /*
                        filterable: {
                            multi: true,
                            dataSource: {
                                transport: {
                                    read: {
                                        url: `${api_base_url}/api/v1/options/device`,
                                        type: 'GET',
                                        beforeSend: function (request) {
                                            request.setRequestHeader('Authorization', `${token_type} ${access_token}`);
                                        },
                                        dataType: 'json',
                                    }
                                }
                            },
                            itemTemplate: function(e) {
                                if (e.field == "all") {
                                    return "";
                                } else {
                                    return "<div class=''><label class='d-flex align-items-center py-8 ps-3 border-bottom cursor-pointer'><input type='checkbox' name='" + e.field + "' value='#=value#' class='k-checkbox k-checkbox-md k-rounded-md'/><span class='ms-8'>#=text#</span></label></div>"
                                }
                            }
                        },
                        */
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
                        // width: 44,
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
                    }].concat(service_columns).concat([{
                        field: 'timestamp',
                        title: 'Last Activity',
                        // width: 33,
                        sortable: true,
                        filterable: false,
                        // filterable: {
                        //     cell: {
                        //         inputWidth: 0,
                        //         showOperators: true,
                        //         operator: 'eq',
                        //     },
                        // },
                        format: '{0: yyyy-MM-dd HH:mm:ss}',
                    },
                    {
                        field: 'ts_1',
                        title: 'Last Success Code',
                        // width: 33,
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
                    },
                    {}
                ]),
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
