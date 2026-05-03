from datetime import date, datetime
from unittest import TestCase

from src.dominio.gasto import Gasto
from src.dominio.reporte_diario import ReporteDiario


class TestReporteDiario(TestCase):
    def test_reporte_diario_calcula_totales_promedio_y_desviacion(self):
        gastos = [
            Gasto(datetime(2026, 5, 3, 10, 0, 0), "Ana", 1000),
            Gasto(datetime(2026, 5, 3, 12, 0, 0), "Bob", 500),
            Gasto(datetime(2026, 5, 2, 20, 0, 0), "Ana", 2500),
        ]

        reporte = ReporteDiario.desde_gastos(gastos, date(2026, 5, 3), 1500)

        self.assertEqual(1500, reporte.total_hoy)
        self.assertEqual(4000, reporte.total_ciclo)
        self.assertEqual(2, reporte.dias_activos)
        self.assertEqual(2000, reporte.promedio_actual)
        self.assertEqual(500, reporte.desviacion)