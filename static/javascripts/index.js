var y = document.getElementById("startInputText");
var temp;

var startLat = undefined;
var startLng = undefined;
var startAdd = undefined;

var defaultBounds = new google.maps.LatLngBounds(
    new google.maps.LatLng(23.63936, 68.14712),
    new google.maps.LatLng(28.20453, 97.34466));

var options = {
    bounds: defaultBounds
};


// Add the datepicker function to the Date input
$('#datepicker').datepicker({
    uiLibrary: 'bootstrap4'
});


// Set the default value of datepicker to current date
function setDate() {
    var today = new Date();

    if (today.getMonth() < 9) {
        var date = '0' + (today.getMonth() + 1) + '/' + today.getDate() + '/' + today.getFullYear();
    } else {
        var date = (today.getMonth() + 1) + '/' + today.getDate() + '/' + today.getFullYear();
    }

    document.getElementById("datepicker").value = date;
}


// Adding Autocomplete Function to Date Input
google.maps.event.addDomListener(window, 'load', function () {
    var places = new google.maps.places.Autocomplete(document.getElementById('startInputText'),
        options);

    google.maps.event.addListener(places, 'place_changed', function () {
        var place = places.getPlace();

        startAdd = place.formatted_address;
        startLat = place.geometry.location.lat();
        startLng = place.geometry.location.lng();

        var mesg = "Latitude: " + startLat;
        mesg += "\nLongitude: " + startLng;
        console.log(mesg);

        document.getElementById("lat").value = startLat
        document.getElementById("lng").value = startLng
    });
});


// Get current location of user
function getLocation() {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(showPosition, showError);
    } else {
        console.log("Geolocation is not supported by this browser.");
    }
}


// Update the latitude longitude variables
function showPosition(position) {
    temp = position.coords.latitude +
        "," + position.coords.longitude;
    startLat = position.coords.latitude;
    startLng = position.coords.longitude;
    GetAddress();

    var mesg = "Latitude: " + startLat;
    mesg += "\nLongitude: " + startLng;
    console.log(mesg);

    document.getElementById("lat").value = startLat
    document.getElementById("lng").value = startLng
}


// Display errors, if any, while fetching user location
function showError(error) {
    switch (error.code) {
        case error.PERMISSION_DENIED:
            console.log("User denied the request for Geolocation.");
            break;
        case error.POSITION_UNAVAILABLE:
            console.log("Location information is unavailable.");
            break;
        case error.TIMEOUT:
            console.log("The request to get user location timed out.");
            break;
        case error.UNKNOWN_ERROR:
            console.log("An unknown error occurred.");
            break;
    }
}


// Update Date input field with fetched location from Google Places API
function GetAddress() {
    var latlngStr = temp.split(',', 2);

    var lat = parseFloat(latlngStr[0]);
    var lng = parseFloat(latlngStr[1]);

    var latlng = new google.maps.LatLng(lat, lng);

    var geocoder = geocoder = new google.maps.Geocoder();
    geocoder.geocode({
        'latLng': latlng
    }, function (results, status) {
        if (status == google.maps.GeocoderStatus.OK) {
            if (results[0]) {
                y.value = results[0].formatted_address;
                startAdd = y.value;
            }
        }
    });
}
