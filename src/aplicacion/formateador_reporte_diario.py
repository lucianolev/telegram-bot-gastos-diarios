class FormateadorReporteDiario:
    def formatear(self, reporte):
        emoji_alerta = self._emoji_alerta(reporte)
        return (
            "📊 *CIERRE DEL DÍA*\n"
            "---"
            f"💰 *Gasto hoy:* ${reporte.total_hoy:,.0f}\n"
            f"🗓️ *Total acumulado:* ${reporte.total_ciclo:,.0f}\n"
            f"📈 *Promedio diario:* ${reporte.promedio_actual:,.0f}\n"
            f"{emoji_alerta} *Desviación:* ${reporte.desviacion:+,.0f} vs objetivo\n\n"
            f"_Ciclo de {reporte.dias_activos} días con actividad._"
        )

    def _emoji_alerta(self, reporte):
        if reporte.promedio_actual > reporte.limite_diario_objetivo:
            return "🚩"
        return "✅"
