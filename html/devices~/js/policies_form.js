function editPoliciesForm() {
    return $('#form-edit-policies').kendoForm({
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
                field: 'sep1',
                colSpan: 12,
                label: false,
                editor: "<div class='separator mx-n15'></div>",
            },
        ],
        change: function (e) {},
    });
}
