// ==================== CONFIGURACIÓN ====================

const EMOTION_EMOJIS = {
    'Enojo': '😠',
    'Asco': '🤢',
    'Miedo': '😨',
    'Felicidad': '😊',
    'Tristeza': '😢',
    'Sorpresa': '😮',
    'Neutral': '😐'
};

const EMOTION_COLORS = {
    'Enojo': '#ef4444',
    'Asco': '#22c55e',
    'Miedo': '#f59e0b',
    'Felicidad': '#3b82f6',
    'Tristeza': '#8b5cf6',
    'Sorpresa': '#ec4899',
    'Neutral': '#6b7280'
};

// ==================== VARIABLES GLOBALES ====================

let videoWs = null;
let dataWs = null;
let emotionPieChart = null;
let hourlyChart = null;

// ==================== INICIALIZACIÓN ====================

document.addEventListener('DOMContentLoaded', async () => {
    console.log('🚀 Iniciando dashboard...');
    
    // Inicializar gráficas
    initCharts();
    
    // Cargar datos iniciales
    await loadInitialData();
    
    // Conectar WebSockets
    connectVideoWebSocket();
    connectDataWebSocket();
    
    // Actualizar cada 30 segundos
    setInterval(loadStats, 30000);
    setInterval(loadRecent, 30000);
});

// ==================== WEBSOCKET VIDEO ====================

function connectVideoWebSocket() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws/video`;
    
    console.log('📹 Conectando WebSocket de video...');
    updateStatus('Conectando...', 'connecting');
    
    videoWs = new WebSocket(wsUrl);
    
    videoWs.onopen = () => {
        console.log('✅ WebSocket de video conectado');
        updateStatus('Conectado', 'connected');
        document.getElementById('videoOverlay').classList.add('hidden');
    };
    
    videoWs.onmessage = (event) => {
        const data = JSON.parse(event.data);
        
        if (data.type === 'frame') {
            // Mostrar frame en canvas
            displayFrame(data.frame);
            
            // Actualizar emoción si hay datos
            if (data.emotion) {
                updateCurrentEmotion(data.emotion);
            }
        }
    };
    
    videoWs.onerror = (error) => {
        console.error('❌ Error en WebSocket de video:', error);
        updateStatus('Error', 'error');
    };
    
    videoWs.onclose = () => {
        console.log('🔌 WebSocket de video cerrado, reconectando...');
        updateStatus('Reconectando...', 'connecting');
        setTimeout(connectVideoWebSocket, 3000);
    };
}

// ==================== WEBSOCKET DATOS ====================

function connectDataWebSocket() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws/data`;
    
    console.log('📊 Conectando WebSocket de datos...');
    
    dataWs = new WebSocket(wsUrl);
    
    dataWs.onopen = () => {
        console.log('✅ WebSocket de datos conectado');
    };
    
    dataWs.onmessage = (event) => {
        const data = JSON.parse(event.data);
        
        if (data.type === 'stats_update') {
            updateStatsDisplay(data.data);
        }
    };
    
    dataWs.onerror = (error) => {
        console.error('❌ Error en WebSocket de datos:', error);
    };
    
    dataWs.onclose = () => {
        console.log('🔌 WebSocket de datos cerrado, reconectando...');
        setTimeout(connectDataWebSocket, 3000);
    };
}

// ==================== MOSTRAR VIDEO ====================

function displayFrame(hexFrame) {
    const canvas = document.getElementById('videoCanvas');
    const ctx = canvas.getContext('2d');
    
    // Convertir hex a bytes
    const bytes = new Uint8Array(hexFrame.match(/.{1,2}/g).map(byte => parseInt(byte, 16)));
    
    // Crear blob y convertir a imagen
    const blob = new Blob([bytes], { type: 'image/jpeg' });
    const url = URL.createObjectURL(blob);
    
    const img = new Image();
    img.onload = () => {
        canvas.width = img.width;
        canvas.height = img.height;
        ctx.drawImage(img, 0, 0);
        URL.revokeObjectURL(url);
    };
    img.src = url;
}

// ==================== ACTUALIZAR EMOCIÓN ACTUAL ====================

function updateCurrentEmotion(emotionData) {
    const emoji = EMOTION_EMOJIS[emotionData.emotion] || '❓';
    const confidence = Math.round(emotionData.confidence * 100);
    
    document.getElementById('emotionEmoji').textContent = emoji;
    document.getElementById('emotionName').textContent = emotionData.emotion;
    document.getElementById('confidenceFill').style.width = `${confidence}%`;
    document.getElementById('confidenceFill').style.background = 
        `linear-gradient(90deg, ${EMOTION_COLORS[emotionData.emotion]}, #519872)`;
    document.getElementById('confidenceText').textContent = `${confidence}% confianza`;
}

// ==================== CARGAR DATOS INICIALES ====================

async function loadInitialData() {
    await Promise.all([
        loadStats(),
        loadRecent(),
        loadHourlyData()
    ]);
}

// ==================== CARGAR ESTADÍSTICAS ====================

async function loadStats() {
    try {
        const response = await fetch('/api/emotions/stats?hours=24');
        const result = await response.json();
        
        if (result.success) {
            updateStatsDisplay(result.data);
        }
    } catch (error) {
        console.error('Error cargando estadísticas:', error);
    }
}

function updateStatsDisplay(stats) {
    // Total de detecciones
    const totalCount = stats.total_detections || 0;
    document.getElementById('total-count').textContent = totalCount;
    document.getElementById('todayTotal').textContent = totalCount;
    
    // Emoción dominante
    const dominant = stats.dominant_emotion;
    if (dominant) {
        document.getElementById('dominantEmoji').textContent = EMOTION_EMOJIS[dominant] || '🤔';
        document.getElementById('dominantName').textContent = dominant;
        
        const dominantCount = stats.emotions[dominant]?.count || 0;
        document.getElementById('dominantCount').textContent = `${dominantCount} detecciones`;
    }
    
    // Confianza promedio
    let totalConfidence = 0;
    let emotionCount = 0;
    
    if (stats.emotions) {
        Object.values(stats.emotions).forEach(emotion => {
            totalConfidence += emotion.avg_confidence * emotion.count;
            emotionCount += emotion.count;
        });
    }
    
    const avgConfidence = emotionCount > 0 ? 
        Math.round((totalConfidence / emotionCount) * 100) : 0;
    document.getElementById('avgConfidence').textContent = `${avgConfidence}%`;
    
    // Actualizar gráfica de pie
    updatePieChart(stats.emotions || {});
}

// ==================== CARGAR EMOCIONES RECIENTES ====================

async function loadRecent() {
    try {
        const response = await fetch('/api/emotions/recent?limit=10');
        const result = await response.json();
        
        if (result.success) {
            displayRecentEmotions(result.data);
        }
    } catch (error) {
        console.error('Error cargando recientes:', error);
    }
}

function displayRecentEmotions(emotions) {
    const container = document.getElementById('recentList');
    
    if (emotions.length === 0) {
        container.innerHTML = '<p style="text-align: center; color: var(--text-secondary);">No hay detecciones recientes</p>';
        return;
    }
    
    container.innerHTML = emotions.map(emotion => {
        const emoji = EMOTION_EMOJIS[emotion.emotion] || '❓';
        const confidence = Math.round(emotion.confidence * 100);
        const time = new Date(emotion.timestamp).toLocaleTimeString('es-ES', {
            hour: '2-digit',
            minute: '2-digit'
        });
        
        return `
            <div class="recent-item">
                <span class="recent-item-emoji">${emoji}</span>
                <div class="recent-item-content">
                    <div class="recent-item-emotion">${emotion.emotion}</div>
                    <div class="recent-item-time">${time}</div>
                </div>
                <span class="recent-item-confidence">${confidence}%</span>
            </div>
        `;
    }).join('');
}

// ==================== CARGAR DATOS POR HORA ====================

async function loadHourlyData() {
    try {
        const response = await fetch('/api/emotions/hourly');
        const result = await response.json();
        
        if (result.success) {
            updateHourlyChart(result.data);
        }
    } catch (error) {
        console.error('Error cargando datos horarios:', error);
    }
}

// ==================== INICIALIZAR GRÁFICAS ====================

function initCharts() {
    // Gráfica de Pie
    const pieCtx = document.getElementById('emotionPieChart').getContext('2d');
    emotionPieChart = new Chart(pieCtx, {
        type: 'doughnut',
        data: {
            labels: [],
            datasets: [{
                data: [],
                backgroundColor: Object.values(EMOTION_COLORS),
                borderWidth: 2,
                borderColor: '#222831'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    position: 'right',
                    labels: {
                        color: '#f8f9fa',
                        font: { size: 12 },
                        padding: 15
                    }
                }
            }
        }
    });
    
    // Gráfica de barras por hora
    const hourlyCtx = document.getElementById('hourlyChart').getContext('2d');
    hourlyChart = new Chart(hourlyCtx, {
        type: 'bar',
        data: {
            labels: Array.from({length: 24}, (_, i) => `${i}:00`),
            datasets: []
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            scales: {
                x: {
                    stacked: true,
                    grid: { color: 'rgba(164, 180, 148, 0.1)' },
                    ticks: { color: '#BEC5AD' }
                },
                y: {
                    stacked: true,
                    grid: { color: 'rgba(164, 180, 148, 0.1)' },
                    ticks: { color: '#BEC5AD' }
                }
            },
            plugins: {
                legend: {
                    labels: {
                        color: '#f8f9fa',
                        font: { size: 11 },
                        padding: 10
                    }
                }
            }
        }
    });
}

// ==================== ACTUALIZAR GRÁFICA DE PIE ====================

function updatePieChart(emotions) {
    const labels = Object.keys(emotions);
    const data = Object.values(emotions).map(e => e.count);
    const colors = labels.map(label => EMOTION_COLORS[label] || '#6b7280');
    
    emotionPieChart.data.labels = labels;
    emotionPieChart.data.datasets[0].data = data;
    emotionPieChart.data.datasets[0].backgroundColor = colors;
    emotionPieChart.update();
}

// ==================== ACTUALIZAR GRÁFICA HORARIA ====================

function updateHourlyChart(hourlyData) {
    // Obtener todas las emociones únicas
    const allEmotions = new Set();
    Object.values(hourlyData).forEach(hour => {
        Object.keys(hour).forEach(emotion => allEmotions.add(emotion));
    });
    
    // Crear datasets por emoción
    const datasets = Array.from(allEmotions).map(emotion => {
        const data = Array(24).fill(0);
        
        Object.entries(hourlyData).forEach(([hour, emotions]) => {
            data[parseInt(hour)] = emotions[emotion] || 0;
        });
        
        return {
            label: emotion,
            data: data,
            backgroundColor: EMOTION_COLORS[emotion] || '#6b7280',
            borderColor: EMOTION_COLORS[emotion] || '#6b7280',
            borderWidth: 1
        };
    });
    
    hourlyChart.data.datasets = datasets;
    hourlyChart.update();
}

// ==================== ACTUALIZAR ESTADO ====================

function updateStatus(text, status) {
    const statusEl = document.getElementById('status');
    statusEl.textContent = text;
    statusEl.className = status;
}

// ==================== FUNCIÓN PÚBLICA PARA REFRESCAR ====================

function refreshRecent() {
    loadRecent();
    
    // Feedback visual
    const btn = event.target.closest('button');
    const icon = btn.querySelector('svg');
    icon.style.animation = 'spin 0.5s linear';
    setTimeout(() => {
        icon.style.animation = '';
        lucide.createIcons();
    }, 500);
}

// ==================== MANEJO DE ERRORES GLOBAL ====================

window.addEventListener('error', (event) => {
    console.error('💥 Error global:', event.error);
});

// ==================== CLEANUP AL CERRAR ====================

window.addEventListener('beforeunload', () => {
    if (videoWs) videoWs.close();
    if (dataWs) dataWs.close();
});