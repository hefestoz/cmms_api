from pydantic import BaseModel
from uuid import UUID
from typing import Optional
from datetime import datetime

class EmpresaCreate(BaseModel):
    nombre: str
    nit: str
    plan_suscripcion: Optional[str] = "basico"

class EmpresaResponse(BaseModel):
    id: UUID
    nombre: str
    nit: str
    plan_suscripcion: str
    created_at: datetime

    model_config = {"from_attributes": True}