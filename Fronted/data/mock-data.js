const MOCK_SPECIES_DATA = [
    {
        id: 1,
        species: "Quetzal Resplandeciente",
        scientific_name: "Pharomachrus mocinno",
        category: "birds",
        conservation_status: "vulnerable",
        lat: 9.5450,
        lng: -84.0080,
        timestamp: "2025-01-27T14:30:00Z",
        confidence: 0.95,
        photo_url: "https://via.placeholder.com/200x200/40B883/FFFFFF?text=Quetzal",
        habitat: "Bosque nuboso",
        reporter: "Ana García",
        weather: "nublado",
        quality_score: 98
    },
    {
        id: 2,
        species: "Perezoso de Tres Dedos",
        scientific_name: "Bradypus variegatus",
        category: "mammals",
        conservation_status: "stable",
        lat: 9.7489,
        lng: -83.7534,
        timestamp: "2025-01-27T13:15:00Z",
        confidence: 0.88,
        photo_url: "https://via.placeholder.com/200x200/8B4513/FFFFFF?text=Perezoso",
        habitat: "Bosque tropical húmedo",
        reporter: "Carlos Méndez",
        weather: "soleado",
        quality_score: 92
    },
    {
        id: 3,
        species: "Iguana Verde",
        scientific_name: "Iguana iguana",
        category: "reptiles",
        conservation_status: "stable",
        lat: 9.9281,
        lng: -84.0907,
        timestamp: "2025-01-27T12:45:00Z",
        confidence: 0.92,
        photo_url: "https://via.placeholder.com/200x200/228B22/FFFFFF?text=Iguana",
        habitat: "Zona costera",
        reporter: "María Rodríguez",
        weather: "soleado",
        quality_score: 89
    },
    {
        id: 4,
        species: "Tucán Pico Iris",
        scientific_name: "Ramphastos sulfuratus",
        category: "birds",
        conservation_status: "stable",
        lat: 10.4594,
        lng: -84.8069,
        timestamp: "2025-01-27T11:20:00Z",
        confidence: 0.91,
        photo_url: "https://via.placeholder.com/200x200/FFD700/000000?text=Tucan",
        habitat: "Bosque tropical",
        reporter: "Luis Fernández",
        weather: "lluvia ligera",
        quality_score: 94
    },
    {
        id: 5,
        species: "Mono Aullador",
        scientific_name: "Alouatta palliata",
        category: "mammals",
        conservation_status: "vulnerable",
        lat: 9.3847,
        lng: -83.8937,
        timestamp: "2025-01-27T10:30:00Z",
        confidence: 0.87,
        photo_url: "https://via.placeholder.com/200x200/8B4513/FFFFFF?text=Mono",
        habitat: "Bosque seco",
        reporter: "Patricia Jiménez",
        weather: "nublado",
        quality_score: 85
    },
    {
        id: 6,
        species: "Rana Venenosa",
        scientific_name: "Phyllobates aurotaenia",
        category: "amphibians",
        conservation_status: "endangered",
        lat: 8.9824,
        lng: -82.8451,
        timestamp: "2025-01-27T09:45:00Z",
        confidence: 0.94,
        photo_url: "https://via.placeholder.com/200x200/FF4500/FFFFFF?text=Rana",
        habitat: "Bosque lluvioso",
        reporter: "David Chen",
        weather: "lluvia",
        quality_score: 97
    },
    {
        id: 7,
        species: "Colibrí Garganta Rubí",
        scientific_name: "Archilochus colubris",
        category: "birds",
        conservation_status: "stable",
        lat: 10.1234,
        lng: -84.5678,
        timestamp: "2025-01-27T08:15:00Z",
        confidence: 0.89,
        photo_url: "https://via.placeholder.com/200x200/DC143C/FFFFFF?text=Colibri",
        habitat: "Jardín urbano",
        reporter: "Elena Vargas",
        weather: "soleado",
        quality_score: 90
    },
    {
        id: 8,
        species: "Jaguar",
        scientific_name: "Panthera onca",
        category: "mammals",
        conservation_status: "endangered",
        lat: 8.5432,
        lng: -83.1234,
        timestamp: "2025-01-27T07:30:00Z",
        confidence: 0.96,
        photo_url: "https://via.placeholder.com/200x200/DAA520/000000?text=Jaguar",
        habitat: "Bosque primario",
        reporter: "Roberto Silva",
        weather: "nublado",
        quality_score: 99
    }
];

const MOCK_STATS_DATA = {
    total_species: 247,
    total_sightings: 1429,
    active_alerts: 3,
    data_quality: 94,
    last_updated: "2025-01-27T15:00:00Z"
};

const MOCK_POPULATION_TRENDS = {
    labels: ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul'],
    datasets: [
        {
            label: 'Aves',
            data: [65, 72, 68, 74, 81, 78, 85],
            borderColor: '#40B883',
            backgroundColor: 'rgba(64, 184, 131, 0.1)',
            tension: 0.4
        },
        {
            label: 'Mamíferos',
            data: [28, 32, 29, 35, 38, 41, 43],
            borderColor: '#8B4513',
            backgroundColor: 'rgba(139, 69, 19, 0.1)',
            tension: 0.4
        },
        {
            label: 'Reptiles',
            data: [18, 21, 19, 23, 26, 24, 28],
            borderColor: '#228B22',
            backgroundColor: 'rgba(34, 139, 34, 0.1)',
            tension: 0.4
        }
    ]
};

const MOCK_ENVIRONMENTAL_ALERTS = [
    {
        id: 1,
        type: "deforestation",
        severity: "high",
        location: "Parque Nacional Corcovado",
        message: "Posible actividad de deforestación detectada en zona protegida",
        timestamp: "2025-01-27T14:45:00Z",
        coordinates: { lat: 8.5367, lng: -83.5914 },
        affected_species: ["Jaguar", "Tapir", "Oso Hormiguero"]
    },
    {
        id: 2,
        type: "pollution",
        severity: "medium",
        location: "Río Tárcoles",
        message: "Niveles elevados de contaminación en fuente de agua",
        timestamp: "2025-01-27T13:20:00Z",
        coordinates: { lat: 9.7645, lng: -84.6438 },
        affected_species: ["Cocodrilo Americano", "Aves acuáticas"]
    },
    {
        id: 3,
        type: "climate",
        severity: "medium",
        location: "Monteverde",
        message: "Cambios en patrones de temperatura afectando ecosistema",
        timestamp: "2025-01-27T12:10:00Z",
        coordinates: { lat: 10.3009, lng: -84.8066 },
        affected_species: ["Quetzal", "Rana Dorada"]
    }
];

const MOCK_PIPELINE_METRICS = {
    last_run: "2025-01-27T15:00:00Z",
    status: "success",
    records_processed: 1429,
    records_cleaned: 1387,
    records_rejected: 42,
    data_quality_score: 94.2,
    processing_time: "2.3 segundos",
    backup_files: [
        {
            type: "raw_data",
            filename: "species_raw_20250127_1500.csv",
            size: "2.4 MB",
            path: "/backups/raw/"
        },
        {
            type: "cleaned_data",
            filename: "species_cleaned_20250127_1500.csv",
            size: "2.1 MB",
            path: "/backups/cleaned/"
        }
    ],
    log_file: {
        filename: "pipeline_log_20250127_1500.json",
        size: "156 KB",
        path: "/logs/"
    }
};

const SPECIES_CATEGORIES = {
    birds: {
        name: "Aves",
        icon: "🦅",
        color: "#40B883",
        count: 128
    },
    mammals: {
        name: "Mamíferos",
        icon: "🦘",
        color: "#8B4513",
        count: 67
    },
    reptiles: {
        name: "Reptiles",
        icon: "🦎",
        color: "#228B22",
        count: 34
    },
    amphibians: {
        name: "Anfibios",
        icon: "🐸",
        color: "#FF4500",
        count: 18
    }
};

const CONSERVATION_STATUS = {
    stable: {
        name: "Estable",
        color: "#28A745",
        icon: "✅"
    },
    vulnerable: {
        name: "Vulnerable",
        color: "#FF8C00",
        icon: "⚠️"
    },
    endangered: {
        name: "En peligro",
        color: "#DC143C",
        icon: "🚨"
    },
    critical: {
        name: "Crítico",
        color: "#8B0000",
        icon: "💀"
    }
};

function generateRandomSighting() {
    const species = [
        "Mono Capuchino", "Puma", "Ocelote", "Tapir",
        "Guacamayo", "Serpiente Terciopelo", "Tortuga Verde"
    ];

    const locations = [
        { lat: 9.7489, lng: -83.7534, name: "San José" },
        { lat: 10.6340, lng: -85.4406, name: "Liberia" },
        { lat: 9.9742, lng: -84.8421, name: "Puntarenas" },
        { lat: 9.6348, lng: -83.2707, name: "Cartago" }
    ];

    const randomSpecies = species[Math.floor(Math.random() * species.length)];
    const randomLocation = locations[Math.floor(Math.random() * locations.length)];

    return {
        id: Date.now(),
        species: randomSpecies,
        lat: randomLocation.lat + (Math.random() - 0.5) * 0.1,
        lng: randomLocation.lng + (Math.random() - 0.5) * 0.1,
        timestamp: new Date().toISOString(),
        confidence: 0.8 + Math.random() * 0.2,
        location: randomLocation.name,
        reporter: "Sistema automático"
    };
}

function simulateAPIDelay(data, delay = 1000) {
    return new Promise(resolve => {
        setTimeout(() => resolve(data), delay);
    });
}

if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        MOCK_SPECIES_DATA,
        MOCK_STATS_DATA,
        MOCK_POPULATION_TRENDS,
        MOCK_ENVIRONMENTAL_ALERTS,
        MOCK_PIPELINE_METRICS,
        SPECIES_CATEGORIES,
        CONSERVATION_STATUS,
        generateRandomSighting,
        simulateAPIDelay
    };
}