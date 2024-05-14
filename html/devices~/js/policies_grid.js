function initPoliciesGrid() {
    // let fakeData = window.gridsFakeData.policies;
    // console.log(fakeData);

    let timer = null;
    let resizeColumn = false;
    let showLoader = true;
    let token = window.isAuth;

    try {
        let { access_token, token_type } = token;

        let editedItem = null;
        var popup;
        var form;
        autoFitColumn = function (grid) {
            setTimeout(function () {
                // grid.autoFitColumn("id");
                grid.autoFitColumn('name');
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

        $('#policies-grid').on('dblclick', "td[role='gridcell']", function (e) {
            var text = $(this).find('.text');
            if (text.length) text.selectText();
            else $(this).selectText();
        });

        $(document).keydown(function (e) {
            if (e.key === 'Escape' && $('#policies-grid').data('kendoGrid')) {
                selectedDataItems = [];
                selectedItemIds = [];
                selectedItemImsi = [];
                $('#policies-grid').data('kendoGrid').clearSelection();
            }
        });

        return $('#policies-grid').kendoGrid({
            dataSource: {
                transport: {
                    read: {
                        url: '/api/v1/modify/policy',
                        type: 'GET',
                        beforeSend: function (request) {
                            request.setRequestHeader('Authorization', `${token_type} ${access_token}`);
                        },
                        // dataType: 'jsonp',
                        // contentType: 'application/json',
                    },
                    create: {
                        url: '/api/v1/modify/policy/',
                        type: 'POST',
                        dataType: 'json',
                        contentType: 'application/json',
                        headers: { 'access-control-allow-credentials': true },
                        beforeSend: function (request) {
                            request.setRequestHeader('Authorization', `${token_type} ${access_token}`);
                        },
                    },
                    update: {
                        url: function (options) {
                            console.log(options);
                            return `/api/v1/modify/policy/${options.id}`;
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
                            return `/api/v1/modify/policy/${options.id}`;
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
                            name: { type: 'string', editable: true },
                        },
                    },
                },
                requestStart: function (e) {
                    setTimeout(function (e) {
                        if (showLoader) $('.k-loading-mask').show();
                    });
                },
            },
            toolbar: [
                {
                    template: kendo.template($('#toolbar-policy-template').html()),
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
                    title: e.model.id ? 'Edit Policy' : 'New Policy',
                });
                popup.center();
            },
            editable: {
                mode: 'popup',
                template: kendo.template($('#popup-editor-policies').html()),
                window: {
                    width: 480,
                    maxHeight: '90%',
                    animation: false,
                    appendTo: '#app-root',
                    visible: false,
                    open: function (e) {
                        // editPoliciesForm();
                        form = editPoliciesForm();
                        popup = e.sender;
                        popup.center();
                    },
                },
            },
            // save: function (e) {
            //     let alredyItem = window.gridsFakeData.policies.data.find(
            //         (i) => i.modify_policy_id === e.model.modify_policy_id
            //     );
            //     if (alredyItem) {
            //         alredyItem.modify_policy_id = e.model.modify_policy_id;
            //         alredyItem.modify_policy_name = e.model.modify_policy_name;
            //     } else {
            //         window.gridsFakeData.policies.data.push({
            //             modify_policy_id: e.model.modify_policy_id,
            //             modify_policy_name: e.model.modify_policy_name,
            //         });
            //     }
            // },
            // remove: function (e) {
            //     let i = window.gridsFakeData.policies.data.find((i) => {
            //         return i.modify_policy_id === e.model.modify_policy_id;
            //     });
            //     window.gridsFakeData.policies.data.splice(i, 1);
            // },
            dataBinding: function (e) {
                clearTimeout(timer);
            },
            dataBound: function (e) {
                showLoader = true;
                // if (!resizeColumn) {
                //     autoFitColumn(e.sender);
                //     resizeColumn = true;
                // }
                // $('#button-add').kendoButton({
                //     rounded: 'medium',
                // });
                // $('#button-refresh').kendoButton({
                //     icon: 'refresh',
                // });
                // $('#button-clear').kendoButton({
                //     rounded: 'medium',
                // });
                // $('#button-debug-pol').kendoButton({
                //     size: 'medium',
                // });
                // $('#button-exec-pol').kendoButton({
                //     size: 'medium',
                // });

                // window.newPolicyRow = () => {
                //     let grid = $('#policies-grid').data('kendoGrid');
                //     grid.addRow();
                // };
                // window.debugPolicy = () => {
                //     $('#policies-window').data('kendoWindow').open().center();
                // };

                // window.clearGridFilter = () => {
                //     $('#policies-grid').data('kendoGrid').dataSource.filter({});
                // };

                // window.refreshGrid = () => {
                //     $('#policies-grid').data('kendoGrid').dataSource.read();
                // };

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
                // {
                //     field: "enabled",
                //     title: "&nbsp;",
                //     width: 44,
                //     template: "<div class='marker block #=enabled == 1 ? 'green' : 'red'#'><i></i></div>",
                //     filterable: false,
                // },
                {
                    field: 'id',
                    title: '#',
                    // width: 33,
                    filterable: false,
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

    // window.optimize_grid(['#policies-grid']);
}
