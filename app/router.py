from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Query, status
from app.datos import RUTAS
from app.esquemas import Ruta, RutaActualizar, RutaCrear

router = APIRouter(prefix="/rutas", tags=["rutas"])


def obtener_ruta(codigo: str) -> dict:
    """Devuelve el diccionario de la rutas o lanza 404."""
    for ruta in RUTAS:
        if ruta["codigo"] == codigo.upper():
            return ruta
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"No existe la ruta '{codigo}'",
    )

RutaEncontrada = Annotated[dict, Depends(obtener_ruta)]

@router.get("", response_model=list[Ruta])
def listar_rutas(
    zona: Annotated[int | None, Query(ge=1, le=8)] = None,
    solo_obligatorias: bool = False,
) -> list[dict]:
    resultado = RUTAS
    if zona is not None:
        resultado = [m for m in resultado if m["zona"] == zona]
    if solo_obligatorias:
        resultado = [m for m in resultado if m["obligatoria"]]
    return resultado


@router.post("", response_model=Ruta, status_code=status.HTTP_201_CREATED)
def crear_ruta(nueva: RutaCrear) -> dict:
    if any(m["codigo"] == nueva.codigo for m in RUTAS):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"La ruta '{nueva.codigo}' ya existe",
        )
    RUTAS.append(nueva.model_dump())
    return RUTAS[-1]


@router.get("/{codigo}", response_model=Ruta)
def ver_ruta(ruta: RutaEncontrada) -> dict:
    return ruta


@router.put("/{codigo}", response_model=Ruta)
def actualizar_ruta(cambios: RutaActualizar, ruta: RutaEncontrada) -> dict:
    ruta.update(cambios.model_dump(exclude_unset=True))
    return ruta


@router.delete("/{codigo}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_ruta(ruta: RutaEncontrada) -> None:
    RUTAS.remove(ruta)