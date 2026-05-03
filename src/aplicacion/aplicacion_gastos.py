from src.dominio.gasto import Gasto
from src.dominio.reporte_diario import ReporteDiario


class AplicacionGastos:
    def __init__(
        self,
        grupo_gastos_id,
        limite_diario_objetivo,
        repositorio,
        asistente,
        reloj,
        formateador_reporte,
    ):
        self._grupo_gastos_id = grupo_gastos_id
        self._limite_diario_objetivo = limite_diario_objetivo
        self._repositorio = repositorio
        self._asistente = asistente
        self._reloj = reloj
        self._formateador_reporte = formateador_reporte

    def procesar_mensaje(self, mensaje):
        if not self._debe_procesarse(mensaje):
            return

        if self._es_comando_reinicio(mensaje):
            self._reiniciar_ciclo()
            return

        monto = self._extraer_monto(mensaje.texto)
        if monto is None:
            return

        self._registrar_gasto(mensaje, monto)

    def enviar_reporte_diario(self):
        gastos = self._repositorio.listar()
        if not gastos:
            self._asistente.enviar_mensaje(
                self._grupo_gastos_id,
                "⚠️ No hay gastos registrados en este ciclo todavía.",
            )
            return

        reporte = self._crear_reporte(gastos)
        texto = self._formateador_reporte.formatear(reporte)
        self._asistente.enviar_mensaje(self._grupo_gastos_id, texto)

    def _debe_procesarse(self, mensaje):
        return mensaje.chat_id == self._grupo_gastos_id

    def _es_comando_reinicio(self, mensaje):
        return mensaje.texto_normalizado().lower() == "empezar nuevo mes"

    def _extraer_monto(self, texto):
        texto_limpio = texto.replace(",", ".").strip()
        try:
            return float(texto_limpio)
        except ValueError:
            return None

    def _registrar_gasto(self, mensaje, monto):
        gasto = Gasto(self._reloj.ahora(), mensaje.usuario, monto)
        self._repositorio.guardar(gasto)
        texto = f"Registrado: *${monto:,.0f}* ✅"
        self._asistente.responder_a(mensaje, texto)

    def _reiniciar_ciclo(self):
        self._repositorio.vaciar_ciclo()
        self._asistente.enviar_mensaje(
            self._grupo_gastos_id,
            "🧹 *Ciclo reiniciado.* La planilla se ha vaciado para el nuevo mes.",
        )

    def _crear_reporte(self, gastos):
        fecha_actual = self._reloj.ahora().date()
        return ReporteDiario.desde_gastos(
            gastos,
            fecha_actual,
            self._limite_diario_objetivo,
        )
