import os

from datetime import datetime
from sqlalchemy import select
from database import sync_session, async_session
from models import User
from celery import Celery

redis_url = os.getenv("REDIS_URL", "redis://redis_container:6379")

app = Celery(__name__, broker=redis_url, backend=redis_url)

@app.on_after_configure.connect
def setup_periodic_tasks(sender: Celery, **kwargs):
    sender.add_periodic_task(5.0, generate_user_report.s(), name='every 10')

@app.task
def create_user(username, email):
    session = sync_session()
    try:
        stmt = select(User).filter(User.username == username)
        result = session.execute(stmt)
        user = result.scalar_one_or_none()

        if user:
            return {"error": "User already exists"}

        new_user = User(username=username, email=email)
        session.add(new_user)
        session.commit()

        return {"username": new_user.username, "email": new_user.email}
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

@app.task(bind=True)
def generate_user_report(self):
    """Task to generate a user report file."""
    session = sync_session()
    result = session.execute(select(User))
    users = result.scalars().all()

    # Prepare the file content
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lines = [f"User Report (Generated on {timestamp})\n\n"]
    
    if not users:
        return "Users not found"
    
    for user in users:
        lines.append(f"Username: {user.username}, Email: {user.email}\n")

    file_path = "user_report.txt"

    # Write to the file
    with open(file_path, "w") as file:
        file.writelines(lines)

    return f"Report generated at {file_path}"
