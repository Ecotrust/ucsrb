$(document).ready(function() {
    $('.method-nav button').click(function(event) {
        app.setState(event.currentTarget.dataset.method);
        // changing the method, so filter form needs to be cleared for new query
        if ($(this).parents('#process-nav').length > 0) {
            app.state.step = 'reset';
            app.nav.short();
        }
        setTimeout(function() {
            $('.method-nav button').each(function() {
                $(this).removeClass('active');
            })
            event.target.classList.add('active');
        }, 900);
    });
    // app.map.layer.otm = new ol.layer.Tile({
    //     source: new ol.source.XYZ({
    //       url: 'https://{a-c}.tile.opentopomap.org/{z}/{x}/{y}.png'
    //     })
    // });
    // app.map.addLayer(app.map.layer.otm);

    $('#load-saved').on('show.bs.modal', function (event) {
        var app.checkScenarioState();
    });
});
