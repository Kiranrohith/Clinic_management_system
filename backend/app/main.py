from fastapi import Depends, FastAPI, Query
from fastapi.responses import StreamingResponse

from app.api import api_router
from app.api.dependencies import get_current_active_user_from_query_token
from app.core.config import settings
from app.database.session import get_db
from app.events.sse import sse_manager
from app.exceptions import register_exception_handlers
from app.middleware.logging import RequestLogMiddleware
from app.models.user import User
from sqlalchemy.orm import Session

app = FastAPI(title=settings.app_name, debug=settings.debug)
app.include_router(api_router)
app.middleware("http")(RequestLogMiddleware())
register_exception_handlers(app)


@app.on_event("startup")
async def startup() -> None:
    import asyncio

    sse_manager.set_loop(asyncio.get_running_loop())


@app.get("/api/v1/events")
async def events(
    access_token: str = Query(...),
    db: Session = Depends(get_db),
):
    current_user: User = get_current_active_user_from_query_token(access_token=access_token, db=db)
    return StreamingResponse(
        sse_manager.stream(current_user.user_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
