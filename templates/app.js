var map = L.map('map').setView([20.5937, 78.9629], 5);

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap contributors'
}).addTo(map);

var marker;

map.on('click', function(e) {
    updateCoordinates(e.latlng.lat, e.latlng.lng);
    if (marker) {
        map.removeLayer(marker);
    }
    marker = L.marker(e.latlng).addTo(map);
    document.getElementById('latitude').value = e.latlng.lat.toFixed(5);
    document.getElementById('longitude').value = e.latlng.lng.toFixed(5);
});

function updateCoordinates(lat, lng) {
    document.getElementById('coordinates').innerHTML = `Latitude: ${lat.toFixed(5)}, Longitude: ${lng.toFixed(5)}`;
}

function submitForm() {
    var formData = new FormData(document.getElementById('locationForm'));
    formData.forEach(function(value, key) {
        console.log(key, value);
        // Here you can send the data to your server or perform any other action
    });
}