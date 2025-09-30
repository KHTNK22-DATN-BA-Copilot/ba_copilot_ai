"""
Database migration runner script for BA Copilot AI Services.
Python version of the migration runner for cross-platform compatibility.
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def check_project_root():
    """Ensure we're running from the project root."""
    if not Path("pyproject.toml").exists():
        print("❌ Error: Please run this script from the project root directory")
        sys.exit(1)

def load_environment():
    """Load environment variables from .env if it exists."""
    env_file = Path(".env")
    if env_file.exists():
        print("📋 Loading environment variables from .env")
        try:
            from dotenv import load_dotenv
            load_dotenv()
        except ImportError:
            print("⚠️  python-dotenv not found, skipping .env loading")

def check_postgres_with_docker():
    """Start and check PostgreSQL container if Docker is available."""
    try:
        # Check if docker-compose is available
        subprocess.run(["docker-compose", "--version"], capture_output=True, check=True)
        
        print("🐳 Starting PostgreSQL container...")
        subprocess.run(["docker-compose", "up", "-d", "postgres"], check=True)
        
        # Wait for PostgreSQL to be ready
        print("⏳ Waiting for PostgreSQL to be ready...")
        postgres_user = os.getenv("POSTGRES_USER", "bacopilot_user")
        postgres_db = os.getenv("POSTGRES_DB", "bacopilot")
        
        for attempt in range(30):  # 30 attempts, 2 seconds each = 60 seconds timeout
            try:
                result = subprocess.run([
                    "docker-compose", "exec", "-T", "postgres", 
                    "pg_isready", f"-U{postgres_user}", f"-d{postgres_db}"
                ], capture_output=True, text=True)
                
                if result.returncode == 0:
                    print("✅ PostgreSQL is ready")
                    return True
                    
            except subprocess.CalledProcessError:
                pass
            
            time.sleep(2)
        
        print("❌ PostgreSQL failed to start within timeout")
        return False
        
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("ℹ️  Docker Compose not available, assuming PostgreSQL is running externally")
        return True

def test_database_connection():
    """Test database connection."""
    print("🔌 Testing database connection...")
    
    try:
        # Add src to path
        sys.path.insert(0, str(Path("src")))
        
        # Try to import and test connection
        try:
            from core.config import settings
            database_url = getattr(settings, 'database_url', 
                                 'postgresql://bacopilot_user:dev_password@localhost:5432/bacopilot')
        except:
            database_url = 'postgresql://bacopilot_user:dev_password@localhost:5432/bacopilot'
        
        from sqlalchemy import create_engine
        engine = create_engine(database_url)
        
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        
        print("✅ Database connection successful")
        return True
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def install_dependencies():
    """Install required dependencies if not available."""
    try:
        import alembic
        return True
    except ImportError:
        print("❌ Alembic not found. Installing dependencies...")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                         check=True)
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install dependencies: {e}")
            return False

def run_migrations():
    """Run Alembic migrations."""
    print("📊 Running Alembic migrations...")
    
    # Change to src directory where alembic.ini should be
    original_dir = os.getcwd()
    src_dir = Path("src")
    
    if src_dir.exists():
        os.chdir(src_dir)
    
    try:
        result = subprocess.run(["alembic", "upgrade", "head"], 
                              capture_output=True, text=True, check=True)
        print("✅ Database migrations completed successfully!")
        if result.stdout:
            print("Migration output:")
            print(result.stdout)
        return True
        
    except subprocess.CalledProcessError as e:
        print("❌ Database migrations failed!")
        if e.stdout:
            print("STDOUT:", e.stdout)
        if e.stderr:
            print("STDERR:", e.stderr)
        return False
        
    finally:
        os.chdir(original_dir)

def main():
    """Main migration runner."""
    print("🗄️  Running database migrations...")
    
    # Check prerequisites
    check_project_root()
    load_environment()
    
    # Ensure database is available
    if not check_postgres_with_docker():
        sys.exit(1)
    
    # Install dependencies if needed
    if not install_dependencies():
        sys.exit(1)
    
    # Test database connection
    if not test_database_connection():
        sys.exit(1)
    
    # Run migrations
    if not run_migrations():
        sys.exit(1)
    
    print("🎉 Migration process completed!")

if __name__ == "__main__":
    main()