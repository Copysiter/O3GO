function initPatternGrid() {
    let timer = null;
    let resizeColumn = false;
    let showLoader = true;

    // let { access_token, token_type } =
    //     window.storageToken.options.offlineStorage.getItem();
    let token = window.isAuth;
    try {
        let { access_token, token_type } = token;
        let editedItem = null;
        var popup;
        var form;
        autoFitColumn = function (grid) {
            setTimeout(function () {
                // grid.autoFitColumn("id");
                grid.autoFitColumn('policy_id');
                grid.autoFitColumn('name');
                grid.autoFitColumn('pattern');
                grid.autoFitColumn('result');
                grid.autoFitColumn('weight');
            });
        };
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

        $('#pattern-grid').on('dblclick', "td[role='gridcell']", function (e) {
            var text = $(this).find('.text');
            if (text.length) text.selectText();
            else $(this).selectText();
        });

        $(document).keydown(function (e) {
            if (e.key === 'Escape' && $('#pattern-grid').data('kendoGrid')) {
                selectedDataItems = [];
                selectedItemIds = [];
                selectedItemImsi = [];
                $('#pattern-grid').data('kendoGrid').clearSelection();
            }
        });

        return $('#pattern-grid').kendoGrid({
            dataSource: {
                transport: {
                    read: {
                        url: '/api/v1/modify/pattern/',
                        type: 'GET',
                        beforeSend: function (request) {
                            request.setRequestHeader('Authorization', `${token_type} ${access_token}`);
                        },
                        // dataType: 'jsonp',
                        // contentType: 'application/json',
                    },
                    create: {
                        url: '/api/v1/modify/pattern/',
                        type: 'POST',
                        // dataType: 'jsonp',
                        contentType: 'application/json',
                        headers: { 'access-control-allow-credentials': true },
                        beforeSend: function (request) {
                            request.setRequestHeader('Authorization', `${token_type} ${access_token}`);
                        },
                    },
                    update: {
                        url: function (options) {
                            console.log(options);
                            return `/api/v1/modify/pattern/${options.id}`;
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
                            return `/api/v1/modify/pattern/${options.id}`;
                        },

                        type: 'DELETE',
                        dataType: 'json',
                        contentType: 'application/json',
                        beforeSend: function (request) {
                            request.setRequestHeader('Authorization', `${token_type} ${access_token}`);
                        },
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
                            data.filter = data.filter.filters;
                        }

                        if (type === 'read') return data;
                        return kendo.stringify(data);
                    },
                    // parameterMap: function (options, type) {
                    //     return kendo.stringify(options);
                    // },
                },
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
                            //id: { type: 'number', editable: false },
                            name: { type: 'string', editable: true },
                            policy_id: { type: 'number', editable: true },
                            //policy: { type: 'object', editable: false },
                            pattern: { type: 'string', editable: true },
                            result: { type: 'string', editable: true },
                            weight: { type: 'number', editable: true },
                        },
                    },
                },
                requestStart: function (e) {
                    setTimeout(function (e) {
                        if (showLoader) $('.k-loading-mask').show();
                    });
                },
                requestEnd: function (e) {
                    if (e.type == 'update') e.sender.pushUpdate(e.response);
                },
            },
            toolbar: [
                {
                    template: kendo.template($('#toolbar-pattern-template').html()),
                },
            ],
            height: '100%',
            reorderable: true,
            resizable: true,
            selectable: 'multiple, row',
            persistSelection: true,
            sortable: true,
            edit: function (e) {
                editedItem = e.model;
                form.data('kendoForm').setOptions({
                    formData: e.model,
                });
                popup.setOptions({
                    title: e.model.id ? 'Edit Pattern' : 'New Pattern',
                });
                popup.center();
            },
            editable: {
                mode: 'popup',
                template: kendo.template($('#popup-editor-pattern').html()),
                window: {
                    width: 480,
                    maxHeight: '90%',
                    animation: false,
                    appendTo: '#app-root',
                    visible: false,
                    open: function (e) {
                        form = editPatternForm();
                        popup = e.sender;
                        popup.center();
                    },
                },
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
                    object: {
                        contains: 'Contains',
                        isnotnullorempty: 'Has value',
                        eq: 'Equal to',
                    },
                },
                suggestionOperator: 'contains',
            },
            pageable: {
                refresh: true,
                pageSizes: [100, 250, 500],
            },
            change: function (e) {
                let selectedRows = this.select();
                window.selectedrouting = [];
                for (var i = 0; i < selectedRows.length; i++) {
                    var dataItem = this.dataItem(selectedRows[i]);
                    window.selectedrouting.push(dataItem);
                }
            },
            columns: [
                {
                    field: 'id',
                    title: 'ID',
                    // width: 33,
                    filterable: false,
                },
                {
                    field: 'policy_id',
                    title: 'Policy',
                    template: function (obj) {
                        // console.log(obj);
                        return obj.policy ? obj.policy.name : '';
                    },
                    filterable: {
                        cell: {
                            inputWidth: 0,
                            showOperators: true,
                            operator: 'eq',
                        },
                        ui: function (element) {
                            element.kendoDropDownList({
                                animation: false,
                                dataSource: [
                                    { text: 'lanck', value: 8 },
                                    { text: 'censor_vox', value: 3 },
                                ],
                                dataTextField: 'text',
                                dataValueField: 'value',
                                valuePrimitive: false,
                                optionLabel: '-- Select Policy --',
                            });
                        },
                    },
                },
                {
                    field: 'name',
                    title: 'Description',
                    filterable: {
                        cell: {
                            inputWidth: 0,
                            showOperators: true,
                            operator: 'eq',
                        },
                    },
                },
                {
                    field: 'pattern',
                    title: 'Pattern',
                    filterable: {
                        cell: {
                            inputWidth: 0,
                            showOperators: true,
                            operator: 'eq',
                        },
                    },
                    template: function(obj) {
                        if (obj.pattern) {
                            return '<pre class="m-0" style="font-family:inherit;">' + obj.pattern + '</pre>'
                        } else {
                            return ''
                        }
                    }
                },
                {
                    field: 'result',
                    title: 'Result',
                    filterable: {
                        cell: {
                            inputWidth: 0,
                            showOperators: true,
                            operator: 'eq',
                        },
                    },
                    template: function(obj) {
                        if (obj.result) {
                            return '<pre class="m-0" style="font-family:inherit;">' + obj.result + '</pre>'
                        } else {
                            return ''
                        }
                    }
                },
                {
                    field: 'weight',
                    title: 'Weight',
                    filterable: {
                        cell: {
                            inputWidth: 0,
                            showOperators: true,
                            operator: 'eq',
                        },
                    },
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
    } catch (error) {
        console.warn(error);
    }

    // window.optimize_grid(['#pattern-grid']);
}
