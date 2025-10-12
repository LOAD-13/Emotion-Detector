"""
Detector de Emociones con IA
Versión: 1.0
Autor: Sistema de Detección Emocional
Descripción: Detecta emociones faciales en tiempo real usando OpenCV y DeepFace
"""

import cv2
import numpy as np
from datetime import datetime
import sys

# Manejo de colores en terminal para Windows
try:
    from colorama import init, Fore, Style
    init(autoreset=True)
    COLORS_AVAILABLE = True
except ImportError:
    COLORS_AVAILABLE = False
    print("⚠️  Instala 'colorama' para colores en terminal: pip install colorama")

# ======================== CONFIGURACIÓN ========================
LOG_FILE = 'emotion_logs.txt'
CAMERA_INDEX = 0
CONFIDENCE_THRESHOLD = 0.5  # Mínimo de confianza para mostrar emoción

# Emojis por emoción
EMOTION_EMOJIS = {
    'Enojo': '😠',
    'Asco': '🤢',
    'Miedo': '😨',
    'Felicidad': '😊',
    'Tristeza': '😢',
    'Sorpresa': '😮',
    'Neutral': '😐'
}

# Colores por emoción
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
    """Guarda log en archivo"""
    try:
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(message + '\n')
    except Exception as e:
        print(f"⚠️  Error al escribir log: {e}")

def print_header():
    """Muestra el header del programa"""
    header = """
╔═══════════════════════════════════════════════════════════╗
║          🎭 DETECTOR DE EMOCIONES CON IA 🎭              ║
║                    Versión 1.0                            ║
╚═══════════════════════════════════════════════════════════╝
"""
    print_colored(header, Fore.CYAN if COLORS_AVAILABLE else None)
    print_colored("📹 Iniciando cámara...", Fore.YELLOW if COLORS_AVAILABLE else None)
    print_colored("⌨️  Presiona 'q' en la ventana de video para salir\n", Fore.YELLOW if COLORS_AVAILABLE else None)
    print("=" * 63)

def load_emotion_model():
    """Carga el modelo de emociones usando DeepFace"""
    try:
        from deepface import DeepFace
        print_colored("🔄 Cargando modelo de IA (DeepFace)...", Fore.YELLOW if COLORS_AVAILABLE else None)
        
        # DeepFace descarga automáticamente el modelo la primera vez
        # Hacemos una predicción dummy para forzar la carga del modelo
        dummy_img = np.zeros((48, 48, 3), dtype=np.uint8)
        try:
            DeepFace.analyze(dummy_img, actions=['emotion'], enforce_detection=False, silent=True)
        except:
            pass  # Ignoramos errores en la carga inicial
        
        print_colored("✅ Modelo cargado exitosamente\n", Fore.GREEN if COLORS_AVAILABLE else None)
        return DeepFace  # Retornamos el módulo completo
    except Exception as e:
        print_colored(f"\n❌ ERROR al cargar modelo: {e}", Fore.RED if COLORS_AVAILABLE else None)
        print_colored("💡 Intenta: pip install deepface tf-keras", Fore.YELLOW if COLORS_AVAILABLE else None)
        sys.exit(1)

def detect_emotion(face_roi, deepface_module):
    """
    Detecta la emoción de un rostro usando DeepFace
    Args:
        face_roi: Región de interés (rostro) en escala de grises
        deepface_module: Módulo DeepFace
    Returns:
        tuple: (emoción, confianza)
    """
    try:
        # Convertir a RGB (DeepFace necesita 3 canales)
        face_roi_rgb = cv2.cvtColor(face_roi, cv2.COLOR_GRAY2RGB)
        
        # Redimensionar
        face_roi_rgb = cv2.resize(face_roi_rgb, (48, 48), interpolation=cv2.INTER_AREA)
        
        # Analizar con DeepFace
        result = deepface_module.analyze(
            face_roi_rgb, 
            actions=['emotion'], 
            enforce_detection=False,
            silent=True
        )
        
        # Extraer emoción dominante
        if isinstance(result, list):
            result = result[0]
        
        emotion_dict = result['emotion']
        dominant_emotion = result['dominant_emotion']
        confidence = emotion_dict[dominant_emotion] / 100.0  # Convertir a decimal
        
        # Mapear emociones de DeepFace a nuestras etiquetas en español
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
        
        return emotion, confidence
    
    except Exception as e:
        # Error silencioso para no saturar la terminal
        return None, 0.0

def log_emotion(emotion, confidence):
    """Registra la emoción detectada en terminal y archivo"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    emoji = EMOTION_EMOJIS.get(emotion, '❓')
    color = EMOTION_COLORS.get(emotion, None)
    
    # Mensaje formateado
    terminal_msg = f"[{timestamp}] {emoji} {emotion:12} ({confidence*100:.1f}%)"
    file_msg = f"[{timestamp}] {emotion} - Confianza: {confidence*100:.1f}%"
    
    # Imprimir en terminal con color
    if confidence >= CONFIDENCE_THRESHOLD:
        print_colored(terminal_msg, color)
        log_to_file(file_msg)

# ======================== FUNCIÓN PRINCIPAL ========================

def main():
    """Función principal del detector"""
    
    # Inicializar
    print_header()
    deepface = load_emotion_model()
    
    # Inicializar log file
    log_to_file(f"\n{'='*60}")
    log_to_file(f"Nueva sesión iniciada: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
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
    
    print_colored("✅ Cámara iniciada - Detectando emociones...\n", Fore.GREEN if COLORS_AVAILABLE else None)
    print("=" * 63)
    
    frame_count = 0
    last_emotion = None
    
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
            
            # Procesar solo el rostro más grande (más cercano a la cámara)
            if len(faces) > 0:
                # Encontrar el rostro más grande
                largest_face = max(faces, key=lambda face: face[2] * face[3])
                x, y, w, h = largest_face
                
                # Extraer región del rostro
                face_roi = gray[y:y+h, x:x+w]
                
                # Detectar emoción cada 10 frames (para no saturar terminal)
                if frame_count % 10 == 0:
                    emotion, confidence = detect_emotion(face_roi, deepface)
                    
                    if emotion and confidence >= CONFIDENCE_THRESHOLD:
                        # Solo mostrar si cambió la emoción
                        if emotion != last_emotion:
                            log_emotion(emotion, confidence)
                            last_emotion = emotion
                
                # Dibujar rectángulo y texto en video
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                
                if last_emotion:
                    emoji = EMOTION_EMOJIS.get(last_emotion, '')
                    label = f"{emoji} {last_emotion}"
                    cv2.putText(
                        frame, label, (x, y-10), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2
                    )
            
            # Mostrar frame
            cv2.imshow('Detector de Emociones - Presiona Q para salir', frame)
            
            # Salir con 'q'
            if cv2.waitKey(1) & 0xFF == ord('q'):
                print("\n" + "=" * 63)
                print_colored("👋 Cerrando detector...", Fore.YELLOW if COLORS_AVAILABLE else None)
                break
    
    except KeyboardInterrupt:
        print("\n" + "=" * 63)
        print_colored("👋 Detenido por usuario", Fore.YELLOW if COLORS_AVAILABLE else None)
    
    finally:
        # Liberar recursos
        cap.release()
        cv2.destroyAllWindows()
        
        # Log final
        log_to_file(f"Sesión finalizada: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        log_to_file("=" * 60 + "\n")
        
        print_colored("✅ Recursos liberados", Fore.GREEN if COLORS_AVAILABLE else None)
        print_colored(f"📄 Logs guardados en: {LOG_FILE}", Fore.CYAN if COLORS_AVAILABLE else None)
        print("\n¡Hasta pronto! 👋\n")

# ======================== EJECUCIÓN ========================

if __name__ == "__main__":
    main()