from contextlib import asynccontextmanager
from fastapi import FastAPI
from sqlalchemy.orm import Session
from app.database import engine, Base, SessionLocal


# Importar todos los modelos para que SQLAlchemy los registre
from app.models import (
    Empresa, Usuario, Ubicacion, 
     Criticidad, Maquinaria, EspecificacionTecnica,
    DocumentoEquipo, PlanMantenimiento, OrdenTrabajo, AuditLog
    )

# auth router para autenticación
from app.routers.auth import router as auth_router
from app.routers.empresas import router as empresas_router
from app.routers.usuarios import router as usuarios_router
from app.routers.ubicaciones import router as ubicaciones_router
from app.routers.maquinaria import router as maquinaria_router
from app.core.seed import seed_criticidades

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Todo lo que va aquí se ejecuta al ARRANCAR el servidor
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_criticidades(db)
        print("✅ tablas creadas y datos iniciales cargados")
    finally:
        db.close()
    print("✅ Conexión a base de datos exitosa")
    yield
    # Todo lo que va después del yield se ejecuta al APAGAR el servidor

app = FastAPI(title="CMMS API", version="1.0.0", lifespan=lifespan)
app.include_router(auth_router)
app.include_router(empresas_router)
app.include_router(usuarios_router)
app.include_router(ubicaciones_router)
app.include_router(maquinaria_router)

@app.get("/")
def root():
    return {"message": "API de Gestión de Mantenimiento funcionando ✅"}