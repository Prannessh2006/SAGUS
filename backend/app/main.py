from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
import sys
import asyncio
from app.routers import student, learning, assessment, health, admin
from app.core.config import settings
from app.graph.neo4j_client import Neo4jClient
from app.routers import knowledge
from app.routers import ingest

logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    neo4j_client = Neo4jClient()
    for attempt in range(10):
        try:
            await neo4j_client.connect()
            logger.info("Neo4j connection established")
            break
        except Exception:
            logger.warning(f"Neo4j not ready (attempt {attempt+1}/10)...")
            await asyncio.sleep(3)
    else:
        raise RuntimeError("Neo4j never became available")
    app.state.neo4j_client = neo4j_client
    yield
    logger.info("Shutting down application...")
    await neo4j_client.close()

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Knowledge Augmented Generation (KAG) Learning Platform API",
    lifespan=lifespan,
    docs_url="/docs",
    redirect_slashes=False,
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=False,
)

app.include_router(ingest.router, prefix="/api/v1/admin", tags=["Ingest"])
app.include_router(knowledge.router)
app.include_router(admin.router, prefix="/api/v1")
app.include_router(health.router, tags=["Health"])
app.include_router(student.router, prefix="/api/v1/student", tags=["Student"])
app.include_router(learning.router, prefix="/api/v1/learning", tags=["Learning"])
app.include_router(assessment.router, prefix="/api/v1/assessment", tags=["Assessment"])

@app.get("/")
async def root():
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "operational",
        "docs": "/docs",
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG,
    )
