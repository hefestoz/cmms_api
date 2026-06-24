from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
import jwt

from app.database import get_db
from app.models.usuario import Usuario, RolUsuario
from app.core.security import decode_access_token
from app.core.config import SECRET_KEY

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> Usuario:
    try:
        payload = decode_access_token(token)
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expirado")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido")

    usuario = db.query(Usuario).filter(Usuario.id == user_id).first()
    if not usuario or not usuario.activo:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario no encontrado o inactivo")
    return usuario

def require_roles(*roles: RolUsuario):
    def dependency(current_user: Usuario = Depends(get_current_user)) -> Usuario:
        if current_user.rol not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Se requiere uno de estos roles: {[r.value for r in roles]}"
            )
        return current_user
    return dependency

def get_superadmin(current_user: Usuario = Depends(get_current_user)) -> Usuario:
    return require_roles(RolUsuario.superadmin)(current_user)

def get_admin_or_above(current_user: Usuario = Depends(get_current_user)) -> Usuario:
    return require_roles(RolUsuario.superadmin, RolUsuario.admin)(current_user)

def get_supervisor_or_above(current_user: Usuario = Depends(get_current_user)) -> Usuario:
    return require_roles(RolUsuario.superadmin, RolUsuario.admin, RolUsuario.supervisor)(current_user)

def get_any_authenticated_user(current_user: Usuario = Depends(get_current_user)) -> Usuario:
    return current_user

def get_tecnico_only(current_user: Usuario = Depends(get_current_user)) -> Usuario:
    return require_roles(RolUsuario.tecnico)(current_user)