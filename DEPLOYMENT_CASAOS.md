# 🏠 Guía de Deployment en CasaOS

## 📋 Prerrequisitos

1. ✅ Raspberry Pi 5 con CasaOS instalado
2. ✅ Docker y Docker Compose funcionando en CasaOS
3. ✅ Cámara USB conectada a la Raspberry Pi
4. ✅ Acceso SSH o terminal en CasaOS
5. ✅ MongoDB Atlas configurado (o MongoDB en CasaOS)

---

## 🚀 Método 1: Despliegue desde imagen pre-construida (Recomendado)

### Paso 1: Transferir archivos a la Raspberry Pi

```bash
# Desde tu laptop, comprimir el proyecto
tar -czf emotion-detector.tar.gz emotion-detector/

# Transferir vía SCP (reemplaza IP y usuario)
scp emotion-detector.tar.gz usuario@192.168.1.X:/home/usuario/

# Conectar por SSH
ssh usuario@192.168.1.X

# Descomprimir
tar -xzf emotion-detector.tar.gz
cd emotion-detector
```

### Paso 2: Configurar variables de entorno

```bash
# Editar .env con tus credenciales de MongoDB Atlas
nano .env

# Asegúrate de tener:
# MONGODB_URI=mongodb+srv://usuario:password@cluster0.xxxxx.mongodb.net/...
# MONGODB_DATABASE=Emotions
# MONGODB_COLLECTION=emotions_log
```

### Paso 3: Verificar acceso a cámara

```bash
# Listar dispositivos de video
ls -la /dev/video*

# Debería mostrar algo como:
# /dev/video0
# /dev/video1

# Si no aparece, instalar v4l-utils
sudo apt-get install v4l-utils

# Verificar cámaras
v4l2-ctl --list-devices
```

### Paso 4: Construir y ejecutar

```bash
# Dar permisos al script
chmod +x build.sh

# Ejecutar
./build.sh

# O manualmente:
docker-compose build
docker-compose up -d
```

### Paso 5: Verificar que funciona

```bash
# Ver logs
docker-compose logs -f

# Verificar estado
docker-compose ps

# Debería mostrar:
# NAME                    STATUS
# emotion-detector-app    Up (healthy)
```

### Paso 6: Acceder al dashboard

Abre tu navegador en: `http://IP_DE_TU_RASPBERRY:8000`

---

## 🎛️ Método 2: Usar interfaz de CasaOS

### Opción A: Importar docker-compose.yml

1. Abre **CasaOS** en tu navegador
2. Ve a **Apps** → **Custom Install**
3. Pega el contenido del `docker-compose.yml`
4. Ajusta variables de entorno
5. Click en **Install**

### Opción B: Crear manualmente

1. En CasaOS, ve a **Apps** → **Custom Install**
2. Configura:
   - **Image**: `python:3.10-slim` (temporalmente)
   - **Port**: `8000:8000`
   - **Devices**: `/dev/video0:/dev/video0`
   - **Environment Variables**:
     ```
     MONGODB_URI=tu_connection_string
     MONGODB_DATABASE=Emotions
     CAMERA_INDEX=0
     ```
3. En **Advanced**, agrega volúmenes
4. Click **Install**

---

## 🔧 Configuración de la Cámara

### Si la cámara no funciona:

```bash
# 1. Verificar permisos
sudo usermod -a -G video $USER

# 2. Reiniciar Docker
sudo systemctl restart docker

# 3. Dar permisos al dispositivo
sudo chmod 666 /dev/video0

# 4. Verificar que Docker tenga acceso
docker run --rm --device=/dev/video0 python:3.10-slim ls -la /dev/video0
```

### Si tienes múltiples cámaras:

Edita el `.env`:
```bash
CAMERA_INDEX=0  # Cambiar a 1, 2, etc. según tu cámara
```

---

## 📊 Monitoreo y Logs

### Ver logs en tiempo real:
```bash
docker-compose logs -f emotion-detector
```

### Ver solo los últimos 100 logs:
```bash
docker-compose logs --tail=100 emotion-detector
```

### Estadísticas de recursos:
```bash
docker stats emotion-detector-app
```

---

## 🔄 Actualización de la Aplicación

```bash
# 1. Detener contenedor
docker-compose down

# 2. Actualizar código (si hay cambios)
git pull  # Si usas Git

# 3. Reconstruir imagen
docker-compose build --no-cache

# 4. Iniciar de nuevo
docker-compose up -d
```

---

## 🛠️ Troubleshooting

### Error: "Cannot access camera"

```bash
# Verificar que la cámara está conectada
lsusb | grep -i camera

# Verificar dispositivo
ls -la /dev/video0

# Dar permisos
sudo chmod 666 /dev/video0
```

### Error: "MongoDB connection failed"

```bash
# Verificar conectividad
curl -I https://www.mongodb.com

# Verificar variables de entorno
docker-compose exec emotion-detector env | grep MONGODB
```

### Error: "Port 8000 already in use"

```bash
# Ver qué está usando el puerto
sudo lsof -i :8000

# Cambiar puerto en docker-compose.yml
ports:
  - "8001:8000"  # Cambia 8001 por otro puerto libre
```

### Alto consumo de recursos

Edita `docker-compose.yml`:
```yaml
deploy:
  resources:
    limits:
      cpus: '1.0'      # Reducir CPUs
      memory: 1G       # Reducir memoria
```

---

## 🔒 Seguridad

### Recomendaciones:

1. **No exponer puerto 8000 a internet directamente**
   - Usa un reverse proxy (Nginx, Traefik)
   - O usa VPN para acceso remoto

2. **Restringir acceso de red en MongoDB Atlas**
   - Agrega solo la IP de tu Raspberry Pi
   - Quita el "0.0.0.0/0" (allow all)

3. **Actualizar regularmente**
   ```bash
   docker-compose pull
   docker-compose up -d
   ```

---

## 📈 Optimización para Raspberry Pi 5

### Configuración recomendada:

```yaml
# En docker-compose.yml
deploy:
  resources:
    limits:
      cpus: '2.0'      # RPi 5 tiene 4 cores, usa 2
      memory: 2G       # De 4GB-8GB totales, usa 2GB
    reservations:
      cpus: '1.0'
      memory: 1G
```

### Reducir FPS del video:

Edita `api/main.py`, línea con `await asyncio.sleep`:
```python
await asyncio.sleep(0.066)  # Cambiar de 0.033 (30 FPS) a 0.066 (15 FPS)
```

---

## 🎯 Comandos Útiles

```bash
# Iniciar
docker-compose up -d

# Detener
docker-compose down

# Reiniciar
docker-compose restart

# Ver logs
docker-compose logs -f

# Reconstruir
docker-compose build --no-cache

# Limpiar todo (CUIDADO: borra volúmenes)
docker-compose down -v

# Entrar al contenedor
docker-compose exec emotion-detector bash
```

---

## ✅ Checklist de Deployment

- [ ] Cámara conectada y funcionando
- [ ] MongoDB Atlas configurado
- [ ] Variables de entorno en `.env`
- [ ] Docker y Docker Compose instalados
- [ ] Puerto 8000 disponible
- [ ] Imagen construida exitosamente
- [ ] Contenedor iniciado y healthy
- [ ] Dashboard accesible desde navegador
- [ ] Video stream funcionando
- [ ] Emociones detectándose correctamente
- [ ] Datos guardándose en MongoDB

---

## 🆘 Soporte

Si tienes problemas, verifica:
1. Logs del contenedor: `docker-compose logs -f`
2. Estado: `docker-compose ps`
3. Recursos: `docker stats`
4. Cámara: `ls -la /dev/video0`
5. Red: `ping mongodb.net`