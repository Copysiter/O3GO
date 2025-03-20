function showEditForm(model) {
    let settingsForm = $('#form-edit-settings').kendoForm({
        orientation: 'vertical',
        formData: model,
        layout: 'grid',
        grid: { cols: 12, gutter: '15px 10px' },
        buttonsTemplate: '',
        items: [
            {
                field: 'name',
                label: 'Name',
                colSpan: 12,
            },
            {
                field: 'key',
                label: 'Key',
                colSpan: 6,
            },
            {
                field: 'order',
                label: 'Order',
                editor: 'NumericTextBox',
                editorOptions: {
                    format: "n0",
                    numberFormat: {
                        // decimal: ".",
                        groupSize: [3],
                        groupSeparator: " ",  // Устанавливаем пробел
                        pattern: ["-n", "n"]
                    }
                },
                colSpan: 6,
            },
            {
                field: 'type',
                label: 'Type',
                editor: "DropDownList",
                editorOptions: {
                    dataSource: [
                        {'value': 0, 'text': 'TEXT'},
                        {'value': 1, 'text': 'INTEGER'},
                        {'value': 2, 'text': 'BOOLEAN'},
                        {'value': 3, 'text': 'DROPDOWN'},
                        {'value': 4, 'text': 'PROXY'},
                    ],
                    dataTextField: "text",
                    dataValueField: "value",
                    // optionLabel: "Select type...",
                    valuePrimitive: true,
                    change: (e) => {
                        console.log(typeof e.sender.value(), e.sender.value());
                        switch (parseInt(e.sender.value())) {
                            case 0:
                                console.log(e.sender.value());
                                $("#options").closest(".k-form-field").hide();
                                $("#str_default").closest(".k-form-field").show();
                                $("#int_default").closest(".k-form-field").hide();
                                $("#bool_default").closest(".k-form-field").hide();
                                $("#proxy_group_default").closest(".k-form-field").hide();
                            break;
                            case 1:
                                console.log(e.sender.value());
                                $("#options").closest(".k-form-field").hide();
                                $("#str_default").closest(".k-form-field").hide();
                                $("#int_default").closest(".k-form-field").show();
                                $("#bool_default").closest(".k-form-field").hide();
                                $("#proxy_group_default").closest(".k-form-field").hide();
                            break;
                            case 2:
                                console.log(e.sender.value());
                                $("#options").closest(".k-form-field").hide();
                                $("#str_default").closest(".k-form-field").hide();
                                $("#int_default").closest(".k-form-field").hide();
                                $("#bool_default").closest(".k-form-field").show();
                                $("#proxy_group_default").closest(".k-form-field").hide();
                            break;
                            case 3:
                                console.log(e.sender.value());
                                $("#options").closest(".k-form-field").show();
                                $("#str_default").closest(".k-form-field").show();
                                $("#int_default").closest(".k-form-field").hide();
                                $("#bool_default").closest(".k-form-field").hide();
                                $("#proxy_group_default").closest(".k-form-field").hide();
                            break;
                            case 4:
                                console.log(e.sender.value());
                                $("#options").closest(".k-form-field").hide();
                                $("#str_default").closest(".k-form-field").hide();
                                $("#int_default").closest(".k-form-field").hide();
                                $("#bool_default").closest(".k-form-field").hide();
                                $("#proxy_group_default").closest(".k-form-field").show();
                            break;
                            default:
                            break;
                        }
                    }
                },
                colSpan: 6,
            },
            {
                field: 'str_default',
                label: 'Default value',
                colSpan: 6,
            },
            {
                field: 'int_default',
                label: 'Default value',
                editor: 'NumericTextBox',
                editorOptions: {
                    format: "n0"
                },
                colSpan: 6,
            },
            {
                field: 'bool_default',
                label: 'Default value',
                editor: "DropDownList",
                editorOptions: {
                    dataSource: [
                        {text: 'TRUE', value: true},
                        {text: 'FALSE', value: false}
                    ],
                    dataTextField: "text",
                    dataValueField: "value",
                    valuePrimitive: true,
                },
                colSpan: 6,
            },
            {
                field: 'proxy_group_default',
                label: 'Default value',
                editor: "DropDownList",
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
                colSpan: 6,
            },
            {
                field: 'options',
                label: 'Options',
                editor: "TextArea",
                editorOptions: {
                    overflow: "auto",
                    rows: 5
                },
                colSpan: 12
            },
            {
                field: 'sep1',
                colSpan: 12,
                label: false,
                editor: "<div class='separator mx-n15 mt-n3'></div>",
            },
            {
                field: 'description',
                label: 'Description',
                editor: "TextArea",
                editorOptions: {
                    overflow: "auto",
                    rows: 5
                },
                colSpan: 12,
            },
            {
                field: 'sep2',
                colSpan: 12,
                label: false,
                editor: "<div class='separator mx-n15 mt-n3'></div>",
            },
            {
                field: 'text',
                colSpan: 6,
                label: false,
                editor: "<div class='mt-3'>Enabled:</div>",
            },
            {
                field: 'is_active',
                label: '',
                editor: 'Switch',
                editorOptions: {
                    width: 70,
                },
                colSpan: 6,
            },
            {
                field: 'sep3',
                colSpan: 12,
                label: false,
                editor: "<div class='separator mx-n15 mt-n3'></div>",
            },
        ],
        change: function (e) {},
    });
    return settingsForm;
}
