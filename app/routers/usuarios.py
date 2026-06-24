from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID

from app.database import get_db
from app.models.usuario import Usuario, RolUsuario
from app.models.empresa import Empresa
from app.schemas.usuario import UsuarioCreate, UsuarioResponse
from app.core.security import hash_password
from app.core.dependencies import get_current_user, get_superadmin, get_admin_or_above

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])

@router.post("/", response_model=UsuarioResponse, status_code=201)
def crear_usuario(
    usuario_data: UsuarioCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    # Superadmin puede crear admins sin empresa o con cualquier empresa
    # Admin solo puede crear supervisores y tecnicos de su propia empresa
    # Supervisor solo puede crear tecnicos de su propia empresa
    if current_user.rol == RolUsuario.superadmin:
        if usuario_data.rol == RolUsuario.superadmin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No se puede crear otro superadmin desde la API"
            )
    elif current_user.rol == RolUsuario.admin:
        if usuario_data.rol not in [RolUsuario.supervisor, RolUsuario.tecnico]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Un admin solo puede crear supervisores y técnicos"
            )
        usuario_data.empresa_id = current_user.empresa_id
    elif current_user.rol == RolUsuario.supervisor:
        if usuario_data.rol != RolUsuario.tecnico:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Un supervisor solo puede crear técnicos"
            )
        usuario_data.empresa_id = current_user.empresa_id
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para crear usuarios"
        )

    # Verificar que la empresa existe si se provee empresa_id
    if usuario_data.empresa_id:
        empresa = db.query(Empresa).filter(Empresa.id == usuario_data.empresa_id).first()
        if not empresa:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Empresa no encontrada"
            )

    # Verificar email duplicado
    existing = db.query(Usuario).filter(Usuario.email == usuario_data.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe un usuario con este email"
        )

    nuevo_usuario = Usuario(
        nombre=usuario_data.nombre,
        email=usuario_data.email,
        password_hash=hash_password(usuario_data.password),
        rol=usuario_data.rol,
        empresa_id=usuario_data.empresa_id
    )
    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)
    return nuevo_usuario

@router.get("/", response_model=list[UsuarioResponse])
def listar_usuarios(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_admin_or_above)
):
    # Superadmin ve todos, admin y supervisor solo ven su empresa
    if current_user.rol == RolUsuario.superadmin:
        return db.query(Usuario).all()
    return db.query(Usuario).filter(
        Usuario.empresa_id == current_user.empresa_id
    ).all()

@router.get("/me", response_model=UsuarioResponse)
def mi_perfil(current_user: Usuario = Depends(get_current_user)):
    return current_user

@router.patch("/{usuario_id}/desactivar", response_model=UsuarioResponse)
def desactivar_usuario(
    usuario_id: UUID,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_admin_or_above)
):
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
    if usuario.rol == RolUsuario.superadmin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No se puede desactivar un superadmin")
    if current_user.rol == RolUsuario.admin and usuario.empresa_id != current_user.empresa_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No puedes modificar usuarios de otra empresa")

    usuario.activo = False
    db.commit()
    db.refresh(usuario)
    return usuario