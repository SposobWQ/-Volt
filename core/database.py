import sqlite3
import json
from datetime import datetime

class Database:
    def __init__(self):
        self.conn = sqlite3.connect('data/music_bot.db', check_same_thread=False)
        self.setup_tables()
    
    def setup_tables(self):
        cursor = self.conn.cursor()
        
        # Плейлисты
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS playlists (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                guild_id TEXT NOT NULL,
                name TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Треки в плейлистах
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS playlist_tracks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                playlist_id INTEGER,
                title TEXT NOT NULL,
                url TEXT NOT NULL,
                duration INTEGER,
                thumbnail TEXT,
                platform TEXT,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (playlist_id) REFERENCES playlists (id)
            )
        ''')
        
        # Настройки серверов
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS server_settings (
                guild_id TEXT PRIMARY KEY,
                admin_roles TEXT,
                dj_roles TEXT,
                max_queue_size INTEGER DEFAULT 100,
                default_volume REAL DEFAULT 0.8,
                require_vote_skip BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Добавь эту таблицу в метод setup_tables()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS voice_settings (
                guild_id TEXT PRIMARY KEY,
                default_voice_channel_id TEXT,
                auto_connect BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        self.conn.commit()
    
    def get_guild_settings(self, guild_id):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM server_settings WHERE guild_id = ?', (str(guild_id),))
        result = cursor.fetchone()
        
        if result:
            return {
                'guild_id': result[0],
                'admin_roles': json.loads(result[1]) if result[1] else [],
                'dj_roles': json.loads(result[2]) if result[2] else [],
                'max_queue_size': result[3],
                'default_volume': result[4],
                'require_vote_skip': bool(result[5])
            }
        return None
    
    def update_guild_settings(self, guild_id, **kwargs):
        # Реализация обновления настроек
        pass

    def close(self):
        if self.conn:
            self.conn.close()
            print("✅ Соединение с БД закрыто")