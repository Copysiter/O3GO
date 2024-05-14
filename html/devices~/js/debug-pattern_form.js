$('#pattern-window').kendoWindow({
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
    title: 'Debug Pattern',
    actions: [/*"Custom", "Minimize", "Maximize", */ 'Close'],
    open: function (e) {},
    close: function (e) {
        $('#form-debug-pattern').data('kendoForm').clear();
        $("#debug-pattern-result").removeClass('alert-danger').removeClass('alert-success').addClass('alert-secondary').html('Result');
    },
});

$('#form-debug-pattern').kendoForm({
    orientation: 'vertical',
    layout: 'grid',
    grid: { cols: 12, gutter: '15px 10px' },
    items: [
        {
            field: 'pattern',
            label: 'Pattern',
            colSpan: 12,
        },
        {
            field: 'sep1',
            colSpan: 12,
            label: false,
            editor: "<div class='separator mx-n15'></div>",
        },
        {
            field: 'result',
            label: 'Result',
            colSpan: 12,
        },
        {
            field: 'sep2',
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
                //placeholder: 'Enter your text...',
            },
        },
        {
            field: 'sep3',
            colSpan: 12,
            label: false,
            editor: "<div class='separator mx-n15'></div>",
        },
        {
            field: 'debug_pattern_result',
            label: false,
            colSpan: 12,
            height: 50,
            editor: "<div id='debug-pattern-result' class='alert alert-secondary' role='alert'>Result</div>",
        },
        {
            field: 'sep4',
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
            let url = '/api/v1/modify/debug/pattern/';
            let type = "POST";
            let result;
            $("#debug-pattern-result").removeClass('alert-danger').removeClass('alert-success').addClass('alert-secondary').html('Sending...');
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
                    $("#debug-pattern-result").removeClass('alert-secondary').removeClass('alert-danger').addClass('alert-success').html('<pre class="m-0" style="font-family:inherit;"><span class="fw-bold">Returned Text: </span>' + data[1] + '</pre>');
                } else {
                    //result = `<div class="alert alert-danger" role="alert">${data[1]}<div class="alert alert-secondary" role="alert">`;
                    $("#debug-pattern-result").removeClass('alert-secondary').removeClass('alert-success').addClass('alert-danger').html('<pre class="m-0" style="font-family:inherit;"><span class="fw-bold">Returned Text: </span>' + data[1] + '</pre>');
                }
            });
        } catch (error) {
            console.warn(error);
        }
    },
    clear: function (e) {
        e.preventDefault();
        $('#pattern-window').data('kendoWindow').close();
    },
});
