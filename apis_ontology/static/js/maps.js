// Initialize map
const map = L.map('map').setView([20, 0], 2);

// Basemap layer
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 18,
    attribution: '&copy; OpenStreetMap contributors'
}).addTo(map);


const markers = L.markerClusterGroup();

// TODO: Replace this in the future with queried data
fetch("/static/data/entities.geojson")
    .then(res => res.json())
    .then(data => {

        L.geoJSON(data, {
            pointToLayer: function (feature, latlng) {

                // TODO: customise entities with appropriate icons
                const marker = L.marker(latlng);

                // popup
                const name = feature.properties.name || "Unknown";
                const type = feature.properties.type || "Unknown";
                const relation = feature.properties.relation || "Unknown";
                marker.bindPopup(
                    `<strong>${relation}</strong><br>` +
                    `<em>${type}</em>`
                );

                return marker;
            }
        }).eachLayer(layer => {
            markers.addLayer(layer);
        });

        map.addLayer(markers);
    })
    .catch(err => console.error("GeoJSON error:", err));
