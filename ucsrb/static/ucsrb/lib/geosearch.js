
/**
  * @constructor
  * @extends {ol.control.Control}
  * @param {Object=} opt_options Control options.
  * Geosearch | geocode | reverse geocode
  */
app.map.geoSearch = function(opt_options) {
    var options = opt_options || {};

    var button = document.createElement('button');
    button.setAttribute('role', 'toggle search box');

    var input = document.createElement('input');
    input.className = 'ol-geo-search-input form-control d-none';
    input.setAttribute('id', 'geo-search-input');
    input.setAttribute('placeholder', 'Search places');
    input.setAttribute('type', 'search');

    var resultsList = document.createElement('div');
    resultsList.setAttribute('id', 'autocomplete-results');

    button.addEventListener('click', app.map.geoSearch.toggleSearchBox, false);

    var element = document.createElement('div');
    element.className = 'ol-geo-search ol-unselectable ol-control geo-search form-inline';
    var wrap = document.createElement('div');
    wrap.className = 'ol-geo-search-wrap dropdown';
    element.appendChild(wrap);
    wrap.appendChild(button);
    wrap.appendChild(input);
    wrap.appendChild(resultsList);

    ol.control.Control.call(this, {
        element: element,
        target: options.target
    });
};

app.map.geoSearch.toggleSearchBox = function() {
    var resultsList = document.getElementById("autocomplete-results");
    resultsList.innerHTML = '';
    var input = document.querySelector('#geo-search-input');
    var btn = document.querySelector('.ol-geo-search button');
    if (input.classList.contains('d-none')) {
        input.classList.remove('d-none');
        app.map.geoSearch.autoCompleteLookup();
        btn.classList.add('close');
    } else {
        input.value = '';
        input.classList.add('d-none');
        btn.classList.remove('close');
        // clear pin added to map
        if (app.map.dropPin.hasOwnProperty('source')) {
            app.map.dropPin.source.clear();
        }
    }
};

/**
 * If seachbox is closed, use the built in logic of toggleSearchBox to open it.
 */
app.map.geoSearch.openSearchBox = function() {
  var input = document.querySelector('#geo-search-input');
  if (input.classList.contains('d-none')) {
    app.map.geoSearch.toggleSearchBox();
  }
}

/**
 * If seachbox is open, use the built in logic of toggleSearchBox to close it.
 */
app.map.geoSearch.closeSearchBox = function() {
  var input = document.querySelector('#geo-search-input');
  if (!input.classList.contains('d-none')) {
    app.map.geoSearch.toggleSearchBox();
  }
}


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
            if (options.length === 0) {
              resultsList.innerHTML += `<button tabindex="0" class="geosearch-result btn btn-link dropdown-item">No results found</button>`;
            } else {
              options.map(function(option, i) {
                  resultsList.innerHTML += `<button data-coords="${option.geometry.coordinates}" tabindex="0" role="button" class="btn btn-link geosearch-result dropdown-item">${option.properties.F_NAME}</button>`;
              });
              resultsList.addEventListener('click', function resultSelect(event) {
                  var x = event.target.dataset.coords.split(',');
                  var y = [parseFloat(x[0]), parseFloat(x[1])];
                  app.map.getView().animate({center: y, zoom: 14});
                  resultsList.innerHTML = '';
                  app.map.dropPin(y);
                  input.value = event.target.innerText;
              });
            }
        } else {
            resultsList.innerHTML = '';
        }
    });
}

/**
 * create array of results that match input value
 * @param  {[string]} val [search input field value]
 * @return {[Array]} options [array of matches]
 */
app.map.geoSearch.autoCompleteResults = function(val) {
    var options = [];
    for (var feature of app.map.geoSearch.geojson.features) {
        if (val.toLowerCase() === feature['properties']['F_NAME'].slice(0, val.length).toLowerCase()) {
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
