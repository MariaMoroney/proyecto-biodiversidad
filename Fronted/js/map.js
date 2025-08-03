let map = null;
let markers = [];
let markerCluster = null;
let currentPopup = null;

const MAP_CONFIG = {
    center: [9.7489, -83.7534],
    zoom: 8,
    minZoom: 6,
    maxZoom: 18,
    maxBounds: [
        [5.5, -87.0],
        [12.0, -82.0]
    ]
};

const SPECIES_ICONS = {
    birds: {
        icon: '🦅',
        color: '#40B883',
        markerColor: 'green'
    },
    mammals: {
        icon: '🦘',
        color: '#8B4513',
        markerColor: 'brown'
    },
    reptiles: {
        icon: '🦎',
        color: '#228B22',
        markerColor: 'darkgreen'
    },
    amphibians: {
        icon: '🐸',
        color: '#FF4500',
        markerColor: 'orange'
    },
    default: {
        icon: '🦋',
        color: '#6A4C93',
        markerColor: 'purple'
    }
};

function initializeMap() {
    try {
        console.log('🗺️ Inicializando mapa interactivo...');

        map = L.map('ecoMap', {
            center: MAP_CONFIG.center,
            zoom: MAP_CONFIG.zoom,
            minZoom: MAP_CONFIG.minZoom,
            maxZoom: MAP_CONFIG.maxZoom,
            maxBounds: MAP_CONFIG.maxBounds,
            maxBoundsViscosity: 1.0
        });

        addBaseLayers();

        setupMarkerClustering();

        addCustomControls();

        if (globalData.species && globalData.species.length > 0) {
            addSpeciesMarkersToMap(globalData.species);
        }

        setupMapEvents();

        console.log('✅ Mapa inicializado correctamente');

    } catch (error) {
        console.error('❌ Error inicializando mapa:', error);
        showMapError();
    }
}

function addBaseLayers() {
    const satelliteLayer = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
        attribution: '&copy; <a href="https://www.esri.com/">Esri</a>',
        maxZoom: 18
    });

    const streetLayer = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
    });

    const topoLayer = L.tileLayer('https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://opentopomap.org">OpenTopoMap</a>'
    });

    satelliteLayer.addTo(map);

    const baseLayers = {
        "🛰️ Satélite": satelliteLayer,
        "🗺️ Calles": streetLayer,
        "🏔️ Topográfico": topoLayer
    };

    L.control.layers(baseLayers).addTo(map);
}

function setupMarkerClustering() {
    if (typeof L.markerClusterGroup === 'function') {
        markerCluster = L.markerClusterGroup({
            chunkedLoading: true,
            spiderfyOnMaxZoom: false,
            showCoverageOnHover: false,
            zoomToBoundsOnClick: true,
            maxClusterRadius: 60,
            iconCreateFunction: function(cluster) {
                const count = cluster.getChildCount();
                let className = 'marker-cluster-small';

                if (count > 10) className = 'marker-cluster-medium';
                if (count > 50) className = 'marker-cluster-large';

                return L.divIcon({
                    html: `<div><span>${count}</span></div>`,
                    className: `marker-cluster ${className}`,
                    iconSize: [40, 40]
                });
            }
        });

        map.addLayer(markerCluster);
        console.log('🔗 Clustering de marcadores habilitado');
    } else {
        console.warn('⚠️ Plugin de clustering no disponible');
    }
}

function addCustomControls() {
    const legend = L.control({ position: 'bottomright' });
    legend.onAdd = function() {
        const div = L.DomUtil.create('div', 'map-legend');
        div.innerHTML = createLegendHTML();
        return div;
    };
    legend.addTo(map);

    const info = L.control({ position: 'topright' });
    info.onAdd = function() {
        const div = L.DomUtil.create('div', 'map-info');
        div.innerHTML = `
            <div class="map-info-content">
                <h4>🦋 EcoVision</h4>
                <p>Haz clic en los marcadores para más información</p>
                <p id="markerCount">Cargando avistamientos...</p>
            </div>
        `;
        return div;
    };
    info.addTo(map);

    addControlStyles();
}

function createLegendHTML() {
    let html = '<h4>🔍 Leyenda</h4>';

    Object.keys(SPECIES_CATEGORIES).forEach(category => {
        const cat = SPECIES_CATEGORIES[category];
        const icon = SPECIES_ICONS[category] || SPECIES_ICONS.default;
        html += `
            <div class="legend-item">
                <span class="legend-icon" style="color: ${icon.color}">${icon.icon}</span>
                <span class="legend-label">${cat.name} (${cat.count})</span>
            </div>
        `;
    });

    return html;
}

function addSpeciesMarkersToMap(speciesData) {
    if (!map) {
        console.warn('⚠️ Mapa no inicializado');
        return;
    }

    console.log(`🔍 Agregando ${speciesData.length} marcadores al mapa`);

    clearMapMarkers();

    speciesData.forEach(species => {
        const marker = createSpeciesMarker(species);
        if (marker) {
            if (markerCluster) {
                markerCluster.addLayer(marker);
            } else {
                marker.addTo(map);
            }
            markers.push(marker);
        }
    });

    updateMarkerCount(speciesData.length);

    if (markers.length > 0) {
        fitMapToMarkers();
    }
}

function createSpeciesMarker(species) {
    try {
        const icon = SPECIES_ICONS[species.category] || SPECIES_ICONS.default;

        const customIcon = L.divIcon({
            className: 'custom-species-marker',
            html: `
                <div class="marker-content" style="background-color: ${icon.color}">
                    <span class="marker-icon">${icon.icon}</span>
                </div>
            `,
            iconSize: [30, 30],
            iconAnchor: [15, 15],
            popupAnchor: [0, -15]
        });

        const marker = L.marker([species.lat, species.lng], {
            icon: customIcon,
            isSpeciesMarker: true
        });

        const popupContent = createPopupContent(species);
        marker.bindPopup(popupContent, {
            maxWidth: 300,
            className: 'species-popup'
        });

        setupMarkerEvents(marker, species);

        return marker;

    } catch (error) {
        console.error('❌ Error creando marcador para especie:', species.species, error);
        return null;
    }
}

function createPopupContent(species) {
    const conservationStatus = CONSERVATION_STATUS[species.conservation_status] || CONSERVATION_STATUS.stable;
    const timeAgo = formatTimeAgo(species.timestamp);

    return `
        <div class="species-popup-content">
            <div class="popup-header">
                <img src="${species.photo_url}" alt="${species.species}" class="popup-image" />
                <div class="popup-title">
                    <h3>${species.species}</h3>
                    <p class="scientific-name">${species.scientific_name}</p>
                </div>
            </div>
            
            <div class="popup-details">
                <div class="detail-row">
                    <span class="detail-label">📍 Hábitat:</span>
                    <span class="detail-value">${species.habitat}</span>
                </div>
                
                <div class="detail-row">
                    <span class="detail-label">👤 Reportado por:</span>
                    <span class="detail-value">${species.reporter}</span>
                </div>
                
                <div class="detail-row">
                    <span class="detail-label">⏰ Hace:</span>
                    <span class="detail-value">${timeAgo}</span>
                </div>
                
                <div class="detail-row">
                    <span class="detail-label">🌤️ Clima:</span>
                    <span class="detail-value">${species.weather}</span>
                </div>
                
                <div class="detail-row">
                    <span class="detail-label">📊 Confianza:</span>
                    <span class="detail-value">${(species.confidence * 100).toFixed(0)}%</span>
                </div>
                
                <div class="detail-row">
                    <span class="detail-label">🛡️ Estado:</span>
                    <span class="detail-value status-${species.conservation_status}">
                        ${conservationStatus.icon} ${conservationStatus.name}
                    </span>
                </div>
            </div>
            
            <div class="popup-actions">
                <button onclick="viewSpeciesDetails('${species.id}')" class="btn-popup">
                    Ver Detalles
                </button>
                <button onclick="reportSimilar('${species.species}')" class="btn-popup">
                    Reportar Similar
                </button>
            </div>
        </div>
    `;
}

function setupMarkerEvents(marker, species) {
    marker.on('click', function() {
        this.getElement().classList.add('marker-active');

        map.setView([species.lat, species.lng], Math.max(map.getZoom(), 12), {
            animate: true,
            duration: 0.5
        });
    });

    marker.on('popupclose', function() {
        this.getElement().classList.remove('marker-active');
    });

    marker.on('mouseover', function() {
        this.getElement().classList.add('marker-hover');
    });

    marker.on('mouseout', function() {
        this.getElement().classList.remove('marker-hover');
    });
}

function setupMapEvents() {
    map.on('zoomend', function() {
        updateMarkerSize();
    });

    map.on('moveend', function() {
        updateVisibleMarkers();
    });

    map.on('click', function(e) {
        console.log('Clic en mapa:', e.latlng);
    });
}

function clearMapMarkers() {
    if (markerCluster) {
        markerCluster.clearLayers();
    } else {
        markers.forEach(marker => {
            map.removeLayer(marker);
        });
    }
    markers = [];
}

function fitMapToMarkers() {
    if (markers.length === 0) return;

    const group = new L.featureGroup(markers);
    map.fitBounds(group.getBounds(), {
        padding: [20, 20],
        maxZoom: 10
    });
}

function updateMarkerCount(count) {
    const countElement = document.getElementById('markerCount');
    if (countElement) {
        countElement.textContent = `${count} avistamientos visibles`;
    }
}

function updateMarkerSize() {
    const zoom = map.getZoom();
    const scale = Math.max(0.8, Math.min(1.2, zoom / 10));

    markers.forEach(marker => {
        const element = marker.getElement();
        if (element) {
            element.style.transform = `scale(${scale})`;
        }
    });
}

function updateVisibleMarkers() {
    const bounds = map.getBounds();
    let visibleCount = 0;

    markers.forEach(marker => {
        if (bounds.contains(marker.getLatLng())) {
            visibleCount++;
        }
    });

    updateMarkerCount(visibleCount);
}

function showMapError() {
    const mapContainer = document.getElementById('ecoMap');
    if (mapContainer) {
        mapContainer.innerHTML = `
            <div class="map-error">
                <div class="error-content">
                    <i class="fas fa-exclamation-triangle"></i>
                    <h3>Error al cargar el mapa</h3>
                    <p>No se pudo inicializar el mapa interactivo.</p>
                    <button onclick="initializeMap()" class="btn-retry">
                        Reintentar
                    </button>
                </div>
            </div>
        `;
    }
}

function addControlStyles() {
    const style = document.createElement('style');
    style.textContent = `
        .map-legend {
            background: white;
            border-radius: 8px;
            padding: 15px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            font-family: inherit;
        }
        
        .map-legend h4 {
            margin: 0 0 10px 0;
            color: var(--forest-green);
            font-size: 1rem;
        }
        
        .legend-item {
            display: flex;
            align-items: center;
            margin: 5px 0;
            gap: 8px;
        }
        
        .legend-icon {
            font-size: 1.2rem;
        }
        
        .legend-label {
            font-size: 0.9rem;
            color: var(--text-primary);
        }
        
        .map-info {
            background: white;
            border-radius: 8px;
            padding: 15px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            min-width: 200px;
        }
        
        .map-info h4 {
            margin: 0 0 10px 0;
            color: var(--forest-green);
        }
        
        .map-info p {
            margin: 5px 0;
            font-size: 0.9rem;
            color: var(--text-secondary);
        }
        
        .custom-species-marker {
            background: transparent;
            border: none;
        }
        
        .marker-content {
            width: 30px;
            height: 30px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 2px 8px rgba(0,0,0,0.3);
            border: 2px solid white;
            transition: all 0.3s ease;
        }
        
        .marker-icon {
            font-size: 1rem;
            filter: drop-shadow(1px 1px 1px rgba(0,0,0,0.5));
        }
        
        .marker-hover .marker-content {
            transform: scale(1.2);
            box-shadow: 0 4px 15px rgba(0,0,0,0.4);
        }
        
        .marker-active .marker-content {
            transform: scale(1.3);
            animation: pulse 1s infinite;
        }
        
        .species-popup .leaflet-popup-content {
            margin: 0;
            padding: 0;
            width: 280px !important;
        }
        
        .species-popup-content {
            font-family: inherit;
        }
        
        .popup-header {
            display: flex;
            gap: 15px;
            padding: 15px;
            background: linear-gradient(135deg, var(--leaf-green), var(--sage-green));
            color: white;
        }
        
        .popup-image {
            width: 60px;
            height: 60px;
            border-radius: 8px;
            object-fit: cover;
            border: 2px solid white;
        }
        
        .popup-title h3 {
            margin: 0;
            font-size: 1.1rem;
            text-shadow: 1px 1px 2px rgba(0,0,0,0.3);
        }
        
        .scientific-name {
            font-style: italic;
            opacity: 0.9;
            font-size: 0.9rem;
            margin: 5px 0 0 0;
        }
        
        .popup-details {
            padding: 15px;
        }
        
        .detail-row {
            display: flex;
            justify-content: space-between;
            margin: 8px 0;
            align-items: center;
        }
        
        .detail-label {
            font-weight: 500;
            font-size: 0.9rem;
            color: var(--text-secondary);
        }
        
        .detail-value {
            font-size: 0.9rem;
            color: var(--text-primary);
            text-align: right;
            max-width: 150px;
        }
        
        .status-endangered {
            color: var(--danger-red);
            font-weight: bold;
        }
        
        .status-vulnerable {
            color: var(--warning-orange);
            font-weight: bold;
        }
        
        .status-stable {
            color: var(--success-green);
            font-weight: bold;
        }
        
        .popup-actions {
            padding: 0 15px 15px 15px;
            display: flex;
            gap: 10px;
        }
        
        .btn-popup {
            flex: 1;
            padding: 8px 12px;
            border: 1px solid var(--leaf-green);
            background: transparent;
            color: var(--leaf-green);
            border-radius: 4px;
            cursor: pointer;
            font-size: 0.8rem;
            transition: all 0.3s ease;
        }
        
        .btn-popup:hover {
            background: var(--leaf-green);
            color: white;
        }
        
        .map-error {
            height: 100%;
            display: flex;
            align-items: center;
            justify-content: center;
            background: #f8f9fa;
        }
        
        .error-content {
            text-align: center;
            color: var(--text-secondary);
        }
        
        .error-content i {
            font-size: 3rem;
            color: var(--warning-orange);
            margin-bottom: 1rem;
        }
        
        .btn-retry {
            background: var(--leaf-green);
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 4px;
            cursor: pointer;
            margin-top: 1rem;
        }
        
        @media (max-width: 768px) {
            .map-legend, .map-info {
                font-size: 0.8rem;
                padding: 10px;
            }
            
            .species-popup-content {
                width: 250px !important;
            }
            
            .popup-header {
                flex-direction: column;
                text-align: center;
            }
        }
    `;
    document.head.appendChild(style);
}

window.EcoMap = {
    initialize: initializeMap,
    addMarkers: addSpeciesMarkersToMap,
    clearMarkers: clearMapMarkers,
    fitToMarkers: fitMapToMarkers
};

window.viewSpeciesDetails = function(speciesId) {
    console.log('Ver detalles de especie:', speciesId);
    window.location.href = `species.html?id=${speciesId}`;
};

window.reportSimilar = function(speciesName) {
    console.log('Reportar especie similar:', speciesName);
    window.location.href = `report.html?species=${encodeURIComponent(speciesName)}`;
};

console.log('🗺️ Map.js cargado correctamente');