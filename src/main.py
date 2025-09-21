from fastapi import FastAPI
from src.models.base import create_tables
from src.routers import auth

# Créer les tables au démarrage
create_tables()

app = FastAPI()

app.include_router(auth.router)
