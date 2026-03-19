# user_database.py - Banco de dados de usuários com segurança
import sqlite3
from datetime import datetime
from typing import Optional, Dict, List
from auth import password_hasher


class UserDatabase:
    """Gerenciador de usuários no banco de dados"""
    
    def __init__(self, db_path: str = "agrisensi.db"):
        self.db_path = db_path
        self.init_user_tables()
        print(f"👤 Sistema de usuários inicializado")
    
    def init_user_tables(self):
        """Cria tabelas de usuários se não existirem"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tabela de usuários
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                name TEXT NOT NULL,
                phone TEXT,
                farm_name TEXT,
                plan TEXT DEFAULT 'free',
                is_active BOOLEAN DEFAULT 1,
                created_at TEXT NOT NULL,
                last_login TEXT,
                email_verified BOOLEAN DEFAULT 0,
                user_type TEXT DEFAULT 'produtor',
                cnpj TEXT,
                company_name TEXT,
                city TEXT,
                state TEXT
            )
        ''')

        # Migração: adicionar colunas novas se banco já existir
        for col, definition in [
            ("user_type", "TEXT DEFAULT 'produtor'"),
            ("cnpj",      "TEXT"),
            ("company_name", "TEXT"),
            ("city",      "TEXT"),
            ("state",     "TEXT"),
            ("vehicle_type", "TEXT"),
        ]:
            try:
                cursor.execute(f"ALTER TABLE users ADD COLUMN {col} {definition}")
            except Exception:
                pass  # Coluna já existe
        
        # Tabela de sessões/dispositivos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                refresh_token TEXT NOT NULL,
                device_info TEXT,
                ip_address TEXT,
                created_at TEXT NOT NULL,
                expires_at TEXT NOT NULL,
                is_active BOOLEAN DEFAULT 1,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Tabela de análises por usuário (para histórico)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_analyses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                session_id TEXT,
                analysis_type TEXT,
                input_data TEXT,
                result TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Tabela de planos/assinaturas
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS subscriptions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                plan_type TEXT NOT NULL,
                status TEXT DEFAULT 'active',
                started_at TEXT NOT NULL,
                expires_at TEXT,
                sensor_serial TEXT,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def create_user(self, email: str, password: str, name: str,
                   phone: Optional[str] = None, farm_name: Optional[str] = None,
                   user_type: str = "produtor", cnpj: Optional[str] = None,
                   company_name: Optional[str] = None, city: Optional[str] = None,
                   state: Optional[str] = None, vehicle_type: Optional[str] = None) -> Dict:
        """Cria novo usuário com senha hasheada"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Verifica se email já existe
            cursor.execute('SELECT id FROM users WHERE email = ?', (email,))
            if cursor.fetchone():
                conn.close()
                return {"success": False, "error": "Email já cadastrado"}
            
            # Hash da senha
            password_hash = password_hasher.hash_password(password)
            
            # Inserir usuário
            cursor.execute('''
                INSERT INTO users (email, password_hash, name, phone, farm_name,
                                   user_type, cnpj, company_name, city, state, vehicle_type, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (email, password_hash, name, phone, farm_name,
                  user_type, cnpj, company_name, city, state, vehicle_type,
                  datetime.now().isoformat()))
            
            user_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            return {
                "success": True,
                "user_id": user_id,
                "email": email,
                "name": name,
                "user_type": user_type,
                "message": "Usuário criado com sucesso!"
            }
            
        except ValueError as e:
            conn.close()
            return {"success": False, "error": str(e)}
        except Exception as e:
            conn.close()
            return {"success": False, "error": "Erro ao criar conta. Tente novamente."}
    
    def authenticate_user(self, email: str, password: str) -> Optional[Dict]:
        """Autentica usuário verificando senha"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, email, password_hash, name, phone, farm_name, plan, is_active,
                   user_type, cnpj, company_name, city, state
            FROM users WHERE email = ?
        ''', (email,))
        
        user = cursor.fetchone()
        
        if not user:
            conn.close()
            return None
        
        # Verificar se usuário está ativo
        if not user['is_active']:
            conn.close()
            return None
        
        # Verificar senha
        if not password_hasher.verify_password(password, user['password_hash']):
            conn.close()
            return None
        
        # Atualizar último login
        cursor.execute('''
            UPDATE users SET last_login = ? WHERE id = ?
        ''', (datetime.now().isoformat(), user['id']))
        
        conn.commit()
        conn.close()
        
        return {
            "user_id": user['id'],
            "email": user['email'],
            "name": user['name'],
            "phone": user['phone'],
            "farm_name": user['farm_name'],
            "plan": user['plan'],
            "user_type": user['user_type'] or "produtor",
            "cnpj": user['cnpj'],
            "company_name": user['company_name'],
            "city": user['city'],
            "state": user['state'],
        }
    
    def get_user_by_id(self, user_id: int) -> Optional[Dict]:
        """Busca usuário por ID"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, email, name, phone, farm_name, plan, user_type, created_at, last_login
            FROM users WHERE id = ?
        ''', (user_id,))
        
        user = cursor.fetchone()
        conn.close()
        
        if user:
            d = dict(user)
            d['user_id'] = d.pop('id', d.get('user_id'))
            return d
        return None
    
    def get_user_by_email(self, email: str) -> Optional[Dict]:
        """Busca usuário por email"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, email, name, phone, farm_name, plan, user_type, created_at, last_login
            FROM users WHERE email = ?
        ''', (email,))
        
        user = cursor.fetchone()
        conn.close()
        
        if user:
            d = dict(user)
            d['user_id'] = d.pop('id', d.get('user_id'))
            return d
        return None
    
    def update_user_plan(self, user_id: int, plan: str) -> bool:
        """Atualiza plano do usuário"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE users SET plan = ? WHERE id = ?
        ''', (plan, user_id))
        
        conn.commit()
        conn.close()
        return True
    
    def save_refresh_token(self, user_id: int, refresh_token: str, 
                          expires_at: str, device_info: str = None, 
                          ip_address: str = None):
        """Salva refresh token para sessão"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO user_sessions 
            (user_id, refresh_token, device_info, ip_address, created_at, expires_at)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, refresh_token, device_info, ip_address, 
              datetime.now().isoformat(), expires_at))
        
        conn.commit()
        conn.close()
    
    def verify_refresh_token(self, refresh_token: str) -> Optional[int]:
        """Verifica se refresh token é válido e retorna user_id"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT user_id FROM user_sessions 
            WHERE refresh_token = ? AND is_active = 1
            AND datetime(expires_at) > datetime('now')
        ''', (refresh_token,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return result[0]
        return None
    
    def save_user_analysis(self, user_id: int, session_id: str, 
                          analysis_type: str, input_data: str, result: str):
        """Salva análise realizada pelo usuário"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO user_analyses 
            (user_id, session_id, analysis_type, input_data, result, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, session_id, analysis_type, input_data, result, 
              datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
    
    def get_user_analyses(self, user_id: int, limit: int = 50) -> List[Dict]:
        """Retorna histórico de análises do usuário"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM user_analyses 
            WHERE user_id = ? 
            ORDER BY created_at DESC 
            LIMIT ?
        ''', (user_id, limit))
        
        analyses = cursor.fetchall()
        conn.close()
        
        return [dict(a) for a in analyses]
    
    def change_password(self, user_id: int, new_password: str) -> bool:
        """Altera senha do usuário"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        password_hash = password_hasher.hash_password(new_password)
        
        cursor.execute('''
            UPDATE users SET password_hash = ? WHERE id = ?
        ''', (password_hash, user_id))
        
        conn.commit()
        conn.close()
        return True
    
    def deactivate_user(self, user_id: int) -> bool:
        """Desativa usuário (soft delete)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE users SET is_active = 0 WHERE id = ?
        ''', (user_id,))
        
        conn.commit()
        conn.close()
        return True


# Instância global
user_db = UserDatabase()
