$(document).ready(function() {
    $('.method-nav button').click(function(event) {
        app.setState(event.currentTarget.dataset.method);
        // changing the method, so filter form needs to be cleared for new query
        if ($(this).parents('#process-nav').length > 0) {
            app.state.step = 'reset';
            app.state.navHeight = 'short';
            app.state.step = 0;
        }
        setTimeout(function() {
            $('.method-nav button').each(function() {
                $(this).removeClass('active');
            })
            event.target.classList.add('active');
            app.nav.showStartOver();
        }, 900);
    });
    // app.map.layer.otm = new ol.layer.Tile({
    //     source: new ol.source.XYZ({
    //       url: 'https://{a-c}.tile.opentopomap.org/{z}/{x}/{y}.png'
    //     })
    // });
    // app.map.addLayer(app.map.layer.otm);

    $('#load-saved').on('show.bs.modal', function (event) {
        var modal = $(this);
        if (app.scenarioInProgress()) {
            app.promptToSave();
        }
        app.request.get_user_scenarios()
            .then(function(response) {
                console.log(response);
                html = '<ul id="load-saved-list">';
                for (scenario in response) {
                    html += `<li><button data-id="${response[scenario].id}">${response[scenario].name}</button> ${response[scenario].description}</li>`;
                }
                html += '</ul>';
                modal.find('.modal-body').html(html);
            })
            .then(function() {
                document.getElementById('load-saved-list').addEventListener('click', function(event) {
                    app.panel.results.init(event.target.dataset.id);
                    app.map.clearLayers();
                    $('#load-saved').modal('hide');
                    $('.method-nav button').each(function() {
                        $(this).removeClass('active');
                    });
                    $('.method-nav button[data-method="aggregate"]').addClass('active');
                    app.nav.showStartOver();
                });
            });
    });
});
