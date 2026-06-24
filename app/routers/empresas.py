from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.empresa import Empresa
from app.models.usuario import Usuario
from app.schemas.empresa import EmpresaCreate, EmpresaResponse
from app.core.dependencies import get_superadmin

router = APIRouter(prefix="/empresas", tags=["Empresas"])

@router.post("/", response_model=EmpresaResponse, status_code=201)
def crear_empresa(
    empresa_data: EmpresaCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_superadmin)
):
    existing = db.query(Empresa).filter(Empresa.nit == empresa_data.nit).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe una empresa con este NIT"
        )
    nueva_empresa = Empresa(
        nombre=empresa_data.nombre,
        nit=empresa_data.nit,
        plan_suscripcion=empresa_data.plan_suscripcion
    )
    db.add(nueva_empresa)
    db.commit()
    db.refresh(nueva_empresa)
    return nueva_empresa

@router.get("/", response_model=list[EmpresaResponse])
def listar_empresas(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_superadmin)
):
    return db.query(Empresa).all()

@router.get("/{empresa_id}", response_model=EmpresaResponse)
def obtener_empresa(
    empresa_id: str,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_superadmin)
):
    empresa = db.query(Empresa).filter(Empresa.id == empresa_id).first()
    if not empresa:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Empresa no encontrada"
        )
    return empresa