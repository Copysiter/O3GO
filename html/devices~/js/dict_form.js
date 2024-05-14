function editDictForm() {
    return $('#form-edit-dict').kendoForm({
        orientation: 'vertical',
        layout: 'grid',
        buttonsTemplate: '',
        grid: { cols: 12, gutter: '15px 10px' },
        items: [
            {
                field: 'name',
                label: 'Name',
                colSpan: 12,
            },
            {
                field: 'dictionary',
                label: 'Dictionary',
                colSpan: 12,
                editor: 'TextArea',
                editorOptions: {
                    overflow: 'auto',
                    rows: 10,
                    placeholder: 'Enter your words...',
                    // value: Array.isArray()
                },
                // change: function (e) {
                //     console.log(e);
                // },
            },
            {
                field: 'sep1',
                colSpan: 12,
                label: false,
                editor: "<div class='separator mx-n15'></div>",
            },
        ],
    });
}
