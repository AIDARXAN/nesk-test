
import os
from fastapi import Depends, FastAPI
from fastapi.responses import FileResponse
from sqlalchemy import select
from tasks import create_user
from pydantic import BaseModel
from fastapi import HTTPException
from database import async_session
from models import User

app = FastAPI()


class UserCreateRequest(BaseModel):
    username: str
    email: str

@app.post("/users/")
async def create_user_endpoint(user: UserCreateRequest):
    """Call Celery task to create a user and wait for the result."""
    task = create_user.apply_async(args=[user.username, user.email])

    result = task.get(timeout=10)

    if isinstance(result, dict) and result.get("error"):
        raise HTTPException(status_code=400, detail=result["error"])

    return {"message": result}

@app.get("/users/{user_id}")
async def get_user_by_id(user_id: int):
    """Fetch a single user by ID"""
    async with async_session() as session:
        stmt = select(User).filter(User.id == user_id)
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()

        if user is None:
            raise HTTPException(status_code=404, detail="User not found")

        return {"username": user.username, "email": user.email}

@app.get("/users/")
async def get_all_users():
    """Fetch all users"""
    async with async_session() as session:
        stmt = select(User)
        result = await session.execute(stmt)
        users = result.scalars().all()

        if not users:
            raise HTTPException(status_code=404, detail="No users found")

        return [
            {
                "id": user. id, 
                "username": user.username, 
                "email": user.email, 
                "last_login": user.last_login
            } for user in users
        ]

@app.get("/download-user-report/")
async def download_user_report():
    """Endpoint to download the user report."""
    file_path = "user_report.txt"

    if not os.path.exists(file_path):
        return {"error": "Report file not found. Please wait for it to be generated."}

    return FileResponse(
        file_path,
        media_type="text/plain",
        filename="user_report.txt"
    )
