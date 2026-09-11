from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from urllib.parse import quote_plus

# Replace these with your actual Render Postgres DB URL
DATABASE_URL = "postgresql://ai_railops_db_user:tHCuLObd3lAGhhJW1eLrs5hOZfSPEN4s@dpg-dahnuu3m8hqs73cl4b6g-a.oregon-postgres.render.com/ai_railops_db"

# If using Render, it will give you this URL automatically
# Example: postgresql://user:pass@db.render.com:5432/mydb

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
