from fastapi import FastAPI
from src.models.base import create_tables
from src.routers import auth, project, api_key

# Créer les tables au démarrage
create_tables()

app = FastAPI(
    title="Loggy",
    version="0.0.1"
)

app.include_router(auth.router)
app.include_router(project.router)
app.include_router(api_key.router)
