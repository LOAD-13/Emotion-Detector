"""
Módulo de conexión y operaciones con MongoDB Atlas
"""

import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from pymongo import MongoClient, DESCENDING
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

class EmotionDatabase:
    """Clase para manejar operaciones con MongoDB"""
    
    def __init__(self):
        """Inicializa la conexión a MongoDB Atlas"""
        self.uri = os.getenv('MONGODB_URI')
        self.db_name = os.getenv('MONGODB_DATABASE', 'Emotions')
        self.collection_name = os.getenv('MONGODB_COLLECTION', 'emotions_log')
        
        if not self.uri:
            raise ValueError("⚠️  MONGODB_URI no está configurado en el archivo .env")
        
        self.client = None
        self.db = None
        self.collection = None
        self._connect()
    
    def _connect(self):
        """Establece conexión con MongoDB"""
        try:
            print("🔄 Conectando a MongoDB Atlas...")
            self.client = MongoClient(
                self.uri,
                serverSelectionTimeoutMS=5000,  # 5 segundos timeout
                connectTimeoutMS=10000
            )
            
            # Verificar conexión
            self.client.admin.command('ping')
            
            self.db = self.client[self.db_name]
            self.collection = self.db[self.collection_name]
            
            print(f"✅ Conectado a MongoDB Atlas")
            print(f"   📊 Base de datos: {self.db_name}")
            print(f"   📁 Colección: {self.collection_name}")
            
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            print(f"❌ Error de conexión a MongoDB: {e}")
            print("\n💡 Verifica:")
            print("   1. Tu connection string en .env")
            print("   2. Network Access en MongoDB Atlas")
            print("   3. Tu conexión a internet")
            raise
    
    def insert_emotion(self, emotion: str, confidence: float, 
                      metadata: Optional[Dict] = None) -> str:
        """
        Inserta una nueva detección de emoción
        
        Args:
            emotion: Nombre de la emoción detectada
            confidence: Nivel de confianza (0-1)
            metadata: Datos adicionales opcionales
            
        Returns:
            ID del documento insertado
        """
        try:
            document = {
                'emotion': emotion,
                'confidence': confidence,
                'timestamp': datetime.now(),
                'date': datetime.now().strftime('%Y-%m-%d'),
                'time': datetime.now().strftime('%H:%M:%S'),
                'hour': datetime.now().hour,
                'day_of_week': datetime.now().strftime('%A'),
                'metadata': metadata or {}
            }
            
            result = self.collection.insert_one(document)
            return str(result.inserted_id)
            
        except Exception as e:
            print(f"⚠️  Error al insertar emoción: {e}")
            return None
    
    def get_recent_emotions(self, limit: int = 50) -> List[Dict]:
        """
        Obtiene las emociones más recientes
        
        Args:
            limit: Número máximo de registros a retornar
            
        Returns:
            Lista de documentos de emociones
        """
        try:
            cursor = self.collection.find().sort('timestamp', DESCENDING).limit(limit)
            emotions = list(cursor)
            
            # Convertir ObjectId a string para JSON
            for emotion in emotions:
                emotion['_id'] = str(emotion['_id'])
                
            return emotions
            
        except Exception as e:
            print(f"⚠️  Error al obtener emociones: {e}")
            return []
    
    def get_emotions_by_date(self, date: str) -> List[Dict]:
        """
        Obtiene todas las emociones de una fecha específica
        
        Args:
            date: Fecha en formato 'YYYY-MM-DD'
            
        Returns:
            Lista de documentos
        """
        try:
            cursor = self.collection.find({'date': date}).sort('timestamp', DESCENDING)
            emotions = list(cursor)
            
            for emotion in emotions:
                emotion['_id'] = str(emotion['_id'])
                
            return emotions
            
        except Exception as e:
            print(f"⚠️  Error al obtener emociones por fecha: {e}")
            return []
    
    def get_emotion_stats(self, hours: int = 24) -> Dict:
        """
        Obtiene estadísticas de emociones en las últimas N horas
        
        Args:
            hours: Número de horas hacia atrás
            
        Returns:
            Diccionario con estadísticas
        """
        try:
            # Calcular timestamp de inicio
            start_time = datetime.now() - timedelta(hours=hours)
            
            # Agregación para contar emociones
            pipeline = [
                {
                    '$match': {
                        'timestamp': {'$gte': start_time}
                    }
                },
                {
                    '$group': {
                        '_id': '$emotion',
                        'count': {'$sum': 1},
                        'avg_confidence': {'$avg': '$confidence'}
                    }
                },
                {
                    '$sort': {'count': -1}
                }
            ]
            
            results = list(self.collection.aggregate(pipeline))
            
            # Formatear resultados
            stats = {
                'period_hours': hours,
                'total_detections': sum(r['count'] for r in results),
                'emotions': {
                    r['_id']: {
                        'count': r['count'],
                        'avg_confidence': round(r['avg_confidence'], 3)
                    }
                    for r in results
                }
            }
            
            # Calcular emoción dominante
            if results:
                stats['dominant_emotion'] = results[0]['_id']
            else:
                stats['dominant_emotion'] = None
            
            return stats
            
        except Exception as e:
            print(f"⚠️  Error al calcular estadísticas: {e}")
            return {}
    
    def get_hourly_distribution(self, date: Optional[str] = None) -> Dict:
        """
        Obtiene la distribución de emociones por hora
        
        Args:
            date: Fecha específica (None para hoy)
            
        Returns:
            Diccionario con distribución por hora
        """
        try:
            target_date = date or datetime.now().strftime('%Y-%m-%d')
            
            pipeline = [
                {
                    '$match': {'date': target_date}
                },
                {
                    '$group': {
                        '_id': {
                            'hour': '$hour',
                            'emotion': '$emotion'
                        },
                        'count': {'$sum': 1}
                    }
                },
                {
                    '$sort': {'_id.hour': 1}
                }
            ]
            
            results = list(self.collection.aggregate(pipeline))
            
            # Organizar por hora
            hourly = {}
            for r in results:
                hour = r['_id']['hour']
                emotion = r['_id']['emotion']
                
                if hour not in hourly:
                    hourly[hour] = {}
                
                hourly[hour][emotion] = r['count']
            
            return hourly
            
        except Exception as e:
            print(f"⚠️  Error al obtener distribución horaria: {e}")
            return {}
    
    def test_connection(self) -> bool:
        """
        Prueba la conexión a MongoDB
        
        Returns:
            True si la conexión es exitosa
        """
        try:
            self.client.admin.command('ping')
            count = self.collection.count_documents({})
            print(f"✅ Conexión exitosa. Documentos en colección: {count}")
            return True
        except Exception as e:
            print(f"❌ Error en conexión: {e}")
            return False
    
    def close(self):
        """Cierra la conexión a MongoDB"""
        if self.client:
            self.client.close()
            print("🔌 Conexión a MongoDB cerrada")


# ============================================
# Script de prueba
# ============================================

if __name__ == "__main__":
    """Prueba de conexión y operaciones básicas"""
    
    print("\n" + "="*60)
    print("🧪 PRUEBA DE CONEXIÓN A MONGODB ATLAS")
    print("="*60 + "\n")
    
    try:
        # Crear instancia
        db = EmotionDatabase()
        
        # Probar conexión
        if db.test_connection():
            print("\n✅ ¡Conexión exitosa!")
            
            # Insertar emoción de prueba
            print("\n📝 Insertando emoción de prueba...")
            emotion_id = db.insert_emotion(
                emotion="Felicidad",
                confidence=0.95,
                metadata={"test": True, "source": "connection_test"}
            )
            
            if emotion_id:
                print(f"✅ Emoción insertada con ID: {emotion_id}")
            
            # Obtener estadísticas
            print("\n📊 Estadísticas de las últimas 24 horas:")
            stats = db.get_emotion_stats(hours=24)
            print(f"   Total detecciones: {stats.get('total_detections', 0)}")
            print(f"   Emoción dominante: {stats.get('dominant_emotion', 'N/A')}")
            
            # Obtener emociones recientes
            print("\n📋 Últimas 5 emociones registradas:")
            recent = db.get_recent_emotions(limit=5)
            for i, emotion in enumerate(recent, 1):
                print(f"   {i}. {emotion['emotion']} ({emotion['confidence']*100:.1f}%) - {emotion['time']}")
        
        # Cerrar conexión
        db.close()
        
    except Exception as e:
        print(f"\n❌ Error durante la prueba: {e}")
    
    print("\n" + "="*60)
    print("🏁 Prueba finalizada")
    print("="*60 + "\n")