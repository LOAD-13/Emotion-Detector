# 🎭 Emotion Detector - AI-Powered Real-time Emotion Recognition

Sistema de detección de emociones en tiempo real utilizando IA, con dashboard web interactivo y almacenamiento en MongoDB Atlas.

![Version](https://img.shields.io/badge/version-2.0-blue)
![Python](https://img.shields.io/badge/python-3.10-green)
![Docker](https://img.shields.io/badge/docker-ready-blue)
![License](https://img.shields.io/badge/license-MIT-green)

---

## ✨ Características

- 🎥 **Detección en tiempo real** desde webcam
- 🧠 **IA con DeepFace** para reconocimiento de 7 emociones
- 📊 **Dashboard web** interactivo con gráficas
- 💾 **MongoDB Atlas** para almacenamiento cloud
- 📈 **Estadísticas avanzadas** y análisis temporal
- 🐳 **Docker** listo para deployment
- 🏠 **Compatible con CasaOS** en Raspberry Pi

---

## 🎯 Emociones Detectadas

| Emoción | Emoji | Descripción |
|---------|-------|-------------|
| Felicidad | 😊 | Expresiones de alegría |
| Tristeza | 😢 | Expresiones de melancolía |
| Enojo | 😠 | Expresiones de ira |
| Sorpresa | 😮 | Expresiones de asombro |
| Miedo | 😨 | Expresiones de temor |
| Asco | 🤢 | Expresiones de repulsión |
| Neutral | 😐 | Expresión neutra |

---

## 🛠️ Tech Stack

### Backend
- **Python 3.10**
- **FastAPI** - API REST y WebSockets
- **OpenCV** - Procesamiento de video
- **DeepFace** - Modelo de IA para emociones
- **TensorFlow** - Framework de deep learning
- **PyMongo** - Cliente MongoDB

### Frontend
- **HTML5 / CSS3 / JavaScript**
- **Chart.js** - Gráficas interactivas
- **Lucide Icons** - Iconografía moderna
- **WebSocket** - Comunicación en tiempo real

### Infrastructure
- **MongoDB Atlas** - Base de datos cloud
- **Docker** - Containerización
- **Docker Compose** - Orquestación

---

## 📋 Requisitos

### Hardware
- Webcam USB o cámara integrada
- Mínimo 2GB RAM (recomendado 4GB+)
- Procesador multi-core (Raspberry Pi 5, PC, etc.)

### Software
- Docker & Docker Compose
- Python 3.10+ (solo para desarrollo local)
- MongoDB Atlas account (gratis)

---

## 🚀 Quick Start

### 1. Clonar repositorio

```bash
git clone https://github.com/tu-usuario/emotion-detector.git
cd emotion-detector
```

### 2. Configurar variables de entorno

```bash
# Copiar .env de ejemplo
cp .env.example .env

# Editar con tus credenciales
nano .env
```

Configurar:
```env
MONGODB_URI=mongodb+srv://usuario:password@cluster.mongodb.net/
MONGODB_DATABASE=Emotions
MONGODB_COLLECTION=emotions_log
CAMERA_INDEX=0
```

### 3. Ejecutar con Docker

```bash
# Linux/Mac
chmod +x build.sh
./build.sh

# Windows
build.bat

# O manualmente
docker-compose up -d
```

### 4. Acceder al dashboard

Abre en tu navegador: **http://localhost:8000**

---

## 💻 Desarrollo Local (sin Docker)

### 1. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 2. Ejecutar aplicación

```bash
# Modo dashboard (recomendado)
python api/main.py

# Modo detector standalone
python detector/emotion_detector.py
```

---

## 🐳 Docker Commands

```bash
# Iniciar
docker-compose up -d

# Detener
docker-compose down

# Ver logs
docker-compose logs -f

# Reiniciar
docker-compose restart

# Reconstruir
docker-compose build --no-cache

# Ver estado
docker-compose ps

# Estadísticas de recursos
docker stats emotion-detector-app
```

---

## 📁 Estructura del Proyecto

```
emotion-detector/
├── api/
│   ├── __init__.py
│   └── main.py              # FastAPI application
├── detector/
│   ├── __init__.py
│   ├── database.py          # MongoDB connection
│   └── emotion_detector.py  # Standalone detector
├── static/
│   ├── css/
│   │   └── style.css        # Dashboard styles
│   └── js/
│       └── dashboard.js     # Frontend logic
├── templates/
│   └── dashboard.html       # Main dashboard
├── .env                     # Environment variables
├── .gitignore
├── requirements.txt         # Python dependencies
├── Dockerfile
├── docker-compose.yml
└── README.md
```

---

## 📊 API Endpoints

### REST API

| Endpoint | Method | Descripción |
|----------|--------|-------------|
| `/` | GET | Dashboard principal |
| `/api/emotions/recent` | GET | Últimas emociones detectadas |
| `/api/emotions/stats` | GET | Estadísticas de emociones |
| `/api/emotions/hourly` | GET | Distribución por hora |
| `/api/emotions/by-date` | GET | Emociones por fecha |
| `/api/emotions/weekly` | GET | Estadísticas semanales |
| `/api/health` | GET | Health check |

### WebSocket

| Endpoint | Descripción |
|----------|-------------|
| `/ws/video` | Stream de video en tiempo real |
| `/ws/data` | Actualizaciones de datos en tiempo real |

---

## 🏠 Deployment en CasaOS / Raspberry Pi

Ver guía completa: [DEPLOYMENT_CASAOS.md](DEPLOYMENT_CASAOS.md)

### Quick deployment

```bash
# 1. Transferir proyecto a Raspberry Pi
scp -r emotion-detector/ usuario@IP_RASPBERRY:~/

# 2. SSH a Raspberry Pi
ssh usuario@IP_RASPBERRY

# 3. Entrar al proyecto
cd emotion-detector

# 4. Ejecutar
./build.sh
```

---

## 🔧 Configuración

### Variables de Entorno

| Variable | Descripción | Default |
|----------|-------------|---------|
| `MONGODB_URI` | Connection string de MongoDB | *requerido* |
| `MONGODB_DATABASE` | Nombre de base de datos | Emotions |
| `MONGODB_COLLECTION` | Nombre de colección | emotions_log |
| `CAMERA_INDEX` | Índice de cámara | 0 |
| `CONFIDENCE_THRESHOLD` | Umbral mínimo de confianza | 0.5 |
| `API_HOST` | Host del servidor API | 0.0.0.0 |
| `API_PORT` | Puerto del servidor API | 8000 |

### Configuración de Cámara

```bash
# Listar cámaras disponibles
ls -la /dev/video*

# Ver información de cámara
v4l2-ctl --list-devices

# Cambiar cámara en .env
CAMERA_INDEX=1  # Para /dev/video1
```

---

## 📈 Características del Dashboard

### 🎥 Video en Tiempo Real
- Stream de cámara con detección de rostros
- Overlay con emoción actual y confianza
- Indicador de estado de conexión

### 📊 Gráficas Interactivas
- **Gráfica de Pie**: Distribución de emociones (24h)
- **Gráfica de Barras**: Timeline por hora
- Actualización automática en tiempo real

### 📋 Estadísticas
- Emoción dominante del día
- Total de detecciones
- Confianza promedio
- Historial de emociones recientes

### 🎨 Diseño
- Paleta de colores personalizada
- Iconos Lucide modernos
- Responsive design
- Animaciones suaves
- Modo oscuro profesional

---

## 🗄️ Estructura de Datos en MongoDB

### Documento de Emoción

```json
{
  "_id": "ObjectId(...)",
  "emotion": "Felicidad",
  "confidence": 0.89,
  "timestamp": "ISODate(2025-10-13T15:30:22.000Z)",
  "date": "2025-10-13",
  "time": "15:30:22",
  "hour": 15,
  "day_of_week": "Monday",
  "metadata": {
    "session_id": "20251013_153022",
    "all_emotions": {
      "Felicidad": 0.89,
      "Neutral": 0.05,
      "Sorpresa": 0.03,
      "Tristeza": 0.02,
      "Enojo": 0.01,
      "Miedo": 0.00,
      "Asco": 0.00
    },
    "source": "dashboard_stream"
  }
}
```

---

## 🔍 Troubleshooting

### Error: "Cannot access camera"

**Solución:**
```bash
# Verificar dispositivo
ls -la /dev/video0

# Dar permisos
sudo chmod 666 /dev/video0

# Agregar usuario al grupo video
sudo usermod -a -G video $USER

# En Docker, verificar devices en docker-compose.yml
devices:
  - /dev/video0:/dev/video0
```

### Error: "MongoDB connection failed"

**Solución:**
```bash
# Verificar connection string en .env
cat .env | grep MONGODB_URI

# Probar conexión
python detector/database.py

# Verificar Network Access en MongoDB Atlas
# Debe incluir tu IP o 0.0.0.0/0
```

### Error: "Port 8000 already in use"

**Solución:**
```bash
# Ver qué usa el puerto
sudo lsof -i :8000

# Matar proceso
sudo kill -9 PID

# O cambiar puerto en .env
API_PORT=8001
```

### Video lento / bajo FPS

**Solución:**
```python
# Reducir resolución en api/main.py
frame = cv2.resize(frame, (320, 240))  # Cambiar de (640, 480)

# Reducir FPS
await asyncio.sleep(0.066)  # Cambiar de 0.033 (de 30 a 15 FPS)

# Detectar menos frecuentemente
if frame_count % 30 == 0:  # Cambiar de 15 a 30
```

### Alto consumo de RAM

**Solución:**
```yaml
# Limitar recursos en docker-compose.yml
deploy:
  resources:
    limits:
      memory: 1G  # Reducir de 2G a 1G
```

---

## 🧪 Testing

### Test de conexión MongoDB

```bash
python detector/database.py
```

### Test del detector standalone

```bash
python detector/emotion_detector.py
```

### Test de API

```bash
# Iniciar servidor
python api/main.py

# En otro terminal, test endpoints
curl http://localhost:8000/api/health
curl http://localhost:8000/api/emotions/stats?hours=24
```

---

## 📊 Monitoreo y Logs

### Ver logs en tiempo real

```bash
# Todos los logs
docker-compose logs -f

# Solo app
docker-compose logs -f emotion-detector

# Últimos 100
docker-compose logs --tail=100 emotion-detector
```

### Estadísticas de recursos

```bash
# Docker stats
docker stats emotion-detector-app

# Logs del sistema
journalctl -u docker -f
```

### Health check

```bash
# Via API
curl http://localhost:8000/api/health

# Via Docker
docker ps  # Ver estado "healthy"
```

---

## 🚀 Próximas Características (Roadmap)

- [ ] Integración con n8n para notificaciones Telegram
- [ ] Soporte para múltiples rostros simultáneos
- [ ] Exportar reportes en PDF
- [ ] Dashboard de análisis histórico avanzado
- [ ] API de predicción de tendencias emocionales
- [ ] Modo headless (sin interfaz gráfica)
- [ ] Soporte para RTSP/IP cameras
- [ ] Integración con Home Assistant
- [ ] Autenticación de usuarios
- [ ] Multi-idioma

---

## 🤝 Contribuir

Las contribuciones son bienvenidas. Por favor:

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

---

## 📝 Changelog

### Version 2.0 (2025-10-13)
- ✨ Dashboard web interactivo
- 🐳 Dockerización completa
- 📊 Gráficas en tiempo real
- 💾 Integración MongoDB Atlas
- 🎨 Nuevo diseño profesional
- 📡 WebSocket para streaming

### Version 1.0 (2025-10-09)
- 🎉 Release inicial
- 🎥 Detección básica de emociones
- 📝 Logs en archivo local

---

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver `LICENSE` para más detalles.

---

## 👤 Autor

**Joaquín Loadenegri**

- GitHub: [@jloadenegri](https://github.com/jloadenegri)

---

## 🙏 Agradecimientos

- [DeepFace](https://github.com/serengil/deepface) por el modelo de IA
- [FastAPI](https://fastapi.tiangolo.com/) por el framework web
- [MongoDB Atlas](https://www.mongodb.com/cloud/atlas) por la base de datos
- [Chart.js](https://www.chartjs.org/) por las gráficas
- [Lucide](https://lucide.dev/) por los iconos

---

## 📞 Soporte

Si tienes problemas o preguntas:

1. Revisa la sección [Troubleshooting](#-troubleshooting)
2. Consulta [DEPLOYMENT_CASAOS.md](DEPLOYMENT_CASAOS.md)
3. Abre un [Issue](https://github.com/tu-usuario/emotion-detector/issues)

---

⭐ **Si te gusta este proyecto, dale una estrella en GitHub!** ⭐