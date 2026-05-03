from datetime import datetime

from src.dominio.gasto import Gasto


class RepositorioDeGastos:
    def __init__(
        self,
        base_de_datos,
        rango_gastos="Gastos!A:C",
        rango_limpieza="Gastos!A2:C5000",
    ):
        self._base_de_datos = base_de_datos
        self._rango_gastos = rango_gastos
        self._rango_limpieza = rango_limpieza

    def guardar(self, gasto):
        fila = self._serializar(gasto)
        self._base_de_datos.agregar_fila(self._rango_gastos, fila)

    def listar(self):
        filas = self._base_de_datos.leer_filas(self._rango_gastos)
        return self._mapear_filas(filas[1:])

    def vaciar_ciclo(self):
        self._base_de_datos.limpiar_rango(self._rango_limpieza)

    def _serializar(self, gasto):
        fecha_hora = gasto.fecha_hora.strftime("%Y-%m-%d %H:%M:%S")
        return [fecha_hora, gasto.usuario, gasto.monto]

    def _mapear_filas(self, filas):
        gastos = []
        for fila in filas:
            gasto = self._crear_gasto_desde_fila(fila)
            if gasto is not None:
                gastos.append(gasto)
        return gastos

    def _crear_gasto_desde_fila(self, fila):
        try:
            fecha_hora = datetime.strptime(fila[0], "%Y-%m-%d %H:%M:%S")
            monto = float(str(fila[2]).replace(",", ""))
            return Gasto(fecha_hora, fila[1], monto)
        except (IndexError, ValueError):
            return None
