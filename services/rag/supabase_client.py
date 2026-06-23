from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

rag_database_url = os.getenv("RAG_DATABASE_URL") or os.getenv("DATABASE_URL")
rag_engine = create_engine(rag_database_url)
RagSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=rag_engine)

def get_rag_db():
    db = RagSessionLocal()
    try:
        yield db
    finally:
        db.close()