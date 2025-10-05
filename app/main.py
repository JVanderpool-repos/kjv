from fastapi import FastAPI
from app.api.routes import router
from app.db.session import engine, Base

# Create tables (for simple deployment; for production use Alembic migrations)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Bible Verse of the Day")
app.include_router(router)
