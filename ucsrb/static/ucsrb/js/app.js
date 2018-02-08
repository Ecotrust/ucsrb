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
        // app.request.get_viewer_select();
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
            console.log('%clistening for stream segement selection...', 'color: #d6afff;');
        })
        .catch(function(data) {
            console.warn('failed to add map layer');
        });
    },
    'filter': function() {
        app.map.addLayer(app.map.layer.huc10);
    },
    'draw': function() {

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
            'Use filters to narrow your treatment region to fewer than 100 acres',
        ],
        filter: [
            'Select forest unit to filter',
            'Use filters to narrow your treatment region to fewer than 100 acres',
        ],
        draw: [
            'Click on the map to start drawing your stand',
            'Add additional points then double-click to finish; Re-select point to edit'
        ],
    },
}

app.panel = {
    form: {
        init: function() {
            app.map.layer.planningUnits.init();
            app.map.layer.scenarios.init();
            app.viewModel.scenarios.createNewScenario('/features/treatmentscenario/form/');
        },
    }
}

/*
* Application AJAX requests object and methods
* {get_segment_by_bbox} segment by bounding box
* {get_segment_by_id} segment by id
* {get_pourpoint_by_id} pourpoint by id
* {filter_results} filter results
*
*/
app.request = {
    get_viewer_select: function() {
        // return $.ajax({
        //     url: `/viewer/select`,
        //     dataType: 'html',
        //   });
    },
    /**
    * Planning Units
    * scenario planning units to filter upon
    * @return {[json]} features list
    */
    get_planningunits: function() {
        return $.ajax({
            url: '/scenario/get_planningunits',
            type: 'GET',
            dataType: 'json',
            success: function() {
                console.log('%csuccessfully returned planning units', 'color: green');
            },
        })
        .done(function(response) {
            return response;
        })
        .fail(function(response) {
            console.log(`%cfail @ get planning units response: %o`, 'color: red', response);
        });
    },
    get_scenarios: function() {
        return $.ajax({
          url: '/ucsrb/get_scenarios/',
          type: 'GET',
          dataType: 'json',
          success: function() {
              console.log('%csuccessfully got scenarios', 'color: green');
          },
        })
        .done(function(response) {
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
        // TODO get real bbox param
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
    * Returns stream segement Object
    * @returns {Object} segment
    * @property {string} name
    * @property {int} id
    * @property {geojson} geometery
    * @property {Array} pourpoints
    * @property {Object|id,geometry,name} list of objects
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
    * Returns pourpoint Object
    * @returns {Object} pourpoint
    * @property {string} name
    * @property {number} id
    * @property {number} acres
    * @property {Object} point_geometry
    * @property {Object} area_geometry
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
