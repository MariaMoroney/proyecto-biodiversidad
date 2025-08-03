// api.js - Cliente API para EcoVision Marine System
const API_CONFIG = {
    BASE_URL: 'http://localhost:8001/api',  // ✅ Actualizado al puerto del backend
    TIMEOUT: 10000,
    RETRY_ATTEMPTS: 3,
    RETRY_DELAY: 1000
};

const DEFAULT_HEADERS = {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
};

class MarineEcoAPI {
    constructor() {
        this.baseURL = API_CONFIG.BASE_URL;
        this.timeout = API_CONFIG.TIMEOUT;
        this.isOnline = false;
    }

    async makeRequest(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const config = {
            method: 'GET',
            headers: { ...DEFAULT_HEADERS },
            signal: AbortSignal.timeout(this.timeout),
            ...options
        };

        console.log(`🌊 Marine API Request: ${config.method} ${url}`);

        for (let attempt = 1; attempt <= API_CONFIG.RETRY_ATTEMPTS; attempt++) {
            try {
                const response = await fetch(url, config);

                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }

                const data = await response.json();
                console.log(`✅ Marine API Response: ${endpoint}`, data);
                this.isOnline = true;
                return data;

            } catch (error) {
                console.warn(`⚠️ Intento ${attempt} falló para ${endpoint}:`, error.message);

                if (attempt === API_CONFIG.RETRY_ATTEMPTS) {
                    console.error(`❌ Todos los intentos fallaron para ${endpoint}`);
                    this.isOnline = false;
                    throw new APIError(endpoint, error.message, attempt);
                }

                await this.delay(API_CONFIG.RETRY_DELAY * attempt);
            }
        }
    }

    // ===================== DASHBOARD & STATS =====================

    async getDashboardStats() {
        try {
            return await this.makeRequest('/dashboard/stats');
        } catch (error) {
            console.error('Error obteniendo estadísticas del dashboard:', error);
            return this.getFallbackDashboardStats();
        }
    }

    async getSystemHealth() {
        try {
            return await this.makeRequest('/health');
        } catch (error) {
            console.error('Error verificando salud del sistema:', error);
            return { status: 'offline', service: 'EcoVision Marine API' };
        }
    }

    // ===================== ESPECIES MARINAS =====================

    async getAllSpecies(skip = 0, limit = 100) {
        try {
            return await this.makeRequest(`/species?skip=${skip}&limit=${limit}`);
        } catch (error) {
            console.error('Error obteniendo especies:', error);
            return this.getFallbackSpeciesData();
        }
    }

    async getSpeciesCategories() {
        try {
            return await this.makeRequest('/species/categories');
        } catch (error) {
            console.error('Error obteniendo categorías de especies:', error);
            return this.getFallbackCategories();
        }
    }

    async getSpeciesByCategory(category) {
        try {
            const allSpecies = await this.getAllSpecies();
            if (category === 'all' || !category) return allSpecies;
            return allSpecies.filter(species =>
                species.species_category?.toLowerCase() === category.toLowerCase()
            );
        } catch (error) {
            console.error(`Error filtrando especies por categoría ${category}:`, error);
            return this.getFallbackSpeciesData();
        }
    }

    // ===================== MAPA & AVISTAMIENTOS =====================

    async getMapData() {
        try {
            return await this.makeRequest('/sightings/map-data');
        } catch (error) {
            console.error('Error obteniendo datos del mapa:', error);
            return this.getFallbackMapData();
        }
    }

    async getRecentSightings(limit = 20) {
        try {
            return await this.makeRequest(`/species?limit=${limit}`);
        } catch (error) {
            console.error('Error obteniendo avistamientos recientes:', error);
            return [];
        }
    }

    // ===================== REPORTES CIUDADANOS =====================

    async submitMarineSighting(sightingData) {
        try {
            console.log('🐠 Enviando reporte de avistamiento marino...');

            // Validar datos requeridos
            const requiredFields = ['species_name', 'location', 'latitude', 'longitude', 'sighting_date', 'observer_name'];
            for (const field of requiredFields) {
                if (!sightingData[field]) {
                    throw new Error(`Campo requerido faltante: ${field}`);
                }
            }

            let body, headers;
            if (sightingData.photo) {
                // Si hay foto, usar FormData
                body = new FormData();
                Object.keys(sightingData).forEach(key => {
                    if (sightingData[key] !== null && sightingData[key] !== undefined) {
                        body.append(key, sightingData[key]);
                    }
                });
                headers = { 'Accept': 'application/json' };
            } else {
                // JSON normal
                body = JSON.stringify(sightingData);
                headers = DEFAULT_HEADERS;
            }

            const result = await this.makeRequest('/sightings', {
                method: 'POST',
                headers,
                body
            });

            console.log('✅ Reporte de avistamiento enviado exitosamente:', result);
            return result;

        } catch (error) {
            console.error('❌ Error enviando reporte de avistamiento:', error);
            throw error;
        }
    }

    async getRecentReports(limit = 20) {
        try {
            return await this.makeRequest(`/species?limit=${limit}`);
        } catch (error) {
            console.error('Error obteniendo reportes recientes:', error);
            return [];
        }
    }

    // ===================== PIPELINE ETL =====================

    async runPipeline() {
        try {
            console.log('🔄 Ejecutando pipeline ETL marino...');
            const result = await this.makeRequest('/pipeline/run', {
                method: 'POST'
            });

            console.log('✅ Pipeline ETL ejecutado exitosamente:', result);

            // Mostrar notificación si existe la función
            if (window.EcoVision?.showToast) {
                window.EcoVision.showToast('Pipeline ejecutado correctamente 🚀', 'success');
            }

            return result;

        } catch (error) {
            console.error('❌ Error ejecutando pipeline ETL:', error);

            if (window.EcoVision?.showToast) {
                window.EcoVision.showToast('Error ejecutando pipeline ❌', 'error');
            }

            throw error;
        }
    }

    async getPipelineStatus() {
        try {
            return await this.makeRequest('/pipeline/status');
        } catch (error) {
            console.error('Error obteniendo estado del pipeline:', error);
            return this.getFallbackPipelineStatus();
        }
    }

    async getPipelineLogs(limit = 10) {
        try {
            return await this.makeRequest(`/pipeline/logs?limit=${limit}`);
        } catch (error) {
            console.error('Error obteniendo logs del pipeline:', error);
            return this.getFallbackPipelineLogs();
        }
    }

    // ===================== DATOS LIMPIOS (REQUERIDO ENTREGABLE) =====================

    async getCleanedData() {
        try {
            return await this.makeRequest('/cleaned-data');
        } catch (error) {
            console.error('Error obteniendo datos limpios:', error);
            return this.getFallbackCleanedData();
        }
    }

    async exportCleanedData(format = 'json') {
        try {
            return await this.makeRequest(`/cleaned-data/export?format=${format}`);
        } catch (error) {
            console.error(`Error exportando datos en formato ${format}:`, error);
            throw error;
        }
    }

    // ===================== ANÁLISIS & TENDENCIAS =====================

    async getPopulationTrends(timeRange = 'month') {
        try {
            // Para desarrollo, usar datos del dashboard
            const stats = await this.getDashboardStats();
            return this.generateTrendsFromStats(stats, timeRange);
        } catch (error) {
            console.error('Error obteniendo tendencias de población:', error);
            return this.getFallbackTrendsData();
        }
    }

    generateTrendsFromStats(stats, timeRange) {
        // Generar datos de tendencias basados en estadísticas actuales
        const periods = timeRange === 'week' ? 7 : timeRange === 'month' ? 30 : 365;
        const labels = [];
        const data = [];

        for (let i = periods; i >= 0; i--) {
            const date = new Date();
            date.setDate(date.getDate() - i);
            labels.push(date.toLocaleDateString('es-CR', {
                month: 'short',
                day: 'numeric'
            }));

            // Simular variación en los datos
            const baseValue = stats.totalSightings || 100;
            const variation = Math.sin(i * 0.2) * 10 + Math.random() * 20;
            data.push(Math.max(0, Math.floor(baseValue * 0.1 + variation)));
        }

        return {
            labels,
            datasets: [{
                label: 'Avistamientos',
                data,
                borderColor: '#3b82f6',
                backgroundColor: 'rgba(59, 130, 246, 0.1)',
                fill: true
            }]
        };
    }

    // ===================== DATOS MOCK FALLBACK =====================

    getFallbackDashboardStats() {
        console.log('🌊 Usando datos mock para dashboard marino');
        return {
            totalSightings: 1247,
            recentSightings: 23,
            speciesCount: 89,
            pendingValidation: 12,
            systemStatus: "Offline - Datos mock"
        };
    }

    getFallbackSpeciesData() {
        console.log('🐠 Usando datos mock para especies marinas');
        return [
            {
                id: 1,
                species_name: "Ballena Jorobada",
                species_category: "Mamífero",
                location: "Golfo de Papagayo",
                latitude: 10.5,
                longitude: -85.8,
                sighting_date: "2024-01-15T10:30:00Z",
                observer_name: "Carlos Marín",
                validation_status: "confirmed",
                data_quality_score: 0.95
            },
            {
                id: 2,
                species_name: "Delfín Nariz de Botella",
                species_category: "Mamífero",
                location: "Bahía Drake",
                latitude: 8.7,
                longitude: -83.6,
                sighting_date: "2024-01-20T14:15:00Z",
                observer_name: "Ana Rodríguez",
                validation_status: "confirmed",
                data_quality_score: 0.88
            },
            {
                id: 3,
                species_name: "Tortuga Verde",
                species_category: "Reptil",
                location: "Playa Ostional",
                latitude: 10.3,
                longitude: -85.9,
                sighting_date: "2024-01-18T08:45:00Z",
                observer_name: "Miguel Torres",
                validation_status: "pending",
                data_quality_score: 0.92
            }
        ];
    }

    getFallbackMapData() {
        console.log('🗺️ Usando datos mock para mapa');
        return this.getFallbackSpeciesData().map(species => ({
            id: species.id,
            lat: species.latitude,
            lng: species.longitude,
            species: species.species_name,
            location: species.location,
            date: species.sighting_date,
            observer: species.observer_name,
            status: species.validation_status
        }));
    }

    getFallbackCategories() {
        return {
            categories: ["Mamífero", "Pez", "Reptil", "Invertebrado"],
            total: 4
        };
    }

    getFallbackPipelineStatus() {
        return {
            status: 'unknown',
            message: 'Backend no disponible - usando datos mock',
            last_execution: new Date().toISOString(),
            records_processed: 0,
            execution_time: 0
        };
    }

    getFallbackPipelineLogs() {
        return [
            {
                id: 1,
                execution_date: new Date().toISOString(),
                records_extracted: 0,
                records_transformed: 0,
                records_loaded: 0,
                records_rejected: 0,
                execution_time_seconds: 0,
                status: 'mock',
                error_message: 'Usando datos mock - backend no disponible'
            }
        ];
    }

    getFallbackCleanedData() {
        console.log('🧹 Usando datos mock para datos limpios');
        return this.getFallbackSpeciesData();
    }

    getFallbackTrendsData() {
        console.log('📈 Usando datos mock para tendencias');
        return {
            labels: ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun'],
            datasets: [{
                label: 'Avistamientos',
                data: [12, 19, 3, 5, 2, 3],
                borderColor: '#3b82f6',
                backgroundColor: 'rgba(59, 130, 246, 0.1)'
            }]
        };
    }

    // ===================== UTILIDADES =====================

    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    async healthCheck() {
        try {
            const health = await this.getSystemHealth();
            return health.status === 'healthy';
        } catch (error) {
            console.warn('❌ Backend no disponible:', error.message);
            return false;
        }
    }

    setBaseURL(newBaseURL) {
        this.baseURL = newBaseURL;
        console.log(`🔧 Base URL actualizada: ${newBaseURL}`);
    }

    getConnectionStatus() {
        return this.isOnline;
    }
}

// Clase de error personalizada
class APIError extends Error {
    constructor(endpoint, message, attempts) {
        super(`Marine API Error en ${endpoint}: ${message} (${attempts} intentos)`);
        this.name = 'MarineAPIError';
        this.endpoint = endpoint;
        this.attempts = attempts;
    }
}

// Instancia global de la API
const MarineAPI = new MarineEcoAPI();

// Interfaz pública para compatibilidad con tu frontend
window.EcoVisionAPI = {
    // Dashboard
    getStats: () => MarineAPI.getDashboardStats(),
    getHealth: () => MarineAPI.getSystemHealth(),

    // Especies
    getSpecies: (skip, limit) => MarineAPI.getAllSpecies(skip, limit),
    getSpeciesByCategory: (category) => MarineAPI.getSpeciesByCategory(category),
    getCategories: () => MarineAPI.getSpeciesCategories(),

    // Mapa
    getMapData: () => MarineAPI.getMapData(),
    getRecentSightings: (limit) => MarineAPI.getRecentSightings(limit),

    // Reportes
    submitSighting: (data) => MarineAPI.submitMarineSighting(data),
    getReports: (limit) => MarineAPI.getRecentReports(limit),

    // Pipeline ETL
    runPipeline: () => MarineAPI.runPipeline(),
    getPipelineStatus: () => MarineAPI.getPipelineStatus(),
    getPipelineLogs: (limit) => MarineAPI.getPipelineLogs(limit),

    // Datos limpios (requerido para entregable)
    getCleanedData: () => MarineAPI.getCleanedData(),
    exportData: (format) => MarineAPI.exportCleanedData(format),

    // Análisis
    getTrends: (range) => MarineAPI.getPopulationTrends(range),

    // Utilidades
    healthCheck: () => MarineAPI.healthCheck(),
    setBaseURL: (url) => MarineAPI.setBaseURL(url),
    isOnline: () => MarineAPI.getConnectionStatus()
};

// Compatibilidad con tu API anterior
window.BiodiversityAPI = window.EcoVisionAPI;

// Inicialización automática
document.addEventListener('DOMContentLoaded', async function() {
    console.log('🌊 Inicializando EcoVision Marine API...');

    const isBackendAvailable = await MarineAPI.healthCheck();

    if (isBackendAvailable) {
        console.log('✅ Backend marino conectado correctamente');
        if (window.EcoVision?.showToast) {
            window.EcoVision.showToast('Conectado al sistema marino 🌊', 'success');
        }
    } else {
        console.warn('⚠️ Usando modo offline con datos mock marinos');
        if (window.EcoVision?.showToast) {
            window.EcoVision.showToast('Modo offline - datos de demostración marina 🐠', 'warning');
        }
    }
});

console.log('🌊 EcoVision Marine API.js cargado correctamente');