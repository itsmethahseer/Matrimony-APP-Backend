from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import settings
import logging

logger = logging.getLogger(__name__)

DATABASE_URL = settings.DATABASE_URL

def get_engine():
    try:
        connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
        engine_inst = create_engine(DATABASE_URL, connect_args=connect_args)
        # Test connection immediately
        with engine_inst.connect() as conn:
            pass
        return engine_inst
    except Exception as e:
        logger.warning(f"Failed to connect to primary DB ({DATABASE_URL}): {e}. Falling back to SQLite.")
        fallback_url = "sqlite:///./matrimony.db"
        return create_engine(fallback_url, connect_args={"check_same_thread": False})

engine = get_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def run_auto_migrations(engine_instance):
    """Automatically add any missing columns to PostgreSQL/SQLite tables safely."""
    cols_to_add = [
        ("caste", "VARCHAR"),
        ("sub_caste", "VARCHAR"),
        ("partner_religion", "JSON"),
        ("partner_caste", "JSON"),
        ("partner_sub_caste", "JSON"),
        ("tagline", "VARCHAR"),
        ("profile_description", "VARCHAR"),
        ("voice_intro_url", "VARCHAR"),
        ("video_intro_url", "VARCHAR"),
        ("future_children_plans", "VARCHAR"),
        ("primary_no", "VARCHAR"),
        ("secondary_no", "VARCHAR"),
        ("email", "VARCHAR"),
        ("whatsapp_no", "VARCHAR"),
        ("contact_person", "VARCHAR"),
        ("full_address", "TEXT"),
        ("preferred_contact_method", "VARCHAR"),
        ("best_time_to_call", "VARCHAR"),
        ("university_or_college", "VARCHAR"),
        ("job_title_or_role", "VARCHAR"),
        ("company_name", "VARCHAR"),
        ("job_experience", "VARCHAR"),
        ("present_state", "VARCHAR"),
        ("present_country", "VARCHAR"),
        ("residential_location", "VARCHAR"),
        ("home_location", "VARCHAR"),
        ("grew_up_in", "VARCHAR"),
        ("willing_to_relocate", "VARCHAR"),
        ("questionnaires", "JSON"),
    ]
    try:
        with engine_instance.begin() as conn:
            for col_name, col_type in cols_to_add:
                try:
                    if "sqlite" in str(engine_instance.url):
                        conn.execute(text(f"ALTER TABLE profiles ADD COLUMN {col_name} {col_type};"))
                    else:
                        conn.execute(text(f"ALTER TABLE profiles ADD COLUMN IF NOT EXISTS {col_name} {col_type};"))
                except Exception:
                    pass # Column already exists or table not yet created
            try:
                if "sqlite" in str(engine_instance.url):
                    conn.execute(text("ALTER TABLE users ADD COLUMN credits INTEGER DEFAULT 25;"))
                else:
                    conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS credits INTEGER DEFAULT 25;"))
            except Exception:
                pass
    except Exception as err:
        logger.warning(f"Auto-migration failed: {err}")

# Run migrations
run_auto_migrations(engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
