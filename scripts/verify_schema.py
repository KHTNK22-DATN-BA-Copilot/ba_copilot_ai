"""
Schema verification and integrity tests for BA Copilot AI Services.
"""

import os
import sys
from pathlib import Path
from typing import List, Dict, Any

def verify_schema():
    """Verify database schema integrity."""
    try:
        # Add src to Python path
        sys.path.insert(0, str(Path("src")))
        
        from sqlalchemy import create_engine, inspect, text
        
        # Get database URL from environment or use default
        database_url = os.getenv("DATABASE_URL", 
                                "postgresql://bacopilot_user:dev_password@localhost:5432/bacopilot")
        
        engine = create_engine(database_url)
        inspector = inspect(engine)
        
        errors = []
        
        # Check required tables exist
        required_tables = ['users', 'documents', 'wireframes', 'conversations', 'messages', 'diagrams']
        existing_tables = inspector.get_table_names()
        
        print(f"📋 Found {len(existing_tables)} tables: {', '.join(existing_tables)}")
        
        for table in required_tables:
            if table not in existing_tables:
                errors.append(f"Missing required table: {table}")
        
        # Check foreign key constraints
        for table in existing_tables:
            if table in required_tables:  # Only check our application tables
                fks = inspector.get_foreign_keys(table)
                for fk in fks:
                    if fk['referred_table'] not in existing_tables:
                        errors.append(f"Foreign key in {table} references non-existent table: {fk['referred_table']}")
        
        # Check required indexes exist
        required_indexes = [
            ('users', 'idx_users_email'),
            ('documents', 'idx_documents_user_id'),
            ('conversations', 'idx_conversations_user_id'),
            ('messages', 'idx_messages_conversation_id'),
        ]
        
        for table, index in required_indexes:
            if table in existing_tables:
                indexes = inspector.get_indexes(table)
                index_names = [idx['name'] for idx in indexes]
                if index not in index_names:
                    errors.append(f"Missing required index: {index} on table {table}")
        
        # Check required columns exist
        required_columns = {
            'users': ['user_id', 'email', 'password_hash', 'full_name', 'created_at', 'updated_at'],
            'documents': ['document_id', 'user_id', 'project_name', 'content', 'created_at', 'updated_at'],
            'wireframes': ['wireframe_id', 'user_id', 'title', 'created_at', 'updated_at'],
            'conversations': ['conversation_id', 'user_id', 'title', 'created_at', 'updated_at'],
            'messages': ['message_id', 'conversation_id', 'role', 'content', 'timestamp'],
            'diagrams': ['diagram_id', 'user_id', 'title', 'diagram_type', 'mermaid_code', 'created_at', 'updated_at']
        }
        
        for table, required_cols in required_columns.items():
            if table in existing_tables:
                columns = inspector.get_columns(table)
                column_names = [col['name'] for col in columns]
                for required_col in required_cols:
                    if required_col not in column_names:
                        errors.append(f"Missing required column: {required_col} in table {table}")
        
        # Test basic data operations
        with engine.connect() as conn:
            # Test if we can perform basic operations
            try:
                conn.execute(text("SELECT 1"))
            except Exception as e:
                errors.append(f"Basic query test failed: {e}")
            
            # Test if extensions are available
            try:
                result = conn.execute(text("SELECT extname FROM pg_extension WHERE extname IN ('uuid-ossp', 'pg_trgm')"))
                extensions = [row[0] for row in result]
                if 'uuid-ossp' not in extensions:
                    errors.append("Required extension 'uuid-ossp' is not installed")
                if 'pg_trgm' not in extensions:
                    errors.append("Required extension 'pg_trgm' is not installed")
            except Exception as e:
                errors.append(f"Extension check failed: {e}")
        
        # Report results
        if errors:
            print("❌ Schema verification failed:")
            for error in errors:
                print(f"  - {error}")
            return False
        else:
            print("✅ Schema verification passed!")
            print(f"📊 Verified {len(required_tables)} tables with all required columns and indexes")
            return True
            
    except Exception as e:
        print(f"❌ Schema verification failed with exception: {e}")
        return False

def main():
    """Main verification function."""
    print("🔍 Starting database schema verification...")
    
    success = verify_schema()
    
    if not success:
        sys.exit(1)
    
    print("🎉 Database schema verification completed successfully!")

if __name__ == "__main__":
    main()