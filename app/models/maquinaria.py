from sqlalchemy import Column, String, Date, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
import enum

from app.database import Base

class EstadoEquipo(enum.Enum):
    activo = "activo"
    inactivo = "inactivo"
    en_mantenimiento = "en_mantenimiento"
    dado_de_baja = "dado_de_baja"

class Maquinaria(Base):
    __tablename__ = "maquinaria_equipos"

    #id_equipo numero interno usado en la empresa para identificar el equipo
    id_equipo = Column(String(50), primary_key=True)
    empresa_id = Column(UUID(as_uuid=True), ForeignKey("empresas.id"), nullable=False)
    nombre_equipo = Column(String(200), nullable=False)
    marca = Column(String(100))
    modelo = Column(String(100))
    num_serie = Column(String(100), unique=True)
    id_ubicacion = Column(UUID(as_uuid=True), ForeignKey("ubicaciones.id"))
    id_criticidad = Column(UUID(as_uuid=True), ForeignKey("criticidades.id"))
    fecha_adquisicion = Column(Date)
    fecha_arranque = Column(Date)
    estado_actual = Column(Enum(EstadoEquipo), default=EstadoEquipo.activo, nullable=False)
    justificacion_criticidad = Column(String(500))
    # Relaciones
    empresa = relationship("Empresa", back_populates="equipos")
    ubicacion = relationship("Ubicacion", back_populates="equipos")
    criticidad = relationship("Criticidad", back_populates="equipos")
    especificaciones_tecnicas = relationship("EspecificacionTecnica", back_populates="equipo")
    documentos = relationship("DocumentoEquipo", back_populates="equipo")
    planes = relationship("PlanMantenimiento", back_populates="equipo")
    ordenes = relationship("OrdenTrabajo", back_populates="equipo")