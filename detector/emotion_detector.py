"""
Detector de Emociones con IA + MongoDB
Versión: 2.0
Descripción: Detecta emociones faciales y guarda en MongoDB Atlas
"""

import cv2
import numpy as np
from datetime import datetime
import sys
import os

# Agregar el directorio padre al path para imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from detector.database import EmotionDatabase

# Manejo de colores en terminal
try:
    from colorama import init, Fore, Style
    init(autoreset=True)
    COLORS_AVAILABLE = True
except ImportError:
    COLORS_AVAILABLE = False

# ======================== CONFIGURACIÓN ========================
from dotenv import load_dotenv
load_dotenv()

CAMERA_INDEX = int(os.getenv('CAMERA_INDEX', 0))
CONFIDENCE_THRESHOLD = float(os.getenv('CONFIDENCE_THRESHOLD', 0.5))
LOG_FILE = 'emotion_logs.txt'  # Backup local

# Emojis y colores
EMOTION_EMOJIS = {
    'Enojo': '😠',
    'Asco': '🤢',
    'Miedo': '😨',
    'Felicidad': '😊',
    'Tristeza': '😢',
    'Sorpresa': '😮',
    'Neutral': '😐'
}

EMOTION_COLORS = {
    'Enojo': Fore.RED,
    'Asco': Fore.GREEN,
    'Miedo': Fore.YELLOW,
    'Felicidad': Fore.CYAN,
    'Tristeza': Fore.BLUE,
    'Sorpresa': Fore.MAGENTA,
    'Neutral': Fore.WHITE
}

# ======================== FUNCIONES AUXILIARES ========================

def print_colored(text, color=None):
    """Imprime texto con color si está disponible"""
    if COLORS_AVAILABLE and color:
        print(color + text + Style.RESET_ALL)
    else:
        print(text)

def log_to_file(message):
    """Guarda log en archivo (backup)"""
    try:
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(message + '\n')
    except Exception as e:
        print(f"⚠️  Error al escribir log: {e}")

def print_header():
    """Muestra el header del programa"""
    header = """
╔═══════════════════════════════════════════════════════════╗
║       🎭 DETECTOR DE EMOCIONES CON IA + MONGODB 🎭       ║
║                    Versión 2.0                            ║
╚═══════════════════════════════════════════════════════════╝
"""
    print_colored(header, Fore.CYAN if COLORS_AVAILABLE else None)
    print_colored("📹 Iniciando sistema...", Fore.YELLOW if COLORS_AVAILABLE else None)
    print("=" * 63)

def load_emotion_model():
    """Carga el modelo de emociones usando DeepFace"""
    try:
        from deepface import DeepFace
        print_colored("🔄 Cargando modelo de IA (DeepFace)...", Fore.YELLOW if COLORS_AVAILABLE else None)
        
        # Predicción dummy para cargar el modelo
        dummy_img = np.zeros((48, 48, 3), dtype=np.uint8)
        try:
            DeepFace.analyze(dummy_img, actions=['emotion'], enforce_detection=False, silent=True)
        except:
            pass
        
        print_colored("✅ Modelo de IA cargado\n", Fore.GREEN if COLORS_AVAILABLE else None)
        return DeepFace
    except Exception as e:
        print_colored(f"\n❌ ERROR al cargar modelo: {e}", Fore.RED if COLORS_AVAILABLE else None)
        sys.exit(1)

def detect_emotion(face_roi, deepface_module):
    """
    Detecta la emoción de un rostro usando DeepFace
    """
    try:
        # Convertir a RGB
        face_roi_rgb = cv2.cvtColor(face_roi, cv2.COLOR_GRAY2RGB)
        face_roi_rgb = cv2.resize(face_roi_rgb, (48, 48), interpolation=cv2.INTER_AREA)
        
        # Analizar con DeepFace
        result = deepface_module.analyze(
            face_roi_rgb, 
            actions=['emotion'], 
            enforce_detection=False,
            silent=True
        )
        
        if isinstance(result, list):
            result = result[0]
        
        emotion_dict = result['emotion']
        dominant_emotion = result['dominant_emotion']
        confidence = emotion_dict[dominant_emotion] / 100.0
        
        # Mapear a español
        emotion_map = {
            'angry': 'Enojo',
            'disgust': 'Asco',
            'fear': 'Miedo',
            'happy': 'Felicidad',
            'sad': 'Tristeza',
            'surprise': 'Sorpresa',
            'neutral': 'Neutral'
        }
        
        emotion = emotion_map.get(dominant_emotion, 'Neutral')
        
        # Retornar también todas las probabilidades
        all_emotions = {emotion_map.get(k, k): v/100.0 for k, v in emotion_dict.items()}
        
        return emotion, confidence, all_emotions
    
    except Exception as e:
        return None, 0.0, {}

def log_emotion(emotion, confidence, all_emotions, db, session_id):
    """
    Registra la emoción en terminal, archivo y MongoDB
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    emoji = EMOTION_EMOJIS.get(emotion, '❓')
    color = EMOTION_COLORS.get(emotion, None)
    
    # Mensaje para terminal
    terminal_msg = f"[{timestamp}] {emoji} {emotion:12} ({confidence*100:.1f}%)"
    
    # Guardar en MongoDB
    try:
        metadata = {
            'session_id': session_id,
            'all_emotions': all_emotions,
            'source': 'webcam_detector'
        }
        
        emotion_id = db.insert_emotion(emotion, confidence, metadata)
        
        if emotion_id:
            terminal_msg += f" [DB: ✅]"
        else:
            terminal_msg += f" [DB: ❌]"
            
    except Exception as e:
        terminal_msg += f" [DB: ⚠️  {str(e)[:20]}]"
    
    # Mostrar en terminal
    if confidence >= CONFIDENCE_THRESHOLD:
        print_colored(terminal_msg, color)
        
        # Backup en archivo
        file_msg = f"[{timestamp}] {emotion} - Confianza: {confidence*100:.1f}%"
        log_to_file(file_msg)

def print_stats(db, session_start):
    """Muestra estadísticas de la sesión"""
    print("\n" + "=" * 63)
    print_colored("📊 ESTADÍSTICAS DE LA SESIÓN", Fore.CYAN if COLORS_AVAILABLE else None)
    print("=" * 63)
    
    try:
        # Calcular duración
        duration = (datetime.now() - session_start).total_seconds() / 60
        print(f"⏱️  Duración: {duration:.1f} minutos")
        
        # Stats de MongoDB
        stats = db.get_emotion_stats(hours=24)
        
        if stats and stats.get('emotions'):
            print(f"\n📈 Total de detecciones hoy: {stats['total_detections']}")
            print(f"🏆 Emoción dominante: {stats.get('dominant_emotion', 'N/A')}")
            
            print("\n📊 Distribución de emociones detectadas:")
            for emotion, data in sorted(stats['emotions'].items(), 
                                       key=lambda x: x[1]['count'], 
                                       reverse=True):
                emoji = EMOTION_EMOJIS.get(emotion, '❓')
                count = data['count']
                avg_conf = data['avg_confidence'] * 100
                print(f"   {emoji} {emotion:12} → {count:3} veces (confianza promedio: {avg_conf:.1f}%)")
        else:
            print("ℹ️  No hay suficientes datos para mostrar estadísticas")
            
    except Exception as e:
        print(f"⚠️  Error al obtener estadísticas: {e}")

# ======================== FUNCIÓN PRINCIPAL ========================

def main():
    """Función principal del detector"""
    
    print_header()
    
    # Inicializar MongoDB
    try:
        db = EmotionDatabase()
        print_colored("✅ MongoDB conectado\n", Fore.GREEN if COLORS_AVAILABLE else None)
    except Exception as e:
        print_colored(f"❌ Error de MongoDB: {e}", Fore.RED if COLORS_AVAILABLE else None)
        print_colored("⚠️  Continuando sin base de datos...\n", Fore.YELLOW if COLORS_AVAILABLE else None)
        db = None
    
    # Cargar modelo de IA
    deepface = load_emotion_model()
    
    # Generar ID de sesión único
    session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    session_start = datetime.now()
    
    # Log de inicio
    log_to_file(f"\n{'='*60}")
    log_to_file(f"Nueva sesión iniciada: {session_start.strftime('%Y-%m-%d %H:%M:%S')}")
    log_to_file(f"Session ID: {session_id}")
    log_to_file(f"{'='*60}")
    
    # Cargar detector de rostros
    face_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
    )
    
    # Iniciar cámara
    cap = cv2.VideoCapture(CAMERA_INDEX)
    
    if not cap.isOpened():
        print_colored("❌ ERROR: No se pudo acceder a la cámara", Fore.RED if COLORS_AVAILABLE else None)
        sys.exit(1)
    
    print_colored("✅ Cámara iniciada - Detectando emociones...", Fore.GREEN if COLORS_AVAILABLE else None)
    print_colored("⌨️  Presiona 'q' en la ventana de video para salir", Fore.YELLOW if COLORS_AVAILABLE else None)
    print_colored("⌨️  Presiona 's' para ver estadísticas\n", Fore.YELLOW if COLORS_AVAILABLE else None)
    print("=" * 63)
    
    frame_count = 0
    last_emotion = None
    detection_count = 0
    
    try:
        while True:
            ret, frame = cap.read()
            
            if not ret:
                print_colored("⚠️  No se pudo capturar frame", Fore.YELLOW if COLORS_AVAILABLE else None)
                break
            
            frame_count += 1
            
            # Convertir a escala de grises
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Detectar rostros
            faces = face_cascade.detectMultiScale(
                gray, 
                scaleFactor=1.3, 
                minNeighbors=5,
                minSize=(30, 30)
            )
            
            # Procesar el rostro más grande
            if len(faces) > 0:
                largest_face = max(faces, key=lambda face: face[2] * face[3])
                x, y, w, h = largest_face
                
                face_roi = gray[y:y+h, x:x+w]
                
                # Detectar emoción cada 10 frames
                if frame_count % 10 == 0:
                    emotion, confidence, all_emotions = detect_emotion(face_roi, deepface)
                    
                    if emotion and confidence >= CONFIDENCE_THRESHOLD:
                        # Solo registrar si cambió la emoción
                        if emotion != last_emotion:
                            if db:
                                log_emotion(emotion, confidence, all_emotions, db, session_id)
                            else:
                                # Log sin DB
                                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                emoji = EMOTION_EMOJIS.get(emotion, '❓')
                                color = EMOTION_COLORS.get(emotion, None)
                                msg = f"[{timestamp}] {emoji} {emotion:12} ({confidence*100:.1f}%) [Sin DB]"
                                print_colored(msg, color)
                            
                            last_emotion = emotion
                            detection_count += 1
                
                # Dibujar en video
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                
                if last_emotion:
                    emoji = EMOTION_EMOJIS.get(last_emotion, '')
                    label = f"{emoji} {last_emotion}"
                    cv2.putText(
                        frame, label, (x, y-10), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2
                    )
                
                # Contador de detecciones en pantalla
                cv2.putText(
                    frame, f"Detecciones: {detection_count}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2
                )
            
            # Mostrar frame
            cv2.imshow('Detector de Emociones [Q=Salir | S=Stats]', frame)
            
            # Controles de teclado
            key = cv2.waitKey(1) & 0xFF
            
            if key == ord('q'):
                print("\n" + "=" * 63)
                print_colored("👋 Cerrando detector...", Fore.YELLOW if COLORS_AVAILABLE else None)
                break
            elif key == ord('s'):
                if db:
                    print_stats(db, session_start)
                else:
                    print("\n⚠️  Base de datos no disponible")
    
    except KeyboardInterrupt:
        print("\n" + "=" * 63)
        print_colored("👋 Detenido por usuario", Fore.YELLOW if COLORS_AVAILABLE else None)
    
    finally:
        # Liberar recursos
        cap.release()
        cv2.destroyAllWindows()
        
        # Estadísticas finales
        if db:
            print_stats(db, session_start)
            db.close()
        
        # Log final
        log_to_file(f"Sesión finalizada: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        log_to_file(f"Total detecciones en sesión: {detection_count}")
        log_to_file("=" * 60 + "\n")
        
        print_colored("\n✅ Recursos liberados", Fore.GREEN if COLORS_AVAILABLE else None)
        print_colored(f"📄 Logs guardados en: {LOG_FILE}", Fore.CYAN if COLORS_AVAILABLE else None)
        
        if db:
            print_colored("💾 Datos guardados en MongoDB Atlas", Fore.CYAN if COLORS_AVAILABLE else None)
        
        print("\n¡Hasta pronto! 👋\n")

# ======================== EJECUCIÓN ========================

if __name__ == "__main__":
    main()