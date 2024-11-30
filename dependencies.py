from fastapi import HTTPException, Header
from database_client import engine, SessionLocal, Base
from config import API_KEY
from cache import redis_connection

# from typing import AsyncGenerator
# import asyncio

# tasks_queue = asyncio.Queue()
# active_workers = []
# MAX_WORKERS = 4


# async def create_worker():
#     print("Creating worker", len(active_workers), "tasks in queue", tasks_queue.qsize(), flush=True)
#     w = asyncio.create_task(worker())
#     active_workers.append(w)


# async def worker():
#     while True:
#         try:
#             task_func, args, kwargs = await tasks_queue.get()
#             await task_func(*args, **kwargs)
#         except asyncio.CancelledError:
#             print("Worker is shutting down gracefully")
#             break
#         except Exception as e:
#             print(f"Error executing task: {e}")
#         finally:
#             tasks_queue.task_done()


# async def manage_workers():
#     while True:
#         if ENV == "production":
#             await addMailingsFromSchedule()
#         if not tasks_queue.empty() and len(active_workers) < MAX_WORKERS:
#             await create_worker()
#         elif tasks_queue.empty() and active_workers:
#             await asyncio.sleep(5)
#             if tasks_queue.empty():
#                 for worker_task in active_workers:
#                     print("Cancelling worker", worker_task, flush=True)
#                     worker_task.cancel()
#                 await asyncio.gather(*active_workers, return_exceptions=True)
#                 active_workers.clear()
#         await asyncio.sleep(10)


def validate_api_key(x_api_key: str = Header(...)):
    try:
        if x_api_key != API_KEY:
            raise HTTPException(status_code=403, detail="Invalid or missing API key")
        return True
    except Exception as e:
        print(f"Error validating API key: {e}", flush=True)
        raise HTTPException(status_code=403, detail="Invalid or missing API key")


async def get_redis():
    async with redis_connection() as redis_client:
        try:
            yield redis_client
        finally:
            pass


async def get_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    db = SessionLocal()
    try:
        yield db
    finally:
        await db.close()
