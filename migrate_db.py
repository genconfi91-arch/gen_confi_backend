from sqlalchemy import create_engine, text
from app.core.config import settings

def migrate():
    engine = create_engine(settings.DATABASE_URL)
    with engine.connect() as conn:
        print("Adding 'avatar_url' column...")
        try:
            conn.execute(text("ALTER TABLE users ADD COLUMN avatar_url VARCHAR(500)"))
            conn.commit()
            print("Successfully added 'avatar_url'")
        except Exception as e:
            print(f"Error adding 'avatar_url' (maybe already exists?): {e}")

        print("Adding 'gender' column...")
        try:
            conn.execute(text("ALTER TABLE users ADD COLUMN gender VARCHAR(20)"))
            conn.commit()
            print("Successfully added 'gender'")
        except Exception as e:
            print(f"Error adding 'gender' (maybe already exists?): {e}")

if __name__ == "__main__":
    migrate()
