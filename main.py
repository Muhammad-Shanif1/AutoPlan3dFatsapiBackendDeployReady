from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from services.db import Base, engine
from services.settings import settings
import services.models
from contextlib import asynccontextmanager

# Create tables immediately on startup
# For production, consider using Alembic for migrations
print("🚀 Initializing database...")
Base.metadata.create_all(bind=engine)
print(f"✅ Tables verified/created: {list(Base.metadata.tables.keys())}")

# include routers
from services.user_router import router as user_router
from services.project_router import router as project_router
from services.graph2plan_api import router as graph2plan_router, initialize_floorplan_app
from services.csp_floorplan_api import router as csp_floorplan_router, initialize_csp_floorplan_app
from services.diffplanner_router import router as diffplanner_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    initialize_floorplan_app()
    initialize_csp_floorplan_app()
    yield
    # Shutdown logic (if any)

app = FastAPI(lifespan=lifespan)

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user_router)
app.include_router(project_router)
app.include_router(graph2plan_router)
app.include_router(csp_floorplan_router)
app.include_router(diffplanner_router)
