from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID
from typing import Optional

from app.database import get_db
from app.models.maquinaria import Maquinaria
from app.models.ubicacion import Ubicacion
from app.models.criticidad import Criticidad
from app.models.usuario import Usuario, RolUsuario
from app.schemas.maquinaria import MaquinariaCreate, MaquinariaResponse
from app.core.dependencies import get_supervisor_or_above, get_any_authenticated_user

router = APIRouter(prefix="/equipos", tags=["Equipos"])

@router.post("/", response_model=MaquinariaResponse, status_code=201)
def crear_equipo(
    equipo_data: MaquinariaCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_supervisor_or_above)
):
    # Verificar que el id_equipo no exista en la misma empresa
    existing = db.query(Maquinaria).filter(
        Maquinaria.id_equipo == equipo_data.id_equipo,
        Maquinaria.empresa_id == current_user.empresa_id
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ya existe un equipo con el código {equipo_data.id_equipo} en esta empresa"
        )

    # Verificar ubicacion si se provee
    if equipo_data.id_ubicacion:
        ubicacion = db.query(Ubicacion).filter(
            Ubicacion.id == equipo_data.id_ubicacion,
            Ubicacion.empresa_id == current_user.empresa_id
        ).first()
        if not ubicacion:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ubicación no encontrada o no pertenece a esta empresa"
            )

    # Verificar criticidad si se provee
    if equipo_data.id_criticidad:
        criticidad = db.query(Criticidad).filter(
            Criticidad.id == equipo_data.id_criticidad
        ).first()
        if not criticidad:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Nivel de criticidad no encontrado"
            )

    nuevo_equipo = Maquinaria(
        id_equipo=equipo_data.id_equipo,
        empresa_id=current_user.empresa_id,
        nombre_equipo=equipo_data.nombre_equipo,
        marca=equipo_data.marca,
        modelo=equipo_data.modelo,
        num_serie=equipo_data.num_serie,
        id_ubicacion=equipo_data.id_ubicacion,
        id_criticidad=equipo_data.id_criticidad,
        fecha_adquisicion=equipo_data.fecha_adquisicion,
        fecha_arranque=equipo_data.fecha_arranque,
        estado_actual=equipo_data.estado_actual,
        justificacion_criticidad=equipo_data.justificacion_criticidad
    )
    db.add(nuevo_equipo)
    db.commit()
    db.refresh(nuevo_equipo)
    return nuevo_equipo

@router.get("/", response_model=list[MaquinariaResponse])
def listar_equipos(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_any_authenticated_user)
):
    return db.query(Maquinaria).filter(
        Maquinaria.empresa_id == current_user.empresa_id
    ).all()

@router.get("/{id_equipo}", response_model=MaquinariaResponse)
def obtener_equipo(
    id_equipo: str,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_any_authenticated_user)
):
    equipo = db.query(Maquinaria).filter(
        Maquinaria.id_equipo == id_equipo,
        Maquinaria.empresa_id == current_user.empresa_id
    ).first()
    if not equipo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Equipo no encontrado"
        )
    return equipo

@router.put("/{id_equipo}", response_model=MaquinariaResponse)
def actualizar_equipo(
    id_equipo: str,
    equipo_data: MaquinariaCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_supervisor_or_above)
):
    equipo = db.query(Maquinaria).filter(
        Maquinaria.id_equipo == id_equipo,
        Maquinaria.empresa_id == current_user.empresa_id
    ).first()
    if not equipo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Equipo no encontrado"
        )

    equipo.nombre_equipo = equipo_data.nombre_equipo
    equipo.marca = equipo_data.marca
    equipo.modelo = equipo_data.modelo
    equipo.num_serie = equipo_data.num_serie
    equipo.id_ubicacion = equipo_data.id_ubicacion
    equipo.id_criticidad = equipo_data.id_criticidad
    equipo.fecha_adquisicion = equipo_data.fecha_adquisicion
    equipo.fecha_arranque = equipo_data.fecha_arranque
    equipo.estado_actual = equipo_data.estado_actual
    equipo.justificacion_criticidad = equipo_data.justificacion_criticidad

    db.commit()
    db.refresh(equipo)
    return equipo