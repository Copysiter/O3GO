function editPatternForm() {
    let { access_token, token_type } = window.isAuth;
    let ds = new kendo.data.DataSource({
        transport: {
            read: {
                url: '/api/v1/option/modify-policies',
                type: 'GET',
                beforeSend: function (request) {
                    request.setRequestHeader(
                        'Authorization',
                        `${token_type} ${access_token}`
                    );
                },
                // dataType: 'jsonp',
                contentType: 'application/json',
            },
        },
    });
    return $('#form-edit-pattern').kendoForm({
        orientation: 'vertical',
        layout: 'grid',
        buttonsTemplate: '',
        grid: { cols: 12, gutter: '15px 10px' },
        items: [
            {
                field: 'policy_id',
                label: 'Policy',
                colSpan: 6,
                editor: 'DropDownList',
                editorOptions: {
                    animation: false,
                    dataSource: ds,
                    dataTextField: 'name',
                    dataValueField: 'id',
                    valuePrimitive: false,
                    downArrow: true,
                    animation: false,
                    autoClose: false,
                    validation: { required: true },
                    dataBound: function (e) {},
                    select: function (e) {},
                    change: function (e) {},
                },
            },
            {
                field: 'weight',
                label: 'Weight',
                editor: 'NumericTextBox',
                editorOptions: {
                    format: '#',
                    min: 0,
                },
                colSpan: 6,
            },
            {
                field: 'sep1',
                colSpan: 12,
                label: false,
                editor: "<div class='separator mx-n15'></div>",
            },
            {
                field: 'name',
                label: 'Description',
                colSpan: 12,
            },
            {
                field: 'sep2',
                colSpan: 12,
                label: false,
                editor: "<div class='separator mx-n15'></div>",
            },
            {
                field: 'pattern',
                label: 'Pattern',
                colSpan: 12,
                editor: 'TextArea',
                editorOptions: {
                    overflow: 'hidden',
                    rows: 5,
                    placeholder: 'Enter your pattern...',
                },
            },
            {
                field: 'sep3',
                colSpan: 12,
                label: false,
                editor: "<div class='separator mx-n15'></div>",
            },
            {
                field: 'result',
                label: 'Result',
                colSpan: 12,
                editor: 'TextArea',
                editorOptions: {
                    overflow: 'hidden',
                    rows: 5,
                },
            },
            {
                field: 'sep4',
                colSpan: 12,
                label: false,
                editor: "<div class='separator mx-n15'></div>",
            },
        ],
        change: function (e) {},
    });
}
