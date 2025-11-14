"""
Migration script to add structured_data column to projects table.

Run this once to update the database schema.
"""

import sys
from pathlib import Path

# Add parent directory to path for shared imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine, text
from shared.config import get_config
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def migrate():
    """Add structured_data JSONB column to projects table."""
    config = get_config()
    engine = create_engine(config.database_url)
    
    with engine.connect() as conn:
        try:
            # Check if column already exists
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='projects' AND column_name='structured_data'
            """))
            
            if result.fetchone():
                logger.info("✅ Column 'structured_data' already exists")
                return
            
            # Add the column
            logger.info("Adding 'structured_data' column to projects table...")
            conn.execute(text("""
                ALTER TABLE projects 
                ADD COLUMN structured_data JSONB
            """))
            conn.commit()
            
            logger.info("✅ Successfully added 'structured_data' column!")
            logger.info("Database schema updated.")
            
        except Exception as e:
            logger.error(f"❌ Migration failed: {e}")
            conn.rollback()
            raise

if __name__ == "__main__":
    migrate()
