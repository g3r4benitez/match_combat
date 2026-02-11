from sqlalchemy import create_engine, text

DB_URL = "postgresql+psycopg2://postgres:x1mtR12D23L@db.hkgctyzpmadkzqphwbio.supabase.co:5432/postgres"
engine = create_engine(DB_URL)

with engine.connect() as conn:
    conn.execute(text("ALTER TABLE competidor ALTER COLUMN historial_str DROP NOT NULL"))
    conn.execute(text("ALTER TABLE competidor ALTER COLUMN comentarios DROP NOT NULL"))
    conn.commit()
    print("✓ Migración completada: historial_str y comentarios ahora son nullable")
