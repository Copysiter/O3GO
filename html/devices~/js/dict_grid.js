function initDictGrid() {
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
                grid.autoFitColumn('name');
                // grid.autoFitColumn('dictionary');
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

        $('#dict-grid').on('dblclick', "td[role='gridcell']", function (e) {
            var text = $(this).find('.text');
            if (text.length) text.selectText();
            else $(this).selectText();
        });

        $(document).keydown(function (e) {
            if (e.key === 'Escape' && $('#dict-grid').data('kendoGrid')) {
                selectedDataItems = [];
                selectedItemIds = [];
                selectedItemImsi = [];
                $('#dict-grid').data('kendoGrid').clearSelection();
            }
        });

        return $('#dict-grid').kendoGrid({
            dataSource: {
                transport: {
                    read: {
                        url: '/api/v1/modify/dict/',
                        type: 'GET',
                        beforeSend: function (request) {
                            request.setRequestHeader('Authorization', `${token_type} ${access_token}`);
                        },
                        // dataType: 'jsonp',
                        // contentType: 'application/json',
                    },
                    create: {
                        url: '/api/v1/modify/dict/',
                        type: 'POST',
                        // dataType: 'json',
                        contentType: 'application/json',
                        headers: { 'access-control-allow-credentials': true },
                        beforeSend: function (request) {
                            request.setRequestHeader('Authorization', `${token_type} ${access_token}`);
                        },
                    },
                    update: {
                        url: function (options) {
                            console.log(options);
                            return `/api/v1/modify/dict/${options.id}`;
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
                            return `/api/v1/modify/dict/${options.id}`;
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
                            name: { type: 'string', editable: true },
                            dictionary: { type: 'object', editable: true },
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
                    template: kendo.template($('#toolbar-dict-template').html()),
                },
            ],
            height: '100%',
            reorderable: true,
            resizable: true,
            selectable: 'multiple, row',
            persistSelection: true,
            sortable: true,
            edit: function (e) {
                typeof e.model.dictionary === 'object'
                    ? (e.model.dictionary = e.model.dictionary.join('\n'))
                    : e.model.dictionary;

                editedItem = e.model;
                form.data('kendoForm').setOptions({
                    formData: e.model,
                });
                popup.setOptions({
                    title: e.model.id ? 'Edit Dictionary' : 'New Dictionary',
                });
                popup.center();
            },
            editable: {
                mode: 'popup',
                template: kendo.template($('#popup-editor-dict').html()),
                window: {
                    width: 480,
                    maxHeight: '90%',
                    animation: false,
                    appendTo: '#app-root',
                    visible: false,
                    open: function (e) {
                        // editPoliciesForm();
                        form = editDictForm();
                        // let form = $("#form-edit-policies").getKendoForm();
                        popup = e.sender;
                        popup.center();
                    },
                },
            },
            // save: function (e) {
            //     let alredyItem = window.gridsFakeData.dict.data.find((i) => {
            //         return i.dictionary_id === e.model.dictionary_id;
            //     });
            //     if (alredyItem) {
            //         alredyItem.dictionary = e.model.dictionary;
            //         alredyItem.dictionary_name = e.model.dictionary_name;
            //     } else {
            //         window.gridsFakeData.dict.data.push({
            //             dictionary: e.model.dictionary,
            //             dictionary_name: e.model.dictionary_name,
            //         });
            //     }
            // },
            // remove: function (e) {
            //     let i = window.gridsFakeData.dict.data.find((i) => {
            //         return i.dictionary_id === e.model.dictionary_id;
            //     });
            //     window.gridsFakeData.dict.data.splice(i, 1);
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
                $('#button-add-dict').kendoButton({
                    rounded: 'medium',
                });
                $('#button-refresh-dict').kendoButton({
                    icon: 'refresh',
                });
                $('#button-clear-dict').kendoButton({
                    rounded: 'medium',
                });

                window.newDictRow = () => {
                    let grid = $('#dict-grid').data('kendoGrid');
                    grid.addRow();
                };

                window.clearGridFilterDict = () => {
                    $('#dict-grid').data('kendoGrid').dataSource.filter({});
                };

                window.refreshGridDict = () => {
                    $('#dict-grid').data('kendoGrid').dataSource.read();
                };

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
                        in: 'Contains',
                        //isnotnullorempty: 'Has value',
                        //eq: 'Equal to',
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
                    field: 'count',
                    title: 'Count',
                    filterable: false,
                    template: function (obj) {
                        if (typeof(obj.dictionary) == "array") {
                            return obj.dictionary.length;
                        } else {
                            return 0;
                        }
                    }
                },
                {
                    field: 'dictionary',
                    title: 'Dictionary',
                    // width: 800,
                    filterable: {
                        cell: {
                            inputWidth: 0,
                            showOperators: true,
                            operator: 'in',
                        },
                    },
                    template: function (obj) {
                        if (!obj.dictionary) return '';
                        return '<div class="d-inline-block text-truncate" style="max-width:640px;">' + 
                            (typeof obj.dictionary === 'object' ? obj.dictionary.join(', ') : obj.dictionary) +
                            '</div>';
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

    // window.optimize_grid(['#dict-grid']);
}