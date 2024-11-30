from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import asyncio
from contextlib import asynccontextmanager

from cache import create_pool, disconnect_pool
from dependencies import db_client, manage_workers


@asynccontextmanager
async def app_lifespan(app: FastAPI):
    await db_client.connect()
    await create_pool()

    manage_workers_task = asyncio.create_task(manage_workers())

    try:
        yield
    finally:
        await disconnect_pool()
        await db_client.disconnect()
        print("Cancelling manage_workers_task", flush=True)
        print(manage_workers_task, flush=True)
        manage_workers_task.cancel()
        print(manage_workers_task, flush=True)


app = FastAPI(lifespan=app_lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def home():
    return {"Message": "Go away..."}
