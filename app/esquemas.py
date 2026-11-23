from pydantic import BaseModel, Field


class RutaBase(BaseModel):
    nombre: str = Field(min_length=3, max_length=60)
    tarifa: int = Field(ge=1, le=1000)
    zona: int = Field(ge=1, le=8)
    nocturna: bool = False


class RutaCrear(RutaBase):
    codigo: str = Field(pattern=r"^[A-Z]{3}\d{3}$")


class RutaActualizar(BaseModel):
    nombre: str | None = Field(default=None, min_length=3, max_length=60)
    tarifa: int | None = Field(default=None, ge=1, le=1000)
    zona: int | None = Field(default=None, ge=1, le=8)
    nocturno: bool | None = None


class Ruta(RutaCrear):
    """Lo que la API devuelve: los cinco campos completos."""