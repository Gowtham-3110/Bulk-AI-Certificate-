import logging
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import APP_NAME, DEBUG
from app.database import init_db
from app.routers import jobs, certificates, web

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("bulk_certificate_app")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: ensure tables exist
    logger.info("Initializing relational database schema...")
    init_db()
    logger.info(f"{APP_NAME} started successfully.")
    yield
    # Shutdown
    logger.info(f"{APP_NAME} shutting down.")


app = FastAPI(
    title=APP_NAME,
    description="High-performance backend API for bulk certificate generation, asynchronous job tracking, and certificate retrieval.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
static_dir = Path(__file__).resolve().parent / "static"
static_dir.mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# Include Routers
app.include_router(jobs.router)
app.include_router(certificates.router)
app.include_router(web.router)


@app.get("/health", status_code=status.HTTP_200_OK, tags=["Health"])
def health_check():
    return {
        "status": "healthy",
        "app": APP_NAME,
        "database": "connected",
    }
