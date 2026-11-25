"""
Uses chancy's public API the way an application would, so a type checker can
confirm what downstream code sees now that chancy ships ``py.typed``.

This file is never executed: ``tests/test_typing.py`` runs mypy over it. Every
line marked ``# type: ignore[...]`` is a call that must be rejected, and mypy
runs with ``--warn-unused-ignores`` so a call that stops being rejected fails
the check too.
"""

from typing import assert_type

from psycopg import AsyncCursor, Cursor
from psycopg.rows import DictRow

from chancy import Chancy, Job, Queue, QueuedJob, Reference, job


@job(queue="default")
def add(a: int, b: int) -> int:
    return a + b


@job()
async def greet(name: str) -> str:
    return f"Hello, {name}!"


def decorated_functions_keep_their_signature() -> None:
    assert_type(add(1, 2), int)
    assert_type(add.job, Job)
    add("1", 2)  # type: ignore[arg-type]
    add(1)  # type: ignore[call-arg]


async def decorated_coroutines_keep_their_signature() -> None:
    assert_type(await greet("world"), str)


async def pushing_jobs(chancy: Chancy) -> None:
    configured = add.job.with_kwargs(a=1, b=2).with_queue("low")
    assert_type(configured, Job)

    assert_type(await chancy.push(add), Reference)
    assert_type(await chancy.push(configured), Reference)

    jobs = [configured, configured.with_priority(10)]
    async for references in chancy.push_many(jobs):
        assert_type(references, list[Reference])
    async for references in chancy.push_many([add, configured]):
        assert_type(references, list[Reference])

    reference = await chancy.push(configured)
    assert_type(await chancy.get_job(reference), QueuedJob | None)
    assert_type(await chancy.wait_for_job(reference), QueuedJob | None)


def pushing_jobs_synchronously(chancy: Chancy) -> None:
    assert_type(chancy.sync_push(add), Reference)
    assert_type(chancy.sync_push(add.job), Reference)

    jobs = [add.job, add.job.with_priority(10)]
    for references in chancy.sync_push_many(jobs):
        assert_type(references, list[Reference])


async def pushing_inside_a_transaction(
    chancy: Chancy,
    cursor: AsyncCursor[DictRow],
    sync_cursor: Cursor[DictRow],
) -> None:
    jobs = [add.job, add.job.with_priority(10)]
    assert_type(await chancy.push_ex(cursor, add), Reference)
    assert_type(await chancy.push_many_ex(cursor, jobs), list[Reference])
    assert_type(chancy.sync_push_many_ex(sync_cursor, jobs), list[Reference])
    chancy.sync_notify(sync_cursor, "custom.event", {"key": "value"})


async def declaring_queues(chancy: Chancy) -> None:
    queue = Queue("default", concurrency=4)
    assert_type(await chancy.declare(queue), Queue)
    assert_type(chancy.sync_declare(queue), Queue)
    assert_type(await chancy.get_all_queues(), list[Queue])
