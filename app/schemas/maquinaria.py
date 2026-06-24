from pydantic import BaseModel
from uuid import UUID
from typing import Optional
from datetime import date
from enum import Enum

class EstadoEquipo(str, Enum):
    activo = "activo"
    inactivo = "inactivo"
    en_mantenimiento = "en_mantenimiento"
    dado_de_baja = "dado_de_baja"

class MaquinariaCreate(BaseModel):
    id_equipo: str
    nombre_equipo: str
    marca: Optional[str] = None
    modelo: Optional[str] = None
    num_serie: Optional[str] = None
    id_ubicacion: Optional[UUID] = None
    id_criticidad: Optional[UUID] = None
    fecha_adquisicion: Optional[date] = None
    fecha_arranque: Optional[date] = None
    estado_actual: EstadoEquipo = EstadoEquipo.activo
    justificacion_criticidad: Optional[str] = None

class MaquinariaResponse(BaseModel):
    id_equipo: str
    empresa_id: UUID
    nombre_equipo: str
    marca: Optional[str] = None
    modelo: Optional[str] = None
    num_serie: Optional[str] = None
    id_ubicacion: Optional[UUID] = None
    id_criticidad: Optional[UUID] = None
    fecha_adquisicion: Optional[date] = None
    fecha_arranque: Optional[date] = None
    estado_actual: EstadoEquipo
    justificacion_criticidad: Optional[str] = None

    model_config = {"from_attributes": True}