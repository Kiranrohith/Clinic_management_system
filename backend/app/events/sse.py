import asyncio
import json
from collections.abc import AsyncGenerator
from itertools import count


class SSEManager:
    def __init__(self):
        self._subscribers: dict[int, set[asyncio.Queue[dict]]] = {}
        self._loop: asyncio.AbstractEventLoop | None = None
        self._message_counter = count(1)

    def set_loop(self, loop: asyncio.AbstractEventLoop) -> None:
        self._loop = loop

    def publish(self, user_id: int, event_type: str, payload: dict) -> None:
        event = {
            "id": str(next(self._message_counter)),
            "event": event_type,
            "data": payload,
        }
        if self._loop is None:
            return
        self._loop.call_soon_threadsafe(self._dispatch, user_id, event)

    def _dispatch(self, user_id: int, event: dict) -> None:
        queues = self._subscribers.get(user_id, set()).copy()
        for queue in queues:
            queue.put_nowait(event)

    async def stream(self, user_id: int) -> AsyncGenerator[str, None]:
        queue: asyncio.Queue[dict] = asyncio.Queue()
        self._subscribers.setdefault(user_id, set()).add(queue)
        try:
            while True:
                try:
                    event = await asyncio.wait_for(queue.get(), timeout=30)
                    yield self._format_event(event["id"], event["event"], event["data"])
                except asyncio.TimeoutError:
                    yield ": keep-alive\n\n"
        finally:
            subscribers = self._subscribers.get(user_id)
            if subscribers is not None:
                subscribers.discard(queue)
                if not subscribers:
                    self._subscribers.pop(user_id, None)

    @staticmethod
    def _format_event(event_id: str, event_type: str, payload: dict) -> str:
        return f"id: {event_id}\nevent: {event_type}\ndata: {json.dumps(payload, default=str)}\n\n"


sse_manager = SSEManager()
