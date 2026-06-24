from pydantic import BaseModel, EmailStr
from uuid import UUID
from enum import Enum
from typing import Optional

class RolUsuario(str, Enum):
    superadmin = "superadmin"
    admin = "admin"
    supervisor = "supervisor"
    tecnico = "tecnico"

class UsuarioCreate(BaseModel):
    nombre: str
    email: EmailStr
    password: str
    rol: RolUsuario = RolUsuario.tecnico
    empresa_id: Optional[UUID] = None

class UsuarioResponse(BaseModel):
    id: UUID
    nombre: str
    email: EmailStr
    rol: RolUsuario
    activo: bool
    empresa_id: Optional[UUID] = None

    model_config = {"from_attributes": True}