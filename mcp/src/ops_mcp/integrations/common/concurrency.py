"""Ayudas para que ninguna tool bloquee el bucle de eventos.

El servidor atiende cada petición en una tarea del bucle de eventos. Mientras una tool espera
(red, disco, otra API) con ``await``, el bucle atiende al resto de agentes. Lo que bloquea
(una librería síncrona, CPU) se manda a un hilo con ``run_blocking``.
"""

from __future__ import annotations

import asyncio
import functools
from collections.abc import Awaitable, Callable, Iterable

import anyio.to_thread
from anyio import CapacityLimiter

# Hilos para trabajo bloqueante, compartidos por todas las tools (el pool por defecto de
# anyio, 40, también lo usan otras partes del servidor).
BLOCKING_LIMITER = CapacityLimiter(8)


async def run_blocking[**P, R](fn: Callable[P, R], /, *args: P.args, **kwargs: P.kwargs) -> R:
    """Ejecuta ``fn`` en un hilo del pool limitado y espera su resultado sin bloquear el bucle."""
    return await anyio.to_thread.run_sync(functools.partial(fn, *args, **kwargs), limiter=BLOCKING_LIMITER)


async def gather_limited[R](calls: Iterable[Callable[[], Awaitable[R]]], limit: int = 8) -> list[R]:
    """Lanza las llamadas a la vez con un máximo de ``limit`` en vuelo; conserva el orden."""
    semaphore = asyncio.Semaphore(limit)

    async def _one(call: Callable[[], Awaitable[R]]) -> R:
        async with semaphore:
            return await call()

    return list(await asyncio.gather(*(_one(call) for call in calls)))
