$(document).ready(function () {
    if (window.isAuth)
        var onSelect = function (e) {
            var splitter = $('#splitter').data('kendoSplitter');
            if (splitter) {
                for (let i = 0; i <= splitter.options.panes.length; i++) {
                    splitter.remove('.k-pane:first');
                }
                if (e.item.innerText === 'Dictionaries') {
                    var newPane = splitter.append({});
                    newPane.html("<div id='dict-grid' class='position-absolute w-100 h-100 d-flex flex-column'></div>");
                    initDictGrid();
                    initDebugDictToolbar();
                    window.optimize_grid(['#dict-grid']);
                } else if (e.item.innerText === 'Patterns and Policies') {
                    var newPane = splitter.append({
                        size: '500px',
                        min: '430px',
                    });
                    newPane.html("<div id='policies-grid' class='position-absolute w-100 h-100 d-flex flex-column'></div>");
                    initPoliciesGrid();
                    initDebugPolicyToolbar();
                    newPane = splitter.insertAfter({}, '.k-pane:first');
                    newPane.html("<div id='pattern-grid' class='position-absolute w-100 h-100 d-flex flex-column'></div>");
                    initPatternGrid();
                    initDebugPatternToolbar();
                    window.optimize_grid(['#pattern-grid', '#policies-grid']);
                }
            } else {
                initPoliciesGrid();
                initPatternGrid();
            }
        };
    if (window.isAuth)
        $('#tabstrip').kendoTabStrip({
            dataTextField: 'Name',
            value: 'Patterns and Policies',
            dataSource: [
                { Name: 'Patterns and Policies', Content: '' },
                { Name: 'Dictionaries', Content: '' },
                // { Name: 'Debug', Content: '' },
            ],
            select: onSelect,
        });
});

function initDebugPolicyToolbar() {
    // window.optimize_grid(['#policies-grid']);

    return $('#toolbar-policy').kendoToolBar({
        items: [
            {
                template: "<div class='k-window-title ps-6'>Policies</div>",
            },
            {
                type: 'spacer',
            },
            {
                type: 'button',
                text: 'Refresh',
                click: function (e) {
                    $('#policies-grid').data('kendoGrid').dataSource.read();
                },
            },
            {
                type: 'button',
                text: 'Clear Filter',
                click: function (e) {
                    $('#policies-grid').data('kendoGrid').dataSource.filter({});
                },
            },
            {
                type: 'button',
                text: 'New Policy',
                click: function (e) {
                    let grid = $('#policies-grid').data('kendoGrid');
                    grid.addRow();
                },
            },
            {
                type: 'button',
                text: 'Debug Policy',
                click: function (e) {
                    $('#policies-window').data('kendoWindow').open().center();
                },
            },
        ],
    });
}
function initDebugPatternToolbar() {
    // window.optimize_grid(['#pattern-grid']);

    return $('#toolbar-pattern').kendoToolBar({
        items: [
            {
                template: "<div class='k-window-title ps-6'>Patterns</div>",
            },
            {
                type: 'spacer',
            },
            {
                type: 'button',
                text: 'Refresh',
                click: function (e) {
                    $('#pattern-grid').data('kendoGrid').dataSource.read();
                },
            },
            {
                type: 'button',
                text: 'Clear Filter',
                click: function (e) {
                    $('#pattern-grid').data('kendoGrid').dataSource.filter({});
                },
            },
            {
                type: 'button',
                text: 'New Pattern',
                click: function (e) {
                    let grid = $('#pattern-grid').data('kendoGrid');
                    grid.addRow();
                },
            },
            {
                type: 'button',
                text: 'Debug Pattern',
                click: function (e) {
                    $('#pattern-window').data('kendoWindow').open().center();
                },
            },
        ],
    });
}
function initDebugDictToolbar() {
    // window.optimize_grid(['#dict-grid']);

    return $('#toolbar-dict').kendoToolBar({
        items: [
            {
                template: "<div class='k-window-title ps-6'>Dictionaries</div>",
            },
            {
                type: 'spacer',
            },
            {
                type: 'button',
                text: 'Refresh',
                click: function (e) {
                    $('#dict-grid').data('kendoGrid').dataSource.read();
                },
            },
            {
                type: 'button',
                text: 'Clear Filter',
                click: function (e) {
                    $('#dict-grid').data('kendoGrid').dataSource.filter({});
                },
            },
            {
                type: 'button',
                text: 'New Dictionary',
                click: function (e) {
                    let grid = $('#dict-grid').data('kendoGrid');
                    grid.addRow();
                },
            },
        ],
    });
}
