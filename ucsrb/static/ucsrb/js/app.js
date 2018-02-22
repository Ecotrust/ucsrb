var app = {
    /**
    * set app state for process method
    * init a process method
    * @param {string} method value from data-attr on html element
    */
    setState: function(method) {
        app.state.setMethod = method;
        app.init[method]();
    },
}

app.init = {
    'select': function() {
        // TODO get bbox from map window and assign to var
        var bbox = [-13505560.671219192, 6217028.00835033, -13356557.351569131, 6280740.477905572];
        app.request.get_segment_by_bbox(bbox)
        .then(function(data) {
            app.map.layer.streams.init(data);
        })
        .then(function() {
            app.map.getView().fit(bbox, {
                duration: 1000
            })
        })
        .then(function() {
            app.map.interaction.select.segment();
        })
        .then(function() {
            app.map.addLayer(app.map.layer.demo_streams);
            // app.map.addLayer(app.map.layer.demo_stream);
        })
        .catch(function(data) {
            console.warn('failed to add map layer');
        });
    },
    'filter': function() {
        app.map.addLayer(app.map.layer.huc10);
    },
    'draw': function() {
        app.map.interaction.draw.init();
    }
}

app.nav = {
    setState: function(height) {
        app.state.navHeight = height;
    },
    short: function() {
        app.state.navHeight = 'short'; // set state
        // style nav
        $('.nav-wrap').addClass('icons-only');
        $('.map-wrap').addClass('short-nav');
        $('.overlay').addClass('fade-out short-overlay');
        setTimeout(function() {
            $('#process-nav').addClass('justify-content-start');
            $('#process-nav').removeClass('justify-content-center');
            $('#process-nav .col').each(function(i) {
                $(this).addClass('col-2');
            })
            $('.overlay').removeClass('fade-out');
            app.state.step = 0;
        }, 1000);
    },
    tall: function() {
        app.state.navHeight = 'tall'; // set state
        $('.nav-wrap').removeClass('icons-only');
        $('.nav-wrap').removeClass('short-nav');
        setTimeout(function() {
            $('#process-nav').removeClass('justify-content-start');
            $('#process-nav').addClass('justify-content-center');
            $('#process-nav .col').each(function(i) {
                $(this).removeClass('col-2');
            })
        }, 1000);
    },
    instructions: {
        select: [
            'Select the stream segment where you want to see changes in flow',
            'Select specific point along stream reach to evaluate changes in flow associated with management activity upstream',
            'Select filters to narrow your treatment region',
        ],
        filter: [
            'Select forest unit to filter',
            'Select filters to narrow your treatment area',
        ],
        draw: [
            'Click on the map to start drawing your management area',
            'Add additional points then double-click to finish; Re-select point to edit'
        ],
    },
}

app.panel = {
    moveLeft: function() {
        app.panel.element.classList.add('left');
        app.panel.element.classList.remove('right');
        app.state.panel.position = 'left'; // set state
    },
    moveRight: function() {
        app.panel.element.classList.add('right');
        app.panel.element.classList.remove('left');
        app.state.panel.position = 'right'; // set state
    },
    setContent: function(content) {
        app.state.panel.content = content;
        app.panel.element.innerHTML = content;
    },
    form: {
        init: function() {
            app.viewModel.scenarios.createNewScenario('/features/treatmentscenario/form/')
                .then(function() {
                    document.querySelector('.submit_button').addEventListener('click', function(event) {
                        window.setTimeout(function() {
                            if (app.viewModel.scenarios.scenarioForm()) {
                                console.log(`%c form not submitted; %o`, 'color: salmon;', event);
                            } else {
                                console.log(`%c form submitted; %o`, 'color: green;', event);
                                app.panel.results.init();
                            }
                        }, 3000); // what for scenarioform to be set to false.
                                    // this happens in scenario.js:94
                                    // using settimeout for now to avoid merge conflict in sceanario.js
                                    // ideally the submitForm function in scenario.js would have a completion event or be a promise
                    });
                })
        },
    },
    results: {
        element: function() {
            return document.querySelector('#results');
        },
        init: function() {
            app.panel.moveLeft();
            app.request.get_results(app.viewModel.scenarios.scenarioList()[0].uid)
                .then(function(response) {
                    app.panel.results.addAggPanel(response);
                    app.panel.results.addHydroPanel(response);
                })
                .catch(function(response) {
                    console.log('%c failed to get results: %o', 'style: salmon;', response);
                });
        },
        addAggPanel: function(content) {
            var html = `<section class="aggregate result-section">`;
                html += `<div class="media">
                            <img class="align-self-center mr-3" src="/static/ucsrb/img/icon/i_pie_chart.svg" alt="aggregate">
                            <div class="media-body">
                                <h4 class="mt-0">Aggregate</h4>
                            </div>
                            <a id="expand" href="" id="expand" /><img class="align-self-top ml-3" src="/static/ucsrb/img/icon/i_expand.svg" alt="expand" /></a>
                         </div>`;
                 html += '<h5>Forest Management</h5>';
                     html += app.panel.results.styleObject(content.aggregate_results.forest_types);
                 html += '<h5>Landforms/Topography</h5>';
                     html += app.panel.results.styleObject(content.aggregate_results['landforms/topography']);
                 html += '<button class="btn btn-outline-primary">Download</button>'
             html += '</section>';
             app.panel.setContent(html);
        },
        addHydroPanel: function(content) {

        },
        styleObject: function(obj) {
            var html = '<dl class="row">';
            for (var key in obj) {
                html += `<dd class="col-sm-5">${obj[key]}</dd>
                         <dt class="col-sm-7">${key}</dt>`
            }
            html += '</dl>'
            return html;
        },
    },
    domElement: function() { // extra function for those who dont like js getters
        return this.element;
    },
    get element() {
        return document.querySelector('#panel');
    }
}

/**
 * Application AJAX requests object and methods
    * {get_results} results for treatment scenario
    * {get_segment_by_bbox} segment by bounding box
    * {get_segment_by_id} segment by id
    * {get_pourpoint_by_id} pourpoint by id
    * {filter_results} filter results
*
*/
app.request = {
    /**
     * get results for treatment scenario
     * @param  {[number]} id treatment scenario id [on scenario this is created]
     * @return {[json]} result data
     */
    get_results: function(id) {
        return $.ajax(`/get_results_by_scenario_id/${id}`)
            .done(function(response) {
                console.log('%csuccessfully returned result: %o', 'color: green', response);
            })
            .fail(function(response) {
                console.log(`%cfail @ get planning units response: %o`, 'color: red', response);
            });
    },
    /**
    * Planning Units
    * scenario planning units to filter upon
    * @return {[json]} features list
    */
    get_planningunits: function() {
        return $.ajax('/scenario/get_planningunits')
            .done(function(response) {
                console.log('%csuccessfully returned planning units: %o', 'color: green', response);
                return response;
            })
            .fail(function(response) {
                console.log(`%cfail @ get planning units response: %o`, 'color: red', response);
            });
    },
    get_scenarios: function() {
        return $.ajax('/ucsrb/get_scenarios/')
            .done(function(response) {
                console.log('%csuccessfully got scenarios: %o', 'color: green', response);
                return response;
            })
            .fail(function(response) {
                console.log(`%cfail @ get scenarios: %o`, 'color: red', response);
            });
    },
    /**
    * get stream segments by bounding box
    * @param {Array} bbox coords from map view
    */
    get_segment_by_bbox: function(bbox) {
        return $.ajax({
            url: `/get_segment_by_bbox`,
            data: {
                bbox_coords: bbox
            },
            dataType: 'json'
        })
            .done(function(response) {
                console.log('%csuccessfully returned segments by bbox', 'color: green');
                return response;
            })
            .fail(function(response) {
                console.log(`%cfail @ get segment by bbox: %o`, 'color: red', response);
                return false;
            });
    },
    /**
     * Request stream segement by id
     * @param {number|int} id
     * @returns {Object} stream segement
     * @property segment name id geometry pourpoints[id, geometry, name]
     */
    get_segment_by_id: function(id) {
        return $.ajax(`/segment/${id}`)
            .done(function(response) {
                return response;
            })
            .fail(function(response) {
                console.log(`%cfail @ segment by id: %o`, 'color: red', response);
            });
    },
    /**
     * Request pourpoint by id
     * @param {number|int} id
     * @returns {Object} pourpoint
     * @property name id acres point_geometry area_geometry
     */
    get_pourpoint_by_id: function(id) {
        return $.ajax(`pourpoint/${id}`)
            .done(function(response) {
                return response;
            })
            .fail(function(response) {
                console.log(`%cfail @ get pourpoint id: %o`, 'color: red', response);
            });
    },
    /**
     * get a pourpoint's basin
     * @param  {number} pp_id [id]
     * @return {[GeoJSON]} drainage basin
     */
    get_basin: function(pp_id) {
        return $.ajax({
            url: '/viewer/select/get_basin',
            data: {
                pourPoint: pp_id,
                method: app.state.method,
            },
            dataType: 'json',
            success: function(response) {
                console.log(`%csuccess: got basin`, 'color: green');
                return response;
            },
            error: function(response, status) {
                console.log(`%cfail @ get basin: %o`, 'color: red', response);
                return status;
            }
        })
    },
    filter_results: function(pourpoint) {
        $.ajax({
            url: "/api/filter_results",
            data: {
                ppid: pourpoint
            },
        })
    },
    saveState: function() {
        $.ajax({
            url: '/sceanrio/treatmentscenario/save',
            type: 'POST',
            data: app.saveState,
            dataType: 'json',
            success: function(response, status) {
                console.log(`%csuccess: ${response}`, 'color: green');
                return status;
            },
            error: function(response, status) {
                console.log(`%cfail @ save state: %o`, 'color: red', response);
                return status;
            }
        })
    }
}
