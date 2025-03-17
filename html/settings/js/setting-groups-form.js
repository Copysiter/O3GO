function showSettingGroupsEditForm(model) {
    let settingsForm = $('#form-edit-setting-groups').kendoForm({
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
                field: 'api_keys',
                label: 'Api Keys',
                editor: 'MultiSelect',
                editorOptions: {
                    dataSource: new kendo.data.DataSource({
                        transport: {
                            read: {
                                url: `http://${api_base_url}/api/v1/options/api_key`,
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
                    noDataTemplate: function (e) {
                        let value = e.instance.input.val();
                        return `
                        <div class='no-data'>
                        <p>Api Key not found.<br>Do you want to add new Api Key ${value} ?</p> 
                        <button class="k-button k-button-solid-base k-button-solid k-button-md k-rounded-md" onclick="addNew('${value}', 'form-edit-setting-groups')">Append</button>
                        </p>
                        `;
                    },
                },
                colSpan: 12,
            },
        ].concat(form_items).concat([
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
        ]),
        change: function (e) {},
    });
    return settingsForm;
}

function addNew(value, id) {
    let widget = $(`#${id} #api_keys`).data('kendoMultiSelect');
    let dataSource = widget.dataSource;
    dataSource.add({
        text: value,
        value: value,
    });
    let allSelected = widget
        .dataItems()
        .concat(dataSource.data()[dataSource.data().length - 1]);
    let multiData = [];
    for (let i = 0; i < allSelected.length; i++) {
        multiData.push({
            text: allSelected[i].text,
            value: allSelected[i].value,
        });
    }
    widget.value(multiData);
    widget.trigger('change');
    widget.close();
    document.querySelector(`#${id} .k-selection-multiple`).lastChild.value = '';
}