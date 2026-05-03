from dataclasses import dataclass


@dataclass(frozen=True)
class Gasto:
    fecha_hora: object
    usuario: str
    monto: float

    def fue_registrado_en(self, fecha):
        return self.fecha_hora.date() == fecha
