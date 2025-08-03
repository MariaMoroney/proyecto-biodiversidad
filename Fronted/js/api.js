const API_CONFIG = {
    BASE_URL: 'http://localhost:8000/api',
    TIMEOUT: 10000,
    RETRY_ATTEMPTS: 3,
    RETRY_DELAY: 1000
};

const DEFAULT_HEADERS = {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
};

class BiodiversityAPI {
    constructor() {
        this.baseURL = API_CONFIG.BASE_URL;
        this.timeout = API_CONFIG.TIMEOUT;
    }

    async makeRequest(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const config = {
            method: 'GET',
            headers: { ...DEFAULT_HEADERS },
            signal: AbortSignal.timeout(this.timeout),
            ...options
        };

        console.log(`📡 API Request: ${config.method} ${url}`);

        for (let attempt = 1; attempt <= API_CONFIG.RETRY_ATTEMPTS; attempt++) {
            try {
                const response = await fetch(url, config);

                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }

                const data = await response.json();
                console.log(`✅ API Response: ${endpoint}`, data);
                return data;

            } catch (error) {
                console.warn(`⚠️ Intento ${attempt} falló para ${endpoint}:`, error.message);

                if (attempt === API_CONFIG.RETRY_ATTEMPTS) {
                    console.error(`❌ Todos los intentos fallaron para ${endpoint}`);
                    throw new APIError(endpoint, error.message, attempt);
                }

                await this.delay(API_CONFIG.RETRY_DELAY * attempt);
            }
        }
    }

    async getCleanedSpeciesData() {
        try {
            return await this.makeRequest('/cleaned-data/species');
        } catch (error) {
            console.error('Error obteniendo especies limpias:', error);
            return this.getFallbackSpeciesData();
        }
    }

    async getSpeciesByCategory(category) {
        try {
            return await this.makeRequest(`/cleaned-data/species?category=${category}`);
        } catch (error) {
            console.error(`Error obteniendo especies de categoría ${category}:`, error);
            return this.getFallbackSpeciesData().filter(species =>
                category === 'all' || species.category === category
            );
        }
    }

    async getSystemStats() {
        try {
            return await this.makeRequest('/stats/general');
        } catch (error) {
            console.error('Error obteniendo estadísticas:', error);
            return this.getFallbackStats();
        }
    }

    async getPopulationTrends(timeRange = 'month') {
        try {
            return await this.makeRequest(`/analytics/population-trends?range=${timeRange}`);
        } catch (error) {
            console.error('Error obteniendo tendencias:', error);
            return this.getFallbackTrendsData();
        }
    }

    async runPipeline() {
        try {
            console.log('🔄 Ejecutando pipeline...');
            const result = await this.makeRequest('/pipeline/run', {
                method: 'POST'
            });

            console.log('✅ Pipeline ejecutado exitosamente:', result);
            return result;

        } catch (error) {
            console.error('❌ Error ejecutando pipeline:', error);
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

    async getPipelineMetrics() {
        try {
            return await this.makeRequest('/pipeline/metrics');
        } catch (error) {
            console.error('Error obteniendo métricas del pipeline:', error);
            return this.getFallbackPipelineMetrics();
        }
    }

    async getPipelineLogs(limit = 50) {
        try {
            return await this.makeRequest(`/pipeline/logs?limit=${limit}`);
        } catch (error) {
            console.error('Error obteniendo logs del pipeline:', error);
            return this.getFallbackLogs();
        }
    }

    async getActiveAlerts() {
        try {
            return await this.makeRequest('/alerts/active');
        } catch (error) {
            console.error('Error obteniendo alertas:', error);
            return this.getFallbackAlerts();
        }
    }

    async createAlert(alertData) {
        try {
            return await this.makeRequest('/alerts', {
                method: 'POST',
                body: JSON.stringify(alertData)
            });
        } catch (error) {
            console.error('Error creando alerta:', error);
            throw error;
        }
    }

    async resolveAlert(alertId) {
        try {
            return await this.makeRequest(`/alerts/${alertId}/resolve`, {
                method: 'PATCH'
            });
        } catch (error) {
            console.error(`Error resolviendo alerta ${alertId}:`, error);
            throw error;
        }
    }

    async submitCitizenReport(reportData) {
        try {
            console.log('📸 Enviando reporte ciudadano...');

            let body, headers;
            if (reportData.photo) {
                body = new FormData();
                Object.keys(reportData).forEach(key => {
                    body.append(key, reportData[key]);
                });
                headers = { 'Accept': 'application/json' };
            } else {
                body = JSON.stringify(reportData);
                headers = DEFAULT_HEADERS;
            }

            return await this.makeRequest('/reports/citizen', {
                method: 'POST',
                headers,
                body
            });

        } catch (error) {
            console.error('Error enviando reporte ciudadano:', error);
            throw error;
        }
    }

    async getRecentReports(limit = 20) {
        try {
            return await this.makeRequest(`/reports?limit=${limit}`);
        } catch (error) {
            console.error('Error obteniendo reportes recientes:', error);
            return [];
        }
    }

    getFallbackSpeciesData() {
        console.log('📦 Usando datos mock para especies');
        return MOCK_SPECIES_DATA || [];
    }

    getFallbackStats() {
        console.log('📦 Usando datos mock para estadísticas');
        return MOCK_STATS_DATA || {
            total_species: 0,
            total_sightings: 0,
            active_alerts: 0,
            data_quality: 0
        };
    }

    getFallbackTrendsData() {
        console.log('📦 Usando datos mock para tendencias');
        return MOCK_POPULATION_TRENDS || { labels: [], datasets: [] };
    }

    getFallbackPipelineStatus() {
        return {
            status: 'unknown',
            last_run: new Date().toISOString(),
            next_run: 'Manual execution required'
        };
    }

    getFallbackPipelineMetrics() {
        console.log('📦 Usando datos mock para métricas del pipeline');
        return MOCK_PIPELINE_METRICS || {
            last_run: new Date().toISOString(),
            status: 'unknown',
            records_processed: 0,
            records_cleaned: 0,
            records_rejected: 0
        };
    }

    getFallbackAlerts() {
        console.log('📦 Usando datos mock para alertas');
        return MOCK_ENVIRONMENTAL_ALERTS || [];
    }

    getFallbackLogs() {
        return [
            {
                timestamp: new Date().toISOString(),
                level: 'info',
                message: 'Conexión con backend no disponible - usando datos mock'
            }
        ];
    }

    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    async healthCheck() {
        try {
            await this.makeRequest('/health');
            return true;
        } catch (error) {
            console.warn('❌ Backend no disponible:', error.message);
            return false;
        }
    }

    setBaseURL(newBaseURL) {
        this.baseURL = newBaseURL;
        console.log(`🔧 Base URL actualizada: ${newBaseURL}`);
    }
}

class APIError extends Error {
    constructor(endpoint, message, attempts) {
        super(`API Error en ${endpoint}: ${message} (${attempts} intentos)`);
        this.name = 'APIError';
        this.endpoint = endpoint;
        this.attempts = attempts;
    }
}

const API = new BiodiversityAPI();

window.BiodiversityAPI = {
    getSpecies: () => API.getCleanedSpeciesData(),
    getSpeciesByCategory: (category) => API.getSpeciesByCategory(category),
    getStats: () => API.getSystemStats(),
    getTrends: (range) => API.getPopulationTrends(range),

    runPipeline: () => API.runPipeline(),
    getPipelineStatus: () => API.getPipelineStatus(),
    getPipelineMetrics: () => API.getPipelineMetrics(),

    getAlerts: () => API.getActiveAlerts(),
    resolveAlert: (id) => API.resolveAlert(id),

    submitReport: (data) => API.submitCitizenReport(data),
    getReports: (limit) => API.getRecentReports(limit),

    healthCheck: () => API.healthCheck(),
    setBaseURL: (url) => API.setBaseURL(url)
};

document.addEventListener('DOMContentLoaded', async function() {
    const isBackendAvailable = await API.healthCheck();

    if (isBackendAvailable) {
        console.log('✅ Backend conectado correctamente');
        if (window.EcoVision) {
            window.EcoVision.showToast('Conectado al servidor 🌐', 'success');
        }
    } else {
        console.warn('⚠️ Usando modo offline con datos mock');
        if (window.EcoVision) {
            window.EcoVision.showToast('Modo offline - usando datos de demostración', 'warning');
        }
    }
});

console.log('📡 API.js cargado correctamente');