let charts = {};

const CHART_COLORS = {
    primary: '#40B883',
    secondary: '#8B4513',
    tertiary: '#228B22',
    quaternary: '#FF4500',
    success: '#28A745',
    warning: '#FF8C00',
    danger: '#DC143C',
    info: '#87CEEB'
};

const BASE_CHART_CONFIG = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
        legend: {
            position: 'bottom',
            labels: {
                usePointStyle: true,
                padding: 20,
                font: {
                    family: 'Segoe UI, Tahoma, Geneva, Verdana, sans-serif',
                    size: 12
                }
            }
        },
        tooltip: {
            backgroundColor: 'rgba(0, 0, 0, 0.8)',
            titleColor: '#fff',
            bodyColor: '#fff',
            borderColor: '#40B883',
            borderWidth: 1,
            cornerRadius: 8,
            displayColors: true
        }
    },
    scales: {
        x: {
            grid: {
                color: 'rgba(0, 0, 0, 0.1)',
                borderColor: 'rgba(0, 0, 0, 0.1)'
            },
            ticks: {
                color: '#666',
                font: {
                    size: 11
                }
            }
        },
        y: {
            grid: {
                color: 'rgba(0, 0, 0, 0.1)',
                borderColor: 'rgba(0, 0, 0, 0.1)'
            },
            ticks: {
                color: '#666',
                font: {
                    size: 11
                }
            }
        }
    },
    animation: {
        duration: 1000,
        easing: 'easeInOutQuart'
    }
};

function initializeCharts() {
    try {
        console.log('📊 Inicializando gráficos...');

        createPopulationTrendsChart();

        createSpeciesDistributionChart();

        createDataQualityChart();

        createTemporalActivityChart();

        console.log('✅ Gráficos inicializados correctamente');

    } catch (error) {
        console.error('❌ Error inicializando gráficos:', error);
        showChartError();
    }
}

function createPopulationTrendsChart() {
    const ctx = document.getElementById('populationChart');
    if (!ctx) {
        console.warn('⚠️ Elemento populationChart no encontrado');
        return;
    }

    const config = {
        type: 'line',
        data: MOCK_POPULATION_TRENDS,
        options: {
            ...BASE_CHART_CONFIG,
            plugins: {
                ...BASE_CHART_CONFIG.plugins,
                title: {
                    display: true,
                    text: 'Tendencias de Avistamientos por Categoría',
                    color: '#2C3E2C',
                    font: {
                        size: 16,
                        weight: 'bold'
                    },
                    padding: 20
                }
            },
            scales: {
                ...BASE_CHART_CONFIG.scales,
                y: {
                    ...BASE_CHART_CONFIG.scales.y,
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Número de Avistamientos',
                        color: '#666'
                    }
                },
                x: {
                    ...BASE_CHART_CONFIG.scales.x,
                    title: {
                        display: true,
                        text: 'Período',
                        color: '#666'
                    }
                }
            },
            interaction: {
                intersect: false,
                mode: 'index'
            }
        }
    };

    charts.populationChart = new Chart(ctx, config);
}

function createSpeciesDistributionChart() {
    const ctx = document.getElementById('distributionChart');
    if (!ctx) return;

    const distributionData = {
        labels: Object.values(SPECIES_CATEGORIES).map(cat => cat.name),
        datasets: [{
            data: Object.values(SPECIES_CATEGORIES).map(cat => cat.count),
            backgroundColor: [
                CHART_COLORS.primary,
                CHART_COLORS.secondary,
                CHART_COLORS.tertiary,
                CHART_COLORS.quaternary
            ],
            borderColor: '#fff',
            borderWidth: 3,
            hoverOffset: 4
        }]
    };

    const config = {
        type: 'doughnut',
        data: distributionData,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'right',
                    labels: {
                        usePointStyle: true,
                        padding: 20,
                        generateLabels: function(chart) {
                            const data = chart.data;
                            if (data.labels.length && data.datasets.length) {
                                return data.labels.map((label, i) => {
                                    const meta = chart.getDatasetMeta(0);
                                    const ds = data.datasets[0];
                                    const arc = meta.data[i];
                                    const value = ds.data[i];
                                    const total = ds.data.reduce((a, b) => a + b, 0);
                                    const percentage = ((value / total) * 100).toFixed(1);

                                    return {
                                        text: `${label}: ${value} (${percentage}%)`,
                                        fillStyle: ds.backgroundColor[i],
                                        strokeStyle: ds.borderColor,
                                        lineWidth: ds.borderWidth,
                                        hidden: isNaN(ds.data[i]) || meta.data[i].hidden,
                                        index: i
                                    };
                                });
                            }
                            return [];
                        }
                    }
                },
                title: {
                    display: true,
                    text: 'Distribución de Especies por Categoría',
                    color: '#2C3E2C',
                    font: {
                        size: 16,
                        weight: 'bold'
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const label = context.label || '';
                            const value = context.raw;
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = ((value / total) * 100).toFixed(1);
                            return `${label}: ${value} especies (${percentage}%)`;
                        }
                    }
                }
            },
            cutout: '60%',
            animation: {
                animateRotate: true,
                animateScale: true,
                duration: 1500
            }
        }
    };

    charts.distributionChart = new Chart(ctx, config);
}

function createDataQualityChart() {
    const ctx = document.getElementById('qualityChart');
    if (!ctx) return;

    const qualityData = {
        labels: ['Datos Válidos', 'Datos Limpiados', 'Datos Rechazados'],
        datasets: [{
            data: [87, 8, 5],
            backgroundColor: [
                CHART_COLORS.success,
                CHART_COLORS.warning,
                CHART_COLORS.danger
            ],
            borderColor: '#fff',
            borderWidth: 2
        }]
    };

    const config = {
        type: 'pie',
        data: qualityData,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        usePointStyle: true,
                        padding: 15
                    }
                },
                title: {
                    display: true,
                    text: 'Calidad de Datos del Pipeline',
                    color: '#2C3E2C',
                    font: {
                        size: 14,
                        weight: 'bold'
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const percentage = context.raw;
                            return `${context.label}: ${percentage}%`;
                        }
                    }
                }
            },
            animation: {
                animateRotate: true,
                duration: 1200
            }
        }
    };

    charts.qualityChart = new Chart(ctx, config);
}

function createTemporalActivityChart() {
    const ctx = document.getElementById('temporalChart');
    if (!ctx) return;

    const temporalData = {
        labels: ['00:00', '04:00', '08:00', '12:00', '16:00', '20:00'],
        datasets: [{
            label: 'Avistamientos por Hora',
            data: [12, 8, 25, 45, 38, 22],
            backgroundColor: 'rgba(64, 184, 131, 0.2)',
            borderColor: CHART_COLORS.primary,
            borderWidth: 2,
            fill: true,
            tension: 0.4,
            pointBackgroundColor: CHART_COLORS.primary,
            pointBorderColor: '#fff',
            pointBorderWidth: 2,
            pointRadius: 5,
            pointHoverRadius: 7
        }]
    };

    const config = {
        type: 'line',
        data: temporalData,
        options: {
            ...BASE_CHART_CONFIG,
            plugins: {
                ...BASE_CHART_CONFIG.plugins,
                title: {
                    display: true,
                    text: 'Actividad de Avistamientos por Hora del Día',
                    color: '#2C3E2C',
                    font: {
                        size: 14,
                        weight: 'bold'
                    }
                }
            },
            scales: {
                ...BASE_CHART_CONFIG.scales,
                y: {
                    ...BASE_CHART_CONFIG.scales.y,
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Número de Avistamientos'
                    }
                },
                x: {
                    ...BASE_CHART_CONFIG.scales.x,
                    title: {
                        display: true,
                        text: 'Hora del Día'
                    }
                }
            }
        }
    };

    charts.temporalChart = new Chart(ctx, config);
}

function updateChartData(chartName, newData) {
    if (!charts[chartName]) {
        console.warn(`⚠️ Gráfico ${chartName} no encontrado`);
        return;
    }

    const chart = charts[chartName];

    if (newData.labels) {
        chart.data.labels = newData.labels;
    }

    if (newData.datasets) {
        chart.data.datasets = newData.datasets;
    }

    chart.update('active');

    console.log(`📊 Gráfico ${chartName} actualizado`);
}

function refreshAllCharts() {
    console.log('🔄 Actualizando todos los gráficos...');

    Object.keys(charts).forEach(chartName => {
        const chart = charts[chartName];
        if (chart) {
            chart.update('resize');
        }
    });
}

function generateRandomTrendData() {
    const months = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun'];
    const datasets = [
        {
            label: 'Aves',
            data: months.map(() => Math.floor(Math.random() * 50) + 30),
            borderColor: CHART_COLORS.primary,
            backgroundColor: 'rgba(64, 184, 131, 0.1)',
            tension: 0.4
        },
        {
            label: 'Mamíferos',
            data: months.map(() => Math.floor(Math.random() * 30) + 15),
            borderColor: CHART_COLORS.secondary,
            backgroundColor: 'rgba(139, 69, 19, 0.1)',
            tension: 0.4
        },
        {
            label: 'Reptiles',
            data: months.map(() => Math.floor(Math.random() * 20) + 10),
            borderColor: CHART_COLORS.tertiary,
            backgroundColor: 'rgba(34, 139, 34, 0.1)',
            tension: 0.4
        }
    ];

    return { labels: months, datasets };
}

function simulateRealTimeUpdate() {
    setInterval(() => {
        if (Math.random() > 0.7) {
            updatePopulationChart();
        }
    }, 30000);
}

function updatePopulationChart() {
    if (!charts.populationChart) return;

    const chart = charts.populationChart;
    const datasets = chart.data.datasets;

    datasets.forEach(dataset => {
        const newValue = Math.floor(Math.random() * 20) + dataset.data[dataset.data.length - 1];
        dataset.data.push(newValue);

        if (dataset.data.length > 7) {
            dataset.data.shift();
        }
    });

    const currentTime = new Date().toLocaleTimeString('es-ES', {
        hour: '2-digit',
        minute: '2-digit'
    });
    chart.data.labels.push(currentTime);

    if (chart.data.labels.length > 7) {
        chart.data.labels.shift();
    }

    chart.update('none');

    if (window.EcoVision && window.EcoVision.showToast) {
        window.EcoVision.showToast('Datos actualizados en tiempo real 📊', 'info', 2000);
    }
}

function showChartError() {
    const chartContainers = document.querySelectorAll('canvas[id$="Chart"]');

    chartContainers.forEach(canvas => {
        const container = canvas.parentElement;
        if (container) {
            container.innerHTML = `
                <div class="chart-error">
                    <i class="fas fa-chart-line" style="font-size: 2rem; color: #ccc; margin-bottom: 1rem;"></i>
                    <p>Error al cargar gráfico</p>
                    <button onclick="initializeCharts()" class="btn-retry-chart">
                        Reintentar
                    </button>
                </div>
            `;
        }
    });
}

function addChartStyles() {
    const style = document.createElement('style');
    style.textContent = `
        .chart-container {
            position: relative;
            height: 300px;
            padding: 20px;
        }
        
        .chart-error {
            height: 100%;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            color: #999;
            text-align: center;
        }
        
        .btn-retry-chart {
            background: var(--leaf-green);
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            cursor: pointer;
            margin-top: 10px;
            font-size: 0.9rem;
        }
        
        .btn-retry-chart:hover {
            background: var(--forest-green);
        }
        
        @media (max-width: 768px) {
            .chart-container {
                height: 250px;
                padding: 15px;
            }
        }
    `;
    document.head.appendChild(style);
}

window.EcoCharts = {
    initialize: initializeCharts,
    update: updateChartData,
    refresh: refreshAllCharts,
    generateRandomData: generateRandomTrendData,
    startRealTime: simulateRealTimeUpdate
};

document.addEventListener('DOMContentLoaded', function() {
    addChartStyles();
});

console.log('📊 Charts.js cargado correctamente');