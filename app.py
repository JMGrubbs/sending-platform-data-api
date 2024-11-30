from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from cache import create_pool, disconnect_pool

from routes.users.routes import user_router


@asynccontextmanager
async def app_lifespan(app: FastAPI):
    await create_pool()

    try:
        yield
    finally:
        await disconnect_pool()


app = FastAPI(lifespan=app_lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user_router, prefix="/users", tags=["users"])


@app.get("/")
def home():
    return {"Message": "Go away..."}
