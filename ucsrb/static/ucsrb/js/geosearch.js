
/**
  * @constructor
  * @extends {ol.control.Control}
  * @param {Object=} opt_options Control options.
  * Geosearch | geocode | reverse geocode
  */
app.map.geoSearch = function(opt_options) {
    var options = opt_options || {};

    var button = document.createElement('button');

    var input = document.createElement('input');
    input.className = 'ol-geo-search-input form-control d-none';
    input.setAttribute('id', 'geo-search-input');
    input.setAttribute('placeholder', 'Search ...');
    input.setAttribute('type', 'search');

    var resultsList = document.createElement('div');
    resultsList.setAttribute('id', 'autocomplete-results');
    resultsList.className = 'dropdown-menu';
    var heading = document.createElement('h6');
    heading.className = 'dropdown-header';
    heading.innerHTML = 'matches';
    resultsList.appendChild(heading);

    var toggleSearchBox = function() {
        var input = document.querySelector('#geo-search-input');
        var resultsList = document.getElementById("autocomplete-results");
        if (input.classList.contains('d-none')) {
            input.classList.remove('d-none');
            app.map.geoSearch.autoCompleteLookup();
        } else {
            input.value = '';
            input.classList.add('d-none');
        }
    };

    button.addEventListener('click', toggleSearchBox, false);

    var element = document.createElement('div');
    element.className = 'ol-geo-search ol-unselectable ol-control geo-search form-inline';
    var wrap = document.createElement('div');
    wrap.className = 'ol-geo-search-wrap';
    element.appendChild(wrap);
    wrap.appendChild(button);
    wrap.appendChild(input);
    wrap.appendChild(resultsList);

    ol.control.Control.call(this, {
        element: element,
        target: options.target
    });
};

/**
 * var to assign geojson returned from geoSearch.requestJSON
 * @type {[Object]}
 */
app.map.geoSearch.geojson;

/**
 * Geosearch geojson object to run qeuries against
 * @return {[json]} [FeatureCollection]
 * Immediately Invoked Function Expression (IIFE)
 * self-executing function
 * might as well grab all the options async upfront
 */
app.map.geoSearch.requestJSON = (function() {
    return $.ajax({
        url: '/static/ucsrb/data/gnis_3857.geojson',
        success: function(response) {
            console.log('%csuccessful returned parsed geosearch data: %o', 'color: green', JSON.parse(response));
            app.map.geoSearch.geojson = JSON.parse(response);
        },
        error: function(response) {
            console.log('%cError during geosearch: %o', 'color: red;', response);
        }
    });
})();

/**
 * search for matches to input field value
 * @return {[type]} [description]
 */
app.map.geoSearch.autoCompleteLookup = function() {
    var input = document.querySelector('#geo-search-input');
    var resultsList = document.getElementById("autocomplete-results");
    input.addEventListener('keyup', function(event) {
        var val = this.value;
        if (val.length > 2) {
            resultsList.innerHTML = '';
            var options = app.map.geoSearch.autoCompleteResults(val);
            options.map(function(option) {
                resultsList.innerHTML += `<a data-coords="${option.geometry.coordinates}" class="geosearch-result dropdown-item">${option.properties.F_NAME}</a>`;
            })
            resultsList.style.display = 'block';
            resultsList.addEventListener('click', function(event) {
                var x = event.target.dataset.coords.split(',');
                var y = [parseFloat(x[0]), parseFloat(x[1])];
                app.map.getView().animate({center: y, zoom: 14});
            });
        } else {
            resultsList.innerHTML = '';
        }
    })
}

/**
 * create array of results that match input value
 * @param  {[string]} val [search input field value]
 * @return {[Array]} options [array of matches]
 */
app.map.geoSearch.autoCompleteResults = function(val) {
    var options = [];
    for (var feature of app.map.geoSearch.geojson.features) {
        if (val === feature['properties']['F_NAME'].slice(0, val.length)) {
            options.push(feature);
        }
    }
    return options;
}

/**
 * [geoSearchControl create openlayers custom control]
 */
ol.inherits(app.map.geoSearch, ol.control.Control);
var geoSearchControl = new app.map.geoSearch();
app.map.addControl(geoSearchControl);
