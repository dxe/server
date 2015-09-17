$(function(){
  function initialize() {
    var mapOptions = {
      zoom: 2,
      // center: {lat: 40.0894127, lng: -98.7182132}, // somewhere in Kansas, middle of US
      center: {lat: 0, lng: 0}, // equator + prime meridian
      mapTypeId: google.maps.MapTypeId.ROADMAP,
      styles:
        [{"featureType":"water","stylers":[{"color":"#46bcec"},{"visibility":"on"}]},{"featureType":"landscape","stylers":[{"color":"#f2f2f2"}]},{"featureType":"road","stylers":[{"saturation":-100},{"lightness":45}]},{"featureType":"road.highway","stylers":[{"visibility":"simplified"}]},{"featureType":"road.arterial","elementType":"labels.icon","stylers":[{"visibility":"off"}]},{"featureType":"administrative","elementType":"labels.text.fill","stylers":[{"color":"#444444"}]},{"featureType":"transit","stylers":[{"visibility":"off"}]},{"featureType":"poi","stylers":[{"visibility":"off"}]}]
    };

    var map = new google.maps.Map(document.getElementById('map-canvas'), mapOptions);

    $.getJSON("chapter_data.json", function(data){
      $.each(data, function(i, chapter){
        console.log(chapter);

        var contentString = '<div id="content">'+
            '<div id="siteNotice">'+
            '<h1 id="firstHeading" class="firstHeading">' + chapter.name + '</h1>'+
            '<div id="bodyContent">'+
            '<p> So this place is cool. They might have a facebook: ' + chapter.facebook + '.</p>'
            '</div>'+
            '</div>'+
            '</div>';

        var infowindow = new google.maps.InfoWindow({
          content: contentString
        });


        var marker = new google.maps.Marker({
          position: new google.maps.LatLng(chapter.lat, chapter.long),
          title: chapter.name
        });
        marker.addListener('click', function() {
          infowindow.open(map, marker);
        });
        marker.setMap(map);
      });
    });
  }

  google.maps.event.addDomListener(window, 'load', initialize);
});
