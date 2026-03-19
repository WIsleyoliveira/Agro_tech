# market_database.py - Banco de dados do mercado local (produtor, comprador, transportador)
import sqlite3
import os
from datetime import datetime
from typing import Optional, Dict, List

DB_PATH = "agrisensi.db"

class MarketDatabase:
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self.init_tables()
        print("🛒 Banco de dados do mercado inicializado")

    def get_conn(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    # ─────────────────────────────────────────
    # INICIALIZAÇÃO DAS TABELAS
    # ─────────────────────────────────────────
    def init_tables(self):
        conn = self.get_conn()
        c = conn.cursor()

        # Perfis de usuário (estende a tabela users)
        c.execute('''
            CREATE TABLE IF NOT EXISTS user_profiles (
                user_id     INTEGER PRIMARY KEY,
                user_type   TEXT NOT NULL DEFAULT 'produtor',
                cnpj        TEXT,
                company_name TEXT,
                city        TEXT,
                state       TEXT,
                bio         TEXT,
                whatsapp    TEXT,
                verified    INTEGER DEFAULT 0,
                created_at  TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')

        # Publicações de produtos (produtor posta o que quer vender)
        c.execute('''
            CREATE TABLE IF NOT EXISTS listings (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id      INTEGER NOT NULL,
                title        TEXT NOT NULL,
                description  TEXT,
                crop         TEXT,
                quantity_kg  REAL,
                price_per_kg REAL,
                city         TEXT,
                state        TEXT,
                image_path   TEXT,
                status       TEXT DEFAULT 'disponivel',
                created_at   TEXT NOT NULL,
                updated_at   TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')

        # Negociações (comprador inicia negócio com produtor)
        c.execute('''
            CREATE TABLE IF NOT EXISTS deals (
                id             INTEGER PRIMARY KEY AUTOINCREMENT,
                listing_id     INTEGER NOT NULL,
                buyer_id       INTEGER NOT NULL,
                producer_id    INTEGER NOT NULL,
                status         TEXT DEFAULT 'negociando',
                transport_fee  REAL,
                transporter_id INTEGER,
                notes          TEXT,
                created_at     TEXT NOT NULL,
                updated_at     TEXT NOT NULL,
                FOREIGN KEY (listing_id)     REFERENCES listings(id),
                FOREIGN KEY (buyer_id)       REFERENCES users(id),
                FOREIGN KEY (producer_id)    REFERENCES users(id),
                FOREIGN KEY (transporter_id) REFERENCES users(id)
            )
        ''')

        # Mensagens entre usuários (chat interno)
        c.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                deal_id     INTEGER,
                sender_id   INTEGER NOT NULL,
                receiver_id INTEGER NOT NULL,
                content     TEXT NOT NULL,
                read_at     TEXT,
                created_at  TEXT NOT NULL,
                FOREIGN KEY (deal_id)     REFERENCES deals(id),
                FOREIGN KEY (sender_id)   REFERENCES users(id),
                FOREIGN KEY (receiver_id) REFERENCES users(id)
            )
        ''')

        # Avaliações (após deal concluído)
        c.execute('''
            CREATE TABLE IF NOT EXISTS ratings (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                deal_id     INTEGER NOT NULL,
                rater_id    INTEGER NOT NULL,
                rated_id    INTEGER NOT NULL,
                stars       INTEGER NOT NULL CHECK(stars BETWEEN 1 AND 5),
                comment     TEXT,
                created_at  TEXT NOT NULL,
                UNIQUE(deal_id, rater_id),
                FOREIGN KEY (deal_id)   REFERENCES deals(id),
                FOREIGN KEY (rater_id)  REFERENCES users(id),
                FOREIGN KEY (rated_id)  REFERENCES users(id)
            )
        ''')

        # Notificações
        c.execute('''
            CREATE TABLE IF NOT EXISTS notifications (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id     INTEGER NOT NULL,
                type        TEXT NOT NULL,
                title       TEXT NOT NULL,
                body        TEXT NOT NULL,
                deal_id     INTEGER,
                read_at     TEXT,
                created_at  TEXT NOT NULL,
                FOREIGN KEY (user_id)  REFERENCES users(id),
                FOREIGN KEY (deal_id)  REFERENCES deals(id)
            )
        ''')

        # Migração segura: adiciona coluna 'entregue' ao status de deals existentes (já suportado via texto)
        # Adiciona coluna delivered_at se não existir
        try:
            c.execute('ALTER TABLE deals ADD COLUMN delivered_at TEXT')
        except Exception:
            pass

        conn.commit()
        conn.close()

    # ─────────────────────────────────────────
    # PERFIS
    # ─────────────────────────────────────────
    def upsert_profile(self, user_id: int, user_type: str,
                       cnpj: str = None, company_name: str = None,
                       city: str = None, state: str = None,
                       bio: str = None, whatsapp: str = None) -> Dict:
        conn = self.get_conn()
        c = conn.cursor()
        try:
            now = datetime.now().isoformat()
            c.execute('SELECT user_id FROM user_profiles WHERE user_id = ?', (user_id,))
            exists = c.fetchone()
            if exists:
                c.execute('''UPDATE user_profiles
                             SET user_type=?, cnpj=?, company_name=?, city=?, state=?,
                                 bio=?, whatsapp=?
                             WHERE user_id=?''',
                          (user_type, cnpj, company_name, city, state, bio, whatsapp, user_id))
            else:
                c.execute('''INSERT INTO user_profiles
                             (user_id, user_type, cnpj, company_name, city, state, bio, whatsapp, created_at)
                             VALUES (?,?,?,?,?,?,?,?,?)''',
                          (user_id, user_type, cnpj, company_name, city, state, bio, whatsapp, now))
            conn.commit()
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}
        finally:
            conn.close()

    def get_profile(self, user_id: int) -> Optional[Dict]:
        conn = self.get_conn()
        c = conn.cursor()
        c.execute('''
            SELECT u.id, u.name, u.email, p.user_type, p.cnpj, p.company_name,
                   p.city, p.state, p.bio, p.whatsapp, p.verified
            FROM users u
            LEFT JOIN user_profiles p ON u.id = p.user_id
            WHERE u.id = ?
        ''', (user_id,))
        row = c.fetchone()
        conn.close()
        return dict(row) if row else None

    def set_verified(self, user_id: int, verified: bool):
        conn = self.get_conn()
        conn.execute('UPDATE user_profiles SET verified=? WHERE user_id=?',
                     (1 if verified else 0, user_id))
        conn.commit()
        conn.close()

    # ─────────────────────────────────────────
    # PUBLICAÇÕES (LISTINGS)
    # ─────────────────────────────────────────
    def create_listing(self, user_id: int, title: str, description: str,
                       crop: str, quantity_kg: float, price_per_kg: float,
                       city: str, state: str, image_path: str = None) -> Dict:
        conn = self.get_conn()
        c = conn.cursor()
        try:
            now = datetime.now().isoformat()
            c.execute('''INSERT INTO listings
                         (user_id, title, description, crop, quantity_kg, price_per_kg,
                          city, state, image_path, status, created_at, updated_at)
                         VALUES (?,?,?,?,?,?,?,?,?,?,?,?)''',
                      (user_id, title, description, crop, quantity_kg, price_per_kg,
                       city, state, image_path, 'disponivel', now, now))
            conn.commit()
            return {"success": True, "listing_id": c.lastrowid}
        except Exception as e:
            return {"success": False, "error": str(e)}
        finally:
            conn.close()

    def get_listings(self, state: str = None, crop: str = None,
                     status: str = 'disponivel', limit: int = 50) -> List[Dict]:
        conn = self.get_conn()
        c = conn.cursor()
        query = '''
            SELECT l.*, u.name as producer_name, p.whatsapp, p.verified
            FROM listings l
            JOIN users u ON l.user_id = u.id
            LEFT JOIN user_profiles p ON l.user_id = p.user_id
            WHERE l.status = ?
        '''
        params = [status]
        if state:
            query += ' AND l.state = ?'
            params.append(state)
        if crop:
            query += ' AND l.crop LIKE ?'
            params.append(f'%{crop}%')
        query += ' ORDER BY l.created_at DESC LIMIT ?'
        params.append(limit)
        c.execute(query, params)
        rows = c.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def get_listing(self, listing_id: int) -> Optional[Dict]:
        conn = self.get_conn()
        c = conn.cursor()
        c.execute('''
            SELECT l.*, u.name as producer_name, p.whatsapp, p.city as producer_city,
                   p.verified, p.user_type
            FROM listings l
            JOIN users u ON l.user_id = u.id
            LEFT JOIN user_profiles p ON l.user_id = p.user_id
            WHERE l.id = ?
        ''', (listing_id,))
        row = c.fetchone()
        conn.close()
        return dict(row) if row else None

    def get_my_listings(self, user_id: int) -> List[Dict]:
        conn = self.get_conn()
        c = conn.cursor()
        c.execute('''SELECT * FROM listings WHERE user_id = ?
                     ORDER BY created_at DESC''', (user_id,))
        rows = c.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def update_listing_status(self, listing_id: int, status: str):
        conn = self.get_conn()
        conn.execute('UPDATE listings SET status=?, updated_at=? WHERE id=?',
                     (status, datetime.now().isoformat(), listing_id))
        conn.commit()
        conn.close()

    def delete_listing(self, listing_id: int, user_id: int) -> bool:
        conn = self.get_conn()
        c = conn.cursor()
        c.execute('DELETE FROM listings WHERE id=? AND user_id=?', (listing_id, user_id))
        conn.commit()
        deleted = c.rowcount > 0
        conn.close()
        return deleted

    # ─────────────────────────────────────────
    # NEGOCIAÇÕES (DEALS)
    # ─────────────────────────────────────────
    def create_deal(self, listing_id: int, buyer_id: int, producer_id: int) -> Dict:
        conn = self.get_conn()
        c = conn.cursor()
        try:
            # Verifica se já existe negociação aberta entre esses dois para essa publicação
            c.execute('''SELECT id FROM deals WHERE listing_id=? AND buyer_id=?
                         AND status NOT IN ('cancelado','recusado')''',
                      (listing_id, buyer_id))
            existing = c.fetchone()
            if existing:
                return {"success": False, "error": "Você já tem uma negociação aberta para esta publicação.",
                        "deal_id": existing["id"]}
            now = datetime.now().isoformat()
            c.execute('''INSERT INTO deals
                         (listing_id, buyer_id, producer_id, status, created_at, updated_at)
                         VALUES (?,?,?,?,?,?)''',
                      (listing_id, buyer_id, producer_id, 'negociando', now, now))
            conn.commit()
            return {"success": True, "deal_id": c.lastrowid}
        except Exception as e:
            return {"success": False, "error": str(e)}
        finally:
            conn.close()

    def update_deal_status(self, deal_id: int, status: str,
                            transport_fee: float = None,
                            transporter_id: int = None) -> Dict:
        conn = self.get_conn()
        c = conn.cursor()
        try:
            now = datetime.now().isoformat()
            if transport_fee is not None and transporter_id is not None:
                c.execute('''UPDATE deals SET status=?, transport_fee=?,
                             transporter_id=?, updated_at=? WHERE id=?''',
                          (status, transport_fee, transporter_id, now, deal_id))
            else:
                c.execute('UPDATE deals SET status=?, updated_at=? WHERE id=?',
                          (status, now, deal_id))
            conn.commit()
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}
        finally:
            conn.close()

    def get_deal(self, deal_id: int) -> Optional[Dict]:
        conn = self.get_conn()
        c = conn.cursor()
        c.execute('''
            SELECT d.*,
                   l.title as listing_title, l.crop, l.quantity_kg, l.price_per_kg, l.image_path,
                   ub.name as buyer_name,
                   up.name as producer_name,
                   ut.name as transporter_name
            FROM deals d
            JOIN listings l      ON d.listing_id    = l.id
            JOIN users ub        ON d.buyer_id       = ub.id
            JOIN users up        ON d.producer_id    = up.id
            LEFT JOIN users ut   ON d.transporter_id = ut.id
            WHERE d.id = ?
        ''', (deal_id,))
        row = c.fetchone()
        conn.close()
        return dict(row) if row else None

    def get_my_deals(self, user_id: int) -> List[Dict]:
        """Retorna todos os negócios onde o usuário é comprador, produtor ou transportador"""
        conn = self.get_conn()
        c = conn.cursor()
        c.execute('''
            SELECT d.*,
                   l.title as listing_title, l.crop, l.quantity_kg, l.price_per_kg, l.state as listing_state,
                   ub.name as buyer_name,
                   up.name as producer_name,
                   ut.name as transporter_name
            FROM deals d
            JOIN listings l      ON d.listing_id    = l.id
            JOIN users ub        ON d.buyer_id       = ub.id
            JOIN users up        ON d.producer_id    = up.id
            LEFT JOIN users ut   ON d.transporter_id = ut.id
            WHERE d.buyer_id=? OR d.producer_id=? OR d.transporter_id=?
            ORDER BY d.updated_at DESC
        ''', (user_id, user_id, user_id))
        rows = c.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def get_open_transports(self) -> List[Dict]:
        """Negócios fechados que ainda precisam de transportador"""
        conn = self.get_conn()
        c = conn.cursor()
        c.execute('''
            SELECT d.*,
                   l.title as listing_title, l.crop, l.quantity_kg, l.price_per_kg,
                   l.city as listing_city, l.state as listing_state,
                   up.name as producer_name,
                   ub.name as buyer_name
            FROM deals d
            JOIN listings l   ON d.listing_id  = l.id
            JOIN users up     ON d.producer_id  = up.id
            JOIN users ub     ON d.buyer_id     = ub.id
            WHERE d.status = 'fechado' AND d.transporter_id IS NULL
            ORDER BY d.updated_at DESC
        ''')
        rows = c.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    # ─────────────────────────────────────────
    # MENSAGENS (CHAT INTERNO)
    # ─────────────────────────────────────────
    def send_message(self, sender_id: int, receiver_id: int,
                     content: str, deal_id: int = None) -> Dict:
        conn = self.get_conn()
        c = conn.cursor()
        try:
            now = datetime.now().isoformat()
            c.execute('''INSERT INTO messages (deal_id, sender_id, receiver_id, content, created_at)
                         VALUES (?,?,?,?,?)''',
                      (deal_id, sender_id, receiver_id, content, now))
            conn.commit()
            return {"success": True, "message_id": c.lastrowid}
        except Exception as e:
            return {"success": False, "error": str(e)}
        finally:
            conn.close()

    def get_conversation(self, user_a: int, user_b: int, deal_id: int = None) -> List[Dict]:
        conn = self.get_conn()
        c = conn.cursor()
        if deal_id:
            c.execute('''
                SELECT m.*, us.name as sender_name
                FROM messages m
                JOIN users us ON m.sender_id = us.id
                WHERE m.deal_id = ?
                ORDER BY m.created_at ASC
            ''', (deal_id,))
        else:
            c.execute('''
                SELECT m.*, us.name as sender_name
                FROM messages m
                JOIN users us ON m.sender_id = us.id
                WHERE (m.sender_id=? AND m.receiver_id=?)
                   OR (m.sender_id=? AND m.receiver_id=?)
                ORDER BY m.created_at ASC
            ''', (user_a, user_b, user_b, user_a))
        rows = c.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def mark_messages_read(self, receiver_id: int, deal_id: int):
        conn = self.get_conn()
        conn.execute('''UPDATE messages SET read_at=?
                        WHERE receiver_id=? AND deal_id=? AND read_at IS NULL''',
                     (datetime.now().isoformat(), receiver_id, deal_id))
        conn.commit()
        conn.close()

    def count_unread(self, user_id: int) -> int:
        conn = self.get_conn()
        c = conn.cursor()
        c.execute('SELECT COUNT(*) FROM messages WHERE receiver_id=? AND read_at IS NULL',
                  (user_id,))
        count = c.fetchone()[0]
        conn.close()
        return count

    def get_inbox(self, user_id: int) -> List[Dict]:
        """Lista conversas com última mensagem de cada negócio"""
        conn = self.get_conn()
        c = conn.cursor()
        c.execute('''
            SELECT m.deal_id, m.content as last_message, m.created_at,
                   d.status as deal_status, l.title as listing_title,
                   CASE WHEN m.sender_id = ? THEN ur.name ELSE us.name END as other_name,
                   CASE WHEN m.sender_id = ? THEN m.receiver_id ELSE m.sender_id END as other_id,
                   SUM(CASE WHEN m.receiver_id=? AND m.read_at IS NULL THEN 1 ELSE 0 END) as unread
            FROM messages m
            LEFT JOIN deals d ON m.deal_id = d.id
            LEFT JOIN listings l ON d.listing_id = l.id
            JOIN users us ON m.sender_id = us.id
            JOIN users ur ON m.receiver_id = ur.id
            WHERE m.sender_id=? OR m.receiver_id=?
            GROUP BY m.deal_id
            ORDER BY m.created_at DESC
        ''', (user_id, user_id, user_id, user_id, user_id))
        rows = c.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    # ─────────────────────────────────────────
    # AVALIAÇÕES (RATINGS)
    # ─────────────────────────────────────────
    def create_rating(self, deal_id: int, rater_id: int, rated_id: int,
                      stars: int, comment: str = None) -> Dict:
        conn = self.get_conn()
        c = conn.cursor()
        try:
            now = datetime.now().isoformat()
            c.execute('''INSERT OR IGNORE INTO ratings
                         (deal_id, rater_id, rated_id, stars, comment, created_at)
                         VALUES (?,?,?,?,?,?)''',
                      (deal_id, rater_id, rated_id, stars, comment, now))
            conn.commit()
            if c.rowcount == 0:
                return {"success": False, "error": "Você já avaliou este negócio."}
            return {"success": True, "rating_id": c.lastrowid}
        except Exception as e:
            return {"success": False, "error": str(e)}
        finally:
            conn.close()

    def get_user_ratings(self, user_id: int) -> Dict:
        conn = self.get_conn()
        c = conn.cursor()
        c.execute('''SELECT stars, comment, created_at, u.name as rater_name
                     FROM ratings r
                     JOIN users u ON r.rater_id = u.id
                     WHERE r.rated_id = ?
                     ORDER BY r.created_at DESC''', (user_id,))
        rows = c.fetchall()
        conn.close()
        if not rows:
            return {"average": 0.0, "count": 0, "ratings": []}
        items = [dict(r) for r in rows]
        avg = round(sum(r["stars"] for r in items) / len(items), 1)
        return {"average": avg, "count": len(items), "ratings": items}

    def can_rate(self, deal_id: int, rater_id: int) -> bool:
        """Verifica se o usuário ainda não avaliou este deal"""
        conn = self.get_conn()
        c = conn.cursor()
        c.execute('SELECT id FROM ratings WHERE deal_id=? AND rater_id=?', (deal_id, rater_id))
        row = c.fetchone()
        conn.close()
        return row is None

    # ─────────────────────────────────────────
    # NOTIFICAÇÕES
    # ─────────────────────────────────────────
    def create_notification(self, user_id: int, ntype: str,
                             title: str, body: str, deal_id: int = None):
        conn = self.get_conn()
        try:
            conn.execute('''INSERT INTO notifications
                            (user_id, type, title, body, deal_id, created_at)
                            VALUES (?,?,?,?,?,?)''',
                         (user_id, ntype, title, body, deal_id, datetime.now().isoformat()))
            conn.commit()
        except Exception:
            pass
        finally:
            conn.close()

    def get_notifications(self, user_id: int, unread_only: bool = False) -> List[Dict]:
        conn = self.get_conn()
        c = conn.cursor()
        q = 'SELECT * FROM notifications WHERE user_id=?'
        if unread_only:
            q += ' AND read_at IS NULL'
        q += ' ORDER BY created_at DESC LIMIT 50'
        c.execute(q, (user_id,))
        rows = c.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def mark_notifications_read(self, user_id: int, notif_id: int = None):
        conn = self.get_conn()
        now = datetime.now().isoformat()
        if notif_id:
            conn.execute('UPDATE notifications SET read_at=? WHERE id=? AND user_id=?',
                         (now, notif_id, user_id))
        else:
            conn.execute('UPDATE notifications SET read_at=? WHERE user_id=? AND read_at IS NULL',
                         (now, user_id))
        conn.commit()
        conn.close()

    def count_unread_notifications(self, user_id: int) -> int:
        conn = self.get_conn()
        c = conn.cursor()
        c.execute('SELECT COUNT(*) FROM notifications WHERE user_id=? AND read_at IS NULL', (user_id,))
        count = c.fetchone()[0]
        conn.close()
        return count

    # ─────────────────────────────────────────
    # DASHBOARD / STATS DO PRODUTOR
    # ─────────────────────────────────────────
    def get_producer_stats(self, user_id: int) -> Dict:
        conn = self.get_conn()
        c = conn.cursor()
        # Anúncios ativos
        c.execute("SELECT COUNT(*) FROM listings WHERE user_id=? AND status='disponivel'", (user_id,))
        active_listings = c.fetchone()[0]
        # Total negócios
        c.execute("SELECT COUNT(*) FROM deals WHERE producer_id=?", (user_id,))
        total_deals = c.fetchone()[0]
        # Negócios fechados/concluídos
        c.execute("SELECT COUNT(*) FROM deals WHERE producer_id=? AND status IN ('fechado','concluido','em_transporte','entregue')", (user_id,))
        closed_deals = c.fetchone()[0]
        # Total kg e R$ negociados
        c.execute('''SELECT COALESCE(SUM(l.quantity_kg),0), COALESCE(SUM(l.quantity_kg * l.price_per_kg),0)
                     FROM deals d JOIN listings l ON d.listing_id=l.id
                     WHERE d.producer_id=? AND d.status IN ('fechado','concluido','em_transporte','entregue')''',
                  (user_id,))
        row = c.fetchone()
        total_kg = round(row[0], 1)
        total_brl = round(row[1], 2)
        # Avaliação média
        ratings = self.get_user_ratings(user_id)
        conn.close()
        return {
            "active_listings": active_listings,
            "total_deals": total_deals,
            "closed_deals": closed_deals,
            "total_kg": total_kg,
            "total_brl": total_brl,
            "rating_avg": ratings["average"],
            "rating_count": ratings["count"],
        }

    def get_listings_with_price_avg(self, state: str = None, crop: str = None,
                                     status: str = 'disponivel', limit: int = 50) -> List[Dict]:
        """Retorna listings com avg de preço da cultura para comparação"""
        conn = self.get_conn()
        c = conn.cursor()
        query = '''
            SELECT l.*, u.name as producer_name, p.whatsapp, p.verified,
                   (SELECT ROUND(AVG(l2.price_per_kg),2) FROM listings l2
                    WHERE l2.crop=l.crop AND l2.status='disponivel') as crop_avg_price,
                   (SELECT ROUND(AVG(r.stars),1) FROM ratings r WHERE r.rated_id=l.user_id) as producer_rating,
                   (SELECT COUNT(*) FROM ratings r WHERE r.rated_id=l.user_id) as producer_rating_count
            FROM listings l
            JOIN users u ON l.user_id = u.id
            LEFT JOIN user_profiles p ON l.user_id = p.user_id
            WHERE l.status = ?
        '''
        params = [status]
        if state:
            query += ' AND l.state = ?'
            params.append(state)
        if crop:
            query += ' AND l.crop LIKE ?'
            params.append(f'%{crop}%')
        query += ' ORDER BY l.created_at DESC LIMIT ?'
        params.append(limit)
        c.execute(query, params)
        rows = c.fetchall()
        conn.close()
        return [dict(r) for r in rows]


market_db = MarketDatabase()
