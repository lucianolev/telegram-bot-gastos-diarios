from datetime import datetime
from unittest import TestCase

from src.aplicacion.aplicacion_gastos import AplicacionGastos
from src.aplicacion.formateador_reporte_diario import FormateadorReporteDiario
from src.dominio.gasto import Gasto
from src.dominio.mensaje import Mensaje
from src.dominio.repositorio_de_gastos import RepositorioDeGastos


class TestAplicacionGastos(TestCase):
    def test_registra_gasto_cuando_recibe_un_numero_del_grupo_configurado(self):
        base_de_datos = BaseDeDatosFalsa()
        repositorio = RepositorioDeGastos(base_de_datos)
        asistente = AsistenteFalso()
        reloj = RelojFalso(datetime(2026, 5, 3, 22, 0, 0))
        aplicacion = AplicacionGastos(
            10,
            5000,
            repositorio,
            asistente,
            reloj,
            FormateadorReporteDiario(),
        )

        mensaje = Mensaje(chat_id=10, usuario="Ana", texto="1500")
        aplicacion.procesar_mensaje(mensaje)

        gastos = repositorio.listar()
        self.assertEqual(1, len(gastos))
        self.assertEqual("Ana", gastos[0].usuario)
        self.assertEqual(1500.0, gastos[0].monto)
        self.assertEqual("Registrado: *$1,500* ✅", asistente.respuestas[0][1])

    def test_ignora_mensajes_que_no_pertenecen_al_grupo(self):
        base_de_datos = BaseDeDatosFalsa()
        repositorio = RepositorioDeGastos(base_de_datos)
        asistente = AsistenteFalso()
        reloj = RelojFalso(datetime(2026, 5, 3, 22, 0, 0))
        aplicacion = AplicacionGastos(
            10,
            5000,
            repositorio,
            asistente,
            reloj,
            FormateadorReporteDiario(),
        )

        mensaje = Mensaje(chat_id=99, usuario="Ana", texto="1500")
        aplicacion.procesar_mensaje(mensaje)

        self.assertEqual([], repositorio.listar())
        self.assertEqual([], asistente.respuestas)

    def test_ignora_texto_que_no_es_ni_comando_ni_monto(self):
        base_de_datos = BaseDeDatosFalsa()
        repositorio = RepositorioDeGastos(base_de_datos)
        asistente = AsistenteFalso()
        reloj = RelojFalso(datetime(2026, 5, 3, 22, 0, 0))
        aplicacion = AplicacionGastos(
            10,
            5000,
            repositorio,
            asistente,
            reloj,
            FormateadorReporteDiario(),
        )

        mensaje = Mensaje(chat_id=10, usuario="Ana", texto="hola")
        aplicacion.procesar_mensaje(mensaje)

        self.assertEqual([], repositorio.listar())
        self.assertEqual([], asistente.respuestas)

    def test_reinicia_el_ciclo_con_el_comando_correspondiente(self):
        base_de_datos = BaseDeDatosFalsa()
        repositorio = RepositorioDeGastos(base_de_datos)
        asistente = AsistenteFalso()
        reloj = RelojFalso(datetime(2026, 5, 3, 22, 0, 0))
        aplicacion = AplicacionGastos(
            10,
            5000,
            repositorio,
            asistente,
            reloj,
            FormateadorReporteDiario(),
        )

        mensaje = Mensaje(chat_id=10, usuario="Ana", texto="empezar nuevo mes")
        aplicacion.procesar_mensaje(mensaje)

        self.assertEqual("Gastos!A2:C5000", base_de_datos.rango_limpiado)
        self.assertEqual(1, len(asistente.mensajes))

    def test_envia_reporte_diario_con_metricas_del_ciclo(self):
        base_de_datos = BaseDeDatosFalsa()
        repositorio = RepositorioDeGastos(base_de_datos)
        repositorio.guardar(Gasto(datetime(2026, 5, 3, 10, 0, 0), "Ana", 1000))
        repositorio.guardar(Gasto(datetime(2026, 5, 3, 12, 0, 0), "Bob", 500))
        repositorio.guardar(Gasto(datetime(2026, 5, 2, 20, 0, 0), "Ana", 2500))
        asistente = AsistenteFalso()
        reloj = RelojFalso(datetime(2026, 5, 3, 22, 0, 0))
        aplicacion = AplicacionGastos(
            10,
            1500,
            repositorio,
            asistente,
            reloj,
            FormateadorReporteDiario(),
        )

        aplicacion.enviar_reporte_diario()

        self.assertEqual(1, len(asistente.mensajes))
        self.assertIn("*Gasto hoy:* $1,500", asistente.mensajes[0][1])
        self.assertIn("*Total acumulado:* $4,000", asistente.mensajes[0][1])

    def test_avisa_cuando_no_hay_gastos(self):
        base_de_datos = BaseDeDatosFalsa()
        repositorio = RepositorioDeGastos(base_de_datos)
        asistente = AsistenteFalso()
        reloj = RelojFalso(datetime(2026, 5, 3, 22, 0, 0))
        aplicacion = AplicacionGastos(
            10,
            5000,
            repositorio,
            asistente,
            reloj,
            FormateadorReporteDiario(),
        )

        aplicacion.enviar_reporte_diario()

        self.assertEqual(
            "⚠️ No hay gastos registrados en este ciclo todavía.",
            asistente.mensajes[0][1],
        )


class BaseDeDatosFalsa:
    def __init__(self):
        self.filas = [["fecha", "usuario", "monto"]]
        self.rango_limpiado = None

    def agregar_fila(self, rango, valores):
        self.filas.append(valores)

    def leer_filas(self, rango):
        return list(self.filas)

    def limpiar_rango(self, rango):
        self.rango_limpiado = rango
        self.filas = [self.filas[0]]


class AsistenteFalso:
    def __init__(self):
        self.mensajes = []
        self.respuestas = []

    def enviar_mensaje(self, chat_id, texto):
        self.mensajes.append((chat_id, texto))

    def responder_a(self, mensaje, texto):
        self.respuestas.append((mensaje, texto))


class RelojFalso:
    def __init__(self, fecha_hora):
        self._fecha_hora = fecha_hora

    def ahora(self):
        return self._fecha_hora
