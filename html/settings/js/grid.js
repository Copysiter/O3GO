window.initGrid = function() {
    let timer = null;
    let showLoader = true;
    let token = window.isAuth;
    const TYPES_MAP = ['TEXT', 'INTEGER', 'BOOLEAN', 'DROPDOWN', 'PROXIES']
    try {
        let { access_token, token_type } = token;

        var popup;

        stripFunnyChars = function (value) {
            return (value+'').replace(/[\x09-\x10]/g, '') ? value : '';
        }

        $('#settings-grid').kendoGrid({
            dataSource: {
                transport: {
                    read: {
                        url: `http://${api_base_url}/api/v1/settings/`,
                        type: 'GET',
                        beforeSend: function (request) {
                            request.setRequestHeader('Authorization', `${token_type} ${access_token}`);
                        },
                        dataType: 'json',
                    },
                    create: {
                        url: `http://${api_base_url}/api/v1/settings/`,
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
                            return `http://${api_base_url}/api/v1/settings/${options.id}`;
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
                            return `http://${api_base_url}/api/v1/settings/${options.id}`;
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
                        fields: {
                            id: { type: 'number', editable: false },
                            name: {
                                type: 'string',
                                editable: true
                            },
                            key: {
                                type: 'string',
                                editable: true,
                                validation: { required: true },
                            },
                            type: {
                                type: 'number',
                                editable: true,
                                validation: { required: true },
                            },
                            description: {
                                type: 'string',
                                editable: true,
                            },
                            options: {
                                type: 'string',
                                editable: true,
                            },
                            is_active: {
                                type: 'boolean',
                                editable: true,
                            }
                        },
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
                    title: e.model.id ? 'Edit Variable' : 'New Variable',
                });
                popup.center();
            },
            editable: {
                mode: 'popup',
                template: kendo.template($('#settings-popup-editor').html()),
                window: {
                    width: 480,
                    maxHeight: '90%',
                    animation: false,
                    appendTo: '#app-root',
                    visible: false,
                    open: function (e) {
                        form = showEditForm();
                        popup = e.sender;
                        popup.center();
                        setTimeout(() => {
                            $('#type').data('kendoDropDownList').trigger('change');
                        });
                    },
                },
            },
            save: function (e) {
                // setTimeout(function () {
                //     initSettingGroupsGrid();
                // })
            },
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
            change: function (e) {
                // let toolbar = $('#settings-toolbar').data('kendoToolBar');
                // let rows = this.select();
                // if (rows.length > 0) {
                //     toolbar.show($('#delete'));
                // } else {
                //     toolbar.hide($('#delete'));
                // }
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
                    // width: 33,
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
                    field: 'key',
                    title: 'Key',
                    filterable: {
                        cell: {
                            inputWidth: 0,
                            showOperators: true,
                            operator: 'eq',
                        },
                    }
                },
                {
                    field: 'type',
                    title: 'Type',
                    filterable: {
                        cell: {
                            inputWidth: 0,
                            showOperators: true,
                            operator: 'eq',
                        },
                    },
                    template: (obj) => {
                        return TYPES_MAP[obj.type];
                    }
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
                {
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
                    title: '',
                    // width: 86,
                },
                {},
            ],
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

        $('#settings-grid').on('dblclick', "td[role='gridcell']", function (e) {
            var text = $(this).find('.text');
            if (text.length) text.selectText();
            else $(this).selectText();
        });

        $(document).keydown(function (e) {
            if (e.key === 'Escape') {
                selectedDataItems = [];
                selectedItemIds = [];
                selectedItemImsi = [];
                $('#settings-grid').data('kendoGrid').clearSelection();
                $('#settings-toolbar').data('kendoToolBar').hide($('#delete'));
            }
        });
    } catch (error) {
        console.warn(error);
    }
    window.optimize_grid(['#settings-grid']);
}
