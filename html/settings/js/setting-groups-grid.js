window.initSettingGroupsGrid = function() {
    let timer = null;
    let showLoader = true;
    let token = window.isAuth;
    const TYPES_MAP = ['TEXT', 'INTEGER', 'BOOLEAN', 'DROPDOWN', 'PROXIES']
    try {
        let { access_token, token_type } = token;

        let popup;
        let setting_columns = []
        let setting_fields = {}

        window.form_items = []

        stripFunnyChars = function (value) {
            return (value+'').replace(/[\x09-\x10]/g, '') ? value : '';
        }

        $.ajax({
            type: 'GET',
            url: `http://${api_base_url}/api/v1/settings/?filters[0][field]=is_active&filters[0][operator]=istrue`,
            headers: {
                Authorization: `${token_type} ${access_token}`,
                accept: 'application/json',
            },
        }).done(function (result) {
            let data = result.data;
            let count = 1;
            data.forEach((obj) => {
                const objKey = obj.key
                let field;
                form_items.push({
                    field: `sep${count}`,
                    colSpan: 12,
                    label: false,
                    editor: "<div class='separator mx-n15 mt-n3'></div>",
                });
                switch (obj.type) {
                    case 0:
                        form_items.push({
                            field: objKey,
                            label: `${obj.name ? obj.name : (obj.description ? obj.description : objKey)}:`,
                            colSpan: 12,
                        });
                        field = {
                            type: 'string',
                            editable: true,
                            defaultValue: obj.str_default
                        };
                    break;
                    case 1:
                        form_items.push({
                            field: objKey,
                            label: `${obj.name ? obj.name : (obj.description ? obj.description : objKey)}:`,
                            editor: 'NumericTextBox',
                            editorOptions: {
                                format: "n0"
                            },
                            colSpan: 12
                        });
                        console.log('int_default:', obj.int_default);
                        console.log('obj.setting:', obj.setting);
                        console.log('obj:', obj);
                        field = {
                            type: 'number',
                            editable: true,
                            defaultValue: obj.int_default
                        }
                    break;
                    case 2:
                        form_items.push({
                            field: `${objKey}_label`,
                            colSpan: 6,
                            label: false,
                            editor: `<div class='mt-3'>${obj.name ? obj.name : (obj.description ? obj.description : objKey)}:</div>`,
                        });
                        form_items.push({
                            field: objKey,
                            label: '',
                            editor: 'Switch',
                            editorOptions: {
                                width: 70,
                            },
                            colSpan: 6,
                        });
                        field = {
                            type: 'boolean',
                            editable: true,
                            defaultValue: obj.bool_default
                        }
                    break;
                    case 3:
                        let options = [];
                        obj.options.split("\n").forEach((option) => {
                            let row = option.split("|");
                            options.push({
                                text: row[0].trim(), value: row[row.length - 1].trim()
                            });
                        });
                        form_items.push({
                            field: objKey,
                            label: `${obj.name ? obj.name : (obj.description ? obj.description : objKey)}:`,
                            colSpan: 12,
                            editor: "DropDownList",
                            editorOptions: {
                                dataSource: options,
                                dataTextField: "text",
                                dataValueField: "value",
                                valuePrimitive: true,
                            }
                        });
                        field = {
                            type: 'string',
                            editable: true,
                            defaultValue: obj.str_default
                        }
                    break;
                    case 4:
                        form_items.push({
                            field: objKey,
                            label: `${obj.name ? obj.name : (obj.description ? obj.description : objKey)}:`,
                            editor: 'DropDownList',
                            editorOptions: {
                                dataSource: new kendo.data.DataSource({
                                    transport: {
                                        read: {
                                            url: `http://${api_base_url}/api/v1/options/proxy_group`,
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
                                dataTextField: 'text',
                                dataValueField: 'value',
                                valuePrimitive: true,
                                downArrow: true,
                                animation: false,
                                autoClose: false,
                                value: 4
                            },
                            colSpan: 12,
                        });
                        field = {
                            type: 'number',
                            editable: true,
                            defaultValue: obj.proxy_group_default
                        }
                    break;
                }
                let column = {
                    field: objKey,
                    title: `${obj.name ? obj.name : objKey}`,
                    sortable: false,
                    filterable: false,
                }
                if (obj.type == 4) {
                    column.template = function (obj) {
                        return obj[objKey + '_name'];
                    }
                }
                setting_columns.push(column);
                setting_fields[objKey] = field;
                count ++;
            });

            $('#setting-groups-grid').kendoGrid({
                dataSource: {
                    transport: {
                        read: {
                            url: `http://${api_base_url}/api/v1/setting_groups/`,
                            type: 'GET',
                            beforeSend: function (request) {
                                request.setRequestHeader('Authorization', `${token_type} ${access_token}`);
                            },
                            dataType: 'json',
                        },
                        create: {
                            url: `http://${api_base_url}/api/v1/setting_groups/`,
                            type: 'POST',
                            dataType: 'json',
                            contentType: 'application/json',
                            beforeSend: function (request) {
                                request.setRequestHeader('Authorization', `${token_type} ${access_token}`);
                            },
                        },
                        update: {
                            url: function (options) {
                                console.log(options);
                                return `http://${api_base_url}/api/v1/setting_groups/${options.id}`;
                            },

                            type: 'PUT',
                            dataType: 'json',
                            contentType: 'application/json',
                            beforeSend: function (request) {
                                request.setRequestHeader('Authorization', `${token_type} ${access_token}`);
                            },
                        },
                        destroy: {
                            url: function (options) {
                                console.log(options);
                                return `http://${api_base_url}/api/v1/setting_groups/${options.id}`;
                            },

                            type: 'DELETE',
                            dataType: 'json',
                            contentType: 'application/json',
                            beforeSend: function (request) {
                                request.setRequestHeader('Authorization', `${token_type} ${access_token}`);
                            },
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
                            fields: Object.assign({}, {
                                id: { type: 'number', editable: false },
                                name: {
                                    type: 'string',
                                    editable: true,
                                    validation: { required: true },
                                },
                                check_period: {
                                    type: 'number',
                                    defaultValue: 1800,
                                    editable: true
                                },
                                timestamp: {
                                    type: 'date'
                                },
                                description: {
                                    type: 'string',
                                    editable: true,
                                },
                                is_active: {
                                    type: 'boolean',
                                    editable: true,
                                }
                            }, setting_fields),
                        },
                    },
                    requestStart: function (e) {
                        setTimeout(function (e) {
                            if (showLoader) $('.k-loading-mask').show();
                        });
                    },
                },
                height: '100%',
                reorderable: true,
                resizable: true,
                selectable: 'multiple, row',
                persistSelection: true,
                sortable: true,
                edit: function (e) {
                    form.data('kendoForm').setOptions({
                        formData: e.model,
                    });
                    popup.setOptions({
                        title: e.model.id ? 'Edit Setting Group' : 'New Setting Group',
                    });
                    popup.center();
                },
                editable: {
                    mode: 'popup',
                    template: kendo.template($('#setting-groups-popup-editor').html()),
                    window: {
                        width: 480,
                        maxHeight: '90%',
                        animation: false,
                        appendTo: '#app-root',
                        visible: false,
                        open: function (e) {
                            form = showSettingGroupsEditForm();
                            popup = e.sender;
                            popup.center();
                        },
                    },
                },
                save: function (e) {

                },
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
                change: function (e) {

                },
                columns: [
                    {
                        field: 'is_active',
                        title: '&nbsp;',
                        // width: 44,
                        template: "<div class='marker block #=is_active == 1 ? 'green' : 'red'#'><i></i></div>",
                        filterable: false,
                    },
                    {
                        field: 'id',
                        title: '#',
                        filterable: false
                    },
                    {
                        field: 'name',
                        title: 'Name',
                        filterable: {
                            cell: {
                                inputWidth: 0,
                                showOperators: true,
                                operator: 'eq',
                            },
                        }
                    },
                    {
                        field: 'check_period',
                        title: 'Check Period',
                        filterable: false
                    },
                    {
                        title: '',
                        command: [
                            {
                                name: 'edit',
                                iconClass: {
                                    edit: 'k-icon k-i-edit',
                                    update: '',
                                    cancel: '',
                                },
                                text: {
                                    edit: '',
                                    update: 'Save',
                                    cancel: 'Cancel',
                                },
                            },
                            { name: 'destroy', text: '' },
                        ],
                    }].concat(setting_columns).concat([{
                        field: 'timestamp',
                        title: 'Timestamp',
                        format: '{0: yyyy-MM-dd HH:mm:ss}',
                        filterable: false
                    },
                    {
                        field: 'description',
                        title: 'Description',
                        filterable: {
                            cell: {
                                inputWidth: 0,
                                showOperators: true,
                                operator: 'eq',
                            },
                        }
                    },
                    {},
                ]),
            });
            window.optimize_grid(['#setting-groups-grid']);

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

        $('#setting-groups-grid').on('dblclick', "td[role='gridcell']", function (e) {
            var text = $(this).find('.text');
            if (text.length) text.selectText();
            else $(this).selectText();
        });

        $(document).keydown(function (e) {
            if (e.key === 'Escape') {
                selectedDataItems = [];
                selectedItemIds = [];
                selectedItemImsi = [];
                $('#setting-groups-grid').data('kendoGrid').clearSelection();
                $('#setting-groups-toolbar').data('kendoToolBar').hide($('#delete'));
            }
        });
    } catch (error) {
        console.warn(error);
    }
}
