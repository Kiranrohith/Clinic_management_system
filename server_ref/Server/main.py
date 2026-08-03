from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from engine.database import init_db_connection
from routes.routes import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db_connection()
    print("Application startup")
    yield
    print("Application shutdown")


app = FastAPI(
    title="Customer Management API",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)