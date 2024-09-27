import asyncio
from functools import wraps
from typing import Awaitable, Callable, TypeVar
from typing_extensions import ParamSpec

from redis.asyncio.client import Redis


P = ParamSpec("P")
T = TypeVar("T")


class AsyncRedisCache:
    prefix: str
    redis: Redis

    @classmethod
    def init(cls, redis: Redis, prefix: str) -> None:
        cls.redis = redis
        cls.prefix = prefix

    @classmethod
    def aredis_cache(
        cls,
        key_generator: Callable[P, str],
        cache_serializer: Callable[[T], str],
        cache_deserializer: Callable[[str], T],
        ttl: int,
    ) -> Callable[[Callable[P, Awaitable[T]]], Callable[P, Awaitable[T]]]:
        def decorator(
            func: Callable[P, Awaitable[T]]
        ) -> Callable[P, Awaitable[T]]:
            lock = asyncio.Lock()

            @wraps(func)
            async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
                cache_key = cls.prefix + key_generator(*args, **kwargs)

                async with lock:
                    cache_value = await cls.redis.get(cache_key)
                    if cache_value is not None:
                        if isinstance(cache_value, bytes):
                            cache_value = cache_value.decode()

                        return cache_deserializer(cache_value)

                    res = await func(*args, **kwargs)
                    await cls.redis.setex(
                        cache_key, ttl, cache_serializer(res)
                    )
                    return res

            return wrapper

        return decorator
