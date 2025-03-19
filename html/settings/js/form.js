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
                        if (e.sender.value() == 3) {
                            $("#options").closest(".k-form-field").show();
                        } else {
                            $("#options").closest(".k-form-field").hide();
                        }
                    }
                },
                colSpan: 6,
            },
            {
                field: 'options',
                label: 'Options',
                editor: "TextArea",
                editorOptions: {
                    overflow: "auto",
                    rows: 5,
                    hidden: true
                },
                hidden: true,
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
