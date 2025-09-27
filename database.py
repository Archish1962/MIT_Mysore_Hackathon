# database.py
import sqlite3
import json
from datetime import datetime
from typing import Dict, Any

class DatabaseManager:
    """Manage SQLite database operations for ISTVON logging"""
    
    def __init__(self, db_name: str = 'istvon_logs.db'):
        self.db_name = db_name
        self.setup_database()
    
    def setup_database(self):
        """Initialize database with required tables"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        # Check if table exists and has new columns
        cursor.execute("PRAGMA table_info(prompt_transformations)")
        columns = [column[1] for column in cursor.fetchall()]
        
        # Main transformations table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS prompt_transformations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                original_prompt TEXT NOT NULL,
                istvon_json TEXT NOT NULL,
                success_flag BOOLEAN NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                domain_category TEXT,
                prompt_length INTEGER,
                transformation_time_ms INTEGER,
                verdict TEXT,
                reason TEXT,
                sanitized_prompt TEXT,
                response TEXT
            )
        ''')
        
        # Add new columns if they don't exist
        new_columns = [
            ('verdict', 'TEXT'),
            ('reason', 'TEXT'),
            ('sanitized_prompt', 'TEXT'),
            ('response', 'TEXT')
        ]
        
        for column_name, column_type in new_columns:
            if column_name not in columns:
                cursor.execute(f'ALTER TABLE prompt_transformations ADD COLUMN {column_name} {column_type}')
        
        # Analytics view
        cursor.execute('''
            CREATE VIEW IF NOT EXISTS transformation_analytics AS
            SELECT 
                domain_category,
                COUNT(*) as total_transformations,
                AVG(prompt_length) as avg_prompt_length,
                AVG(transformation_time_ms) as avg_processing_time,
                (COUNT(CASE WHEN success_flag = 1 THEN 1 END) * 100.0 / COUNT(*)) as success_rate
            FROM prompt_transformations 
            GROUP BY domain_category
        ''')
        
        conn.commit()
        conn.close()
    
    def log_transformation(self, original_prompt: str, istvon_json: Dict, 
                          success: bool, domain: str = "auto", 
                          processing_time: int = 0, verdict: str = None,
                          reason: str = None, sanitized_prompt: str = None,
                          response: str = None):
        """Log a prompt transformation to the database"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO prompt_transformations 
            (original_prompt, istvon_json, success_flag, domain_category, prompt_length, 
             transformation_time_ms, verdict, reason, sanitized_prompt, response)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            original_prompt, 
            json.dumps(istvon_json), 
            success, 
            domain, 
            len(original_prompt),
            processing_time,
            verdict,
            reason,
            sanitized_prompt,
            response
        ))
        
        conn.commit()
        conn.close()
    
    def get_analytics(self) -> Dict[str, Any]:
        """Get transformation analytics"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                COUNT(*) as total,
                AVG(prompt_length) as avg_length,
                COUNT(CASE WHEN success_flag = 1 THEN 1 END) * 100.0 / COUNT(*) as success_rate
            FROM prompt_transformations
        ''')
        
        result = cursor.fetchone()
        conn.close()
        
        return {
            "total_transformations": result[0],
            "avg_prompt_length": round(result[1] or 0, 1),
            "success_rate": round(result[2] or 0, 1)
        }
    
    def get_recent_transformations(self, limit: int = 5):
        """Get recent transformations for display"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT original_prompt, istvon_json, created_at, success_flag
            FROM prompt_transformations 
            ORDER BY created_at DESC 
            LIMIT ?
        ''', (limit,))
        
        results = cursor.fetchall()
        conn.close()
        
        return [
            {
                "prompt": row[0][:100] + "..." if len(row[0]) > 100 else row[0],
                "timestamp": row[2],
                "success": bool(row[3])
            }
            for row in results
        ]
    
    def get_sanitized_prompts(self, limit: int = 10):
        """Get recent sanitized prompts for display"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT original_prompt, istvon_json, sanitized_prompt, created_at, verdict
            FROM prompt_transformations 
            WHERE sanitized_prompt IS NOT NULL AND sanitized_prompt != ''
            ORDER BY created_at DESC 
            LIMIT ?
        ''', (limit,))
        
        results = cursor.fetchall()
        conn.close()
        
        return [
            {
                "original_prompt": row[0],
                "istvon_json": json.loads(row[1]) if row[1] else {},
                "sanitized_prompt": row[2],
                "timestamp": row[3],
                "verdict": row[4]
            }
            for row in results
        ]