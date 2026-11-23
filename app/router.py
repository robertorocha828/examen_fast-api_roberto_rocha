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
    solo_nocturno: bool = False,
) -> list[dict]:
    resultado = RUTAS
    if zona is not None:
        resultado = [m for m in resultado if m["zona"] == zona]
    if solo_nocturno:
        resultado = [m for m in resultado if m["nocturno"]]
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

@router.get("/proyeccion", response_model=dict)
def calcular_proyeccion(
    frecuencias: Annotated[int, Query(ge=1, le=20)],
    zona: Annotated[int | None, Query(ge=1, le=8)] = None,) -> dict:
    seleccion = []
    for ruta in RUTAS:
        if zona is None or ruta["zona"] == zona:
            seleccion.append(ruta)

    if not seleccion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No hay ruta en la zona {zona}",
        )

    suma_tarifas = 0
    es_nocturna = 0

    for ruta in seleccion:
        suma_tarifas += ruta["tarifa"]
        if ruta["nocturno"]:
            es_nocturna += 1

    ingreso_base = suma_tarifas * frecuencias
    ingreso_estimado = suma_tarifas * frecuencias
    if es_nocturna:
        ingreso_estimado *= 1.20

    return {
        "rutas": len(seleccion),
        "frecuencias": frecuencias,
        "tarifa_promedio": round(suma_tarifas / len(seleccion), 2),
        "ingreso_base": ingreso_base,
        "Rutas con recargo": es_nocturna,
        "ingreso_estimado": ingreso_estimado,
        "porcentaje_nocturnas": round(es_nocturna / len(seleccion) * 100, 1),
    }

@router.get("/asignacion-rutas")
def resumen_rutas(
    asignadas: Annotated[list[str] | None, Query()] = None,) -> dict:
    codigos_asignados = {codigo.upper() for codigo in (asignadas or [])}

    if not RUTAS:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="No hay rutas registradas",)

    total = 0
    cantidad_asignadas = 0
    pendientes = 0
    tarifa_pendiente_total = 0
    pendiente_mas_cara = None
    tarifa_maxima_pendiente = None

    for ruta in RUTAS:
        total += 1
        if ruta["codigo"] in codigos_asignados:
            cantidad_asignadas += 1
        else:
            pendientes += 1
            tarifa = ruta["tarifa"]
            tarifa_pendiente_total += tarifa
            if tarifa_maxima_pendiente is None or tarifa > tarifa_maxima_pendiente:
                tarifa_maxima_pendiente = tarifa
                pendiente_mas_cara = ruta["codigo"]

    return {
        "total": total,
        "asignadas": cantidad_asignadas,
        "pendientes": pendientes,
        "porcentaje_cobertura": round(cantidad_asignadas / total * 100, 1),
        "tarifa_pendiente_total": tarifa_pendiente_total,
        "pendiente_mas_cara": pendiente_mas_cara,
    }



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

    