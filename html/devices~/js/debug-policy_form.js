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

$('#policies-window').kendoWindow({
    modal: true,
    width: 640,
    height: 'auto',
    maxHeight: '90%',
    opacity: '0.1',
    visible: false,
    animation: false,
    draggable: false,
    resizable: false,
    appendTo: 'body',
    title: 'Debug Policy',
    actions: [/*"Custom", "Minimize", "Maximize", */ 'Close'],
    open: function (e) {},
    close: function (e) {
        $('#form-debug-policy').data("kendoForm").clear();
        $("#debug-policy-result").removeClass('alert-danger').removeClass('alert-success').addClass('alert-secondary').html('Result');
    },
});

$('#form-debug-policy').kendoForm({
    orientation: 'vertical',
    layout: 'grid',
    grid: { cols: 12, gutter: '15px 10px' },
    items: [
        {
            field: 'policy_id',
            label: 'Policy',
            colSpan: 12,
            editor: 'DropDownList',
            editorOptions: {
                animation: false,
                dataSource: ds,
                dataTextField: 'name',
                dataValueField: 'id',
                optionLabel: false,
                valuePrimitive: true,
                downArrow: true,
                //validation: { required: true },
                dataBound: function (e) {
                    this.select(0);
                    this.trigger("change");
                },
                //select: function (e) {},
                //change: function (e) {},
            },
        },
        {
            field: 'sep1',
            colSpan: 12,
            label: false,
            editor: "<div class='separator mx-n15'></div>",
        },
        {
            field: 'text',
            label: 'Text',
            colSpan: 12,
            editor: 'TextArea',
            editorOptions: {
                overflow: 'hidden',
                rows: 5,
                //§placeholder: 'Enter your text...',
            },
        },
        {
            field: 'sep2',
            colSpan: 12,
            label: false,
            editor: "<div class='separator mx-n15'></div>",
        },
        {
            field: 'debug_policy_result',
            label: false,
            colSpan: 12,
            height: 50,
            editor: "<div id='debug-policy-result' class='alert alert-secondary' role='alert'>Result</div>",
        },
        {
            field: 'sep3',
            colSpan: 12,
            label: false,
            editor: "<div class='separator mx-n15'></div>",
        },
    ],
    buttonsTemplate: "<div class='w-100 mt-15 mb-n15'><button id='form-save' type='submit' class='k-button k-button-lg k-rounded-md k-button-solid k-button-solid-base me-4'>Submit</button><button id='window-cancel' class='k-button k-button-lg k-rounded-md k-button-solid k-button-solid-base k-form-clear ms-4'>Cancel</button></div>",
    submit: function(e) {
        e.preventDefault();
        let token = window.isAuth;
        try {
            let { access_token, token_type } = token;
            let data = e.model;
            let url = '/api/v1/modify/debug/policy/';
            let type = "POST";
            let result;
            $("#debug-policy-result").removeClass('alert-danger').removeClass('alert-success').addClass('alert-secondary').html('Sending...');
            $.ajax({
                url: url,
                type: type,
                dataType: 'json',
                data: JSON.stringify(data),
                contentType: 'application/json;charset=UTF-8',
                beforeSend: function (xhr) {
                    xhr.setRequestHeader ("Authorization", `${token_type} ${access_token}`);
                },
                success: function(data) {

                },
                error: function(jqXHR, textStatus, ex) {

                }
            }).then(function(data) {
                if (data[0]) {
                    //result = `<div class="alert alert-success" role="alert">${data[1]}<div class="alert alert-secondary" role="alert">`;
                    $("#debug-policy-result").removeClass('alert-secondary').removeClass('alert-danger').addClass('alert-success').html('<pre class="m-0" style="font-family:inherit;"><div class=""><span class="fw-bold">Pattern: </span>' + data[1] + '</div><span class="fw-bold">Result: </span>' + data[2] + '</div><div class=""><span class="fw-bold">Returned Text: </span>' +  data[3] + "</pre></div>");
                } else {
                    //result = `<div class="alert alert-danger" role="alert">${data[1]}<div class="alert alert-secondary" role="alert">`;
                    $("#debug-policy-result").removeClass('alert-secondary').removeClass('alert-success').addClass('alert-danger').html('<pre class="m-0" style="font-family:inherit;"><div class=""><span class="fw-bold">Pattern: </span> no matches</div><div class=""><span class="fw-bold">Returned Text: </span>' +  data[3] + "</div></pre>");
                }
            });
        } catch (error) {
            console.warn(error);
        }
    },
    clear: function (e) {
        e.preventDefault();
        $('#policies-window').data('kendoWindow').close();
    },
});
