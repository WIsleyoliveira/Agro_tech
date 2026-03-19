# database.py - Banco de dados SQLite para leituras do sensor
import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional

class SensorDatabase:
    def __init__(self, db_path: str = "agrisensi.db"):
        self.db_path = db_path
        self.init_database()
        print(f"📊 Banco de dados inicializado: {db_path}")
    
    def init_database(self):
        """Cria as tabelas se não existirem"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tabela de leituras do sensor
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sensor_readings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                sample_number INTEGER NOT NULL,
                ph REAL NOT NULL,
                humidity REAL NOT NULL,
                nitrogen REAL,
                phosphorus REAL,
                potassium REAL,
                timestamp TEXT NOT NULL,
                notes TEXT
            )
        ''')
        
        # Tabela de sessões
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sampling_sessions (
                session_id TEXT PRIMARY KEY,
                total_samples INTEGER NOT NULL,
                completed_samples INTEGER DEFAULT 0,
                status TEXT DEFAULT 'active',
                crop TEXT,
                field_name TEXT,
                created_at TEXT NOT NULL
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def save_sensor_reading(self, reading_data: Dict) -> int:
        """Salva uma leitura do sensor"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO sensor_readings 
            (session_id, sample_number, ph, humidity, nitrogen, phosphorus, potassium, timestamp, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            reading_data.get('session_id'),
            reading_data.get('sample_number'),
            reading_data.get('ph'),
            reading_data.get('humidity'),
            reading_data.get('nitrogen'),
            reading_data.get('phosphorus'),
            reading_data.get('potassium'),
            reading_data.get('timestamp', datetime.now().isoformat()),
            reading_data.get('notes')
        ))
        
        reading_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return reading_id
    
    def get_session_readings(self, session_id: str) -> List[Dict]:
        """Retorna todas as leituras de uma sessão"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM sensor_readings 
            WHERE session_id = ? 
            ORDER BY sample_number ASC
        ''', (session_id,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def calculate_session_average(self, session_id: str) -> Dict:
        """Calcula a média dos valores de uma sessão"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                AVG(ph) as avg_ph,
                AVG(humidity) as avg_humidity,
                AVG(nitrogen) as avg_nitrogen,
                AVG(phosphorus) as avg_phosphorus,
                AVG(potassium) as avg_potassium,
                COUNT(*) as total_readings
            FROM sensor_readings 
            WHERE session_id = ?
        ''', (session_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                'ph': round(result[0], 2) if result[0] else None,
                'humidity': round(result[1], 2) if result[1] else None,
                'nitrogen': round(result[2], 2) if result[2] else None,
                'phosphorus': round(result[3], 2) if result[3] else None,
                'potassium': round(result[4], 2) if result[4] else None,
                'total_readings': result[5]
            }
        return None


db = SensorDatabase()
