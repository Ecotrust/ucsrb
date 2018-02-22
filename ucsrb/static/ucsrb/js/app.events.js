$(document).ready(function() {
  $('#process-nav button').click(function(event) {
    app.setState(event.currentTarget.dataset.method);
    app.nav.short();
    setTimeout(function() {
      $('#process-nav button').each(function() {
        $(this).removeClass('active');
      })
      event.target.classList.add('active');
    }, 1000);
  });
  // app.map.layer.otm = new ol.layer.Tile({
  //     source: new ol.source.XYZ({
  //       url: 'https://{a-c}.tile.opentopomap.org/{z}/{x}/{y}.png'
  //     })
  // });
  // app.map.addLayer(app.map.layer.otm);
});
