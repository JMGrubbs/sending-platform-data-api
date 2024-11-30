from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional


from dependencies import validate_api_key, get_db

user_router = APIRouter()


@user_router.get("/get", dependencies=[Depends(validate_api_key)])
async def read_users(username: Optional[str] = Query(None), db=Depends(get_db)):
    try:
        return {"message": "Hello World"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading users: {e}")


@user_router.post("/create", dependencies=[Depends(validate_api_key)])
async def create_user(user: dict, db=Depends(get_db)):
    try:
        return {"message": "Hello World"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating user: {e}")
