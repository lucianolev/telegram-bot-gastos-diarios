from typing import Any, Literal

import flask

from src.dominio.webserver import WebServer


class FlaskServer(WebServer):
    def __init__(self, aplicacion, asistente):
        self._aplicacion = aplicacion
        self._asistente = asistente
        self._app = flask.Flask(__name__)
        self._registrar_rutas()

    @property
    def app(self):
        return self._app

    def manejar(self, request):
        if self._es_envio_de_mensaje_por_chat(request):
            return self._manejar_post_de_mensaje_recibido(request)
        if self._es_pedido_programado_de_reporte_diario(request):
            return self._manejar_envio_de_reporte()

        return "Método no permitido", 405

    def _es_envio_de_mensaje_por_chat(self, request) -> Any:
        return request.method == "POST"

    def _es_pedido_programado_de_reporte_diario(self, request):
        return request.args.get("action") == "reporte"

    def _registrar_rutas(self):
        self._app.add_url_rule("/", view_func=self._index, methods=["GET", "POST"])

    def _index(self):
        return self.manejar(flask.request)

    def _manejar_envio_de_reporte(self):
        self._aplicacion.enviar_reporte_diario()
        return "Reporte enviado con éxito", 2

    def _manejar_post_de_mensaje_recibido(self, request):
        request_payload = request.get_json(force=True)
        mensaje = self._asistente.construir_mensaje(request_payload)
        if mensaje is not None:
            self._aplicacion.procesar_mensaje(mensaje)
        return "OK", 200
