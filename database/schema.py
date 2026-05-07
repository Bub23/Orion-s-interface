import sqlite3
from datetime import datetime
import os

DB_PATH = "database/orion.db"

def init_db():
    """Initialize SQLite database with all schemas"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            subscription_tier TEXT DEFAULT 'free',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Content table (ideas/prompts)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS content (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            content_type TEXT NOT NULL,
            input_text TEXT NOT NULL,
            source TEXT NOT NULL,
            viral_score REAL DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)
    
    # Hooks table (generated viral hooks)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS hooks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content_id INTEGER NOT NULL,
            hook_text TEXT NOT NULL,
            hook_type TEXT NOT NULL,
            performance_score REAL DEFAULT 0,
            times_used INTEGER DEFAULT 0,
            is_high_performer BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (content_id) REFERENCES content(id)
        )
    """)
    
    # Videos table (rendered content)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS videos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content_id INTEGER NOT NULL,
            hook_id INTEGER NOT NULL,
            render_type TEXT NOT NULL,
            video_url TEXT,
            script TEXT NOT NULL,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (content_id) REFERENCES content(id),
            FOREIGN KEY (hook_id) REFERENCES hooks(id)
        )
    """)
    
    # Posts table (published content across platforms)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            video_id INTEGER NOT NULL,
            platform TEXT NOT NULL,
            post_id TEXT,
            published_at TIMESTAMP,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (video_id) REFERENCES videos(id)
        )
    """)
    
    # Performance metrics table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS performance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            post_id INTEGER NOT NULL,
            views INTEGER DEFAULT 0,
            engagement INTEGER DEFAULT 0,
            clicks INTEGER DEFAULT 0,
            shares INTEGER DEFAULT 0,
            comments INTEGER DEFAULT 0,
            retention_rate REAL DEFAULT 0,
            ctr REAL DEFAULT 0,
            viral_score REAL DEFAULT 0,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (post_id) REFERENCES posts(id)
        )
    """)
    
    # Hook patterns table (learning system)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS hook_patterns (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pattern_type TEXT NOT NULL,
            pattern_text TEXT NOT NULL,
            success_rate REAL DEFAULT 0,
            times_tested INTEGER DEFAULT 0,
            times_succeeded INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Subscriptions table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS subscriptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL UNIQUE,
            tier TEXT NOT NULL,
            active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)
    
    # Remix history table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS remixes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            original_content_id INTEGER NOT NULL,
            remix_content_id INTEGER NOT NULL,
            remix_type TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (original_content_id) REFERENCES content(id),
            FOREIGN KEY (remix_content_id) REFERENCES content(id)
        )
    """)
    
    conn.commit()
    conn.close()
    print("Database initialized")

if __name__ == "__main__":
    os.makedirs("database", exist_ok=True)
    init_db()
