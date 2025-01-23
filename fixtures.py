from users.models import User
from faker import Faker
from users.database import sync_session
import os

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE")
MYSQL_HOST = "mysql_db"
MYSQL_PORT = os.getenv("MYSQL_PORT", "3306")

# Generate test data
fake = Faker()

DATABASE_URL = f"mysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}"

sync_engine = create_engine(
    DATABASE_URL, 
    pool_size=10,
    max_overflow=20
)
sync_session = sessionmaker(bind=sync_engine)

def generate_test_data(db_session, num_records=5):
    """Generate and add test data to the database."""
    users = []
    for _ in range(num_records):
        user = User(
            username=fake.name(),
            email=fake.email()
        )
        users.append(user)
    
    # Add the users to the session and commit
    db_session.add_all(users)
    db_session.commit()

def main():
    # Create a session
    db_session = sync_session()

    # Generate and add test data to the database
    generate_test_data(db_session)

    # Query and display the added data
    users = db_session.query(User).all()
    for user in users:
        print(f"{user.id}: {user.username} - {user.email}")
    
    # Close the session
    db_session.close()

if __name__ == "__main__":
    main()
