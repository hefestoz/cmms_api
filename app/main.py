from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.database import engine, Base

# Importar todos los modelos para que SQLAlchemy los registre
from app.models import Empresa, Usuario, Ubicacion, Criticidad, Maquinaria, EspecificacionTecnica, DocumentoEquipo, PlanMantenimiento, OrdenTrabajo, AuditLog

# auth router para autenticación
from app.routers.auth import router as auth_router
from app.routers.empresas import router as empresas_router
from app.routers.usuarios import router as usuarios_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Todo lo que va aquí se ejecuta al ARRANCAR el servidor
    Base.metadata.create_all(bind=engine)
    print("✅ Conexión a base de datos exitosa")
    yield
    # Todo lo que va después del yield se ejecuta al APAGAR el servidor

app = FastAPI(title="CMMS API", version="1.0.0", lifespan=lifespan)
app.include_router(auth_router)
app.include_router(empresas_router)
app.include_router(usuarios_router)

@app.get("/")
def root():
    return {"message": "API de Gestión de Mantenimiento funcionando ✅"}