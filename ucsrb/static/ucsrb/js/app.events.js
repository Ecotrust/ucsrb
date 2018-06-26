$(document).ready(function() {

    var pageguideOne = tl.pg.init({
        pg_caption: '?',
        steps_element: '#tlyPageGuide',
    });

    $(function () {
      $('[data-toggle="tooltip"]').tooltip()
    });

    // set init mask of watershed
    window.setTimeout(function() {
      app.map.setBoundaryLayer(app.map.layer.boundary.layer)
  }, 100);

    // Set initial panel content
    app.nav.stepActions.initial = app.panel.getPanelContentElement.innerHTML;

    $('.method-nav button').click(function(event) {
        app.setState(event.currentTarget.dataset.method);
        // changing the method, so filter form needs to be cleared for new query
        if ($(this).parents('#process-nav').length > 0) {
            app.state.setStep = 'reset';
            app.viewModel.scenarios.reset({cancel: true});
            app.state.navHeight = 'short';
            app.state.setStep = 0;
        }
        $('.method-nav button').each(function() {
            $(this).removeClass('active');
        })
        event.target.classList.add('active');
        app.nav.showStartOver();
        app.nav.showAnonSave();

        // next set of page guide
        pageguideOne.close()
        var pageguideTwo = tl.pg.init({
            pg_caption: '?',
            steps_element: '#stepTwoPageGuide',
        });

        // disable tool tips for performance
        $('[data-toggle="tooltip"]').tooltip('dispose')

        // Hide more method details collapsable
        $('#collapsable-help-wrap').addClass('d-none');
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
            .done(function(response) {
                var html = '<ul id="load-saved-list">'
                for (scenario in response) {
                    html += `<li><button data-id="${response[scenario].id}" class="scenario-name btn btn-link">${response[scenario].name} <span class="description">${response[scenario].description}</span></button></li>`;
                }
                html += '</ul>';
                modal.find('.load-saved-wrap').html(html);
            })
            .then(function() {
                document.getElementById('load-saved-list').addEventListener('click', function(event) {
                    $('#load-saved').modal('hide');
                    app.resultsInit(event.target.dataset.id);
                    app.map.clearLayers();
                    $('.method-nav button').each(function() {
                        $(this).removeClass('active');
                    });
                    $('.method-nav button[data-method="aggregate"]').addClass('active');
                    app.nav.showStartOver();
                });
            });
    });

    $('.username-wrap').on('click', function(event) {
        if (event.target.dataset.action === 'sign-in-modal') {
            $('#login-modal').modal('show');
        }
    });

    /**
     * [description]
     * @method
     * @param  {[type]} event [description]
     * @return {[type]}       [description]
     */
    $('#nav-anon-save').on('click', function(event) {
        var reqData = {
            'Scenario Name': app.state.formModel.lastChange,
            'Scenario Type': app.state.getMethod,
            'filters': app.state.formModel.filters,
        }
        app.request.saveIntermediateScenario(reqData);
    });

    /**
     * [Check if unsaved work and ask user before it is lost]
     * @method
     * @param  {[type]} event [description]
     * @return {[type]}       [description]
     */
    $('header').on('click', function(event) {
        console.log('navigated to %o', event.target);
        if (app.viewModel.scenarios.scenarioForm()) {
            if (event.target.href > 0 && event.target.href[0] !== '#') {
                if (!window.confirm("Any unsaved changes you have made will be lost")) {
                    event.preventDefault();
                }
            } else if (event.target.button > 0 && event.target.button) {

            }
        } else {
            return;
        }
    });
});
