from dataclasses import dataclass


@dataclass(frozen=True)
class ReporteDiario:
    total_hoy: float
    total_ciclo: float
    promedio_actual: float
    desviacion: float
    dias_activos: int
    limite_diario_objetivo: float

    @classmethod
    def desde_gastos(cls, gastos, fecha_actual, limite_diario_objetivo):
        total_hoy = cls._total_hoy(gastos, fecha_actual)
        total_ciclo = cls._total_ciclo(gastos)
        dias_activos = cls._dias_activos(gastos)
        promedio = total_ciclo / dias_activos
        desviacion = promedio - limite_diario_objetivo
        return cls(
            total_hoy,
            total_ciclo,
            promedio,
            desviacion,
            dias_activos,
            limite_diario_objetivo,
        )

    @staticmethod
    def _total_hoy(gastos, fecha_actual):
        return sum(gasto.monto for gasto in gastos if gasto.fue_registrado_en(fecha_actual))

    @staticmethod
    def _total_ciclo(gastos):
        return sum(gasto.monto for gasto in gastos)

    @staticmethod
    def _dias_activos(gastos):
        fechas = {gasto.fecha_hora.date() for gasto in gastos}
        return len(fechas) or 1
