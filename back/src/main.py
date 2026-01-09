import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from .database.session import dispose_engine, init_db
from .routers.users import router as users_router


logging.basicConfig(level=logging.INFO)
api_logger = logging.getLogger("api")
api_logger.setLevel(logging.INFO)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield
    await dispose_engine()


def create_app() -> FastAPI:
    app = FastAPI(title="StackTracker", version="0.1.0", lifespan=lifespan)

    # Routers
    app.include_router(users_router, prefix="/api", tags=["users"])

    @app.get("/")
    def read_root():
        return {"message": "StackTracker up"}

    @app.get("/health")
    async def health():
        logging.getLogger("app").debug("Health endpoint accessed")
        return {"status": "ok"}

    logger = logging.getLogger("api")
    logger.info("API initialized")
    return app


app = create_app()
