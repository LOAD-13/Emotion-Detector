"""
Backend API para el Dashboard de Emociones
FastAPI + WebSocket para streaming en tiempo real
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi import Request
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta
import sys
import os
import json
import asyncio
import cv2
import numpy as np
from typing import List

# Agregar path para imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from detector.database import EmotionDatabase
from dotenv import load_dotenv

load_dotenv()

# ======================== CONFIGURACIÓN ========================

app = FastAPI(
    title="Emotion Detector Dashboard",
    description="Dashboard en tiempo real para detección de emociones con IA",
    version="2.0"
)

# CORS (para desarrollo)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Templates y archivos estáticos
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Base de datos
db = EmotionDatabase()

# Lista de conexiones WebSocket activas
active_connections: List[WebSocket] = []

# ======================== WEBSOCKET MANAGER ========================

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                pass

manager = ConnectionManager()

# ======================== RUTAS HTML ========================

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Página principal del dashboard"""
    return templates.TemplateResponse("dashboard.html", {"request": request})

# ======================== API ENDPOINTS ========================

@app.get("/api/emotions/recent")
async def get_recent_emotions(limit: int = 50):
    """Obtiene las emociones más recientes"""
    try:
        emotions = db.get_recent_emotions(limit=limit)
        return {"success": True, "data": emotions, "count": len(emotions)}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/api/emotions/stats")
async def get_emotion_stats(hours: int = 24):
    """Obtiene estadísticas de emociones"""
    try:
        stats = db.get_emotion_stats(hours=hours)
        return {"success": True, "data": stats}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/api/emotions/hourly")
async def get_hourly_distribution(date: str = None):
    """Obtiene distribución horaria de emociones"""
    try:
        if not date:
            date = datetime.now().strftime('%Y-%m-%d')
        
        hourly = db.get_hourly_distribution(date=date)
        return {"success": True, "data": hourly, "date": date}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/api/emotions/by-date")
async def get_emotions_by_date(date: str):
    """Obtiene todas las emociones de una fecha específica"""
    try:
        emotions = db.get_emotions_by_date(date=date)
        return {"success": True, "data": emotions, "count": len(emotions)}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/api/emotions/weekly")
async def get_weekly_stats():
    """Obtiene estadísticas de la última semana"""
    try:
        # Obtener datos de los últimos 7 días
        weekly_data = {}
        
        for i in range(7):
            date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
            emotions = db.get_emotions_by_date(date)
            
            # Contar emociones por día
            emotion_counts = {}
            for emotion_doc in emotions:
                emotion = emotion_doc['emotion']
                emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
            
            weekly_data[date] = {
                'total': len(emotions),
                'emotions': emotion_counts
            }
        
        return {"success": True, "data": weekly_data}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/api/health")
async def health_check():
    """Verifica el estado de la API y MongoDB"""
    try:
        db_status = db.test_connection()
        return {
            "status": "healthy" if db_status else "degraded",
            "database": "connected" if db_status else "disconnected",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

# ======================== WEBSOCKET PARA VIDEO ========================

@app.websocket("/ws/video")
async def websocket_video_endpoint(websocket: WebSocket):
    """WebSocket para streaming de video en tiempo real"""
    await manager.connect(websocket)
    
    # Cargar modelo DeepFace
    try:
        from deepface import DeepFace
        
        # Inicializar cámara
        cap = cv2.VideoCapture(0)
        face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
        
        frame_count = 0
        last_emotion = None
        session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        emotion_map = {
            'angry': 'Enojo',
            'disgust': 'Asco',
            'fear': 'Miedo',
            'happy': 'Felicidad',
            'sad': 'Tristeza',
            'surprise': 'Sorpresa',
            'neutral': 'Neutral'
        }
        
        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                frame_count += 1
                
                # Reducir resolución para mejor performance
                frame = cv2.resize(frame, (640, 480))
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                
                # Detectar rostros
                faces = face_cascade.detectMultiScale(gray, 1.3, 5, minSize=(30, 30))
                
                emotion_data = None
                
                if len(faces) > 0 and frame_count % 15 == 0:  # Cada 15 frames
                    largest_face = max(faces, key=lambda face: face[2] * face[3])
                    x, y, w, h = largest_face
                    
                    face_roi = gray[y:y+h, x:x+w]
                    face_roi_rgb = cv2.cvtColor(face_roi, cv2.COLOR_GRAY2RGB)
                    face_roi_rgb = cv2.resize(face_roi_rgb, (48, 48))
                    
                    try:
                        result = DeepFace.analyze(
                            face_roi_rgb,
                            actions=['emotion'],
                            enforce_detection=False,
                            silent=True
                        )
                        
                        if isinstance(result, list):
                            result = result[0]
                        
                        emotion_dict = result['emotion']
                        dominant_emotion_en = result['dominant_emotion']
                        emotion_es = emotion_map.get(dominant_emotion_en, 'Neutral')
                        confidence = emotion_dict[dominant_emotion_en] / 100.0
                        
                        if emotion_es != last_emotion and confidence > 0.5:
                            # Guardar en MongoDB
                            all_emotions = {
                                emotion_map.get(k, k): v/100.0 
                                for k, v in emotion_dict.items()
                            }
                            
                            metadata = {
                                'session_id': session_id,
                                'all_emotions': all_emotions,
                                'source': 'dashboard_stream'
                            }
                            
                            db.insert_emotion(emotion_es, confidence, metadata)
                            
                            emotion_data = {
                                'emotion': emotion_es,
                                'confidence': confidence,
                                'all_emotions': all_emotions
                            }
                            
                            last_emotion = emotion_es
                    
                    except Exception as e:
                        print(f"Error en detección: {e}")
                
                # Codificar frame a JPEG
                _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 70])
                frame_base64 = buffer.tobytes()
                
                # Enviar frame y datos de emoción
                await websocket.send_json({
                    'type': 'frame',
                    'frame': frame_base64.hex(),
                    'emotion': emotion_data
                })
                
                await asyncio.sleep(0.033)  # ~30 FPS
                
        except WebSocketDisconnect:
            manager.disconnect(websocket)
        finally:
            cap.release()
            
    except Exception as e:
        print(f"Error en WebSocket: {e}")
        manager.disconnect(websocket)

# ======================== WEBSOCKET PARA DATOS ========================

@app.websocket("/ws/data")
async def websocket_data_endpoint(websocket: WebSocket):
    """WebSocket para actualizar datos en tiempo real"""
    await manager.connect(websocket)
    
    try:
        while True:
            # Enviar estadísticas actualizadas cada 5 segundos
            stats = db.get_emotion_stats(hours=24)
            await websocket.send_json({
                'type': 'stats_update',
                'data': stats
            })
            
            await asyncio.sleep(5)
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# ======================== STARTUP/SHUTDOWN ========================

@app.on_event("startup")
async def startup_event():
    """Evento al iniciar la aplicación"""
    print("\n" + "="*60)
    print("🚀 DASHBOARD DE EMOCIONES INICIADO")
    print("="*60)
    print(f"📊 API disponible en: http://localhost:8000")
    print(f"🎨 Dashboard disponible en: http://localhost:8000")
    print(f"📡 WebSocket Video: ws://localhost:8000/ws/video")
    print(f"📈 WebSocket Data: ws://localhost:8000/ws/data")
    print("="*60 + "\n")

@app.on_event("shutdown")
async def shutdown_event():
    """Evento al cerrar la aplicación"""
    db.close()
    print("\n👋 Dashboard cerrado correctamente\n")

if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv('API_PORT', 8000))
    host = os.getenv('API_HOST', '0.0.0.0')
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=True,
        log_level="info"
    )