window.showAnalyticsNotification = function(message, type) {
    let notification = $('#analytics-notification').data('kendoNotification');
    if (!notification) {
        $('#analytics-notification').kendoNotification({
            position: { top: 54, right: 12 },
            stacking: 'down',
            autoHideAfter: 5000,
            width: 'auto',
        });
        notification = $('#analytics-notification').data('kendoNotification');
    }
    notification.show(message, type || 'info');
}

window.viewAnalytics = function(id) {
    const token = window.isAuth;
    const { access_token, token_type } = token;
    fetch(`${api_base_url}/api/v1/analytics/${id}/html`, {
        method: 'GET',
        headers: { Authorization: `${token_type} ${access_token}` },
    }).then(response => {
        if (!response.ok) throw new Error('HTML report is not ready');
        return response.blob();
    }).then(blob => {
        const url = window.URL.createObjectURL(blob);
        window.open(url, '_blank');
    }).catch(error => showAnalyticsNotification(error.message, 'error'));
}

window.downloadAnalytics = function(id) {
    const token = window.isAuth;
    const { access_token, token_type } = token;
    fetch(`${api_base_url}/api/v1/analytics/${id}/xlsx`, {
        method: 'GET',
        headers: { Authorization: `${token_type} ${access_token}` },
    }).then(response => {
        if (!response.ok) throw new Error('XLSX report is not ready');
        return response.blob().then(blob => ({ response, blob }));
    }).then(({ response, blob }) => {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        const disposition = response.headers.get('Content-Disposition') || '';
        const match = disposition.match(/filename=([^;]+)/);
        a.href = url;
        a.download = match ? match[1].replace(/"/g, '') : `analytics_${id}.xlsx`;
        document.body.appendChild(a);
        a.click();
        a.remove();
        window.URL.revokeObjectURL(url);
    }).catch(error => showAnalyticsNotification(error.message, 'error'));
}

window.initGrid = function() {
    let showLoader = true;
    let token = window.isAuth;
    try {
        let { access_token, token_type } = token;
        $('#analytics-grid').kendoGrid({
            dataSource: {
                transport: {
                    read: {
                        url: `${api_base_url}/api/v1/analytics/`,
                        type: 'GET',
                        beforeSend: function (request) {
                            request.setRequestHeader('Authorization', `${token_type} ${access_token}`);
                        },
                        dataType: 'json',
                    },
                    destroy: {
                        url: function (options) {
                            return `${api_base_url}/api/v1/analytics/${options.id}`;
                        },
                        type: 'DELETE',
                        dataType: 'json',
                        contentType: 'application/json',
                        beforeSend: function (request) {
                            request.setRequestHeader('Authorization', `${token_type} ${access_token}`);
                        },
                    },
                    parameterMap: function (data, type) {
                        if (data.hasOwnProperty('take')) {
                            data.limit = data.take;
                            delete data.take;
                        }
                        if (data.hasOwnProperty('page')) delete data.page;
                        if (data.hasOwnProperty('pageSize')) delete data.pageSize;
                        if (data.hasOwnProperty('filter') && data.filter) {
                            data.filter = data.filter.filters;
                        }
                        if (type === 'read') return data;
                        return kendo.stringify(data);
                    },
                },
                pageSize: 100,
                autoSync: true,
                serverPaging: true,
                serverFiltering: true,
                serverSorting: true,
                schema: {
                    data: function (response) {
                        if (response.data !== undefined) return response.data;
                        return response;
                    },
                    total: 'total',
                    model: {
                        id: 'id',
                        fields: {
                            id: { type: 'number', editable: false },
                            period: { type: 'string', editable: false },
                            status: { type: 'string', editable: false },
                            created_at: { type: 'date', editable: false },
                            finished_at: { type: 'date', editable: false },
                        },
                    },
                },
                requestStart: function () {
                    setTimeout(function () {
                        if (showLoader) $('.k-loading-mask').show();
                    });
                },
                requestEnd: function (e) {
                    if (e.type === 'destroy') {
                        showAnalyticsNotification('Analytics report deleted', 'success');
                        this.read();
                    }
                },
                error: function (e) {
                    const detail = e.xhr && e.xhr.responseJSON && e.xhr.responseJSON.detail
                        ? e.xhr.responseJSON.detail
                        : 'Failed to delete analytics report';
                    showAnalyticsNotification(detail, 'error');
                    this.read();
                },
            },
            height: '100%',
            reorderable: true,
            resizable: true,
            selectable: 'row',
            sortable: true,
            pageable: {
                refresh: true,
                pageSizes: [100, 250, 500],
            },
            filterable: {
                mode: 'menu',
                extra: false,
            },
            editable: {
                confirmation: "Delete analytics report and files?"
            },
            dataBound: function () {
                showLoader = true;
            },
            columns: [
                { field: 'id', title: '#', filterable: false },
                { field: 'period', title: 'Period' },
                {
                    field: 'status',
                    title: 'Status',
                    template: function (obj) {
                        const style = obj.status === 'done'
                            ? 'background:#e6f4ea;color:#137333;'
                            : (obj.status === 'failed'
                                ? 'background:#fce8e6;color:#c5221f;'
                                : 'background:#fef7e0;color:#9c5700;');
                        return `<span class='badge px-8 py-2 rounded' style='${style}'>${obj.status}</span>`;
                    }
                },
                { field: 'created_at', title: 'Created', format: '{0: yyyy-MM-dd HH:mm:ss}', filterable: false },
                { field: 'finished_at', title: 'Finished', format: '{0: yyyy-MM-dd HH:mm:ss}', filterable: false },
                {
                    title: 'HTML',
                    filterable: false,
                    sortable: false,
                    template: function (obj) {
                        if (obj.status !== 'done') return '—';
                        return `<a href='#' onclick='viewAnalytics(${obj.id}); return false;'>View HTML</a>`;
                    }
                },
                {
                    title: 'XLSX',
                    filterable: false,
                    sortable: false,
                    template: function (obj) {
                        if (obj.status !== 'done') return '—';
                        return `<a href='#' onclick='downloadAnalytics(${obj.id}); return false;'>Download XLSX</a>`;
                    }
                },
                {
                    command: [
                        { name: 'destroy', text: '' }
                    ],
                    title: ''
                },
                {},
            ],
        });
        window.optimize_grid(['#analytics-grid']);
    } catch (error) {
        console.warn(error);
    }
}
