import asyncio
from fastapi import HTTPException, Header
from databases import Database
from typing import AsyncGenerator
import boto3

from jetstream_v2.controller import process_basic_mailing
from database_client import db_client
from settings import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION, API_KEY, ENV
from cache import redis_connection

tasks_queue = asyncio.Queue()
active_workers = []
MAX_WORKERS = 4


async def create_worker():
    print("Creating worker", len(active_workers), "tasks in queue", tasks_queue.qsize(), flush=True)
    w = asyncio.create_task(worker())
    active_workers.append(w)


async def worker():
    while True:
        try:
            task_func, args, kwargs = await tasks_queue.get()
            await task_func(*args, **kwargs)
        except asyncio.CancelledError:
            print("Worker is shutting down gracefully")
            break
        except Exception as e:
            print(f"Error executing task: {e}")
        finally:
            tasks_queue.task_done()


async def manage_workers():
    while True:
        if ENV == "production":
            await addMailingsFromSchedule()
        if not tasks_queue.empty() and len(active_workers) < MAX_WORKERS:
            await create_worker()
        elif tasks_queue.empty() and active_workers:
            await asyncio.sleep(5)
            if tasks_queue.empty():
                for worker_task in active_workers:
                    print("Cancelling worker", worker_task, flush=True)
                    worker_task.cancel()
                await asyncio.gather(*active_workers, return_exceptions=True)
                active_workers.clear()
        await asyncio.sleep(10)


async def addMailingsFromSchedule():
    try:
        sql = """
            SELECT *
            FROM app.mailing_schedule
            WHERE status = 'scheduled'
            AND CAST(deploydatetime AS TIMESTAMPTZ)
                BETWEEN (NOW() - INTERVAL '45 minutes')
                AND (NOW() + INTERVAL '15 minutes')
            AND test = TRUE
            ORDER BY CAST(deploydatetime AS TIMESTAMPTZ);
        """

        result = await db_client.fetch_all(sql)
        result_dict = [dict(row) for row in result]
        if len(result_dict) > 0:
            print(f"Found {len(result_dict)} mailings to send", flush=True)
        ids = [result["id"] for result in result_dict]
        if ids:
            update_sql = """
                UPDATE app.mailing_schedule
                SET status = 'sent'
                WHERE id = ANY(:ids);
            """
            await db_client.execute(update_sql, {"ids": ids})

        if result_dict and ENV == "production":
            for result in result_dict:
                await tasks_queue.put(
                    (
                        process_basic_mailing,
                        (result, db_client),
                        {},
                    )
                )
        return True
    except Exception as e:
        print(f"Error getting mailings to send: {e}", flush=True)
    return False


async def get_db() -> AsyncGenerator[Database, None]:
    try:
        yield db_client
    finally:
        pass


def validate_api_key(x_api_key: str = Header(...)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid or missing API key")
    return True


async def get_redis():
    async with redis_connection() as redis_client:
        yield redis_client


def get_s3_client():
    s3_client = boto3.client(
        "s3",
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=AWS_REGION,
    )
    try:
        yield s3_client
    finally:
        pass
