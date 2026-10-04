// FoodBridge Core Client Script & Enhanced High-Accuracy Location Services
document.addEventListener('DOMContentLoaded', () => {
    // Initialize Bootstrap tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));
    
    // High-Accuracy GPS Auto-Detector
    const gpsButtons = document.querySelectorAll('.btn-gps-detect');
    gpsButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            const targetLatId = btn.getAttribute('data-lat-id') || 'inputLatitude';
            const targetLngId = btn.getAttribute('data-lng-id') || 'inputLongitude';
            const targetAddrId = btn.getAttribute('data-addr-id') || 'inputAddress';
            
            detectHighAccuracyGPS(btn, targetLatId, targetLngId, targetAddrId);
        });
    });
});

/**
 * High-Accuracy Hardware GPS with fallback and reverse geocoding
 */
function detectHighAccuracyGPS(buttonElement, latId, lngId, addrId) {
    if (!navigator.geolocation) {
        alert('Geolocation is not supported by your browser.');
        return;
    }

    const originalHTML = buttonElement.innerHTML;
    buttonElement.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span> Acquiring High-Precision GPS...';
    buttonElement.disabled = true;

    const geoOptions = {
        enableHighAccuracy: true, // Forces device hardware GPS instead of coarse IP
        timeout: 12000,           // 12 second timeout
        maximumAge: 0             // Do not use cached position
    };

    navigator.geolocation.getCurrentPosition(
        (position) => {
            const lat = position.coords.latitude;
            const lng = position.coords.longitude;
            const accuracy = Math.round(position.coords.accuracy);

            const latInput = document.getElementById(latId);
            const lngInput = document.getElementById(lngId);
            if (latInput) latInput.value = lat.toFixed(6);
            if (lngInput) lngInput.value = lng.toFixed(6);

            buttonElement.innerHTML = `<i class="bi bi-check-circle-fill text-success"></i> GPS Locked (±${accuracy}m)`;
            buttonElement.classList.remove('btn-outline-primary', 'btn-outline-secondary');
            buttonElement.classList.add('btn-light', 'text-success', 'border-success');
            buttonElement.disabled = false;

            // Reverse Geocode to populate address in English
            if (addrId) {
                const addrInput = document.getElementById(addrId);
                fetch(`https://nominatim.openstreetmap.org/reverse?format=jsonv2&lat=${lat}&lon=${lng}&accept-language=en`)
                    .then(res => res.json())
                    .then(data => {
                        if (data && data.display_name && addrInput && !addrInput.value) {
                            addrInput.value = data.display_name;
                        }
                    })
                    .catch(err => console.log('Reverse geocoding error:', err));
            }

            // If an active map picker exists, move marker
            if (window.activeLocationPickerMarker && window.activeLocationPickerMap) {
                window.activeLocationPickerMarker.setLatLng([lat, lng]);
                window.activeLocationPickerMap.setView([lat, lng], 16);
            }
        },
        (error) => {
            let errorMsg = 'Could not acquire precise GPS.';
            if (error.code === error.PERMISSION_DENIED) {
                errorMsg = 'Location permission was denied. Please allow location access or select your location on the map.';
            } else if (error.code === error.TIMEOUT) {
                errorMsg = 'GPS timed out. Please select on the map or search your address.';
            }
            alert(errorMsg);
            buttonElement.innerHTML = originalHTML;
            buttonElement.disabled = false;
        },
        geoOptions
    );
}

/**
 * Universal Interactive Map Pin Picker
 */
let pickerMap = null;
let pickerMarker = null;

function openLocationPickerModal(latInputId, lngInputId, addrInputId) {
    const modalEl = document.getElementById('locationPickerModal');
    if (!modalEl) return;

    const modal = new bootstrap.Modal(modalEl);
    modal.show();

    const latInput = document.getElementById(latInputId);
    const lngInput = document.getElementById(lngInputId);

    let startLat = parseFloat(latInput ? latInput.value : 13.0827) || 13.0827;
    let startLng = parseFloat(lngInput ? lngInput.value : 80.2707) || 80.2707;

    setTimeout(() => {
        if (!pickerMap) {
            pickerMap = L.map('pickerMapContainer').setView([startLat, startLng], 15);
            L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                attribution: '&copy; OpenStreetMap contributors'
            }).addTo(pickerMap);

            pickerMarker = L.marker([startLat, startLng], {
                draggable: true,
                autoPan: true
            }).addTo(pickerMap);

            pickerMarker.bindPopup("<strong>Drag or click map to adjust exact pin</strong>").openPopup();

            // Click anywhere on map to move marker
            pickerMap.on('click', (e) => {
                pickerMarker.setLatLng(e.latlng);
                updatePickerCoordinates(e.latlng.lat, e.latlng.lng, latInputId, lngInputId, addrInputId);
            });

            // Drag marker event
            pickerMarker.on('dragend', () => {
                const pos = pickerMarker.getLatLng();
                updatePickerCoordinates(pos.lat, pos.lng, latInputId, lngInputId, addrInputId);
            });

            window.activeLocationPickerMap = pickerMap;
            window.activeLocationPickerMarker = pickerMarker;
        } else {
            pickerMap.invalidateSize();
            pickerMap.setView([startLat, startLng], 15);
            pickerMarker.setLatLng([startLat, startLng]);
        }
    }, 300);

    // Save Location Button in Modal
    const confirmBtn = document.getElementById('btnConfirmLocation');
    if (confirmBtn) {
        confirmBtn.onclick = () => {
            const pos = pickerMarker.getLatLng();
            if (latInput) latInput.value = pos.lat.toFixed(6);
            if (lngInput) lngInput.value = pos.lng.toFixed(6);
            modal.hide();
        };
    }
}

function updatePickerCoordinates(lat, lng, latInputId, lngInputId, addrInputId) {
    const latInput = document.getElementById(latInputId);
    const lngInput = document.getElementById(lngInputId);
    const addrInput = document.getElementById(addrInputId);

    if (latInput) latInput.value = lat.toFixed(6);
    if (lngInput) lngInput.value = lng.toFixed(6);

    const infoText = document.getElementById('pickerCoordsDisplay');
    if (infoText) {
        infoText.innerText = `Lat: ${lat.toFixed(6)}, Lng: ${lng.toFixed(6)}`;
    }

    // Reverse geocode in English
    fetch(`https://nominatim.openstreetmap.org/reverse?format=jsonv2&lat=${lat}&lon=${lng}&accept-language=en`)
        .then(res => res.json())
        .then(data => {
            if (data && data.display_name) {
                if (addrInput) addrInput.value = data.display_name;
                const addrDisplay = document.getElementById('pickerAddressDisplay');
                if (addrDisplay) addrDisplay.innerText = data.display_name;
            }
        })
        .catch(err => console.log(err));
}

/**
 * Search Location with Nominatim in English
 */
function searchMapAddress() {
    const query = document.getElementById('pickerSearchInput').value.trim();
    if (!query || !pickerMap) return;

    fetch(`https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(query)}&accept-language=en`)
        .then(res => res.json())
        .then(results => {
            if (results && results.length > 0) {
                const first = results[0];
                const lat = parseFloat(first.lat);
                const lon = parseFloat(first.lon);

                pickerMap.setView([lat, lon], 16);
                pickerMarker.setLatLng([lat, lon]);
                updatePickerCoordinates(lat, lon, 'inputLatitude', 'inputLongitude', 'inputAddress');
            } else {
                alert('Location not found. Please try another search term or click directly on the map.');
            }
        })
        .catch(err => console.error('Search error:', err));
}

/**
 * Quick Preset Locations (Campus, Major Centers)
 */
function setPresetLocation(lat, lng, label, addressText) {
    const latInput = document.getElementById('inputLatitude');
    const lngInput = document.getElementById('inputLongitude');
    const addrInput = document.getElementById('inputAddress') || document.getElementById('pickupAddressText');

    if (latInput) latInput.value = lat.toFixed(6);
    if (lngInput) lngInput.value = lng.toFixed(6);
    if (addrInput && addressText) addrInput.value = addressText;

    if (pickerMap && pickerMarker) {
        pickerMap.setView([lat, lng], 16);
        pickerMarker.setLatLng([lat, lng]);
    }
}
