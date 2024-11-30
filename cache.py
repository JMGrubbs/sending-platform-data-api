from redis.asyncio import Redis, ConnectionPool
from contextlib import asynccontextmanager
from settings import PUBLIC_CACHE

pool: ConnectionPool = None


async def create_pool() -> None:
    try:
        global pool
        pool = ConnectionPool.from_url(
            f"redis://{PUBLIC_CACHE['RedisHost']}:{PUBLIC_CACHE['RedisPort']}/0",
            decode_responses=True,
            max_connections=1000,
        )
        print("Redis connection pool created", pool, flush=True)
    except Exception as e:
        print(f"Error creating Redis connection pool: {e}", flush=True)
        raise e
    return None


async def disconnect_pool() -> None:
    try:
        print(f"Before disconnect: available={pool._available_connections}, in-use={pool._in_use_connections}")
        await pool.disconnect(inuse_connections=True)

        print(f"After disconnect: available={pool._available_connections}, in-use={pool._in_use_connections}")

        if len(pool._in_use_connections) == 0:
            print("Redis pool disconnected successfully.")
        else:
            print("Redis pool still has active connections.")
    except Exception as e:
        print(f"Error disconnecting Redis connection pool: {e}", flush=True)


@asynccontextmanager
async def redis_connection():
    global pool
    client = Redis(connection_pool=pool)
    try:
        yield client
    finally:
        await client.close()
