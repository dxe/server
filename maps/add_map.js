$(function(){
  function initialize() {
    var mapOptions = {
      zoom: 2,
      center: {lat: 25.151388, lng: 18.509137}, // some place in Libya so that nada and aussie chapters are visible
      mapTypeId: google.maps.MapTypeId.ROADMAP,
      styles:
        [{"featureType":"administrative","elementType":"geometry.fill","stylers":[{"color":"#5e5e5e"}]},{"featureType":"administrative","elementType":"labels.text","stylers":[{"hue":"#ff0000"}]},{"featureType":"administrative","elementType":"labels.text.fill","stylers":[{"color":"#612020"},{"weight":"6.40"}]},{"featureType":"administrative","elementType":"labels.text.stroke","stylers":[{"color":"#939292"},{"weight":"3.00"},{"lightness":"-15"}]},{"featureType":"administrative.country","elementType":"geometry.fill","stylers":[{"hue":"#ff0000"},{"visibility":"on"}]},{"featureType":"administrative.country","elementType":"geometry.stroke","stylers":[{"hue":"#ff0000"},{"visibility":"on"}]},{"featureType":"administrative.land_parcel","elementType":"geometry.fill","stylers":[{"color":"#ffffff"},{"visibility":"on"}]},{"featureType":"landscape","elementType":"all","stylers":[{"color":"#f2f2f2"}]},{"featureType":"landscape","elementType":"geometry.fill","stylers":[{"visibility":"on"},{"color":"#5e5e5e"},{"weight":"1"}]},{"featureType":"poi","elementType":"all","stylers":[{"visibility":"off"}]},{"featureType":"road","elementType":"all","stylers":[{"saturation":-100},{"lightness":45},{"visibility":"simplified"}]},{"featureType":"water","elementType":"all","stylers":[{"color":"#46bcec"},{"visibility":"on"}]},{"featureType":"water","elementType":"geometry.fill","stylers":[{"color":"#282828"}]},{"featureType":"water","elementType":"labels.text","stylers":[{"visibility":"off"}]}]
// this theme: https://snazzymaps.com/style/40892/dxe-map
    };

    var map = new google.maps.Map(document.getElementById('map-canvas'), mapOptions);

    var infowindow = new google.maps.InfoWindow({});

    $.getJSON("chapter_data.json", function(data){
      $.each(data, function(i, chapter){

        var fbString = "";
        var contactString = "Email the <a href='mailto:mentoring@directactioneverywhere.com'>mentoring network</a> to be put in contact!<br>";

        if(chapter["email"]){
          contactString = "Contact: <a href='mailto:" + chapter.email + "'>Email.</a> ";
            // TODO html escaping stuff
        }
        if(chapter["facebook"]){
          fbString = "<a target='_blank' href='" + chapter.facebook + "'>Facebook.</a>";
            // TODO html escaping stuff
        }


        var contentString = '<div id="content">'+
            '<div id="siteNotice">'+
            '<h1 id="firstHeading" class="firstHeading"> DxE ' + chapter.name + '</h1>'+
            '<div id="bodyContent">'+
            '<p>' + contactString + fbString + '</p>'
            '</div>'+
            '</div>'+
            '</div>';



        var marker = new google.maps.Marker({
          position: new google.maps.LatLng(chapter.lat, chapter.long),
          title: chapter.name,
          icon: 'dxe_marker.png'
        });
        marker.addListener('click', function() {
          infowindow.setContent(contentString);
          infowindow.open(map, marker);
        });
        marker.setMap(map);
      });
    });

  // Limit the zoom level
  google.maps.event.addListener(map, 'zoom_changed', function () {
    var minZoomLevel = 2;
    if (map.getZoom() < minZoomLevel) map.setZoom(minZoomLevel);
  });
  }

  google.maps.event.addDomListener(window, 'load', initialize);

});
